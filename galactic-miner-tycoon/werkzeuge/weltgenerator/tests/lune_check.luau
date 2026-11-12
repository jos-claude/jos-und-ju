--!nocheck
-- Nachgebaute Roblox-Umgebung fuer den WorldBuilder, ausgefuehrt mit Lune.
-- Aufruf: lune run lune_check.luau <modus> <pfad> <ergebnis.json> <szenario>
--   modus  : init (Ordner mit init.luau, Settings.luau, Data/) | bundle-module | bundle-script (pfad = BuildIsland1.luau)
--   szenario: full | terrain_off | props_off
-- Alles Aufgezeichnete (Terrain-Aufrufe, Instanzbaum, Lighting, Logs) wird als JSON geschrieben.

local fs = require("@lune/fs")
local luau = require("@lune/luau")
local process = require("@lune/process")
local serde = require("@lune/serde")

local MODE, ROOT, OUTFILE, SCENARIO = process.args[1], process.args[2], process.args[3], process.args[4] or "full"

local rtypeof_raw = typeof
local function rtypeof(v)
	if type(v) == "table" then
		local mt = getmetatable(v)
		if mt and mt.__type then
			return mt.__type
		end
	end
	return rtypeof_raw(v)
end

local LOGS = {}
local NOTES = {} -- Dinge, die in echtem Roblox still geaendert werden (Klemmung) oder auffallen
local function note(msg)
	if #NOTES < 200 then
		table.insert(NOTES, msg)
	end
end

----------------------------------------------------------------------
-- Enums (nur echte Roblox-Werte; Unbekanntes wirft wie in Roblox)
----------------------------------------------------------------------
local ENUM_VALUES = {
	Material = { "Plastic", "Wood", "Slate", "Concrete", "CorrodedMetal", "DiamondPlate", "Foil", "Grass", "Ice", "Marble", "Granite", "Brick", "Pebble", "Sand", "Fabric", "SmoothPlastic", "Metal", "WoodPlanks", "Cobblestone", "Air", "Water", "Rock", "Glacier", "Snow", "Sandstone", "Mud", "Basalt", "Ground", "CrackedLava", "Neon", "Glass", "Asphalt", "LeafyGrass", "Salt", "Limestone", "Pavement", "ForceField", "Plaster", "Cardboard", "Carpet", "CeramicTiles", "ClayRoofTiles", "Leather", "Rubber", "RoofShingles" },
	PartType = { "Ball", "Block", "Cylinder", "Wedge", "CornerWedge" },
	MeshType = { "Head", "Torso", "Wedge", "Sphere", "Cylinder", "FileMesh", "Brick" },
	SurfaceType = { "Smooth", "Glue", "Weld", "Studs", "Inlet", "Universal", "Hinge", "Motor", "SteppingMotor", "SmoothNoOutlines" },
	Technology = { "Legacy", "Voxel", "Compatibility", "ShadowMap", "Future" },
}
local EnumItemMT = { __type = "EnumItem", __tostring = function(self) return `Enum.{self.EnumType}.{self.Name}` end }
local EnumTypes = {}
for enumName, names in ENUM_VALUES do
	local items = {}
	for i, n in names do
		items[n] = setmetatable({ Name = n, Value = i - 1, EnumType = enumName }, EnumItemMT)
	end
	EnumTypes[enumName] = setmetatable({}, {
		__index = function(_, k)
			local it = items[k]
			if it == nil then
				error(`{tostring(k)} is not a valid member of Enum.{enumName}`, 2)
			end
			return it
		end,
		__type = "Enum",
	})
end
local Enum = setmetatable({}, {
	__index = function(_, k)
		local e = EnumTypes[k]
		if not e then
			error(`{tostring(k)} is not a valid member of Enum`, 2)
		end
		return e
	end,
})

