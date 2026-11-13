--!strict
-- Greybox-Platzhalter für Kauffelder und die Schmiede (Schritt 5 und 6).
-- Kauffeld (spiel/14 "Kaufflächen"): flache Platte, darüber Name und Preis mit Erz-Symbol.
--   Grün = bezahlbar, rot = zu wenig Erz, grau = gerade nicht kaufbar (z. B. "später").
-- Schmiede (Raum 2): Boden, Wände, Front nach Norden mit gesperrter grauer Tür (zeigt den Preis).
-- Später ersetzt durch Jos' Modelle (BaseRoom usw.): dann nur die build-Funktionen austauschen.

local TweenService = game:GetService("TweenService")

local Greybox = require(script.Parent:WaitForChild("Greybox"))

local part = Greybox.part
local surfaceText = Greybox.surfaceText
local COLORS = Greybox.COLORS

local GreyboxShop = {}

GreyboxShop.STATE_COLORS = {
	ok = Color3.fromRGB(80, 200, 100),
	poor = Color3.fromRGB(220, 70, 60),
	blocked = Color3.fromRGB(130, 134, 142),
}

local DOOR_COLOR = Color3.fromRGB(110, 114, 122)
local DOOR_OPEN_SECONDS = 0.9

export type PadState = "ok" | "poor" | "blocked"

export type CostEntry = { ore: string, amount: number, color: Color3 }

export type Pad = {
	id: string,
	part: BasePart,
	panel: Frame,
	title: TextLabel,
	costRow: Frame,
	sub: TextLabel,
	costKey: string,
}

local function textLabel(name: string, parent: Instance, size: UDim2, position: UDim2): TextLabel
	local l = Instance.new("TextLabel")
	l.Name = name
	l.BackgroundTransparency = 1
	l.Size = size
	l.Position = position
	l.Font = Enum.Font.FredokaOne
	l.TextColor3 = Color3.fromRGB(255, 255, 255)
	l.TextWrapped = true
	l.TextScaled = true
	l.Text = ""
	l.Parent = parent
	return l
end

-- Kauffeld bauen. x/z = Mitte, groundY = Boden (Oberkante Hallenboden wird +0,2 angenommen).
function GreyboxShop.buildPad(parent: Instance, id: string, x: number, z: number, groundY: number, size: number): Pad
	local model = Instance.new("Model")
	model.Name = `GMT_PH_BuyPad_{id}`
	model:SetAttribute("PadId", id)

	part("Rim", Vector3.new(size + 0.6, 0.2, size + 0.6), CFrame.new(x, groundY + 0.25, z), COLORS.steelDark, Enum.Material.Metal, model)
	local plate = part(
		"Plate",
		Vector3.new(size, 0.25, size),
		CFrame.new(x, groundY + 0.35, z),
		GreyboxShop.STATE_COLORS.blocked,
		Enum.Material.Neon,
		model
	)
	plate.Transparency = 0.25
	plate.CanCollide = false
	model.PrimaryPart = plate

	local gui = Instance.new("BillboardGui")
	gui.Name = "PriceGui"
	gui.Size = UDim2.new(8, 0, 3.6, 0)
	gui.StudsOffset = Vector3.new(0, 4.2, 0)
	gui.MaxDistance = 90
	gui.LightInfluence = 0
	local panel = Instance.new("Frame")
	panel.Name = "Panel"
	panel.Size = UDim2.fromScale(1, 1)
	panel.BackgroundColor3 = GreyboxShop.STATE_COLORS.blocked
	panel.BackgroundTransparency = 0.1
	panel.Parent = gui
	local corner = Instance.new("UICorner")
	corner.CornerRadius = UDim.new(0.15, 0)
	corner.Parent = panel
	local stroke = Instance.new("UIStroke")
	stroke.Thickness = 2
	stroke.Color = Color3.fromRGB(20, 22, 30)
	stroke.Transparency = 0.4
	stroke.Parent = panel

	local title = textLabel("Title", panel, UDim2.fromScale(0.92, 0.34), UDim2.fromScale(0.04, 0.03))
	local costRow = Instance.new("Frame")
	costRow.Name = "CostRow"
	costRow.BackgroundTransparency = 1
	costRow.Size = UDim2.fromScale(0.92, 0.36)
	costRow.Position = UDim2.fromScale(0.04, 0.37)
	costRow.Parent = panel
	local layout = Instance.new("UIListLayout")
	layout.FillDirection = Enum.FillDirection.Horizontal
	layout.HorizontalAlignment = Enum.HorizontalAlignment.Center
	layout.VerticalAlignment = Enum.VerticalAlignment.Center
	layout.Padding = UDim.new(0.03, 0)
	layout.SortOrder = Enum.SortOrder.LayoutOrder
	layout.Parent = costRow
	local sub = textLabel("Sub", panel, UDim2.fromScale(0.92, 0.22), UDim2.fromScale(0.04, 0.75))
	sub.TextColor3 = Color3.fromRGB(240, 240, 245)

	gui.Parent = plate
	model.Parent = parent
	return { id = id, part = plate, panel = panel, title = title, costRow = costRow, sub = sub, costKey = "" }
