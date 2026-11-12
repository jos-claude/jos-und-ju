--!strict
-- Greybox-Platzhalter für Start-Halle, Lager-Kasten und Erz-Vorkommen (Schritt 3).
-- Einfache Boxen in Orange und Stahlgrau. Alles heißt GMT_PH_... und liegt in Workspace.GMT_Gameplay.
-- Später ersetzt Jos sie durch seine Modelle: dann nur die build-Funktionen hier austauschen,
-- die Namen der Teile mit Bedeutung (Fill, Label, MinePrompt, Attribute) bleiben gleich.

local Greybox = {}

Greybox.COLORS = {
	orange = Color3.fromRGB(232, 128, 52),
	steel = Color3.fromRGB(120, 128, 138),
	steelDark = Color3.fromRGB(70, 76, 86),
	floor = Color3.fromRGB(150, 156, 162),
	glass = Color3.fromRGB(190, 225, 240),
	dropZone = Color3.fromRGB(90, 200, 110),
	rock = Color3.fromRGB(92, 84, 80),
	signText = Color3.fromRGB(255, 244, 228),
}

local COLORS = Greybox.COLORS

local function part(
	name: string,
	size: Vector3,
	cframe: CFrame,
	color: Color3,
	material: Enum.Material?,
	parent: Instance
): Part
	local p = Instance.new("Part")
	p.Name = name
	p.Size = size
	p.CFrame = cframe
	p.Color = color
	p.Material = material or Enum.Material.SmoothPlastic
	p.Anchored = true
	p.TopSurface = Enum.SurfaceType.Smooth
	p.BottomSurface = Enum.SurfaceType.Smooth
	p.Parent = parent
	return p
end

local function surfaceText(target: BasePart, face: Enum.NormalId, text: string, textColor: Color3): TextLabel
	local gui = Instance.new("SurfaceGui")
	gui.Name = "SignGui"
	gui.Face = face
	gui.SizingMode = Enum.SurfaceGuiSizingMode.PixelsPerStud
	gui.PixelsPerStud = 40
	gui.LightInfluence = 0
	local label = Instance.new("TextLabel")
	label.Name = "Text"
	label.Size = UDim2.fromScale(1, 1)
	label.BackgroundTransparency = 1
	label.TextColor3 = textColor
	label.Font = Enum.Font.FredokaOne
	label.TextScaled = true
	label.Text = text
	label.Parent = gui
	gui.Parent = target
	return label
end

-- Start-Halle (Raum 1): Boden, drei Wände, offene Front nach Norden (-Z) mit Stahlrahmen und Schild.
function Greybox.buildHall(parent: Instance, hall: any, groundY: number): Model
	local model = Instance.new("Model")
	model.Name = "GMT_PH_StartHall"
	model:SetAttribute("RoomId", "room_1")

	local cx, cz = hall.centerX, hall.centerZ
	local w, d, h, t = hall.width, hall.depth, hall.wallHeight, hall.wallThickness
	local front = cz - d / 2
	local back = cz + d / 2

	part("Floor", Vector3.new(w, 0.4, d), CFrame.new(cx, groundY, cz), COLORS.floor, Enum.Material.Concrete, model)
	part("WallBack", Vector3.new(w, h, t), CFrame.new(cx, groundY + h / 2, back - t / 2), COLORS.orange, nil, model)
	part(
		"WallLeft",
		Vector3.new(t, h, d),
		CFrame.new(cx - w / 2 + t / 2, groundY + h / 2, cz),
		COLORS.orange,
		nil,
		model
	)
	part(
		"WallRight",
		Vector3.new(t, h, d),
		CFrame.new(cx + w / 2 - t / 2, groundY + h / 2, cz),
		COLORS.orange,
		nil,
		model
	)
	-- Stahlrahmen an der offenen Front
	part(
		"PillarLeft",
		Vector3.new(2, h + 2, 2),
		CFrame.new(cx - w / 2 + 1, groundY + (h + 2) / 2, front + 1),
		COLORS.steel,
		Enum.Material.Metal,
		model
	)
	part(
		"PillarRight",
		Vector3.new(2, h + 2, 2),
		CFrame.new(cx + w / 2 - 1, groundY + (h + 2) / 2, front + 1),
		COLORS.steel,
		Enum.Material.Metal,
		model
	)
	part(
		"FrontBeam",
		Vector3.new(w, 2.5, 2),
		CFrame.new(cx, groundY + h + 1.25, front + 1),
		COLORS.steel,
		Enum.Material.Metal,
		model
	)
	-- Namensschild über dem Eingang, Schrift zeigt nach Norden (Front-Seite = -Z)
	local sign = part(
		"NameSign",
		Vector3.new(18, 4, 0.5),
		CFrame.new(cx, groundY + h + 4.5, front + 0.75),
		COLORS.steelDark,
		nil,
		model
	)
	surfaceText(sign, Enum.NormalId.Front, "START-HALLE", COLORS.signText)

	model.PrimaryPart = model:FindFirstChild("Floor") :: BasePart
	model.Parent = parent
	return model
