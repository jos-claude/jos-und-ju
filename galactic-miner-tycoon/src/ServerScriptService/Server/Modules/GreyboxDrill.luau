--!strict
-- Greybox-Platzhalter für einen Bohrer (Schritt 5): vier Stahlbeine über dem Felsen des Vorkommens,
-- orange Plattform, Motor-Block, Bohrkopf nach unten in den Felsen, Puffer-Anzeige "30/50" darüber.
-- Später ersetzt durch Jos' Modell drill_iron: dann nur buildDrill austauschen. Die Namen mit
-- Bedeutung bleiben gleich (Bit, Motor, TakePrompt, BufferGui, Attribute NodeId/DrillId/Buffer/BufferCap).

local Greybox = require(script.Parent:WaitForChild("Greybox"))

local part = Greybox.part
local COLORS = Greybox.COLORS

local GreyboxDrill = {}

GreyboxDrill.PLATFORM_HEIGHT = 4.6 -- Unterkante der Plattform über dem Boden (Felsen ist ca. 3,4 hoch)
GreyboxDrill.LEG_OFFSET = 3.9 -- Abstand der Beine von der Mitte (Felsen reicht ca. 4,3 diagonal)

local FULL_COLOR = Color3.fromRGB(255, 150, 60)
local TEXT_COLOR = Color3.fromRGB(255, 255, 255)

export type DrillModel = {
	model: Model,
	motor: BasePart,
	bit: BasePart,
	label: TextLabel,
	bar: Frame,
	prompt: ProximityPrompt,
}

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
	model.Name = `GMT_PH_Drill_{nodeId}`
	model:SetAttribute("NodeId", nodeId)
	model:SetAttribute("DrillId", drillId)

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

	model.PrimaryPart = platform

	-- Puffer-Anzeige über dem Motor (Billboard, immer zur Kamera gedreht).
	local gui = Instance.new("BillboardGui")
	gui.Name = "BufferGui"
	gui.Size = UDim2.new(6, 0, 2.2, 0)
	gui.StudsOffset = Vector3.new(0, 3.4, 0)
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
	gui.Parent = motor

	-- Erz aus dem Puffer holen. Taste F, damit es nicht mit "Hacken" (E) am Felsen kollidiert.
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
	prompt.Parent = platform

	model.Parent = parent
	return { model = model, motor = motor, bit = bit, label = label, bar = bar, prompt = prompt }
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
