--!strict
-- Galactic Miner Tycoon – Modelle nach dem Import in Roblox Studio einrichten.
--
-- Benutzung (Roblox Studio):
--   1. Die .fbx- (oder .glb-)Dateien aus assets/modelle/ mit "Import 3D" importieren
--      (Datei > Import 3D).
--   2. Die importierten Modelle im Explorer markieren (oder nichts markieren,
--      dann wird ganz Workspace durchsucht).
--   3. Dieses Skript komplett in die Command Bar (Ansicht > Command Bar) kopieren
--      und Enter drücken.
--
-- Was es macht:
--   - Sortiert importierte Teile nach dem ersten Namensteil in Modelle
--     ("ConveyorStraight_Orange" -> Modell "ConveyorStraight").
--   - Färbt jede MeshPart nach dem letzten Namensteil (Orange, SteelGrey, Cyan …)
--     in kräftigen Comic-Farben, Material SmoothPlastic.
--   - Leuchten werden Neon, Glas wird Glass mit Transparenz.
--   - Verankert alles, kleine Deko-Teile ohne Kollision.
--   - Bringt jedes Modell auf seine Größe in Studs (falls der Import anders skaliert hat).
-- Das Skript kann gefahrlos mehrmals laufen.

local Selection = game:GetService("Selection")

type Look = { color: string, material: Enum.Material, transparency: number, collide: boolean, plain: boolean? }

-- Gleiche Farben wie blender-skripte/gmt_materials.py
local LOOKS: { [string]: Look } = {
	Orange = { color = "#F08A1C", material = Enum.Material.SmoothPlastic, transparency = 0, collide = true },
	OrangeLight = { color = "#FFAE3D", material = Enum.Material.SmoothPlastic, transparency = 0, collide = true },
	Amber = { color = "#F2A626", material = Enum.Material.SmoothPlastic, transparency = 0, collide = true },
	Yellow = { color = "#FFD200", material = Enum.Material.SmoothPlastic, transparency = 0, collide = false },
	Black = { color = "#141416", material = Enum.Material.SmoothPlastic, transparency = 0, collide = false },
	White = { color = "#EEEBE5", material = Enum.Material.SmoothPlastic, transparency = 0, collide = false },
	Cream = { color = "#E6DCC2", material = Enum.Material.SmoothPlastic, transparency = 0, collide = false },
	GaugeOrange = { color = "#FF6A00", material = Enum.Material.SmoothPlastic, transparency = 0, collide = false },
	Slate = { color = "#36475C", material = Enum.Material.SmoothPlastic, transparency = 0, collide = true },
	DarkGrey = { color = "#2A2E34", material = Enum.Material.SmoothPlastic, transparency = 0, collide = true },
	SteelGrey = { color = "#7A848E", material = Enum.Material.SmoothPlastic, transparency = 0, collide = true },
	SteelDark = { color = "#3F454C", material = Enum.Material.SmoothPlastic, transparency = 0, collide = true },
	SteelLight = { color = "#C3C8CD", material = Enum.Material.SmoothPlastic, transparency = 0, collide = false },
	Gunmetal = { color = "#4A423D", material = Enum.Material.SmoothPlastic, transparency = 0, collide = true },
	TreadPlate = { color = "#A9ADB0", material = Enum.Material.SmoothPlastic, transparency = 0, collide = true },
	Belt = { color = "#23262B", material = Enum.Material.SmoothPlastic, transparency = 0, collide = true },
	OreRock = { color = "#8A766A", material = Enum.Material.SmoothPlastic, transparency = 0, collide = true },
	OreRockDark = { color = "#3E3631", material = Enum.Material.SmoothPlastic, transparency = 0, collide = true },
	-- ohne Textur, immer so einstellen:
	Cyan = { color = "#3FF5E3", material = Enum.Material.Neon, transparency = 0, collide = false, plain = true },
	Glass = { color = "#BFD3DC", material = Enum.Material.Glass, transparency = 0.1, collide = true, plain = true },
	GlassDark = { color = "#4E5D66", material = Enum.Material.Glass, transparency = 0.5, collide = true, plain = true },
}

-- Größte Ausdehnung jedes Modells in Studs (aus den Blender-Exporten).
local SIZES: { [string]: number } = {
	ConveyorStraight = 8.0,
	ConveyorSegment = 4.98,
	ConveyorCurve = 8.49,
	ConveyorCurveLeft = 8.49,
	ConveyorEnd = 6.325,
	OreChunkA = 1.056,
	OreChunkB = 0.72,
	OreChunkC = 1.07,
	OreBin = 9.35,
	BaseHall = 17.7,
	BaseRoom = 10.45,
}

local function split(name: string): (string, string?)
	-- Importer hängen manchmal Zusätze an (z. B. ".001"), die werden ignoriert
	local clean = string.gsub(name, "%.%d+$", "")
	local parts = string.split(clean, "_")
	if #parts < 2 then
		return clean, nil
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
				if look and LOOKS[look] and SIZES[modelName] then
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
local textured = 0

for _, part in parts do
	local modelName, lookName = split(part.Name)
	local look = LOOKS[lookName :: string]
	local surface = part:FindFirstChildOfClass("SurfaceAppearance")
	if look.plain then
		if surface then
			surface:Destroy()
		end
		part.Color = Color3.fromHex(look.color)
		part.Material = look.material
		part.Transparency = look.transparency
	elseif surface then
		textured += 1 -- Textur vom Import behalten
	else
		part.Color = Color3.fromHex(look.color)
		part.Material = look.material
		part.Transparency = 0
	end
	part.Anchored = true
	part.CanCollide = look.collide
	part.CanTouch = look.collide

	-- In ein Modell mit dem Modellnamen einsortieren
	local current = part.Parent
	if current and current:IsA("Model") and current.Name == modelName then
		models[modelName] = current
	else
		local target = models[modelName]
		if not target then
			if current and current:IsA("Model") then
				touchedContainers[current] = true
			end
			target = Instance.new("Model")
			target.Name = modelName
			target.Parent = if current and current:IsA("Model") then current.Parent else (current or workspace)
			models[modelName] = target
		end
		part.Parent = target
	end
end

-- Leere Import-Hüllen aufräumen
for container in touchedContainers do
	if container.Parent and #container:GetDescendants() == 0 then
		container:Destroy()
	end
end

local count = 0
for name, model in models do
	count += 1
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
print(("[GMT] fertig: %d Teile (%d mit Textur) in %d Modellen eingerichtet"):format(#parts, textured, count))
