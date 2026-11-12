--!strict
-- WorldBuilder: baut die Welt von Insel 1 (Heimatplanet) in Roblox Studio auf.
--
-- Benutzung (Studio, Edit-Modus, Befehlsleiste unter View -> Command Bar):
--     require(game.ServerStorage.WorldBuilder).Build()
-- Nur Teile neu bauen:
--     require(game.ServerStorage.WorldBuilder).Build({ terrain = false })   -- nur Deko + Licht
--     require(game.ServerStorage.WorldBuilder).Build({ props = false })     -- nur Terrain + Licht
-- Alternativ ohne Rojo: das Einzel-Skript welt/BuildIsland1.luau (gleicher Code, Daten eingebettet).
-- Ergebnis: Terrain in Workspace.Terrain, Deko in Workspace.Island1, Licht/Himmel unter Lighting.
--
-- Die Daten in ./Data erzeugt der Weltgenerator (werkzeuge/weltgenerator). Nicht von Hand aendern.
-- Eigene Einstellungen (z. B. Skybox-IDs) stehen in ./Settings.
-- Doku: technik/weltgenerator.md

local Workspace = game:GetService("Workspace")
local Lighting = game:GetService("Lighting")
local ServerStorage = game:GetService("ServerStorage")

-- BEGIN LOADER (bundle.py ersetzt diesen Block durch eingebettete Daten -> welt/BuildIsland1.luau)
local function findModule(path: string): Instance
	local node: Instance = script
	for name in string.gmatch(path, "[^/]+") do
		node = node:WaitForChild(name)
	end
	return node
end

local function loadData(path: string): any
	return require(findModule(path) :: ModuleScript)
end

local function listData(path: string): { string }
	local names = {}
	for _, child in findModule(path):GetChildren() do
		if child:IsA("ModuleScript") then
			table.insert(names, path .. "/" .. child.Name)
		end
	end
	table.sort(names)
	return names
end
-- END LOADER

local Settings = loadData("Settings")
local WORLD_FOLDER = "Island1"

local WorldBuilder = {}

type Options = {
	terrain: boolean?,
	props: boolean?,
	lighting: boolean?,
	hideBaseplate: boolean?,
	quiet: boolean?,
}

local function log(msg: string)
	print("[WorldBuilder] " .. msg)
end

----------------------------------------------------------------------
-- Daten dekodieren
----------------------------------------------------------------------

local B64: { [number]: number } = {}
do
	local alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
	for i = 1, 64 do
		B64[string.byte(alphabet, i)] = i - 1
	end
end

