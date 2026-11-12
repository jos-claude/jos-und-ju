--!strict
-- Wo erscheint ein Erz-Vorkommen? Reine Rechnung ohne Welt-Objekte, damit sie sich ohne Play prüfen lässt.
-- Regeln: Ring je Erz (Entscheidung 020), nie auf einem anderen Vorkommen (daten/ressourcen.md),
-- nicht im Spawn-Bereich und nicht in Halle/Lager (Config/BaseLayout.luau).
--
-- Gleicher Seed + gleiche Nummer + gleiche schon vorhandene Vorkommen = gleiche Position.
-- Jedes Vorkommen hat einen eigenen Zufalls-Startwert (Seed, Erz-Stufe, Nummer), deshalb ändert
-- ein später erscheinendes Vorkommen nie die Lage der früheren.

local NodePlacement = {}

export type Point = { x: number, z: number }

export type Rect = { minX: number, maxX: number, minZ: number, maxZ: number }

export type Rules = {
	minRadius: number,
	maxRadius: number,
	minSpacing: number,
	maxAttempts: number,
	clearCircles: { { x: number, z: number, r: number } },
	clearRects: { Rect },
}

local MAX_SEED = 2147483647

function NodePlacement.seedFor(mapSeed: number, oreTier: number, index: number): number
	return (mapSeed + oreTier * 7919 + index * 104729) % MAX_SEED
end

function NodePlacement.isFree(x: number, z: number, rules: Rules, existing: { Point }): boolean
	local radius = math.sqrt(x * x + z * z)
	if radius < rules.minRadius or radius > rules.maxRadius then
		return false
	end
	for _, circle in rules.clearCircles do
		local dx, dz = x - circle.x, z - circle.z
		if dx * dx + dz * dz < circle.r * circle.r then
			return false
		end
	end
	for _, rect in rules.clearRects do
		if x >= rect.minX and x <= rect.maxX and z >= rect.minZ and z <= rect.maxZ then
			return false
		end
	end
	local spacing2 = rules.minSpacing * rules.minSpacing
	for _, other in existing do
		local dx, dz = x - other.x, z - other.z
		if dx * dx + dz * dz < spacing2 then
			return false
		end
	end
	return true
end

-- Sucht eine freie Stelle im Ring. nil = keine gefunden (dann lieber kein Vorkommen als ein falsches).
function NodePlacement.pick(mapSeed: number, oreTier: number, index: number, rules: Rules, existing: { Point }): Point?
	local rng = Random.new(NodePlacement.seedFor(mapSeed, oreTier, index))
	local min2 = rules.minRadius * rules.minRadius
	local max2 = rules.maxRadius * rules.maxRadius
	for _ = 1, rules.maxAttempts do
		local angle = rng:NextNumber() * 2 * math.pi
		-- Gleichmäßig über die FLÄCHE des Rings (sonst stünden zu viele Vorkommen innen).
		local radius = math.sqrt(rng:NextNumber() * (max2 - min2) + min2)
		-- Azimut 0 = Norden = -Z, 90° = Osten = +X (welt-design-insel-1.md)
		local x = math.round(radius * math.sin(angle) * 10) / 10
		local z = math.round(-radius * math.cos(angle) * 10) / 10
		if NodePlacement.isFree(x, z, rules, existing) then
			return { x = x, z = z }
		end
	end
	return nil
end

return NodePlacement
