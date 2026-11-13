--!strict
-- Bohrer-Modell (Schritt 5): bevorzugt das 3D-Modell drill_iron (assets/asset-liste.md, Kopie über
-- GameModels), sonst ein Greybox-Platzhalter. Beide bekommen dieselben Teile mit Bedeutung:
--   BufferGui (Puffer "30/50" über dem Motor), TakePrompt ("Erz holen", Taste F),
--   Attribute NodeId, DrillId, Buffer, BufferCap, Full; Teile mit Attribut Spin drehen sich (Client).
-- Das 3D-Modell steht NEBEN dem Felsen, der Bohrkopf steckt im Felsen (Sockel schaut zum Felsen).
-- Der Greybox-Bohrer steht mit vier Beinen ÜBER dem Felsen.

local Greybox = require(script.Parent:WaitForChild("Greybox"))
local GameModels = require(script.Parent:WaitForChild("GameModels"))

local part = Greybox.part
local COLORS = Greybox.COLORS

local GreyboxDrill = {}

GreyboxDrill.PLATFORM_HEIGHT = 4.6 -- Greybox: Unterkante der Plattform über dem Boden (Felsen ca. 3,4 hoch)
GreyboxDrill.LEG_OFFSET = 3.9 -- Greybox: Abstand der Beine von der Mitte (Felsen reicht ca. 4,3 diagonal)

-- Teile im 3D-Modell drill_iron (Namen aus dem Import)
local MODEL_MOTOR = "Drill_MotorHead"
local MODEL_BODY = "Drill_Body"
local MODEL_BIT = "Drill_Bit"
local MODEL_SINK = 0.05 -- etwas einsinken lassen, damit keine Lücke zum Boden bleibt

local FULL_COLOR = Color3.fromRGB(255, 150, 60)
local TEXT_COLOR = Color3.fromRGB(255, 255, 255)

export type DrillModel = {
	model: Model,
	motor: BasePart,
	label: TextLabel,
	bar: Frame,
	prompt: ProximityPrompt,
}

function GreyboxDrill.modelName(nodeId: string): string
	return `GMT_Drill_{nodeId}`
end

-- Puffer-Anzeige über `adornee` (Billboard, immer zur Kamera gedreht).
local function bufferGui(adornee: BasePart, oreColor: Color3, offsetY: number): (TextLabel, Frame)
	local gui = Instance.new("BillboardGui")
	gui.Name = "BufferGui"
	gui.Size = UDim2.new(6, 0, 2.2, 0)
	gui.StudsOffset = Vector3.new(0, offsetY, 0)
	gui.MaxDistance = 150
	gui.LightInfluence = 0
	gui.AlwaysOnTop = false
	local frame = Instance.new("Frame")
	frame.Name = "Panel"
	frame.Size = UDim2.fromScale(1, 1)
	frame.BackgroundColor3 = Color3.fromRGB(28, 30, 44)
	frame.BackgroundTransparency = 0.2
	frame.Parent = gui
	local corner = Instance.new("UICorner")
	corner.CornerRadius = UDim.new(0.2, 0)
	corner.Parent = frame
	local label = Instance.new("TextLabel")
	label.Name = "Value"
	label.BackgroundTransparency = 1
	label.Size = UDim2.fromScale(1, 0.64)
	label.Font = Enum.Font.FredokaOne
	label.TextColor3 = TEXT_COLOR
	label.TextWrapped = true
	label.TextScaled = true
	label.Text = "0/0"
	label.Parent = frame
	local barBack = Instance.new("Frame")
	barBack.Name = "BarBack"
	barBack.Position = UDim2.fromScale(0.08, 0.7)
	barBack.Size = UDim2.fromScale(0.84, 0.18)
	barBack.BackgroundColor3 = Color3.fromRGB(60, 62, 78)
	barBack.BorderSizePixel = 0
	barBack.Parent = frame
	local bar = Instance.new("Frame")
	bar.Name = "Bar"
	bar.Size = UDim2.fromScale(0, 1)
	bar.BackgroundColor3 = oreColor
	bar.BorderSizePixel = 0
	bar.Parent = barBack
	gui.Parent = adornee
	return label, bar
end

-- Erz aus dem Puffer holen. Taste F, damit es nicht mit "Hacken" (E) am Felsen kollidiert.
local function takePrompt(parent: BasePart, promptDistance: number): ProximityPrompt
	local prompt = Instance.new("ProximityPrompt")
	prompt.Name = "TakePrompt"
	prompt.ActionText = "Erz holen"
	prompt.ObjectText = "Bohrer"
	prompt.HoldDuration = 0
	prompt.KeyboardKeyCode = Enum.KeyCode.F
	prompt.GamepadKeyCode = Enum.KeyCode.ButtonY
	prompt.MaxActivationDistance = promptDistance
	prompt.RequiresLineOfSight = false
	prompt.UIOffset = Vector2.new(0, -60)
	prompt.Parent = parent
	return prompt
end

local function tag(model: Model, nodeId: string, drillId: string)
	model.Name = GreyboxDrill.modelName(nodeId)
	model:SetAttribute("NodeId", nodeId)
	model:SetAttribute("DrillId", drillId)
end