end

-- Preiszeile: je Erz ein farbiges Symbol und die Zahl. Wird nur neu gebaut, wenn sich der Preis ändert.
local function setCost(pad: Pad, entries: { CostEntry })
	local keyParts = {}
	for _, entry in entries do
		table.insert(keyParts, `{entry.ore}={entry.amount}`)
	end
	local key = table.concat(keyParts, ",")
	if key == pad.costKey then
		return
	end
	pad.costKey = key
	for _, child in pad.costRow:GetChildren() do
		if child:IsA("GuiObject") then
			child:Destroy()
		end
	end
	for i, entry in entries do
		local icon = Instance.new("Frame")
		icon.Name = `Icon_{entry.ore}`
		icon.LayoutOrder = i * 2
		icon.Size = UDim2.fromScale(0.12, 0.8)
		icon.SizeConstraint = Enum.SizeConstraint.RelativeYY
		icon.BackgroundColor3 = entry.color
		local c = Instance.new("UICorner")
		c.CornerRadius = UDim.new(0.3, 0)
		c.Parent = icon
		local s = Instance.new("UIStroke")
		s.Thickness = 1.5
		s.Color = Color3.fromRGB(255, 255, 255)
		s.Parent = icon
		icon.Parent = pad.costRow
		local amount = textLabel(`Amount_{entry.ore}`, pad.costRow, UDim2.fromScale(0.22, 1), UDim2.new())
		amount.LayoutOrder = i * 2 + 1
		amount.TextXAlignment = Enum.TextXAlignment.Left
		amount.Text = tostring(entry.amount)
	end
	pad.costRow.Visible = #entries > 0
end

function GreyboxShop.setPad(pad: Pad, title: string, entries: { CostEntry }, state: PadState, subText: string)
	local color = GreyboxShop.STATE_COLORS[state]
	pad.title.Text = title
	setCost(pad, entries)
	pad.sub.Text = subText
	pad.panel.BackgroundColor3 = color
	pad.part.Color = color
	pad.part:SetAttribute("State", state)
end

-- Schmiede (Raum 2) ------------------------------------------------------------------------------

export type Room = {
	model: Model,
	door: BasePart,
	doorLabel: TextLabel,
	doorClosedCFrame: CFrame,
}

