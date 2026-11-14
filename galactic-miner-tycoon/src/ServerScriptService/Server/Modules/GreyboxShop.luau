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
		icon.Size = UDim2.fromScale(0.8, 0.8) -- RelativeYY: beide Werte beziehen sich auf die Höhe → Quadrat
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

export type ShutterPart = { part: BasePart, closed: CFrame, transparency: number }

export type Room = {
	model: Model,
	door: BasePart, -- Greybox: sichtbare Tür. 3D-Modell: unsichtbare Sperre im Torbogen
	doorLabel: TextLabel,
	doorClosedCFrame: CFrame,
	shutter: { ShutterPart }?, -- nur beim 3D-Modell: Teile des Rolltors
}

-- Schmiede aus dem 3D-Modell (z. B. BaseRoom "gesperrter Raum mit Rolltor", assets/asset-liste.md).
-- Gibt nil zurück, wenn das Modell fehlt oder nicht passt (dann baut der Aufrufer die Greybox).
-- * Kopie wird um forge.modelScale vergrößert, Rolltor zeigt nach Norden (-Z),
-- * so tief gesetzt, dass die Unterkante des Rolltors auf dem Boden liegt (der Sockel steckt im Gelände),
-- * Mitte der Hülle auf (forge.centerX, forge.centerZ).
-- Das Modell hat keinen Innenraum (Wände nur von außen sichtbar). Darum bekommt es innen dünne
-- Platzhalter-Wände, einen Boden und eine Decke. Kollision kommt nur von diesen Wänden.
local LINING_INSET = 0.35
local LINING_THICKNESS = 0.6

