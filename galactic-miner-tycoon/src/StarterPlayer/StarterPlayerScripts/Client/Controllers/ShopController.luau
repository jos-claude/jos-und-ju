--!strict
-- Rückmeldung auf dem Client für Kauffelder und Bohrer (Schritt 5 und 6). Entscheiden tut der Server
-- (ShopService, DrillService); hier gibt es nur Ton und Animation (Skill game-feel-juice):
--   Kauf:       zwei helle Töne (kleiner Akkord), Feld federt, Meldung steigt auf
--   Zu teuer:   tiefer Ton, "Zu wenig Eisen" steigt auf
--   Aufstellen: Bohrer wächst mit "Back" auf volle Größe, dumpfer Metall-Ton
--   Erz holen:  "+N" über dem Bohrer, Ton steigt mit der Menge
--   Bohrkopf dreht sich, solange der Puffer nicht voll ist
-- Töne sind Platzhalter (eingebaute Roblox-Töne), später austauschbar. Alle Feel-Zahlen in CONFIG.

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local SoundService = game:GetService("SoundService")
local TweenService = game:GetService("TweenService")

local Config = ReplicatedStorage:WaitForChild("Shared"):WaitForChild("Config")
local BaseLayout = require(Config:WaitForChild("BaseLayout"))

local CONFIG = {
	-- Töne (eingebaute Roblox-Töne, Platzhalter)
	BUY_SOUND = "rbxasset://sounds/electronicpingshort.wav",
	BUY_VOLUME = 0.5,
	BUY_PITCHES = { 1.26, 1.68 }, -- zwei Töne der Dur-Pentatonik nacheinander
	BUY_CHORD_DELAY = 0.09,
	FAIL_SOUND = "rbxasset://sounds/collide.wav",
	FAIL_VOLUME = 0.35,
	FAIL_PITCH = 0.7,
	PLACE_SOUND = "rbxasset://sounds/metal.ogg",
	PLACE_VOLUME = 0.6,
	PLACE_PITCH = 0.62,
	TAKE_SOUND = "rbxasset://sounds/electronicpingshort.wav",
	TAKE_VOLUME = 0.4,
	TAKE_PITCH_MIN = 0.94, -- wenig Erz
	TAKE_PITCH_MAX = 1.41, -- 25 Erz und mehr
	TAKE_PITCH_FULL_AT = 25,
	-- Feld federt beim Kauf
	PAD_SQUASH = 0.85,
	PAD_SQUASH_TIME = 0.07,
	PAD_SETTLE_TIME = 0.25,
	-- Bohrer erscheint
	PLACE_START_SCALE = 0.4,
	PLACE_GROW_TIME = 0.35,
	-- Bohrkopf
	BIT_SPIN_SPEED = 6, -- Umdrehungen (rad) pro Sekunde
	-- Aufsteigende Meldung
	POPUP_START_OFFSET = 5,
	POPUP_RISE = 3,
	POPUP_TIME = 1.1,
	POPUP_GOOD = Color3.fromRGB(120, 240, 140),
	POPUP_BAD = Color3.fromRGB(255, 150, 60),
	POPUP_ORE = Color3.fromRGB(255, 214, 90),
}

local DRILL_MESSAGES: { [string]: string } = {
	empty = "Leer",
	full = "Voll!",
	no_drill = "Erst einen Bohrer kaufen",
	occupied = "Hier steht schon einer",
	too_far = "Zu weit weg",
}

local ShopController = {}

local sounds: { [string]: Sound } = {}
local animToken: { [Model]: number } = {}

local function makeSound(name: string, id: string, volume: number): Sound
	local folder = SoundService:FindFirstChild("GMT_Sfx") or Instance.new("Folder")
	folder.Name = "GMT_Sfx"
	folder.Parent = SoundService
	local sound = Instance.new("Sound")
	sound.Name = name
	sound.SoundId = id
	sound.Volume = volume
	sound.Parent = folder
	return sound
end

local function play(name: string, pitch: number)
	local sound = sounds[name]
	if sound then
		sound.PlaybackSpeed = pitch
		sound.TimePosition = 0
		sound:Play()
	end
end

local function gameplayChild(name: string): Instance?
	local root = workspace:FindFirstChild(BaseLayout.FOLDER_NAME)
	return root and root:FindFirstChild(name)
end