end

export type StorageBin = {
	model: Model,
	fill: BasePart,
	label: TextLabel,
	innerHeight: number,
	fillBottomY: number,
}

-- Lager-Kasten mit Glaswand (Füllstand sichtbar) und Abladefeld davor.
function Greybox.buildStorage(
	parent: Instance,
	storage: any,
	binId: string,
	oreName: string,
	oreColor: Color3,
	groundY: number
): StorageBin
	local folder = Instance.new("Model")
	folder.Name = "GMT_PH_Storage"

	local bin = Instance.new("Model")
	bin.Name = `GMT_PH_StorageBin_{binId}`
	bin:SetAttribute("BinId", binId)

	local x, z = storage.binX, storage.binZ
	local w, h, d = storage.binWidth, storage.binHeight, storage.binDepth
	local wall = 0.6
	local floorTop = groundY + 0.2 -- Oberkante des Hallenbodens

	part("Bottom", Vector3.new(w, wall, d), CFrame.new(x, floorTop + wall / 2, z), COLORS.steel, Enum.Material.Metal, bin)
	part(
		"Back",
		Vector3.new(w, h, wall),
		CFrame.new(x, floorTop + h / 2, z + d / 2 - wall / 2),
		COLORS.steel,
		Enum.Material.Metal,
		bin
	)
	part(
		"SideLeft",
		Vector3.new(wall, h, d),
		CFrame.new(x - w / 2 + wall / 2, floorTop + h / 2, z),
		COLORS.steel,
		Enum.Material.Metal,
		bin
	)
	part(
		"SideRight",
		Vector3.new(wall, h, d),
		CFrame.new(x + w / 2 - wall / 2, floorTop + h / 2, z),
		COLORS.steel,
		Enum.Material.Metal,
		bin
	)
	part(
		"Rim",
		Vector3.new(w, 0.5, wall),
		CFrame.new(x, floorTop + h + 0.25, z - d / 2 + wall / 2),
		COLORS.steelDark,
		Enum.Material.Metal,
		bin
	)
	local glass = part(
		"GlassFront",
		Vector3.new(w - 2 * wall, h, 0.3),
		CFrame.new(x, floorTop + h / 2, z - d / 2 + 0.15),
		COLORS.glass,
		Enum.Material.Glass,
		bin
	)
	glass.Transparency = 0.6

	local innerHeight = h - wall - 0.2
	local fillBottomY = floorTop + wall
	local fill = part(
		"Fill",
		Vector3.new(w - 2 * wall - 0.2, 0.05, d - 2 * wall - 0.2),
		CFrame.new(x, fillBottomY + 0.025, z + 0.1),
		oreColor,
		Enum.Material.Slate,
		bin
	)
	fill.CanCollide = false
	fill.Transparency = 1

	local labelPart = part(
		"Label",
		Vector3.new(w, 2.4, 0.4),
		CFrame.new(x, floorTop + h + 1.9, z - d / 2 + 0.2),
		COLORS.steelDark,
		nil,
		bin
	)
	local label = surfaceText(labelPart, Enum.NormalId.Front, `{string.upper(oreName)} 0/0`, COLORS.signText)

	bin.PrimaryPart = bin:FindFirstChild("Bottom") :: BasePart
	bin.Parent = folder

	-- Abladefeld: drauflaufen = alles Getragene kommt in den passenden Kasten.
	local zone = part(
		"GMT_PH_DropZone",
		Vector3.new(storage.dropZoneWidth, 0.1, storage.dropZoneDepth),
		CFrame.new(storage.dropZoneX, floorTop + 0.06, storage.dropZoneZ),
		COLORS.dropZone,
		Enum.Material.Neon,
		folder
	)
	zone.CanCollide = false
	zone.CanQuery = false
	zone.Transparency = 0.35
	surfaceText(zone, Enum.NormalId.Top, "ABLADEN", Color3.fromRGB(20, 60, 30))

	folder.Parent = parent
	return { model = bin, fill = fill, label = label, innerHeight = innerHeight, fillBottomY = fillBottomY }