-- 3D-Modell neben den Felsen stellen. Gibt nil zurück, wenn das Modell fehlt.
-- facing = waagerechte Richtung vom Felsen zur Stelle, an der der Sockel stehen soll.
function GreyboxDrill.buildFromModel(
	modelName: string,
	parent: Instance,
	nodeId: string,
	drillId: string,
	rockX: number,
	rockZ: number,
	facing: Vector3,
	offset: number,
	groundAt: (x: number, z: number) -> number,
	oreColor: Color3,
	promptDistance: number
): DrillModel?
	local model = GameModels.clone(modelName)
	if not model then
		return nil
	end
	local motor = model:FindFirstChild(MODEL_MOTOR, true)
	local body = model:FindFirstChild(MODEL_BODY, true)
	local bit = model:FindFirstChild(MODEL_BIT, true)
	if not (motor and motor:IsA("BasePart") and body and body:IsA("BasePart")) then
		warn(`[GreyboxDrill] {modelName} hat kein {MODEL_MOTOR}/{MODEL_BODY}, nehme Greybox`)
		model:Destroy()
		return nil
	end
	tag(model, nodeId, drillId)

	local dir = Vector3.new(facing.X, 0, facing.Z)
	dir = if dir.Magnitude > 0.01 then dir.Unit else Vector3.new(0, 0, 1)
	local baseX, baseZ = rockX + dir.X * offset, rockZ + dir.Z * offset
	local y = groundAt(baseX, baseZ) - MODEL_SINK
	-- Der Bohrkopf liegt im Modell auf der -Z-Seite der Sockel-Mitte: lookAt zeigt mit -Z zum Felsen.
	model:PivotTo(CFrame.lookAt(Vector3.new(baseX, y, baseZ), Vector3.new(rockX, y, rockZ)))

	if bit and bit:IsA("BasePart") then
		bit.CanCollide = false -- steckt im Felsen
		bit:SetAttribute("Spin", true)
	end
	local label, bar = bufferGui(motor, oreColor, 3.2)
	local prompt = takePrompt(body, promptDistance)
	model.Parent = parent
	return { model = model, motor = motor, label = label, bar = bar, prompt = prompt }
end

-- Greybox-Bohrer (Ersatz, wenn das 3D-Modell fehlt): vier Stahlbeine über dem Felsen.
function GreyboxDrill.buildDrill(
	parent: Instance,
	nodeId: string,
	drillId: string,
	x: number,
	z: number,
	groundY: number,
	oreColor: Color3,
	promptDistance: number
): DrillModel
	local model = Instance.new("Model")
	tag(model, nodeId, drillId)

	local top = groundY + GreyboxDrill.PLATFORM_HEIGHT
	local legHeight = GreyboxDrill.PLATFORM_HEIGHT + 0.3 -- etwas in den Boden
	for i, offset in { Vector2.new(1, 1), Vector2.new(-1, 1), Vector2.new(1, -1), Vector2.new(-1, -1) } do
		part(
			`Leg{i}`,
			Vector3.new(0.7, legHeight, 0.7),
			CFrame.new(
				x + offset.X * GreyboxDrill.LEG_OFFSET,
				groundY - 0.3 + legHeight / 2,
				z + offset.Y * GreyboxDrill.LEG_OFFSET
			),
			COLORS.steel,
			Enum.Material.Metal,
			model
		)
	end
	local platform = part(
		"Platform",
		Vector3.new(GreyboxDrill.LEG_OFFSET * 2 + 1.2, 0.8, GreyboxDrill.LEG_OFFSET * 2 + 1.2),
		CFrame.new(x, top + 0.4, z),
		COLORS.orange,
		nil,
		model
	)
	local motor = part("Motor", Vector3.new(3.4, 3, 3.4), CFrame.new(x, top + 0.8 + 1.5, z), COLORS.orange, nil, model)
	part(
		"Stripe",
		Vector3.new(3.5, 0.5, 3.5),
		CFrame.new(x, top + 0.8 + 2.4, z),
		COLORS.steelDark,
		Enum.Material.Metal,
		model
	)
	-- Bohrkopf: Zylinder (liegt in Roblox entlang X, darum um Z gedreht), reicht bis in den Felsen.
	local bitLength = GreyboxDrill.PLATFORM_HEIGHT - 1.4
	local bit = part(
		"Bit",
		Vector3.new(bitLength, 1.4, 1.4),
		CFrame.new(x, top - bitLength / 2, z) * CFrame.Angles(0, 0, math.rad(90)),
		COLORS.steel,
		Enum.Material.DiamondPlate,
		model
	)
	bit.Shape = Enum.PartType.Cylinder
	bit.CanCollide = false
	bit:SetAttribute("Spin", true)
	-- Farbiger Ring am Bohrkopf: zeigt, welches Erz er fördert.
	local ring = part(
		"OreRing",
		Vector3.new(0.4, 1.8, 1.8),
		CFrame.new(x, top - 0.5, z) * CFrame.Angles(0, 0, math.rad(90)),
		oreColor,
		Enum.Material.SmoothPlastic,
		model
	)
	ring.Shape = Enum.PartType.Cylinder
	ring.CanCollide = false
	ring:SetAttribute("Spin", true)

	model.PrimaryPart = platform
	local label, bar = bufferGui(motor, oreColor, 3.4)
	local prompt = takePrompt(platform, promptDistance)
	model.Parent = parent
	return { model = model, motor = motor, label = label, bar = bar, prompt = prompt }
end

function GreyboxDrill.setBuffer(drill: DrillModel, buffer: number, capacity: number)
	local full = buffer >= capacity
	drill.label.Text = if full then `VOLL {buffer}/{capacity}` else `{buffer}/{capacity}`
	drill.label.TextColor3 = if full then FULL_COLOR else TEXT_COLOR
	drill.bar.Size = UDim2.fromScale(if capacity > 0 then math.clamp(buffer / capacity, 0, 1) else 0, 1)
	drill.model:SetAttribute("Buffer", buffer)
	drill.model:SetAttribute("BufferCap", capacity)
	drill.model:SetAttribute("Full", full)
end

return GreyboxDrill