----------------------------------------------------------------------
-- Vector3 / CFrame / Color3 / Region3
----------------------------------------------------------------------
local V3 = {}
local V3MT
V3MT = {
	__type = "Vector3",
	__index = function(self, k)
		if k == "Magnitude" then
			return math.sqrt(self.X ^ 2 + self.Y ^ 2 + self.Z ^ 2)
		end
		error(`{k} is not a valid member of Vector3`, 2)
	end,
	__add = function(a, b) return V3.new(a.X + b.X, a.Y + b.Y, a.Z + b.Z) end,
	__sub = function(a, b) return V3.new(a.X - b.X, a.Y - b.Y, a.Z - b.Z) end,
	__mul = function(a, b)
		if type(a) == "number" then return V3.new(a * b.X, a * b.Y, a * b.Z) end
		if type(b) == "number" then return V3.new(a.X * b, a.Y * b, a.Z * b) end
		return V3.new(a.X * b.X, a.Y * b.Y, a.Z * b.Z)
	end,
	__div = function(a, b)
		if type(b) == "number" then return V3.new(a.X / b, a.Y / b, a.Z / b) end
		return V3.new(a.X / b.X, a.Y / b.Y, a.Z / b.Z)
	end,
	__unm = function(a) return V3.new(-a.X, -a.Y, -a.Z) end,
	__eq = function(a, b) return a.X == b.X and a.Y == b.Y and a.Z == b.Z end,
}
local function checknum(v, argn, fname)
	if type(v) ~= "number" then
		error(`invalid argument #{argn} to '{fname}' (number expected, got {rtypeof(v)})`, 3)
	end
	return v
end
function V3.new(x, y, z)
	x, y, z = x or 0, y or 0, z or 0
	checknum(x, 1, "new"); checknum(y, 2, "new"); checknum(z, 3, "new")
	return setmetatable({ X = x, Y = y, Z = z }, V3MT)
end
V3.zero = V3.new(0, 0, 0)

local CF = {}
local CFMT
local function cfmul(a, b)
	local A, B = a.c, b.c
	local r = table.create(12)
	for i = 0, 2 do
		for j = 0, 2 do
			r[4 + i * 3 + j] = A[4 + i * 3] * B[4 + j] + A[5 + i * 3] * B[7 + j] + A[6 + i * 3] * B[10 + j]
		end
	end
	r[1] = A[1] + A[4] * B[1] + A[5] * B[2] + A[6] * B[3]
	r[2] = A[2] + A[7] * B[1] + A[8] * B[2] + A[9] * B[3]
	r[3] = A[3] + A[10] * B[1] + A[11] * B[2] + A[12] * B[3]
	return setmetatable({ c = r }, CFMT)
end
CFMT = {
	__type = "CFrame",
	__index = function(self, k)
		local c = self.c
		if k == "Position" then return V3.new(c[1], c[2], c[3]) end
		if k == "X" then return c[1] end
		if k == "Y" then return c[2] end
		if k == "Z" then return c[3] end
		if k == "GetComponents" then return function(s) return table.unpack(s.c) end end
		error(`{k} is not a valid member of CFrame`, 2)
	end,
	__mul = function(a, b)
		if rtypeof(b) == "CFrame" then return cfmul(a, b) end
		if rtypeof(b) == "Vector3" then
			local c = a.c
			return V3.new(c[1] + c[4] * b.X + c[5] * b.Y + c[6] * b.Z, c[2] + c[7] * b.X + c[8] * b.Y + c[9] * b.Z, c[3] + c[10] * b.X + c[11] * b.Y + c[12] * b.Z)
		end
		error("CFrame * unsupported", 2)
	end,
}
function CF.new(...)
	local n = select("#", ...)
	local a = { ... }
	if n == 0 then
		return setmetatable({ c = { 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1 } }, CFMT)
	elseif n == 1 and rtypeof(a[1]) == "Vector3" then
		return setmetatable({ c = { a[1].X, a[1].Y, a[1].Z, 1, 0, 0, 0, 1, 0, 0, 0, 1 } }, CFMT)
	elseif n == 3 then
		for i = 1, 3 do checknum(a[i], i, "new") end
		return setmetatable({ c = { a[1], a[2], a[3], 1, 0, 0, 0, 1, 0, 0, 0, 1 } }, CFMT)
	elseif n == 12 then
		for i = 1, 12 do checknum(a[i], i, "new") end
		return setmetatable({ c = { table.unpack(a) } }, CFMT)
	end
	error(`CFrame.new: unsupported argument count {n}`, 2)
end
function CF.Angles(rx, ry, rz)
	checknum(rx, 1, "Angles"); checknum(ry, 2, "Angles"); checknum(rz, 3, "Angles")
	local cx, sx, cy, sy, cz, sz = math.cos(rx), math.sin(rx), math.cos(ry), math.sin(ry), math.cos(rz), math.sin(rz)
	local X = setmetatable({ c = { 0, 0, 0, 1, 0, 0, 0, cx, -sx, 0, sx, cx } }, CFMT)
	local Y = setmetatable({ c = { 0, 0, 0, cy, 0, sy, 0, 1, 0, -sy, 0, cy } }, CFMT)
	local Z = setmetatable({ c = { 0, 0, 0, cz, -sz, 0, sz, cz, 0, 0, 0, 1 } }, CFMT)
	return X * Y * Z -- wie Roblox: Rx * Ry * Rz