-- Base64 -> buffer. Gibt den Puffer und die Anzahl gueltiger Bytes zurueck.
local function decodeBase64(s: string): (buffer, number)
	local len = #s
	local out = buffer.create(math.max(1, (len // 4) * 3))
	local o = 0
	for i = 1, len - 3, 4 do
		local a, b, c, d = string.byte(s, i, i + 3)
		local va, vb = B64[a], B64[b]
		local n = va * 262144 + vb * 4096
		if c == 61 then -- "="
			buffer.writeu8(out, o, n // 65536)
			o += 1
			break
		end
		n += B64[c] * 64
		if d == 61 then
			buffer.writeu8(out, o, n // 65536)
			buffer.writeu8(out, o + 1, (n // 256) % 256)
			o += 2
			break
		end
		n += B64[d]
		buffer.writeu8(out, o, n // 65536)
		buffer.writeu8(out, o + 1, (n // 256) % 256)
		buffer.writeu8(out, o + 2, n % 256)
		o += 3
	end
	return out, o
end

local function readChannel(name: string, count: number): (buffer, number)
	local parts = table.create(count)
	for k = 1, count do
		parts[k] = loadData(string.format("Data/Terrain/%s_%02d", name, k))
	end
	return decodeBase64(table.concat(parts))
end

local function readVarint(buf: buffer, pos: number): (number, number)
	local result = 0
	local mult = 1
	while true do
		local byte = buffer.readu8(buf, pos)
		pos += 1
		if byte < 128 then
			return result + byte * mult, pos
		end
		result += (byte - 128) * mult
		mult *= 128
	end
end

-- Hoehen: Vorhersage (links + oben - oben-links) plus kodierter Rest. Ergebnis: u16 je Spalte.
local function decodeHeights(bytes: buffer, n: number): buffer
	local q = buffer.create(n * n * 2)
	local pos = 0
	local zeros = 0
	for idx = 0, n * n - 1 do
		local r = 0
		if zeros > 0 then
			zeros -= 1
		else
			local t
			t, pos = readVarint(bytes, pos)
			if t % 2 == 1 then
				zeros = (t - 1) // 2 - 1
			else
				local z = t // 2
				if z % 2 == 0 then
					r = z // 2
				else
					r = -((z + 1) // 2)
				end
			end
		end
		local row = idx // n
		local col = idx - row * n
		local pred
		if row == 0 then
			pred = if col == 0 then 0 else buffer.readu16(q, (idx - 1) * 2)
		elseif col == 0 then
			pred = buffer.readu16(q, (idx - n) * 2)
		else
			pred = buffer.readu16(q, (idx - 1) * 2)
				+ buffer.readu16(q, (idx - n) * 2)
				- buffer.readu16(q, (idx - n - 1) * 2)
		end
		buffer.writeu16(q, idx * 2, pred + r)
	end
	return q
end

-- Lauflaengen-kodierter Byte-Kanal -> u8 je Spalte.
local function decodeRle(bytes: buffer, nbytes: number, total: number): buffer
	local out = buffer.create(total)
	local pos = 0
	local idx = 0
	while pos < nbytes and idx < total do
		local value, run
		value, pos = readVarint(bytes, pos)
		run, pos = readVarint(bytes, pos)
		if value ~= 0 then
			buffer.fill(out, idx, value, run)
		end
		idx += run
	end
	return out
end

----------------------------------------------------------------------
-- Terrain
----------------------------------------------------------------------

local function buildTerrain(meta: any)
	local terrain = Workspace.Terrain
	local grid = meta.grid
	local n: number = grid.n
	local cell: number = grid.cell
	local origin: number = grid.origin
	local hmin: number = grid.hmin
	local hq: number = grid.hq

	log("Dekodiere Terrain-Daten ...")
	local hBytes = readChannel("H", meta.chunks.H)
	local H = decodeHeights(hBytes, n)
	local mBytes, mLen = readChannel("M", meta.chunks.M)
	local M = decodeRle(mBytes, mLen, n * n)
	local wBytes, wLen = readChannel("W", meta.chunks.W)
	local W = decodeRle(wBytes, wLen, n * n)
	local sBytes, sLen = readChannel("S", meta.chunks.S)
	local S = decodeRle(sBytes, sLen, n * n)
	local dBytes, dLen = readChannel("D", meta.chunks.D)
	local D = decodeRle(dBytes, dLen, n * n)

	-- Material-Tabellen
	local mats: { Enum.Material } = {}
	for i, name in meta.materials do
		mats[i - 1] = if name == "Air" then Enum.Material.Air else (Enum.Material :: any)[name]
	end
	local layers = meta.layers
	local topDepth: number = layers.topDepth
	local subDepth: number = layers.subDepth
	local subsoil: { [number]: Enum.Material } = {}
	for i, name in meta.materials do
		local sub = layers.subsoil[name] or layers.bedrock
		subsoil[i - 1] = (Enum.Material :: any)[sub]
	end
	local bedrock: Enum.Material = (Enum.Material :: any)[layers.bedrock]

	-- Gesteinsschichten: Tabelle je Stud innerhalb einer Periode
	local strata = meta.strata
	local strataLookup: { Enum.Material } = {}
	local period = 0
	for _, band in strata.bands do
		local m = (Enum.Material :: any)[band[1]]
		for _ = 1, band[2] do
			strataLookup[period] = m
			period += 1
		end
	end
	local strataBase: number = strata.base
	local waterLevels: { number } = meta.waterLevels
	local AIR = Enum.Material.Air
	local WATER = Enum.Material.Water
	local STRATA_FLAG = 32

	log("Loesche altes Terrain ...")
	terrain:Clear()

	-- Farben erst nach Clear() setzen
	if meta.materialColors then
		for name, color in meta.materialColors do
			pcall(function()
				terrain:SetMaterialColor((Enum.Material :: any)[name], color)
			end)
		end
	end
	if meta.water then
		for prop, value in meta.water do
			pcall(function()
				(terrain :: any)[prop] = value
			end)
		end
	end

	-- Neue Voxel-API mit eigenem Wasser-Kanal (Wasser fuellt auch halbvolle Ufer-Voxel).
	-- Faellt sie aus, nehmen wir WriteVoxels (Wasser dann nur in leeren Voxeln).
	local useChannels = true

	local CHUNK = 16
	local chunksPerAxis = math.ceil(n / CHUNK)
	local done = 0
	local totalChunks = chunksPerAxis * chunksPerAxis
	local lastReport = os.clock()

	for cz = 0, n - 1, CHUNK do
		for cx = 0, n - 1, CHUNK do
			local sx = math.min(CHUNK, n - cx)
			local sz = math.min(CHUNK, n - cz)
			-- Hoehenbereich des Blocks bestimmen
			local ymin, ymax = math.huge, -math.huge
			for z = cz, cz + sz - 1 do
				for x = cx, cx + sx - 1 do
					local idx = z * n + x
					local q = buffer.readu16(H, idx * 2)
					if q > 0 then
						local h = q / hq + hmin
						local bottom = h - buffer.readu8(D, idx) * cell
						if bottom < ymin then
							ymin = bottom
						end
						if h > ymax then
							ymax = h
						end
						local w = buffer.readu8(W, idx)
						if w > 0 and waterLevels[w] > ymax then
							ymax = waterLevels[w]
						end
					end
				end
			end
			if ymax > ymin then
				local y0 = math.floor(ymin / cell) * cell
				local y1 = math.ceil(ymax / cell) * cell
				local ny = math.max(1, (y1 - y0) // cell)
				local materials = table.create(sx)
				local occupancy = table.create(sx)
				local liquid = table.create(sx)
				for ix = 1, sx do
					local mx = table.create(ny)
					local ox = table.create(ny)
					local lx = table.create(ny)
					materials[ix] = mx
					occupancy[ix] = ox
					liquid[ix] = lx
					for iy = 1, ny do
						mx[iy] = table.create(sz, AIR)
						ox[iy] = table.create(sz, 0)
						lx[iy] = table.create(sz, 0)
					end
				end
				for iz = 1, sz do
					for ix = 1, sx do
						local idx = (cz + iz - 1) * n + (cx + ix - 1)
						local q = buffer.readu16(H, idx * 2)
						local w = buffer.readu8(W, idx)
						local waterLevel = if w > 0 then waterLevels[w] else -math.huge
						if q > 0 then
							local h = q / hq + hmin
							local bottom = h - buffer.readu8(D, idx) * cell
							local code = buffer.readu8(M, idx)
							local isStrata = code >= STRATA_FLAG
							local topIndex = if isStrata then code - STRATA_FLAG else code
							local topMat = mats[topIndex]
							local off = buffer.readu8(S, idx) + strataBase
							for iy = 1, ny do
								local yb = y0 + (iy - 1) * cell
								if yb < h and yb + cell > bottom then
									local occ = math.min(1, (h - yb) / cell)
									local depth = h - (yb + cell * 0.5)
									local m
									if isStrata then
										if topIndex ~= 0 and depth < topDepth then
											m = topMat
										else
											m = strataLookup[math.floor(yb + cell * 0.5 + off) % period]
										end
									elseif depth < topDepth then
										m = topMat
									elseif depth < subDepth then
										m = subsoil[topIndex]
									else
										m = bedrock
									end
									if m == AIR then
										m = bedrock -- Schutz: Material-Index 0 ohne Schicht-Flag
									end
									materials[ix][iy][iz] = m
									occupancy[ix][iy][iz] = occ
								end
								if yb < waterLevel and yb + cell > h then
									liquid[ix][iy][iz] = math.min(1, (waterLevel - yb) / cell)
								end
							end
						end
					end
				end
				local region = Region3.new(
					Vector3.new(origin + cx * cell, y0, origin + cz * cell),
					Vector3.new(origin + (cx + sx) * cell, y0 + ny * cell, origin + (cz + sz) * cell)
				)
				local written = false
				if useChannels then
					written = pcall(function()
						terrain:WriteVoxelChannels(region, cell, {
							SolidMaterial = materials,
							SolidOccupancy = occupancy,
							LiquidOccupancy = liquid,
						})
					end)
					if not written then
						useChannels = false
						log("WriteVoxelChannels nicht verfuegbar, nutze WriteVoxels.")
					end
				end
				if not written then
					-- Wasser nur in Voxeln ohne festes Material
					for ix = 1, sx do
						for iy = 1, ny do
							local mRow, oRow, lRow = materials[ix][iy], occupancy[ix][iy], liquid[ix][iy]
							for iz = 1, sz do
								if oRow[iz] == 0 and lRow[iz] > 0 then
									mRow[iz] = WATER
									oRow[iz] = lRow[iz]
								end
							end
						end
					end
					terrain:WriteVoxels(region, cell, materials, occupancy)
				end
			end
			done += 1
			if os.clock() - lastReport > 0.25 then
				lastReport = os.clock()
				task.wait()
			end
		end
		log(string.format("Terrain %d %%", math.floor(done / totalChunks * 100)))
	end

	-- Zusatzformen (Boegen, Felsbrocken, schwebende Inseln ...)
	local ops = loadData("Data/TerrainOps")
	for _, op in ops do
		local m = (Enum.Material :: any)[op.material]
		if op.op == "Ball" then
			terrain:FillBall(Vector3.new(op.c[1], op.c[2], op.c[3]), op.r, m)
		elseif op.op == "Block" then
			terrain:FillBlock(CFrame.new(table.unpack(op.cf)), Vector3.new(op.size[1], op.size[2], op.size[3]), m)
		elseif op.op == "Cylinder" then
			terrain:FillCylinder(CFrame.new(table.unpack(op.cf)), op.height, op.r, m)
		elseif op.op == "Wedge" then
			terrain:FillWedge(CFrame.new(table.unpack(op.cf)), Vector3.new(op.size[1], op.size[2], op.size[3]), m)
		end
	end
	log(string.format("Terrain fertig (%d Zusatzformen)", #ops))
end

----------------------------------------------------------------------
-- Deko (Pflanzen, Felsen, Kristalle ...)
----------------------------------------------------------------------

local SHAPES = {
	Block = Enum.PartType.Block,
	Ball = Enum.PartType.Ball,
	Cylinder = Enum.PartType.Cylinder,
}

local function makePrototype(def: any, colors: any): BasePart
	local part: BasePart
	if def.shape == "Wedge" then
		part = Instance.new("WedgePart")
	else
		local p = Instance.new("Part")
		if def.shape == "Ellipsoid" then
			local mesh = Instance.new("SpecialMesh")
			mesh.MeshType = Enum.MeshType.Sphere
			mesh.Parent = p
		elseif SHAPES[def.shape] then
			p.Shape = SHAPES[def.shape]
		end
		part = p
	end
	part.Anchored = true
	part.CanCollide = def.collide == true
	part.CanQuery = def.collide == true
	part.CanTouch = false
	part.CastShadow = def.castShadow ~= false
	part.TopSurface = Enum.SurfaceType.Smooth
	part.BottomSurface = Enum.SurfaceType.Smooth
	part.Material = (Enum.Material :: any)[def.material] or Enum.Material.SmoothPlastic
	part.Color = colors[def.role] or Color3.new(1, 0, 1)
	part.Transparency = def.transparency or 0
	part.Reflectance = def.reflectance or 0
	part.Name = def.role
	if def.light then
		local light = Instance.new("PointLight")
		light.Range = def.light.range
		light.Brightness = def.light.brightness
		light.Color = def.light.color or colors[def.light.role or def.role] or Color3.new(1, 1, 1)
		light.Shadows = false
		light.Parent = part
	end
	return part
end

local function buildProps(): number
	local templates = loadData("Data/Templates")
	local root = Workspace:FindFirstChild(WORLD_FOLDER)
	if root then
		root:Destroy()
	end
	local world = Instance.new("Folder")
	world.Name = WORLD_FOLDER
	local folders: { [string]: Folder } = {}
	local function folderFor(category: string): Folder
		local f = folders[category]
		if not f then
			f = Instance.new("Folder")
			f.Name = category
			f.Parent = world
			folders[category] = f
		end
		return f
	end

	-- Prototypen je Vorlage und Farbvariante
	local protos: { [string]: { [number]: { BasePart } } } = {}
	local function getProtos(name: string, variant: number): { BasePart }
		local byVariant = protos[name]
		if not byVariant then
			byVariant = {}
			protos[name] = byVariant
		end
		local list = byVariant[variant]
		if not list then
			local t = templates[name]
			local colors = t.variants[variant] or t.variants[1]
			list = {}
			for i, def in t.parts do
				list[i] = makePrototype(def, colors)
			end
			byVariant[variant] = list
		end
		return list
	end

	local count = 0
	local lastYield = os.clock()
	for _, modulePath in listData("Data/Placements") do
		local groups = loadData(modulePath)
		for _, group in groups do
			local t = templates[group.template]
			if not t then
				warn("[WorldBuilder] Unbekannte Vorlage: " .. tostring(group.template))
				continue
			end
			local parent = folderFor(t.category)
			local items = group.items
			for i = 1, #items, 8 do
				local x, y, z = items[i], items[i + 1], items[i + 2]
				local ry, rx, rz = items[i + 3], items[i + 4], items[i + 5]
				local s, variant = items[i + 6], items[i + 7]
				local place = CFrame.new(x, y, z) * CFrame.Angles(0, ry, 0) * CFrame.Angles(rx, 0, rz)
				local model = Instance.new("Model")
				model.Name = group.template
				local list = getProtos(group.template, variant)
				for j, def in t.parts do
					local p = list[j]:Clone()
					local cf = def.cf
					local size = def.size
					p.Size = Vector3.new(size[1] * s, size[2] * s, size[3] * s)
					p.CFrame = place
						* CFrame.new(
							cf[1] * s, cf[2] * s, cf[3] * s,
							cf[4], cf[5], cf[6],
							cf[7], cf[8], cf[9],
							cf[10], cf[11], cf[12]
						)
					local light = p:FindFirstChildOfClass("PointLight")
					if light then
						light.Range = math.min(60, light.Range * s)
					end
					p.Parent = model
				end
				model.WorldPivot = place
				model.Parent = parent
				count += 1
				if os.clock() - lastYield > 0.25 then
					lastYield = os.clock()
					task.wait()
				end
			end
		end
	end
	world.Parent = Workspace
	log(string.format("Deko fertig: %d Objekte", count))
	return count
end

----------------------------------------------------------------------
-- Licht, Atmosphaere, Himmel
----------------------------------------------------------------------

local function backupFolder(): Folder
	local f = ServerStorage:FindFirstChild("WorldBuilderBackup")
	if not f then
		f = Instance.new("Folder")
		f.Name = "WorldBuilderBackup"
		f.Parent = ServerStorage
	end
	return f :: Folder
end

local function setProps(inst: Instance, props: any)
	for prop, value in props do
		local ok, err = pcall(function()
			(inst :: any)[prop] = value
		end)
		if not ok then
			warn(string.format("[WorldBuilder] %s.%s nicht gesetzt: %s", inst.ClassName, prop, tostring(err)))
		end
	end
end

local function applyLighting(meta: any)
	local cfg = meta.lighting
	if not cfg then
		return
	end
	setProps(Lighting, cfg.Lighting or {})
	-- Eigene Effekte eines frueheren Builds ersetzen, fremde Effekte und Himmel sichern statt loeschen
	local backup = backupFolder()
	for _, child in Lighting:GetChildren() do
		if string.sub(child.Name, 1, 5) == "World" and child:GetAttribute("WorldBuilder") then
			child:Destroy()
		elseif
			child:IsA("Sky")
			or child:IsA("Atmosphere")
			or child:IsA("BloomEffect")
			or child:IsA("ColorCorrectionEffect")
			or child:IsA("SunRaysEffect")
			or child:IsA("DepthOfFieldEffect")
		then
			child.Parent = backup
		end
	end
	local classes = {
		Atmosphere = "Atmosphere",
		Bloom = "BloomEffect",
		ColorCorrection = "ColorCorrectionEffect",
		SunRays = "SunRaysEffect",
		DepthOfField = "DepthOfFieldEffect",
		Sky = "Sky",
	}
	for key, className in classes do
		local props = cfg[key]
		if props then
			local inst = Instance.new(className)
			inst.Name = "World" .. key
			inst:SetAttribute("WorldBuilder", true)
			setProps(inst, props)
			inst.Parent = Lighting
		end
	end
	-- Skybox-Bilder aus Settings (nach dem Hochladen in Studio eintragen)
	local sky = Lighting:FindFirstChild("WorldSky")
	local ids = Settings.skybox
	if sky and ids and ids.Bk and ids.Bk ~= "" then
		setProps(sky, {
			SkyboxBk = ids.Bk,
			SkyboxDn = ids.Dn,
			SkyboxFt = ids.Ft,
			SkyboxLf = ids.Lf,
			SkyboxRt = ids.Rt,
			SkyboxUp = ids.Up,
		})
		log("Skybox-Bilder gesetzt.")
	else
		log("Hinweis: Noch keine Skybox-IDs in WorldBuilder.Settings eingetragen (siehe technik/weltgenerator.md).")
	end
end

----------------------------------------------------------------------
-- Oeffentliche Funktion
----------------------------------------------------------------------

function WorldBuilder.Build(options: Options?)
	local opts: Options = options or {}
	local started = os.clock()
	local meta = loadData("Data/Meta")
	log(string.format("Baue %s (Seed %s) ...", tostring(meta.name), tostring(meta.seed)))

	if opts.hideBaseplate ~= false then
		-- Baseplate nicht loeschen, nur ausblenden (sie liegt unter dem Terrain-Plateau auf y = 0)
		local baseplate = Workspace:FindFirstChild("Baseplate")
		if baseplate and baseplate:IsA("BasePart") then
			baseplate.Transparency = 1
			baseplate.CanCollide = false
			baseplate.CanQuery = false
			baseplate.CanTouch = false
			baseplate.CastShadow = false
			local texture = baseplate:FindFirstChildOfClass("Texture")
			if texture then
				texture.Transparency = 1
			end
			log("Baseplate ausgeblendet (nicht geloescht).")
		end
	end
	if opts.terrain ~= false then
		buildTerrain(meta)
	end
	if opts.props ~= false then
		buildProps()
	end
	if opts.lighting ~= false then
		applyLighting(meta)
	end
	local spawn = meta.spawn
	if spawn then
		local spawnLocation = Workspace:FindFirstChildOfClass("SpawnLocation")
		if spawnLocation then
			spawnLocation.CFrame = CFrame.new(spawn[1], spawn[2] + spawnLocation.Size.Y / 2, spawn[3])
		end
	end
	pcall(function()
		game:GetService("ChangeHistoryService"):SetWaypoint("WorldBuilder")
	end)
	log(string.format("Fertig in %.1f s.", os.clock() - started))
end

return WorldBuilder