function GreyboxShop.buildForge(parent: Instance, forge: any, groundY: number): Room
	local model = Instance.new("Model")
	model.Name = "GMT_PH_Forge"
	model:SetAttribute("RoomId", "forge")

	local cx, cz = forge.centerX, forge.centerZ
	local w, d, h, t = forge.width, forge.depth, forge.wallHeight, forge.wallThickness
	local front = cz - d / 2
	local back = cz + d / 2
	local doorW, doorH = forge.doorWidth, forge.doorHeight
	local sideW = (w - doorW) / 2

	part("Floor", Vector3.new(w, 0.4, d), CFrame.new(cx, groundY, cz), COLORS.floor, Enum.Material.Concrete, model)
	part("WallBack", Vector3.new(w, h, t), CFrame.new(cx, groundY + h / 2, back - t / 2), COLORS.orange, nil, model)
	part("WallLeft", Vector3.new(t, h, d), CFrame.new(cx - w / 2 + t / 2, groundY + h / 2, cz), COLORS.orange, nil, model)
	part("WallRight", Vector3.new(t, h, d), CFrame.new(cx + w / 2 - t / 2, groundY + h / 2, cz), COLORS.orange, nil, model)
	-- Front: zwei Wandstücke neben der Tür und ein Sturz darüber
	part(
		"WallFrontLeft",
		Vector3.new(sideW, h, t),
		CFrame.new(cx - w / 2 + sideW / 2, groundY + h / 2, front + t / 2),
		COLORS.orange,
		nil,
		model
	)
	part(
		"WallFrontRight",
		Vector3.new(sideW, h, t),
		CFrame.new(cx + w / 2 - sideW / 2, groundY + h / 2, front + t / 2),
		COLORS.orange,
		nil,
		model
	)
	part(
		"Lintel",
		Vector3.new(doorW, h - doorH, t),
		CFrame.new(cx, groundY + doorH + (h - doorH) / 2, front + t / 2),
		COLORS.steel,
		Enum.Material.Metal,
		model
	)
	-- Dach, damit es ein Raum ist (Halle hat keins, die Schmiede schon: drinnen etwas dunkler)
	part("Roof", Vector3.new(w, 0.6, d), CFrame.new(cx, groundY + h + 0.3, cz), COLORS.steelDark, Enum.Material.Metal, model)

	local sign = part(
		"NameSign",
		Vector3.new(14, 3.4, 0.5),
		CFrame.new(cx, groundY + h + 2.4, front + 0.3),
		COLORS.steelDark,
		nil,
		model
	)
	surfaceText(sign, Enum.NormalId.Front, "SCHMIEDE", COLORS.signText)

	local doorCFrame = CFrame.new(cx, groundY + doorH / 2, front + t / 2)
	local door = part("Door", Vector3.new(doorW, doorH, t * 0.8), doorCFrame, DOOR_COLOR, Enum.Material.DiamondPlate, model)
	local doorLabel = surfaceText(door, Enum.NormalId.Front, "GESPERRT", COLORS.signText)

	model.PrimaryPart = model:FindFirstChild("Floor") :: BasePart
	model.Parent = parent
	return { model = model, door = door, doorLabel = doorLabel, doorClosedCFrame = doorCFrame }
end

-- Tür öffnen: fährt in den Boden. instant = ohne Animation (z. B. beim Laden eines Spielstands).
function GreyboxShop.openDoor(room: Room, instant: boolean)
	room.model:SetAttribute("Open", true)
	room.door.CanCollide = false
	local target = room.doorClosedCFrame * CFrame.new(0, -room.door.Size.Y - 0.2, 0)
	if instant then
		room.door.CFrame = target
		room.door.Transparency = 1
		return
	end
	local tween = TweenService:Create(
		room.door,
		TweenInfo.new(DOOR_OPEN_SECONDS, Enum.EasingStyle.Quad, Enum.EasingDirection.In),
		{ CFrame = target }
	)
	tween.Completed:Connect(function()
		room.door.Transparency = 1
	end)
	tween:Play()
end

function GreyboxShop.closeDoor(room: Room, text: string)
	room.model:SetAttribute("Open", false)
	room.door.CFrame = room.doorClosedCFrame
	room.door.Transparency = 0
	room.door.CanCollide = true
	room.doorLabel.Text = text
end

-- Platzhalter "Lobby (später)": graue Platte mit Schild, ohne Funktion.
function GreyboxShop.buildPlaceholderPad(parent: Instance, name: string, text: string, x: number, z: number, groundY: number, size: number): Model
	local model = Instance.new("Model")
	model.Name = name
	local plate = part(
		"Plate",
		Vector3.new(size, 0.25, size),
		CFrame.new(x, groundY + 0.33, z),
		GreyboxShop.STATE_COLORS.blocked,
		Enum.Material.SmoothPlastic,
		model
	)
	plate.CanCollide = false
	surfaceText(plate, Enum.NormalId.Top, text, Color3.fromRGB(40, 42, 50))
	model.PrimaryPart = plate
	model.Parent = parent
	return model
end

return GreyboxShop