local function padModel(padId: string): Model?
	local pads = gameplayChild("BuyPads")
	local model = pads and pads:FindFirstChild(`GMT_PH_BuyPad_{padId}`)
	return if model and model:IsA("Model") then model else nil
end

-- Teil mit der Puffer-Anzeige (3D-Modell: Drill_MotorHead, Greybox: Motor).
local function motorOf(model: Model): BasePart?
	local gui = model:FindFirstChild("BufferGui", true)
	local motor = gui and gui.Parent
	return if motor and motor:IsA("BasePart") then motor else nil
end

local function drillModel(nodeId: string): Model?
	local drills = gameplayChild("Drills")
	local model = drills and drills:FindFirstChild(`GMT_Drill_{nodeId}`)
	return if model and model:IsA("Model") then model else nil
end

-- Modell lokal skalieren: von `from` über `via` (optional) auf 1. Nur auf diesem Client.
local function animateScale(model: Model, from: number, via: number?, firstTime: number, settleTime: number)
	local token = (animToken[model] or 0) + 1
	animToken[model] = token
	local value = Instance.new("NumberValue")
	value.Value = from
	value.Changed:Connect(function(v: number)
		if animToken[model] == token and model.Parent then
			model:ScaleTo(v)
		end
	end)
	local function finish()
		if animToken[model] == token and model.Parent then
			model:ScaleTo(1)
		end
		value:Destroy()
	end
	local settle = TweenService:Create(
		value,
		TweenInfo.new(settleTime, Enum.EasingStyle.Back, Enum.EasingDirection.Out),
		{ Value = 1 }
	)
	settle.Completed:Connect(finish)
	if via then
		local first = TweenService:Create(
			value,
			TweenInfo.new(firstTime, Enum.EasingStyle.Quad, Enum.EasingDirection.Out),
			{ Value = via }
		)
		first.Completed:Connect(function()
			settle:Play()
		end)
		first:Play()
	else
		if animToken[model] == token and model.Parent then
			model:ScaleTo(from)
		end
		settle:Play()
	end
end

local function popup(adornee: BasePart, text: string, color: Color3)
	local gui = Instance.new("BillboardGui")
	gui.Name = "GMT_Popup"
	gui.Size = UDim2.fromOffset(260, 48)
	gui.StudsOffset = Vector3.new(0, CONFIG.POPUP_START_OFFSET, 0)
	gui.AlwaysOnTop = true
	gui.LightInfluence = 0
	gui.Adornee = adornee
	local label = Instance.new("TextLabel")
	label.Size = UDim2.fromScale(1, 1)
	label.BackgroundTransparency = 1
	label.Font = Enum.Font.FredokaOne
	label.TextWrapped = true
	label.TextScaled = true
	label.TextColor3 = color
	label.Text = text
	local stroke = Instance.new("UIStroke")
	stroke.Thickness = 2
	stroke.Color = Color3.fromRGB(30, 20, 10)
	stroke.Parent = label
	label.Parent = gui
	gui.Parent = adornee

	local info = TweenInfo.new(CONFIG.POPUP_TIME, Enum.EasingStyle.Quad, Enum.EasingDirection.Out)
	TweenService:Create(gui, info, { StudsOffset = Vector3.new(0, CONFIG.POPUP_START_OFFSET + CONFIG.POPUP_RISE, 0) }):Play()
	local fadeInfo =
		TweenInfo.new(CONFIG.POPUP_TIME * 0.4, Enum.EasingStyle.Quad, Enum.EasingDirection.In, 0, false, CONFIG.POPUP_TIME * 0.6)
	TweenService:Create(label, fadeInfo, { TextTransparency = 1 }):Play()
	TweenService:Create(stroke, fadeInfo, { Transparency = 1 }):Play()
	task.delay(CONFIG.POPUP_TIME + 0.05, function()
		gui:Destroy()
	end)
end

local function onShopResult(padId: string, ok: boolean, _reason: string, text: string)
	local model = padModel(padId)
	local plate = model and model.PrimaryPart
	if ok then
		play("Buy", CONFIG.BUY_PITCHES[1])
		task.delay(CONFIG.BUY_CHORD_DELAY, function()
			play("Buy2", CONFIG.BUY_PITCHES[2])
		end)
		if model then
			animateScale(model, 1, CONFIG.PAD_SQUASH, CONFIG.PAD_SQUASH_TIME, CONFIG.PAD_SETTLE_TIME)
		end
		if plate then
			popup(plate, text, CONFIG.POPUP_GOOD)
		end
	else
		play("Fail", CONFIG.FAIL_PITCH)
		if plate then
			popup(plate, text, CONFIG.POPUP_BAD)
		end
	end