end
CF.identity = CF.new()

local C3MT = { __type = "Color3" }
local C3 = {}
function C3.fromRGB(r, g, b)
	return setmetatable({ R = r / 255, G = g / 255, B = b / 255 }, C3MT)
end
function C3.new(r, g, b)
	return setmetatable({ R = r or 0, G = g or 0, B = b or 0 }, C3MT)
end

local R3 = {}
local R3MT = { __type = "Region3" }
function R3.new(min, max)
	if rtypeof(min) ~= "Vector3" or rtypeof(max) ~= "Vector3" then
		error("Region3.new: Vector3 erwartet", 2)
	end
	return setmetatable({ Min = min, Max = max, Size = max - min }, R3MT)
end

----------------------------------------------------------------------
-- Instanzen
----------------------------------------------------------------------
local BASEPART = {
	Anchored = "boolean", CanCollide = "boolean", CanQuery = "boolean", CanTouch = "boolean", CastShadow = "boolean",
	Massless = "boolean", Locked = "boolean",
	TopSurface = "Enum.SurfaceType", BottomSurface = "Enum.SurfaceType", LeftSurface = "Enum.SurfaceType",
	RightSurface = "Enum.SurfaceType", FrontSurface = "Enum.SurfaceType", BackSurface = "Enum.SurfaceType",
	Material = "Enum.Material", Color = "Color3", Transparency = "number", Reflectance = "number",
	Size = "Vector3", CFrame = "CFrame",
}
local function merge(...)
	local t = {}
	for _, s in { ... } do for k, v in s do t[k] = v end end
	return t
end
local CLASSES = {
	Instance = { props = { Name = "string" }, anc = {} },
	Folder = { props = {}, anc = { "Instance" } },
	Model = { props = { WorldPivot = "CFrame" }, anc = { "Instance" } },
	ModuleScript = { props = {}, anc = { "Instance" } },
	DataModel = { props = {}, anc = { "Instance" } },
	Workspace = { props = {}, anc = { "Instance" } },
	ServerStorage = { props = {}, anc = { "Instance" } },
	ChangeHistoryService = { props = {}, anc = { "Instance" } },
	Part = { props = merge(BASEPART, { Shape = "Enum.PartType" }), anc = { "BasePart", "PVInstance", "Instance" } },
	WedgePart = { props = merge(BASEPART), anc = { "BasePart", "PVInstance", "Instance" } },
	SpawnLocation = { props = merge(BASEPART, { Neutral = "boolean", Duration = "number" }), anc = { "Part", "BasePart", "PVInstance", "Instance" } },
	Texture = { props = { Transparency = "number", Texture = "string", StudsPerTileU = "number", StudsPerTileV = "number" }, anc = { "Decal", "FaceInstance", "Instance" } },
	SpecialMesh = { props = { MeshType = "Enum.MeshType", Scale = "Vector3", Offset = "Vector3", MeshId = "string", TextureId = "string" }, anc = { "FileMesh", "DataModelMesh", "Instance" } },
	PointLight = { props = { Range = "number", Brightness = "number", Color = "Color3", Shadows = "boolean", Enabled = "boolean" }, anc = { "Light", "Instance" } },
	Terrain = { props = { WaterColor = "Color3", WaterReflectance = "number", WaterTransparency = "number", WaterWaveSize = "number", WaterWaveSpeed = "number", Decoration = "boolean" }, anc = { "BasePart", "PVInstance", "Instance" } },
	Lighting = { props = {
		ClockTime = "number", TimeOfDay = "string", Brightness = "number", Ambient = "Color3", OutdoorAmbient = "Color3",
		ColorShift_Top = "Color3", ColorShift_Bottom = "Color3", ExposureCompensation = "number", FogColor = "Color3",
		FogEnd = "number", FogStart = "number", GeographicLatitude = "number", GlobalShadows = "boolean",
		EnvironmentDiffuseScale = "number", EnvironmentSpecularScale = "number", ShadowSoftness = "number",
		Technology = "Enum.Technology",
	}, anc = { "Instance" } },
	Atmosphere = { props = { Density = "number", Offset = "number", Color = "Color3", Decay = "Color3", Glare = "number", Haze = "number" }, anc = { "Instance" } },
	Sky = { props = {
		SkyboxBk = "string", SkyboxDn = "string", SkyboxFt = "string", SkyboxLf = "string", SkyboxRt = "string", SkyboxUp = "string",
		CelestialBodiesShown = "boolean", StarCount = "number", SunAngularSize = "number", MoonAngularSize = "number",
		SunTextureId = "string", MoonTextureId = "string",
	}, anc = { "Instance" } },
	BloomEffect = { props = { Enabled = "boolean", Intensity = "number", Size = "number", Threshold = "number" }, anc = { "PostEffect", "Instance" } },
	ColorCorrectionEffect = { props = { Enabled = "boolean", Brightness = "number", Contrast = "number", Saturation = "number", TintColor = "Color3" }, anc = { "PostEffect", "Instance" } },
	SunRaysEffect = { props = { Enabled = "boolean", Intensity = "number", Spread = "number" }, anc = { "PostEffect", "Instance" } },
	DepthOfFieldEffect = { props = { Enabled = "boolean", FarIntensity = "number", FocusDistance = "number", InFocusRadius = "number", NearIntensity = "number" }, anc = { "PostEffect", "Instance" } },
}
for _, c in CLASSES do
	c.props = merge(CLASSES.Instance.props, c.props)
