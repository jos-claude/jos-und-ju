--!nocheck
-- Prueft die Dekoder des WorldBuilders (Base64, Varint, RLE, Hoehen) einzeln mit Zufallsvektoren.
-- Aufruf: lune run decoders_check.luau <builder.luau> <eingabe.json> <ausgabe.json>
-- Der Dekoder-Abschnitt wird per Textmarken aus dem Builder-Quelltext geschnitten und mit leerer Umgebung geladen.
local fs = require("@lune/fs")
local luau = require("@lune/luau")
local process = require("@lune/process")
local serde = require("@lune/serde")

local src = fs.readFile(process.args[1])
local a = string.find(src, "local B64:", 1, true)
local b = string.find(src, "-- Terrain\n", a, true)
assert(a and b, "Textmarken im Builder nicht gefunden")
local section = string.sub(src, a, b - 1)
section = section .. "\nreturn { decodeBase64 = decodeBase64, readVarint = readVarint, decodeHeights = decodeHeights, decodeRle = decodeRle }\n"
local env = { loadData = function() error("loadData im Dekodertest nicht erwartet") end }
local lib = luau.load(section, { environment = env, debugName = "decoders" })()

local input = serde.decode("json", fs.readFile(process.args[2]))
local out = { b64 = {}, varint = {}, rle = {}, heights = {} }

local function hex(buf, n)
	local t = table.create(n)
	for i = 0, n - 1 do t[i + 1] = buffer.readu8(buf, i) end
	return t
end

for i, case in input.b64 do
	local ok, buf, n = pcall(lib.decodeBase64, table.concat(case.chunks))
	out.b64[i] = ok and { n = n, bytes = hex(buf, n) } or { err = tostring(buf) }
end
for i, case in input.varint do
	local buf = buffer.create(#case.bytes)
	for k, v in case.bytes do buffer.writeu8(buf, k - 1, v) end
	local vals, pos = {}, 0
	local ok, err = pcall(function()
		for _ = 1, case.count do
			local v
			v, pos = lib.readVarint(buf, pos)
			table.insert(vals, v)
		end
	end)
	out.varint[i] = { values = vals, pos = pos, err = (not ok) and tostring(err) or nil }
end
for i, case in input.rle do
	local buf = buffer.create(math.max(1, #case.bytes))
	for k, v in case.bytes do buffer.writeu8(buf, k - 1, v) end
	local ok, res = pcall(lib.decodeRle, buf, #case.bytes, case.total)
	out.rle[i] = ok and { values = hex(res, case.total) } or { err = tostring(res) }
end
for i, case in input.heights do
	local buf = buffer.create(math.max(1, #case.bytes))
	for k, v in case.bytes do buffer.writeu8(buf, k - 1, v) end
	local ok, res = pcall(lib.decodeHeights, buf, case.n)
	if ok then
		local vals = table.create(case.n * case.n)
		for k = 0, case.n * case.n - 1 do vals[k + 1] = buffer.readu16(res, k * 2) end
		out.heights[i] = { values = vals }
	else
		out.heights[i] = { err = tostring(res) }
	end
end
fs.writeFile(process.args[3], serde.encode("json", out))
print("decoders_check fertig")
