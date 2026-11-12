--!nonstrict
-- Exportiert jede Deko-Vorlage als Roblox-Modell-Datei (.rbxm) nach assets/modelle/umwelt/.
-- Jede Datei enthaelt einen Folder mit einem Model je Farbvariante (nebeneinander aufgereiht).
-- In Studio: Rechtsklick auf Workspace -> "Insert from File..." -> .rbxm waehlen.
--
-- Start (nach python3 generate.py):  lune run werkzeuge/weltgenerator/export_models.luau
-- Benutzt die Lune-Bibliothek @lune/roblox (Instanzen bauen und als .rbxm speichern).

local fs = require("@lune/fs")
local luau = require("@lune/luau")
local process = require("@lune/process")
local roblox = require("@lune/roblox")

local Instance = roblox.Instance
local Vector3 = roblox.Vector3
local CFrame = roblox.CFrame
local Color3 = roblox.Color3
local Enum = roblox.Enum

local root = process.cwd
-- Pfade relativ zum Repo-Hauptordner oder zum Spielordner erlauben
local game = if fs.isDir(root .. "/galactic-miner-tycoon") then root .. "/galactic-miner-tycoon" else root
local templatesPath = game .. "/src/ServerStorage/WorldBuilder/Data/Templates.luau"
local outDir = game .. "/assets/modelle/umwelt"

local chunk = luau.load(fs.readFile(templatesPath), {
	debugName = "Templates",
	environment = { Color3 = Color3 },
})
local templates = chunk()

if not fs.isDir(outDir) then
	fs.writeDir(outDir)
end

local SHAPES = {
	Block = Enum.PartType.Block,
	Ball = Enum.PartType.Ball,
	Cylinder = Enum.PartType.Cylinder,
}

local function buildPart(def, colors, offset)
	local part
	if def.shape == "Wedge" then
		part = Instance.new("WedgePart")
	else
		part = Instance.new("Part")
		if def.shape == "Ellipsoid" then
			local mesh = Instance.new("SpecialMesh")
			mesh.MeshType = Enum.MeshType.Sphere
			mesh.Parent = part
		elseif SHAPES[def.shape] then
			part.Shape = SHAPES[def.shape]
		end
	end
	local cf = def.cf
	part.Name = def.role
	part.Anchored = true
	part.CanCollide = def.collide == true
	part.CanQuery = def.collide == true
	part.CanTouch = false
	part.CastShadow = def.castShadow ~= false
	part.TopSurface = Enum.SurfaceType.Smooth
	part.BottomSurface = Enum.SurfaceType.Smooth
	part.Material = Enum.Material[def.material] or Enum.Material.SmoothPlastic
	part.Color = colors[def.role] or Color3.new(1, 0, 1)
	part.Transparency = def.transparency or 0
	part.Reflectance = def.reflectance or 0
	part.Size = Vector3.new(def.size[1], def.size[2], def.size[3])
	part.CFrame = offset
		* CFrame.new(cf[1], cf[2], cf[3], cf[4], cf[5], cf[6], cf[7], cf[8], cf[9], cf[10], cf[11], cf[12])
	if def.light then
		local light = Instance.new("PointLight")
		light.Range = def.light.range
		light.Brightness = def.light.brightness
		light.Color = colors[def.light.role or def.role] or Color3.new(1, 1, 1)
		light.Shadows = false
		light.Parent = part
	end
	return part
end

local names = {}
for name in templates do
	table.insert(names, name)
end
table.sort(names)

for _, name in names do
	local t = templates[name]
	-- Breite der Vorlage grob schaetzen, damit die Varianten nebeneinander stehen
	local extent = 4
	for _, def in t.parts do
		local cf, size = def.cf, def.size
		extent = math.max(extent, math.abs(cf[1]) + size[1], math.abs(cf[3]) + size[3])
	end
	local folder = Instance.new("Folder")
	folder.Name = name
	for v, colors in t.variants do
		local offset = CFrame.new((v - 1) * extent * 2.5, 0, 0)
		local model = Instance.new("Model")
		model.Name = if #t.variants > 1 then string.format("%s_%d", name, v) else name
		for _, def in t.parts do
			buildPart(def, colors, offset).Parent = model
		end
		model.WorldPivot = offset
		model.Parent = folder
	end
	fs.writeFile(string.format("%s/%s.rbxm", outDir, name), roblox.serializeModel({ folder }))
	print(string.format("%-24s %2d Teile, %d Varianten", name, #t.parts, #t.variants))
end
print("Gespeichert in " .. outDir)