end

local function defaultFor(spec)
	if spec == "number" then return 0 end
	if spec == "boolean" then return false end
	if spec == "string" then return "" end
	if spec == "Vector3" then return V3.new(0, 0, 0) end
	if spec == "CFrame" then return CF.new() end
	if spec == "Color3" then return C3.new(0.63, 0.63, 0.63) end
	local en = string.match(spec, "^Enum%.(.+)$")
	if en then return EnumTypes[en][ENUM_VALUES[en][1]] end
end

local Methods = {}
local TerrainRec
local Instance = {}
local InstMT = {}

local function isInst(v)
	return type(v) == "table" and getmetatable(v) == InstMT
end

local function removeChild(parent, child)
	local kids = rawget(parent, "_kids")
	local i = table.find(kids, child)
	if i then table.remove(kids, i) end
end

local function setParent(inst, newParent)
	if newParent ~= nil and not isInst(newParent) then
		error("Attempt to set Parent to non-Instance", 3)
	end
	local old = rawget(inst, "_parent")
	if old then removeChild(old, inst) end
	rawset(inst, "_parent", newParent)
	if newParent then table.insert(rawget(newParent, "_kids"), inst) end
end

local function checkValue(spec, value, class, prop)
	local ok
	local t = rtypeof(value)
	if spec == "number" then ok = t == "number" and value == value
	elseif spec == "boolean" then ok = t == "boolean"
	elseif spec == "string" then ok = t == "string"
	elseif spec == "Vector3" or spec == "CFrame" or spec == "Color3" then ok = t == spec
	else
		local en = string.match(spec, "^Enum%.(.+)$")
		ok = t == "EnumItem" and value.EnumType == en
	end
	if not ok then
		error(`Unable to assign property {prop}. {spec} expected, got {t} ({tostring(value)}) on {class}`, 3)
	end
end

function Instance.new(className, parent)
	local def = CLASSES[className]
	if not def then
		error(`Unable to create an Instance of type "{tostring(className)}"`, 2)
	end
	local inst = setmetatable({ _class = className, _def = def, _set = {}, _setOrder = {}, _kids = {}, _parent = nil, _alive = true }, InstMT)
	rawget(inst, "_set").Name = className
	if className == "Terrain" then rawset(inst, "_set", { Name = "Terrain" }) end
	return inst
end

InstMT.__type = "Instance"
InstMT.__index = function(self, k)
	local class = rawget(self, "_class")
	local def = rawget(self, "_def")
	if k == "ClassName" then return class end
	if k == "Parent" then return rawget(self, "_parent") end
	local spec = def.props[k]
	if spec then
		local set = rawget(self, "_set")
		local v = set[k]
		if v == nil then
			v = defaultFor(spec)
			if k == "Size" then v = V3.new(4, 1, 2) end
		end
		if k == "Position" then end
		return v
	end
	if class == "Terrain" and TerrainRec and TerrainRec.methods[k] then
		return TerrainRec.methods[k]
	end
	local m = Methods[k]
	if m then return m end
	if class == "Part" or class == "WedgePart" or class == "SpawnLocation" or class == "Terrain" then
		if k == "Position" then return rawget(self, "_set").CFrame and self.CFrame.Position or V3.new(0, 0, 0) end
	end
	for _, kid in rawget(self, "_kids") do
		if rawget(kid, "_set").Name == k then return kid end
	end
	error(`{tostring(k)} is not a valid member of {class} "{rawget(self, "_set").Name}"`, 2)