end

function Greybox.setBinFill(bin: StorageBin, oreName: string, amount: number, capacity: number)
	local ratio = if capacity > 0 then math.clamp(amount / capacity, 0, 1) else 0
	local height = math.max(0.05, bin.innerHeight * ratio)
	local size = bin.fill.Size
	bin.fill.Size = Vector3.new(size.X, height, size.Z)
	local pos = bin.fill.Position
	bin.fill.Position = Vector3.new(pos.X, bin.fillBottomY + height / 2, pos.Z)
	bin.fill.Transparency = if amount > 0 then 0 else 1
	bin.label.Text = `{string.upper(oreName)} {amount}/{capacity}`
	bin.model:SetAttribute("Amount", amount)
	bin.model:SetAttribute("Capacity", capacity)
end

-- Erz-Vorkommen: Felsbrocken mit farbigen Erz-Stücken und einem Prompt zum Hacken.
function Greybox.buildOreNode(
	nodeId: string,
	ore: string,
	oreName: string,
	x: number,
	z: number,
	groundY: number,
	shapeSeed: number,
	oreColor: Color3,
	promptDistance: number
): Model
	local model = Instance.new("Model")
	model.Name = `GMT_PH_OreNode_{nodeId}`
	model:SetAttribute("NodeId", nodeId)
	model:SetAttribute("Ore", ore)
	model:SetAttribute("GroundY", groundY)

	local rng = Random.new(shapeSeed)
	local yaw = rng:NextNumber() * math.pi * 2
	local rockHeight = 3.2
	local sink = 0.4 -- etwas einsinken lassen, damit keine Lücke zum Boden bleibt
	local rock = part(
		"Rock",
		Vector3.new(6.5, rockHeight, 5.5),
		CFrame.new(x, groundY + rockHeight / 2 - sink, z) * CFrame.Angles(0, yaw, 0),
		COLORS.rock,
		Enum.Material.Slate,
		model
	)
	for i = 1, 4 do
		local angle = yaw + i * (math.pi / 2) + rng:NextNumber() * 0.6
		local radius = 1.4 + rng:NextNumber() * 0.9
		local s = 1.2 + rng:NextNumber() * 0.9
		part(
			`Ore{i}`,
			Vector3.new(s, s * 0.8, s),
			CFrame.new(
				x + math.cos(angle) * radius,
				groundY + rockHeight - sink - 0.1 + rng:NextNumber() * 0.5,
				z + math.sin(angle) * radius
			) * CFrame.Angles(rng:NextNumber(), rng:NextNumber(), rng:NextNumber()),
			oreColor,
			Enum.Material.Slate,
			model
		)
	end
	model.PrimaryPart = rock

	local prompt = Instance.new("ProximityPrompt")
	prompt.Name = "MinePrompt"
	prompt.ActionText = "Hacken"
	prompt.ObjectText = oreName
	prompt.HoldDuration = 0
	prompt.KeyboardKeyCode = Enum.KeyCode.E
	prompt.MaxActivationDistance = promptDistance
	prompt.RequiresLineOfSight = false
	prompt.Parent = rock

	return model
end

return Greybox