function GreyboxShop.buildForgeFromModel(parent: Instance, forge: any, groundY: number): Room?
	local GameModels = require(script.Parent:WaitForChild("GameModels"))
	local model = forge.modelName and GameModels.clone(forge.modelName)
	if not model then
		return nil
	end
	local shell = GameModels.partsMatching(model, "_Orange$")
	local shutterParts = GameModels.partsMatching(model, "Shutter")
	if #shell == 0 or #shutterParts == 0 then
		warn(`[GreyboxShop] {forge.modelName}: Hülle (_Orange) oder Rolltor (Shutter) fehlt, nehme Greybox`)
		model:Destroy()
		return nil
	end
	model.Name = "GMT_Forge"
	model:SetAttribute("RoomId", "forge")
	model:ScaleTo(model:GetScale() * forge.modelScale)

	-- Drehen, bis das Rolltor nach -Z zeigt (auf volle 90° gerundet).
	local sMin, sMax = GameModels.bounds(shell)
	local tMin, tMax = GameModels.bounds(shutterParts)
	local center = (sMin + sMax) / 2
	local toShutter = (tMin + tMax) / 2 - center
	local heading = math.atan2(-toShutter.X, -toShutter.Z)
	heading = math.round(heading / (math.pi / 2)) * (math.pi / 2)
	if math.abs(heading) > 0.01 then
		model:PivotTo(CFrame.new(center) * CFrame.Angles(0, -heading, 0) * CFrame.new(-center) * model:GetPivot())
	end

	-- Verschieben: Hüllen-Mitte auf die Schmiede-Mitte, Rolltor-Unterkante auf den Hallenboden.
	sMin, sMax = GameModels.bounds(shell)
	tMin, tMax = GameModels.bounds(shutterParts)
	local floorTop = groundY + 0.2
	local shift = Vector3.new(
		forge.centerX - (sMin.X + sMax.X) / 2,
		floorTop - tMin.Y,
		forge.centerZ - (sMin.Z + sMax.Z) / 2
	)
	model:PivotTo(CFrame.new(shift) * model:GetPivot())
	sMin, sMax = GameModels.bounds(shell)
	tMin, tMax = GameModels.bounds(shutterParts)

	for _, d in model:GetDescendants() do
		if d:IsA("BasePart") then
			d.CanCollide = false -- Kollision kommt von den Innenwänden (die Hülle wäre sonst ein voller Block)
			d.CanTouch = false
		end
	end

	-- Innenwände (nur von innen zu sehen, liegen knapp in der Hülle)
	local lining = Instance.new("Model")
	lining.Name = "Lining"
	local inMin = Vector3.new(sMin.X + LINING_INSET, floorTop, sMin.Z + LINING_INSET)
	local inMax = Vector3.new(sMax.X - LINING_INSET, sMax.Y - LINING_INSET, sMax.Z - LINING_INSET)
	local t = LINING_THICKNESS
	local w, d, h = inMax.X - inMin.X, inMax.Z - inMin.Z, inMax.Y - inMin.Y
	local cx, cz = (inMin.X + inMax.X) / 2, (inMin.Z + inMax.Z) / 2
	local wallColor = COLORS.orange
	part("Floor", Vector3.new(w, 0.4, d), CFrame.new(cx, groundY, cz), COLORS.floor, Enum.Material.Concrete, lining)
	part("Ceiling", Vector3.new(w, t, d), CFrame.new(cx, inMax.Y - t / 2, cz), COLORS.steelDark, Enum.Material.Metal, lining)
	part("WallBack", Vector3.new(w, h, t), CFrame.new(cx, floorTop + h / 2, inMax.Z - t / 2), wallColor, nil, lining)
	part("WallLeft", Vector3.new(t, h, d), CFrame.new(inMin.X + t / 2, floorTop + h / 2, cz), wallColor, nil, lining)
	part("WallRight", Vector3.new(t, h, d), CFrame.new(inMax.X - t / 2, floorTop + h / 2, cz), wallColor, nil, lining)
	-- Front mit Öffnung so breit und hoch wie das Rolltor
	local openMinX, openMaxX = tMin.X + 0.3, tMax.X - 0.3
	local openTop = tMax.Y - 0.3
	local frontZ = inMin.Z + t / 2
	local leftW = openMinX - inMin.X
	local rightW = inMax.X - openMaxX
	if leftW > 0.1 then
		part("WallFrontLeft", Vector3.new(leftW, h, t), CFrame.new(inMin.X + leftW / 2, floorTop + h / 2, frontZ), wallColor, nil, lining)
	end
	if rightW > 0.1 then
		part("WallFrontRight", Vector3.new(rightW, h, t), CFrame.new(openMaxX + rightW / 2, floorTop + h / 2, frontZ), wallColor, nil, lining)
	end
	if inMax.Y - openTop > 0.1 then
		part(
			"Lintel",
			Vector3.new(openMaxX - openMinX, inMax.Y - openTop, t),
			CFrame.new((openMinX + openMaxX) / 2, (openTop + inMax.Y) / 2, frontZ),
			COLORS.steel,
			Enum.Material.Metal,
			lining
		)
	end
	-- Schwelle im Torbogen (von außen sichtbar), damit man nicht über eine Kante stolpert
	local zA, zB = tMin.Z - 0.3, inMin.Z + t + 0.3
	part(
		"Threshold",
		Vector3.new(tMax.X - tMin.X, 0.4, zB - zA),
		CFrame.new((tMin.X + tMax.X) / 2, groundY, (zA + zB) / 2),
		COLORS.steelDark,
		Enum.Material.DiamondPlate,
		lining
	)
	lining.Parent = model

	-- Sperre im Torbogen: unsichtbar, trägt das Preisschild auf der Außenseite (-Z = Front)
	local doorCFrame = CFrame.new((tMin.X + tMax.X) / 2, (tMin.Y + tMax.Y) / 2, tMin.Z - 0.05)
	local door = part("DoorBlocker", Vector3.new(tMax.X - tMin.X, tMax.Y - tMin.Y, 0.2), doorCFrame, DOOR_COLOR, nil, model)
	door.Transparency = 1
	local doorLabel = surfaceText(door, Enum.NormalId.Front, "GESPERRT", COLORS.signText)

	-- Namensschild über dem Rolltor
	local sign = part(
		"NameSign",
		Vector3.new(math.min(14, tMax.X - tMin.X), 2.6, 0.4),
		CFrame.new((tMin.X + tMax.X) / 2, tMax.Y + 1.8, sMin.Z - 0.25),
		COLORS.steelDark,
		nil,
		model
	)
	surfaceText(sign, Enum.NormalId.Front, "SCHMIEDE", COLORS.signText)

	local shutter: { ShutterPart } = {}
	for _, p in shutterParts do
		table.insert(shutter, { part = p, closed = p.CFrame, transparency = p.Transparency })
	end

	model.Parent = parent
	return { model = model, door = door, doorLabel = doorLabel, doorClosedCFrame = doorCFrame, shutter = shutter }
end

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
	if room.shutter then
		-- 3D-Modell: Rolltor fährt hoch und blendet aus, Preisschild verschwindet.
		room.doorLabel.Visible = false
		local rise = room.door.Size.Y * 0.6
		for _, s in room.shutter do
			local target = s.closed + Vector3.new(0, rise, 0)
			if instant then
				s.part.CFrame = target
				s.part.Transparency = 1
			else
				TweenService:Create(
					s.part,
					TweenInfo.new(DOOR_OPEN_SECONDS, Enum.EasingStyle.Quad, Enum.EasingDirection.In),
					{ CFrame = target, Transparency = 1 }
				):Play()
			end
		end
		return
	end
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
	room.door.CanCollide = true
	room.doorLabel.Text = text
	room.doorLabel.Visible = true
	if room.shutter then
		room.door.Transparency = 1 -- unsichtbare Sperre, man sieht das Rolltor
		for _, s in room.shutter do
			s.part.CFrame = s.closed
			s.part.Transparency = s.transparency
		end
	else
		room.door.Transparency = 0
	end
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