end
InstMT.__newindex = function(self, k, v)
	local class = rawget(self, "_class")
	if k == "Parent" then
		setParent(self, v)
		return
	end
	local spec = rawget(self, "_def").props[k]
	if not spec then
		error(`{tostring(k)} is not a valid member of {class}`, 2)
	end
	checkValue(spec, v, class, k)
	if k == "Size" and (class == "Part" or class == "WedgePart") then
		for _, c in { v.X, v.Y, v.Z } do
			if c > 2048 then error("Part size exceeds 2048", 2) end
			if c < 0.05 then note(`Part.Size-Komponente {c} < 0.05 wird in Roblox geklemmt`) end
		end
	end
	if k == "Range" and class == "PointLight" and v > 60 then
		note(`PointLight.Range {v} > 60 wird geklemmt`)
	end
	rawget(self, "_set")[k] = v
	local order = rawget(self, "_setOrder")
	if not table.find(order, k) then table.insert(order, k) end
end

function Methods.IsA(self, cls)
	if rawget(self, "_class") == cls then return true end
	return table.find(rawget(self, "_def").anc, cls) ~= nil
end
function Methods.GetChildren(self) return table.clone(rawget(self, "_kids")) end
function Methods.FindFirstChild(self, name)
	for _, kid in rawget(self, "_kids") do
		if rawget(kid, "_set").Name == name then return kid end
	end
	return nil
end
function Methods.WaitForChild(self, name)
	local c = Methods.FindFirstChild(self, name)
	if not c then
		error(`Infinite yield: WaitForChild("{name}") auf {rawget(self, "_set").Name} (Kind existiert nicht)`, 2)
	end
	return c
end
function Methods.FindFirstChildOfClass(self, cls)
	for _, kid in rawget(self, "_kids") do
		if rawget(kid, "_class") == cls then return kid end
	end
	return nil
end
function Methods.Destroy(self)
	setParent(self, nil)
	rawset(self, "_alive", false)
	for _, kid in table.clone(rawget(self, "_kids")) do Methods.Destroy(kid) end
end
function Methods.Clone(self)
	local copy = Instance.new(rawget(self, "_class"))
	rawset(copy, "_set", table.clone(rawget(self, "_set")))
	rawset(copy, "_setOrder", table.clone(rawget(self, "_setOrder")))
	for _, kid in rawget(self, "_kids") do
		local k2 = Methods.Clone(kid)
		setParent(k2, copy)
	end
	return copy