end

local function onDrillResult(kind: string, nodeId: string, amount: number)
	if kind == "placed" then
		play("Place", CONFIG.PLACE_PITCH)
		-- Das Modell kommt per Replikation evtl. erst kurz nach der Meldung an.
		task.spawn(function()
			local drills = gameplayChild("Drills")
			local model = drills and drills:WaitForChild(`GMT_Drill_{nodeId}`, 2)
			if model and model:IsA("Model") then
				animateScale(model, CONFIG.PLACE_START_SCALE, nil, 0, CONFIG.PLACE_GROW_TIME)
				local motor = motorOf(model)
				if motor then
					popup(motor, "Bohrer läuft!", CONFIG.POPUP_GOOD)
				end
			end
		end)
		return
	end
	local model = drillModel(nodeId)
	local motor = model and motorOf(model)
	if kind == "taken" then
		local t = math.clamp(amount / CONFIG.TAKE_PITCH_FULL_AT, 0, 1)
		play("Take", CONFIG.TAKE_PITCH_MIN + (CONFIG.TAKE_PITCH_MAX - CONFIG.TAKE_PITCH_MIN) * t)
		if motor then
			popup(motor, `+{amount}`, CONFIG.POPUP_ORE)
		end
		return
	end
	play("Fail", CONFIG.FAIL_PITCH)
	local text = DRILL_MESSAGES[kind]
	if text and motor then
		popup(motor, text, CONFIG.POPUP_BAD)
	end
end

-- Bohrköpfe drehen (nur lokal, jeder gerenderte Frame). Voller Puffer = Stillstand.
-- Gedreht werden alle Teile mit dem Attribut Spin, um die senkrechte Achse durch ihre Mitte.
local spinParts: { [Model]: { BasePart } } = {}

local function partsToSpin(model: Model): { BasePart }
	local list = spinParts[model]
	if not list then
		list = {}
		for _, d in model:GetDescendants() do
			if d:IsA("BasePart") and d:GetAttribute("Spin") == true then
				table.insert(list, d)
			end
		end
		if #list > 0 then -- leer = Teile noch nicht repliziert, nächsten Frame neu suchen
			spinParts[model] = list
			model.Destroying:Once(function()
				spinParts[model] = nil
			end)
		end
	end
	return list :: { BasePart }
end

local function spinBits(dt: number)
	local drills = gameplayChild("Drills")
	if not drills then
		return
	end
	local turn = CFrame.Angles(0, CONFIG.BIT_SPIN_SPEED * dt, 0)
	for _, model in drills:GetChildren() do
		if model:IsA("Model") and model:GetAttribute("Full") ~= true then
			for _, p in partsToSpin(model) do
				local pos = p.Position
				p.CFrame = CFrame.new(pos) * turn * (p.CFrame - pos)
			end
		end
	end
end

function ShopController.Init()
	sounds.Buy = makeSound("Buy", CONFIG.BUY_SOUND, CONFIG.BUY_VOLUME)
	sounds.Buy2 = makeSound("Buy2", CONFIG.BUY_SOUND, CONFIG.BUY_VOLUME)
	sounds.Fail = makeSound("ShopFail", CONFIG.FAIL_SOUND, CONFIG.FAIL_VOLUME)
	sounds.Place = makeSound("DrillPlace", CONFIG.PLACE_SOUND, CONFIG.PLACE_VOLUME)
	sounds.Take = makeSound("DrillTake", CONFIG.TAKE_SOUND, CONFIG.TAKE_VOLUME)
end

function ShopController.Start()
	local remotes = ReplicatedStorage:WaitForChild("GMT_Remotes", 30)
	if not remotes then
		warn("[ShopController] GMT_Remotes fehlt")
		return
	end
	local shopResult = remotes:WaitForChild("ShopResult", 30)
	local drillResult = remotes:WaitForChild("DrillResult", 30)
	if shopResult and shopResult:IsA("RemoteEvent") then
		shopResult.OnClientEvent:Connect(onShopResult)
	end
	if drillResult and drillResult:IsA("RemoteEvent") then
		drillResult.OnClientEvent:Connect(onDrillResult)
	end
	RunService.RenderStepped:Connect(spinBits)
end

return ShopController
