--!strict
-- Galactic Miner Tycoon – Modelle nach dem FBX-Import in Roblox Studio einrichten.
--
-- Benutzung (Roblox Studio):
--   1. Die .fbx-Dateien aus assets/modelle/ mit "Import 3D" importieren
--      (Datei > Import 3D, Einstellung "Import Only As Model" an).
--   2. Die importierten Modelle im Explorer markieren (oder nichts markieren,
--      dann wird ganz Workspace durchsucht).
--   3. Dieses Skript komplett in die Command Bar (Ansicht > Command Bar) kopieren
--      und Enter drücken.
--
-- Was es macht:
--   - Teilt importierte Teile nach dem ersten Namensteil in Modelle auf
--     ("ConveyorStraight_Orange" -> Modell "ConveyorStraight").
--   - Färbt jede MeshPart nach dem letzten Namensteil (Orange, SteelGrey, Cyan …),
--     setzt Material (Cyan = Neon, Glas = Glass) und Transparenz.
--   - Verankert alles, kleine Deko-Teile ohne Kollision.
--   - Bringt jedes Modell auf seine Größe in Studs (falls der Import anders skaliert hat).
-- Das Skript kann gefahrlos mehrmals laufen.

local Selection = game:GetService("Selection")

type Look = { color: string, material: Enum.Material, transparency: number, collide: boolean }

-- Gleiche Farben wie gmt_lib.py (PALETTE) und Jus Bohrer.
local LOOKS: { [string]: Look } = {
	Orange = { color = "#F2A12E", material = Enum.Material.SmoothPlastic, transparency = 0, collide = true },
	Amber = { color = "#EDBA4E", material = Enum.Material.SmoothPlastic, transparency = 0, collide = true },
	Yellow = { color = "#F6D117", material = Enum.Material.SmoothPlastic, transparency = 0, collide = false },
	Black = { color = "#1C1C1D", material = Enum.Material.SmoothPlastic, transparency = 0, collide = false },
	SteelGrey = { color = "#8C939B", material = Enum.Material.SmoothPlastic, transparency = 0, collide = true },
	SteelDark = { color = "#5E656D", material = Enum.Material.SmoothPlastic, transparency = 0, collide = true },
	SteelLight = { color = "#BABEC4", material = Enum.Material.SmoothPlastic, transparency = 0, collide = false },
	DarkGrey = { color = "#3A3F46", material = Enum.Material.SmoothPlastic, transparency = 0, collide = true },
	White = { color = "#E6E3DD", material = Enum.Material.SmoothPlastic, transparency = 0, collide = false },
	Cyan = { color = "#5FE3DA", material = Enum.Material.Neon, transparency = 0, collide = false },
	Glass = { color = "#CFE8F1", material = Enum.Material.Glass, transparency = 0.35, collide = true },
	GlassDark = { color = "#6E7F89", material = Enum.Material.Glass, transparency = 0.55, collide = true },
	GaugeOrange = { color = "#F07A12", material = Enum.Material.SmoothPlastic, transparency = 0, collide = false },
	OreRock = { color = "#7B6C61", material = Enum.Material.SmoothPlastic, transparency = 0, collide = true },
	OreRockDark = { color = "#5F544D", material = Enum.Material.SmoothPlastic, transparency = 0, collide = true },
}

-- Größte Ausdehnung jedes Modells in Studs (aus Blender, 1 Einheit = 1 Stud).
local SIZES: { [string]: number } = {
	-- @SIZES@ (wird von export_sizes.py ausgefüllt)
}

local function split(name: string): (string, string?)
	local parts = string.split(name, "_")
	if #parts < 2 then
		return name, nil
	end
	return parts[1], parts[#parts]
end

local function collectParts(roots: { Instance }): { MeshPart }
	local found: { MeshPart } = {}
	for _, root in roots do
		local list = root:GetDescendants()
		if root:IsA("MeshPart") then
			table.insert(list, root)
		end
		for _, inst in list do
			if inst:IsA("MeshPart") then
				local modelName, look = split(inst.Name)
				if look and LOOKS[look] and (SIZES[modelName] or next(SIZES) == nil) then
					table.insert(found, inst)
				end
			end
		end
	end
	return found
end

local roots = Selection:Get()
if #roots == 0 then
	roots = { workspace }
end

local parts = collectParts(roots)
local models: { [string]: Model } = {}
local touchedContainers: { [Instance]: boolean } = {}

for _, part in parts do
	local modelName, lookName = split(part.Name)
	local look = LOOKS[lookName :: string]
	part.Color = Color3.fromHex(look.color)
	part.Material = look.material
	part.Transparency = look.transparency
	part.Anchored = true
	part.CanCollide = look.collide
	part.CanTouch = look.collide
	-- Eingebettete Texturen/SurfaceAppearance vom Import entfernen, damit die Farbe greift
	for _, child in part:GetChildren() do
		if child:IsA("SurfaceAppearance") then
			child:Destroy()
		end
	end
	if part.TextureID ~= "" then
		part.TextureID = ""
	end

	-- In ein Modell mit dem Modellnamen einsortieren
	local current = part.Parent
	if not (current and current:IsA("Model") and current.Name == modelName) then
		local target = models[modelName]
		if not target then
			local container = current and current.Parent or workspace
			if current and current:IsA("Model") then
				touchedContainers[current] = true
			end
			target = Instance.new("Model")
			target.Name = modelName
			target.Parent = if current and current:IsA("Model") then current.Parent else container
			models[modelName] = target
		end
		part.Parent = target
	else
		models[modelName] = current :: Model
	end
end

-- Leere Import-Hüllen aufräumen
for container in touchedContainers do
	if container.Parent and #container:GetDescendants() == 0 then
		container:Destroy()
	end
end

for name, model in models do
	local wanted = SIZES[name]
	if wanted then
		local size = model:GetExtentsSize()
		local biggest = math.max(size.X, size.Y, size.Z)
		if biggest > 0 and math.abs(biggest - wanted) / wanted > 0.02 then
			model:ScaleTo(model:GetScale() * wanted / biggest)
		end
	end
	if not model.PrimaryPart then
		local best: MeshPart? = nil
		for _, p in model:GetChildren() do
			if p:IsA("MeshPart") and (best == nil or p.Size.Magnitude > (best :: MeshPart).Size.Magnitude) then
				best = p
			end
		end
		model.PrimaryPart = best
	end
	print(("[GMT] %s: %d Teile, Größe %s"):format(name, #model:GetChildren(), tostring(model:GetExtentsSize())))
end
print(("[GMT] fertig: %d Teile in %d Modellen eingerichtet"):format(#parts, (function()
	local n = 0
	for _ in models do
		n += 1
	end
	return n
end)()))