end
function Methods.GetService() error("kein DataModel", 2) end
function Methods.SetWaypoint(self, name) TerrainRec.history[#TerrainRec.history + 1] = name end

----------------------------------------------------------------------
-- Terrain-Mock mit Aufzeichnung
----------------------------------------------------------------------
TerrainRec = { calls = {}, methods = {}, history = {} }
local function argcheck(fn, i, v, t)
	if rtypeof(v) ~= t then
		error(`invalid argument #{i} to '{fn}' ({t} expected, got {rtypeof(v)})`, 3)
	end
end
local function matcheck(fn, i, v)
	if rtypeof(v) ~= "EnumItem" or v.EnumType ~= "Material" then
		error(`invalid argument #{i} to '{fn}' (Enum.Material expected, got {rtypeof(v)})`, 3)
	end
end
local function cfc(cf) return table.clone(cf.c) end
function TerrainRec.methods.Clear(self)
	table.insert(TerrainRec.calls, { m = "Clear" })
end
function TerrainRec.methods.SetMaterialColor(self, mat, color)
	matcheck("SetMaterialColor", 1, mat)
	argcheck("SetMaterialColor", 2, color, "Color3")
	table.insert(TerrainRec.calls, { m = "SetMaterialColor", mat = mat.Name, color = { color.R, color.G, color.B } })
end
function TerrainRec.methods.FillBall(self, c, r, mat)
	argcheck("FillBall", 1, c, "Vector3"); checknum(r, 2, "FillBall"); matcheck("FillBall", 3, mat)
	table.insert(TerrainRec.calls, { m = "FillBall", c = { c.X, c.Y, c.Z }, r = r, mat = mat.Name })
end
function TerrainRec.methods.FillBlock(self, cf, size, mat)
	argcheck("FillBlock", 1, cf, "CFrame"); argcheck("FillBlock", 2, size, "Vector3"); matcheck("FillBlock", 3, mat)
	table.insert(TerrainRec.calls, { m = "FillBlock", cf = cfc(cf), size = { size.X, size.Y, size.Z }, mat = mat.Name })
end
function TerrainRec.methods.FillCylinder(self, cf, h, r, mat)
	argcheck("FillCylinder", 1, cf, "CFrame"); checknum(h, 2, "FillCylinder"); checknum(r, 3, "FillCylinder"); matcheck("FillCylinder", 4, mat)
	table.insert(TerrainRec.calls, { m = "FillCylinder", cf = cfc(cf), height = h, r = r, mat = mat.Name })
end
function TerrainRec.methods.FillWedge(self, cf, size, mat)
	argcheck("FillWedge", 1, cf, "CFrame"); argcheck("FillWedge", 2, size, "Vector3"); matcheck("FillWedge", 3, mat)
	table.insert(TerrainRec.calls, { m = "FillWedge", cf = cfc(cf), size = { size.X, size.Y, size.Z }, mat = mat.Name })
end
function TerrainRec.methods.WriteVoxels(self, region, res, materials, occupancy)
	argcheck("WriteVoxels", 1, region, "Region3")
	checknum(res, 2, "WriteVoxels")
	if res ~= 4 then error("WriteVoxels: Aufloesung muss 4 sein", 2) end
	for _, ax in { "X", "Y", "Z" } do
		if (region.Min[ax] / 4) % 1 ~= 0 or (region.Max[ax] / 4) % 1 ~= 0 then
			error("WriteVoxels: Region3 nicht am 4-Stud-Raster ausgerichtet (" .. ax .. ")", 2)
		end
	end
	local sx, sy, sz = region.Size.X / 4, region.Size.Y / 4, region.Size.Z / 4
	if type(materials) ~= "table" or type(occupancy) ~= "table" then error("WriteVoxels: Tabellen erwartet", 2) end
	if #materials ~= sx or #occupancy ~= sx then error(`WriteVoxels: X-Groesse {#materials} statt {sx}`, 2) end
	local call = { m = "WriteVoxels", min = { region.Min.X, region.Min.Y, region.Min.Z }, max = { region.Max.X, region.Max.Y, region.Max.Z }, dims = { sx, sy, sz }, vx = {}, vy = {}, vz = {}, mat = {}, occ = {}, badAirOcc = 0, badSolidZero = 0 }
	local ox, oy, oz = region.Min.X / 4, region.Min.Y / 4, region.Min.Z / 4
	local AIR = Enum.Material.Air
	local n = 0
	for i = 1, sx do
		local my, oyy = materials[i], occupancy[i]
		if type(my) ~= "table" or #my ~= sy or #oyy ~= sy then error(`WriteVoxels: Y-Groesse falsch bei x={i}`, 2) end
		for j = 1, sy do
			local mz, ozz = my[j], oyy[j]
			if type(mz) ~= "table" or #mz ~= sz or #ozz ~= sz then error(`WriteVoxels: Z-Groesse falsch bei x={i},y={j}`, 2) end
			for k = 1, sz do
				local m, o = mz[k], ozz[k]
				if rtypeof(m) ~= "EnumItem" or m.EnumType ~= "Material" then error(`WriteVoxels: Material fehlt/ungueltig bei {i},{j},{k}`, 2) end
				if type(o) ~= "number" or o ~= o or o < 0 or o > 1 then error(`WriteVoxels: Belegung ausserhalb 0..1 bei {i},{j},{k}: {tostring(o)}`, 2) end
				if m == AIR then
					if o > 0 then call.badAirOcc += 1 end
				else
					if o == 0 then call.badSolidZero += 1 end
					n += 1
					call.vx[n] = ox + i - 1
					call.vy[n] = oy + j - 1
					call.vz[n] = oz + k - 1
					call.mat[n] = m.Name
					call.occ[n] = o
				end
			end
		end
	end
	table.insert(TerrainRec.calls, call)
end

----------------------------------------------------------------------
-- Welt
----------------------------------------------------------------------
local function newNamed(class, name, parent)
	local i = Instance.new(class)
	i.Name = name
	if parent then i.Parent = parent end
	return i
end
local gameInst = newNamed("DataModel", "Game")
local workspaceInst = newNamed("Workspace", "Workspace", gameInst)
local lightingInst = newNamed("Lighting", "Lighting", gameInst)
local storageInst = newNamed("ServerStorage", "ServerStorage", gameInst)
local historyInst = newNamed("ChangeHistoryService", "ChangeHistoryService", gameInst)
local terrainInst = newNamed("Terrain", "Terrain", workspaceInst)
function Methods.GetService(self, name)
	local c = Methods.FindFirstChild(gameInst, name)
	if not c then error(`'{name}' is not a valid Service name`, 2) end
	return c
end

-- Ausgangszustand eines frischen Studio-Projekts (plus Altlasten, die der Builder wegsichern soll)
local baseplate = newNamed("Part", "Baseplate", workspaceInst)
baseplate.Size = V3.new(2048, 16, 2048)
baseplate.Anchored = true
baseplate.CanCollide = true; baseplate.CanQuery = true; baseplate.CanTouch = true; baseplate.CastShadow = true
local bpTexture = newNamed("Texture", "Texture", baseplate)
bpTexture.Transparency = 0
local spawnLoc = newNamed("SpawnLocation", "SpawnLocation", workspaceInst)
spawnLoc.Size = V3.new(12, 1, 12)
spawnLoc.CFrame = CF.new(0, 0.5, 0)
newNamed("Sky", "OldSky", lightingInst)
newNamed("Atmosphere", "OldAtmosphere", lightingInst)
newNamed("BloomEffect", "OldBloom", lightingInst)
newNamed("Folder", "KeepMe", lightingInst) -- bleibt unberuehrt
-- schon vorhandene alte Insel (muss ersetzt werden)
local oldIsland = newNamed("Folder", "Island1", workspaceInst)
newNamed("Folder", "AlterInhalt", oldIsland)

-- Dateien -> ModuleScript-Baum (wie Rojo)
local function makeModule(name, path)
	local m = newNamed("ModuleScript", name, nil)
	rawset(m, "_path", path)
	return m
end
local function scanDir(dirPath, parent)
	for _, entry in fs.readDir(dirPath) do
		local full = dirPath .. "/" .. entry
		if fs.isDir(full) then
			local f = newNamed("Folder", entry, parent)
			scanDir(full, f)
		elseif string.sub(entry, -5) == ".luau" and entry ~= "init.luau" then
			local m = makeModule(string.sub(entry, 1, -6), full)
			m.Parent = parent
		end
	end
end

local baseEnv
local requireCache = {}
local function loadModule(obj)
	local cached = requireCache[obj]
	if cached then return cached.value end
	local src = fs.readFile(rawget(obj, "_path"))
	local env = table.clone(baseEnv)
	env.script = obj
	local fn = luau.load(src, { environment = env, debugName = rawget(obj, "_path") })
	local value = fn()
	requireCache[obj] = { value = value }
	return value
end

local function plain(v)
	local t = rtypeof(v)
	if t == "Vector3" then return { v.X, v.Y, v.Z } end
	if t == "CFrame" then return table.clone(v.c) end
	if t == "Color3" then return { v.R, v.G, v.B } end
	if t == "EnumItem" then return tostring(v) end
	if type(v) == "number" then
		if v ~= v then return "NaN" end
		if v == math.huge then return "inf" end
		if v == -math.huge then return "-inf" end
	end
	return v
end
local function dump(inst, skipKids)
	local props = {}
	for k, v in rawget(inst, "_set") do
		props[k] = plain(v)
	end
	local out = { class = rawget(inst, "_class"), name = rawget(inst, "_set").Name, props = props, kids = {} }
	if not skipKids then
		for _, kid in rawget(inst, "_kids") do
			table.insert(out.kids, dump(kid))
		end
	end
	return out
end

local taskWaits = 0
baseEnv = {
	game = gameInst, workspace = workspaceInst, Workspace = workspaceInst,
	Instance = Instance, Enum = Enum, Vector3 = V3, CFrame = CF, Color3 = C3, Region3 = R3,
	typeof = rtypeof,
	print = function(...)
		local t = {}
		for i = 1, select("#", ...) do t[i] = tostring((select(i, ...))) end
		table.insert(LOGS, { k = "print", m = table.concat(t, " ") })
	end,
	warn = function(...)
		local t = {}
		for i = 1, select("#", ...) do t[i] = tostring((select(i, ...))) end
		table.insert(LOGS, { k = "warn", m = table.concat(t, " ") })
	end,
	require = function(m)
		if not isInst(m) or not Methods.IsA(m, "ModuleScript") then error("require: ModuleScript erwartet", 2) end
		return loadModule(m)
	end,
	task = { wait = function() taskWaits += 1; return 0.03 end, spawn = function(f, ...) return f(...) end, defer = function(f, ...) return f(...) end },
}

----------------------------------------------------------------------
-- Lauf
----------------------------------------------------------------------
local result = { mode = MODE, scenario = SCENARIO, builds = {}, notes = NOTES, error = nil }

local function snapshot(detail)
	local snap = {
		terrain = TerrainRec.calls,
		logs = LOGS,
		taskWaits = taskWaits,
		history = TerrainRec.history,
		baseplate = dump(baseplate),
		spawn = dump(spawnLoc, true),
		terrainProps = dump(terrainInst, true),
		lighting = dump(lightingInst),
		backup = (function()
			local b = Methods.FindFirstChild(storageInst, "WorldBuilderBackup")
			return b and dump(b) or nil
		end)(),
		workspaceKids = (function()
			local names = {}
			for _, k in rawget(workspaceInst, "_kids") do table.insert(names, rawget(k, "_class") .. ":" .. rawget(k, "_set").Name) end
			return names
		end)(),
		islands = {},
	}
	for _, k in rawget(workspaceInst, "_kids") do
		if rawget(k, "_set").Name == "Island1" then
			table.insert(snap.islands, detail and dump(k) or { class = "Folder", name = "Island1", kids = {}, count = #rawget(k, "_kids") })
		end
	end
	TerrainRec.calls = {}
	TerrainRec.history = {}
	LOGS = {}
	return snap
end

local function runBuilds(WB)
	local plans
	if SCENARIO == "full" then
		plans = { {}, {} }
	elseif SCENARIO == "terrain_off" then
		plans = { { terrain = false, lighting = false } }
	elseif SCENARIO == "terrain_only" then
		plans = { { props = false, lighting = false } }
	elseif SCENARIO == "lighting_only" then
		plans = { { terrain = false, props = false } }
	elseif SCENARIO == "props_off" then
		plans = { { props = false, hideBaseplate = false } }
	else
		error("Unbekanntes Szenario " .. SCENARIO)
	end
	for i, opts in plans do
		local t0 = os.clock()
		local ok, err = xpcall(function() WB.Build(opts) end, function(e) return tostring(e) .. "\n" .. debug.traceback() end)
		local snap = snapshot(i == 1)
		snap.options = opts
		snap.ok = ok
		snap.err = err
		snap.seconds = os.clock() - t0
		table.insert(result.builds, snap)
		if not ok then break end
	end
end

local ok, err = xpcall(function()
	-- das Terrain-Objekt braucht Zugriff auf seine Methoden
	if MODE == "init" then
		local init = makeModule("WorldBuilder", ROOT .. "/init.luau")
		scanDir(ROOT, init)
		local WB = loadModule(init)
		runBuilds(WB)
	elseif MODE == "bundle-module" then
		local m = makeModule("BuildIsland1", ROOT)
		local WB = loadModule(m)
		runBuilds(WB)
	elseif MODE == "bundle-script" then
		-- wie Befehlsleiste: script ist nil, das Skript baut sofort
		local src = fs.readFile(ROOT)
		local env = table.clone(baseEnv)
		env.script = nil
		local fn = luau.load(src, { environment = env, debugName = ROOT })
		local t0 = os.clock()
		local ok2, err2 = xpcall(fn, function(e) return tostring(e) .. "\n" .. debug.traceback() end)
		local snap = snapshot(true)
		snap.options = "(sofort)"
		snap.ok = ok2
		snap.err = err2
		snap.seconds = os.clock() - t0
		table.insert(result.builds, snap)
	else
		error("Unbekannter Modus " .. tostring(MODE))
	end
end, function(e) return tostring(e) .. "\n" .. debug.traceback() end)
if not ok then result.error = err end
fs.writeFile(OUTFILE, serde.encode("json", result))
print(`lune_check fertig: modus={MODE} szenario={SCENARIO} builds={#result.builds} fehler={result.error and "JA" or "nein"}`)
