--!strict
-- Handabbau auf dem Client: Taste E halten (Handy/Controller: Prompt-Knopf halten) am Erz-Vorkommen
-- = jede Sekunde ein Schlag (Tempo aus dem Attribut SwingSeconds). Der Server entscheidet (PickaxeService).
-- Gefühl (Skill game-feel-juice), jeder Schlag reagiert sofort (≤ 0,1 s):
--   Ton (Tonhöhe steigt, je voller der Tragevorrat ist), Felsen staucht kurz und federt zurück,
--   Erz-Splitter fliegen, "+1" steigt auf. Voll: tiefer Ton, "Voll!", Hacken hört auf.
-- Abladen am Lager: "+10" über dem Kasten und ein heller Ton (BaseService meldet DepositResult).
-- Alle Feel-Zahlen in CONFIG.

local Players = game:GetService("Players")
local ProximityPromptService = game:GetService("ProximityPromptService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local SoundService = game:GetService("SoundService")
local TweenService = game:GetService("TweenService")

local Config = ReplicatedStorage:WaitForChild("Shared"):WaitForChild("Config")
local Bins = require(Config:WaitForChild("Bins"))
local BaseLayout = require(Config:WaitForChild("BaseLayout"))

local CONFIG = {
	-- Töne (eingebaute Roblox-Töne, in Studio geprüft: laden)
	SWING_SOUND = "rbxasset://sounds/metal.ogg",
	FULL_SOUND = "rbxasset://sounds/collide.wav",
	DEPOSIT_SOUND = "rbxasset://sounds/electronicpingshort.wav",
	SWING_VOLUME = 0.5,
	FULL_VOLUME = 0.4,
	DEPOSIT_VOLUME = 0.45,
	-- Ton-Leiter (Dur-Pentatonik), Stufe = wie voll der Tragevorrat nach dem Schlag ist
	SWING_PITCHES = { 0.84, 0.94, 1.06, 1.26, 1.41, 1.68 },
	FULL_PITCH = 0.7,
	DEPOSIT_PITCH = 1.0,
	-- Felsen stauchen und zurückfedern
	SQUASH_SCALE = 0.88,
	SQUASH_TIME = 0.06,
	SETTLE_TIME = 0.22,
	-- Splitter
	CHIP_COUNT = 6,
	CHIP_SPEED_MIN = 8,
	CHIP_SPEED_MAX = 14,
	CHIP_SIZE = 0.35,
	CHIP_LIFETIME = 0.5,
	-- Aufsteigende Zahl
	POPUP_START_OFFSET = 3,
	POPUP_RISE = 3,
	POPUP_TIME = 0.7,
	POPUP_COLOR = Color3.fromRGB(255, 214, 90),
	POPUP_BAD_COLOR = Color3.fromRGB(255, 150, 60),
	POPUP_DEPOSIT_COLOR = Color3.fromRGB(120, 240, 140),
	-- Wie lange der Client vor dem ersten Server-Wert mit 1 s rechnet
	DEFAULT_SWING_SECONDS = 1.0,
}

local MESSAGES: { [string]: string } = {
	full = "Voll!",
	too_hard = "Zu hart!",
	no_bin = "Kein Kasten!",
	bin_full = "Kasten voll!",
}

local PickaxeController = {}

local player = Players.LocalPlayer
local sounds: { [string]: Sound } = {}
local holdingPrompt: ProximityPrompt? = nil
local loopToken = 0
local punchToken: { [Model]: number } = {}
local swingEvent: RemoteEvent

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

local function nodeFromPrompt(prompt: ProximityPrompt): Model?
	if prompt.Name ~= "MinePrompt" then
		return nil
	end
	local model = prompt:FindFirstAncestorOfClass("Model")
	if model and model:GetAttribute("NodeId") then
		return model
	end
	return nil
end

local function nodeModelById(nodeId: string): Model?
	local root = workspace:FindFirstChild(BaseLayout.FOLDER_NAME)
	local nodes = root and root:FindFirstChild("OreNodes")
	local model = nodes and nodes:FindFirstChild(`GMT_PH_OreNode_{nodeId}`)
	return if model and model:IsA("Model") then model else nil
end

-- Felsen kurz stauchen und mit "Back" zurückfedern (nur auf diesem Client).
local function punch(model: Model)
	local token = (punchToken[model] or 0) + 1
	punchToken[model] = token
	local value = Instance.new("NumberValue")
	value.Value = 1
	value.Changed:Connect(function(v: number)
		if punchToken[model] == token and model.Parent then
			model:ScaleTo(v)
		end
	end)
	local down = TweenService:Create(
		value,
		TweenInfo.new(CONFIG.SQUASH_TIME, Enum.EasingStyle.Quad, Enum.EasingDirection.Out),
		{ Value = CONFIG.SQUASH_SCALE }
	)
	local up = TweenService:Create(
		value,
		TweenInfo.new(CONFIG.SETTLE_TIME, Enum.EasingStyle.Back, Enum.EasingDirection.Out),
		{ Value = 1 }
	)
	down.Completed:Connect(function()
		up:Play()
	end)
	up.Completed:Connect(function()
		if punchToken[model] == token and model.Parent then
			model:ScaleTo(1)
		end
		value:Destroy()
	end)
	down:Play()
end

local function chips(model: Model)
	local rock = model.PrimaryPart
	if not rock then
		return
	end
	local emitter = rock:FindFirstChild("GMT_Chips")
	if not emitter then
		local attachment = Instance.new("Attachment")
		attachment.Name = "GMT_ChipsAttachment"
		attachment.Position = Vector3.new(0, rock.Size.Y / 2 + 0.5, 0)
		attachment.Parent = rock
		local e = Instance.new("ParticleEmitter")
		e.Name = "GMT_Chips"
		e.Rate = 0
		e.Color = ColorSequence.new(BaseLayout.oreColors[model:GetAttribute("Ore") :: string] or Color3.new(1, 1, 1))
		e.Size = NumberSequence.new(CONFIG.CHIP_SIZE)
		e.Speed = NumberRange.new(CONFIG.CHIP_SPEED_MIN, CONFIG.CHIP_SPEED_MAX)
		e.SpreadAngle = Vector2.new(60, 60)
		e.Lifetime = NumberRange.new(CONFIG.CHIP_LIFETIME)
		e.Acceleration = Vector3.new(0, -workspace.Gravity, 0)
		e.EmissionDirection = Enum.NormalId.Top
		e.LightInfluence = 0
		e.Parent = attachment
		emitter = e
	end
	(emitter :: ParticleEmitter):Emit(CONFIG.CHIP_COUNT)
end

local function popup(adornee: BasePart, text: string, color: Color3)
	local gui = Instance.new("BillboardGui")
	gui.Name = "GMT_Popup"
	gui.Size = UDim2.fromOffset(160, 56)
	gui.StudsOffset = Vector3.new(0, CONFIG.POPUP_START_OFFSET, 0)
	gui.AlwaysOnTop = true
	gui.LightInfluence = 0
	gui.Adornee = adornee
	local label = Instance.new("TextLabel")
	label.Size = UDim2.fromScale(1, 1)
	label.BackgroundTransparency = 1
	label.Font = Enum.Font.FredokaOne
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
	TweenService:Create(gui, info, { StudsOffset = Vector3.new(0, CONFIG.POPUP_START_OFFSET + CONFIG.POPUP_RISE, 0) })
		:Play()
	local fadeInfo = TweenInfo.new(CONFIG.POPUP_TIME * 0.5, Enum.EasingStyle.Quad, Enum.EasingDirection.In, 0, false, CONFIG.POPUP_TIME * 0.5)
	TweenService:Create(label, fadeInfo, { TextTransparency = 1 }):Play()
	TweenService:Create(stroke, fadeInfo, { Transparency = 1 }):Play()
	task.delay(CONFIG.POPUP_TIME + 0.05, function()
		gui:Destroy()
	end)
end

local function pitchForFill(carried: number, capacity: number): number
	local ladder = CONFIG.SWING_PITCHES
	if capacity <= 0 then
		return ladder[1]
	end
	local ratio = math.clamp(carried / capacity, 0, 1)
	return ladder[1 + math.floor(ratio * (#ladder - 1) + 0.5)]
end

local function stopMining()
	holdingPrompt = nil
	loopToken += 1
end

-- Ein Schlag: sofort Ton und Stauchen (Vorhersage), Zahl kommt mit der Antwort des Servers.
local function swing(model: Model)
	local nodeId = model:GetAttribute("NodeId") :: string
	local carried = (player:GetAttribute("CarriedTotal") or 0) :: number
	local capacity = (player:GetAttribute("CarryCapacity") or 0) :: number
	if capacity > 0 and carried >= capacity then
		-- Schon voll: kein Schlag, nur Rückmeldung (der HUD-Hinweis sagt, wohin)
		play("Full", CONFIG.FULL_PITCH)
		if model.PrimaryPart then
			popup(model.PrimaryPart, MESSAGES.full, CONFIG.POPUP_BAD_COLOR)
		end
		stopMining()
		return
	end
	play("Swing", pitchForFill(carried + 1, capacity))
	punch(model)
	swingEvent:FireServer(nodeId)
end

local function startMining(prompt: ProximityPrompt, model: Model)
	holdingPrompt = prompt
	loopToken += 1
	local token = loopToken
	task.spawn(function()
		while holdingPrompt == prompt and loopToken == token and model.Parent do
			swing(model)
			local seconds = (player:GetAttribute("SwingSeconds") or CONFIG.DEFAULT_SWING_SECONDS) :: number
			task.wait(seconds)
		end
	end)
end

local function onPickaxeResult(nodeId: string, gained: number, carriedTotal: number, capacity: number, reason: string)
	local model = nodeModelById(nodeId)
	local rock = model and model.PrimaryPart
	if reason == "ok" then
		if model and rock then
			chips(model)
			popup(rock, `+{gained}`, CONFIG.POPUP_COLOR)
		end
		if carriedTotal >= capacity then
			play("Full", CONFIG.FULL_PITCH)
			if rock then
				task.delay(0.25, popup, rock, MESSAGES.full, CONFIG.POPUP_BAD_COLOR)
			end
			stopMining()
		end
	elseif reason == "cooldown" then
		return -- zu schnell geklickt, einfach ignorieren
	else
		local message = MESSAGES[reason]
		if message and rock then
			popup(rock, message, CONFIG.POPUP_BAD_COLOR)
		end
		if reason ~= "too_far" then
			play("Full", CONFIG.FULL_PITCH)
		end
		stopMining()
	end
end

local function binLabel(oreId: string): BasePart?
	local binId = (Bins.byOre :: any)[oreId]
	local root = workspace:FindFirstChild(BaseLayout.FOLDER_NAME)
	local bin = root and root:FindFirstChild(`GMT_PH_StorageBin_{binId}`, true)
	local labelPart = bin and bin:FindFirstChild("Label")
	return if labelPart and labelPart:IsA("BasePart") then labelPart else nil
end

local function onDepositResult(oreId: string, moved: number, _binAmount: number, _binCapacity: number, reason: string)
	local labelPart = binLabel(oreId)
	if moved > 0 then
		play("Deposit", CONFIG.DEPOSIT_PITCH)
		if labelPart then
			popup(labelPart, `+{moved}`, CONFIG.POPUP_DEPOSIT_COLOR)
		end
	end
	if reason == "bin_full" then
		play("Full", CONFIG.FULL_PITCH)
		if labelPart then
			task.delay(if moved > 0 then 0.3 else 0, popup, labelPart, MESSAGES.bin_full, CONFIG.POPUP_BAD_COLOR)
		end
	end
end

function PickaxeController.Init()
	sounds.Swing = makeSound("Swing", CONFIG.SWING_SOUND, CONFIG.SWING_VOLUME)
	sounds.Full = makeSound("Full", CONFIG.FULL_SOUND, CONFIG.FULL_VOLUME)
	sounds.Deposit = makeSound("Deposit", CONFIG.DEPOSIT_SOUND, CONFIG.DEPOSIT_VOLUME)
end

function PickaxeController.Start()
	local remotes = ReplicatedStorage:WaitForChild("GMT_Remotes")
	swingEvent = remotes:WaitForChild("SwingPickaxe") :: RemoteEvent
	;(remotes:WaitForChild("PickaxeResult") :: RemoteEvent).OnClientEvent:Connect(onPickaxeResult)
	;(remotes:WaitForChild("DepositResult") :: RemoteEvent).OnClientEvent:Connect(onDepositResult)

	ProximityPromptService.PromptTriggered:Connect(function(prompt: ProximityPrompt)
		local model = nodeFromPrompt(prompt)
		if model then
			startMining(prompt, model)
		end
	end)
	ProximityPromptService.PromptTriggerEnded:Connect(function(prompt: ProximityPrompt)
		if prompt == holdingPrompt then
			stopMining()
		end
	end)
	ProximityPromptService.PromptHidden:Connect(function(prompt: ProximityPrompt)
		if prompt == holdingPrompt then
			stopMining() -- weggelaufen
		end
	end)
	print("[PickaxeController] Handabbau bereit (E halten am Erz)")
end

return PickaxeController
