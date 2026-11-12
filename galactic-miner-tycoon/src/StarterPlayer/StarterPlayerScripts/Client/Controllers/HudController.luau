--!strict
-- HUD oben in der Mitte (spiel/14-ui-und-bedienung.md): Lager-Menge (Eisen-Kasten) und Tragevorrat.
-- Wenig UI, große Zahlen, handy-tauglich. Liest nur Attribute am eigenen Player (PlayerState.luau auf dem Server):
--   Bin_iron_ore / BinCap_iron_ore, CarriedTotal / CarryCapacity
-- Zahlen zählen kurz hoch, das Feld "poppt" bei jedem Zuwachs. Ist man voll, erscheint ein Hinweis.
-- Alle Feel-Zahlen stehen in CONFIG (Skill game-feel-juice): ändern = Zahl ändern, kein Umbau.

local Players = game:GetService("Players")
local TweenService = game:GetService("TweenService")

local CONFIG = {
	-- Hochzählen und Pop
	COUNT_TIME = 0.25,
	POP_SCALE = 1.12,
	POP_TIME = 0.07,
	SETTLE_TIME = 0.22,
	-- Größe (Pixel bei Bildschirmbreite REFERENCE_WIDTH, wird mit UIScale angepasst)
	PANEL_WIDTH = 190,
	PANEL_HEIGHT = 64,
	GAP = 10,
	TOP_OFFSET = 6,
	REFERENCE_WIDTH = 1000,
	MIN_UI_SCALE = 0.8,
	MAX_UI_SCALE = 1.25,
	-- Farben
	BG = Color3.fromRGB(28, 30, 44),
	BG_TRANSPARENCY = 0.2,
	TEXT = Color3.fromRGB(255, 255, 255),
	CAPTION = Color3.fromRGB(200, 205, 220),
	FULL = Color3.fromRGB(255, 150, 60),
	IRON = Color3.fromRGB(196, 104, 60),
	-- Hinweis, wenn der Tragevorrat voll ist
	FULL_HINT = "Voll! Bring das Erz zum Abladefeld im Lager",
	HINT_PULSE_TIME = 0.6,
}

local HudController = {}

type Panel = {
	frame: Frame,
	value: TextLabel,
	pop: UIScale,
	number: NumberValue,
	capacity: number,
	tween: Tween?,
	popTween: Tween?,
}

local player = Players.LocalPlayer
local panels: { [string]: Panel } = {}
local hint: TextLabel

-- 1234 → "1,2K" (Handy: große, kurze Zahlen)
function HudController.FormatNumber(n: number): string
	n = math.floor(n + 0.5)
	if n < 1000 then
		return tostring(n)
	elseif n < 1000000 then
		return (string.format("%.1fK", n / 1000):gsub("%.", ","):gsub(",0K", "K"))
	end
	return (string.format("%.1fM", n / 1000000):gsub("%.", ","):gsub(",0M", "M"))
end

local function corner(parent: Instance, radius: number)
	local c = Instance.new("UICorner")
	c.CornerRadius = UDim.new(0, radius)
	c.Parent = parent
end

local function label(name: string, parent: Instance, text: string, color: Color3, size: UDim2, position: UDim2): TextLabel
	local l = Instance.new("TextLabel")
	l.Name = name
	l.BackgroundTransparency = 1
	l.Font = Enum.Font.FredokaOne
	l.TextScaled = true
	l.TextColor3 = color
	l.Text = text
	l.Size = size
	l.Position = position
	l.TextXAlignment = Enum.TextXAlignment.Left
	l.Parent = parent
	return l
end

local function makePanel(root: Instance, name: string, caption: string, iconColor: Color3, order: number): Panel
	local frame = Instance.new("Frame")
	frame.Name = name
	frame.LayoutOrder = order
	frame.Size = UDim2.fromOffset(CONFIG.PANEL_WIDTH, CONFIG.PANEL_HEIGHT)
	frame.BackgroundColor3 = CONFIG.BG
	frame.BackgroundTransparency = CONFIG.BG_TRANSPARENCY
	corner(frame, 14)
	local stroke = Instance.new("UIStroke")
	stroke.Color = Color3.fromRGB(255, 255, 255)
	stroke.Transparency = 0.8
	stroke.Thickness = 2
	stroke.Parent = frame
	local pop = Instance.new("UIScale")
	pop.Parent = frame

	local icon = Instance.new("Frame")
	icon.Name = "Icon"
	icon.Size = UDim2.fromOffset(40, 40)
	icon.Position = UDim2.fromOffset(12, 12)
	icon.BackgroundColor3 = iconColor
	corner(icon, 10)
	icon.Parent = frame

	label("Caption", frame, caption, CONFIG.CAPTION, UDim2.new(1, -66, 0, 16), UDim2.fromOffset(60, 6))
	local value = label("Value", frame, "0/0", CONFIG.TEXT, UDim2.new(1, -66, 0, 38), UDim2.fromOffset(60, 22))

	frame.Parent = root
	local number = Instance.new("NumberValue")
	number.Parent = frame

	local panel: Panel = { frame = frame, value = value, pop = pop, number = number, capacity = 0 }
	number.Changed:Connect(function(v: number)
		value.Text = `{HudController.FormatNumber(v)}/{HudController.FormatNumber(panel.capacity)}`
	end)
	return panel
end

local function popPanel(panel: Panel)
	if panel.popTween then
		panel.popTween:Cancel()
	end
	local up = TweenService:Create(
		panel.pop,
		TweenInfo.new(CONFIG.POP_TIME, Enum.EasingStyle.Quad, Enum.EasingDirection.Out),
		{ Scale = CONFIG.POP_SCALE }
	)
	local down = TweenService:Create(
		panel.pop,
		TweenInfo.new(CONFIG.SETTLE_TIME, Enum.EasingStyle.Back, Enum.EasingDirection.Out),
		{ Scale = 1 }
	)
	up.Completed:Connect(function(state)
		if state == Enum.PlaybackState.Completed then
			panel.popTween = down
			down:Play()
		end
	end)
	panel.popTween = up
	up:Play()
end

-- Neuen Wert anzeigen: hochzählen (ein NumberValue, alter Tween wird abgebrochen gegen Flackern).
local function setPanel(panel: Panel, amount: number, capacity: number)
	local increased = amount > panel.number.Value
	panel.capacity = capacity
	if panel.tween then
		panel.tween:Cancel()
	end
	local tween = TweenService:Create(
		panel.number,
		TweenInfo.new(CONFIG.COUNT_TIME, Enum.EasingStyle.Quad, Enum.EasingDirection.Out),
		{ Value = amount }
	)
	panel.tween = tween
	tween:Play()
	-- Text sofort richtig, falls sich nur die Kapazität ändert
	panel.value.Text = `{HudController.FormatNumber(panel.number.Value)}/{HudController.FormatNumber(capacity)}`
	local full = capacity > 0 and amount >= capacity
	panel.value.TextColor3 = if full then CONFIG.FULL else CONFIG.TEXT
	if increased then
		popPanel(panel)
	end
end

local function refresh()
	local carried = player:GetAttribute("CarriedTotal") or 0
	local carryCap = player:GetAttribute("CarryCapacity") or 0
	setPanel(panels.Carry, carried :: number, carryCap :: number)

	local stored = player:GetAttribute("Bin_iron_ore") or 0
	local storedCap = player:GetAttribute("BinCap_iron_ore") or 0
	setPanel(panels.Storage, stored :: number, storedCap :: number)

	local full = (carryCap :: number) > 0 and (carried :: number) >= (carryCap :: number)
	hint.Visible = full
end

local function buildGui()
	local gui = Instance.new("ScreenGui")
	gui.Name = "GMT_Hud"
	gui.ResetOnSpawn = false
	gui.ScreenInsets = Enum.ScreenInsets.CoreUISafeInsets
	gui.ZIndexBehavior = Enum.ZIndexBehavior.Sibling

	local root = Instance.new("Frame")
	root.Name = "Top"
	root.AnchorPoint = Vector2.new(0.5, 0)
	root.Position = UDim2.new(0.5, 0, 0, CONFIG.TOP_OFFSET)
	root.Size = UDim2.fromOffset(CONFIG.PANEL_WIDTH * 2 + CONFIG.GAP, CONFIG.PANEL_HEIGHT + 44)
	root.BackgroundTransparency = 1
	root.Parent = gui

	local screenScale = Instance.new("UIScale")
	screenScale.Parent = root

	local row = Instance.new("Frame")
	row.Name = "Row"
	row.Size = UDim2.new(1, 0, 0, CONFIG.PANEL_HEIGHT)
	row.BackgroundTransparency = 1
	row.Parent = root
	local layout = Instance.new("UIListLayout")
	layout.FillDirection = Enum.FillDirection.Horizontal
	layout.HorizontalAlignment = Enum.HorizontalAlignment.Center
	layout.Padding = UDim.new(0, CONFIG.GAP)
	layout.SortOrder = Enum.SortOrder.LayoutOrder
	layout.Parent = row

	panels.Storage = makePanel(row, "Storage", "LAGER · EISEN", CONFIG.IRON, 1)
	panels.Carry = makePanel(row, "Carry", "TRAGEN", CONFIG.IRON, 2)

	hint = label(
		"FullHint",
		root,
		CONFIG.FULL_HINT,
		CONFIG.FULL,
		UDim2.new(1, 0, 0, 28),
		UDim2.fromOffset(0, CONFIG.PANEL_HEIGHT + 8)
	)
	hint.TextXAlignment = Enum.TextXAlignment.Center
	local hintStroke = Instance.new("UIStroke")
	hintStroke.Thickness = 2
	hintStroke.Color = Color3.fromRGB(40, 20, 10)
	hintStroke.Parent = hint
	hint.Visible = false
	TweenService:Create(
		hint,
		TweenInfo.new(CONFIG.HINT_PULSE_TIME, Enum.EasingStyle.Sine, Enum.EasingDirection.InOut, -1, true),
		{ TextTransparency = 0.35 }
	):Play()

	-- Größe an den Bildschirm anpassen (Handy kleiner, großer Monitor etwas größer)
	local function rescale()
		local camera = workspace.CurrentCamera
		if camera then
			local width = camera.ViewportSize.X
			screenScale.Scale = math.clamp(width / CONFIG.REFERENCE_WIDTH, CONFIG.MIN_UI_SCALE, CONFIG.MAX_UI_SCALE)
		end
	end
	rescale()
	if workspace.CurrentCamera then
		workspace.CurrentCamera:GetPropertyChangedSignal("ViewportSize"):Connect(rescale)
	end

	gui.Parent = player:WaitForChild("PlayerGui")
end

function HudController.Init() end

function HudController.Start()
	buildGui()
	for _, name in { "CarriedTotal", "CarryCapacity", "Bin_iron_ore", "BinCap_iron_ore" } do
		player:GetAttributeChangedSignal(name):Connect(refresh)
	end
	refresh()
end

return HudController
