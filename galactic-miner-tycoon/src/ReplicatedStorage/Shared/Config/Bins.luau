--!strict
-- Lager-Kästen: ein Kasten pro Erz, schaltet das Erz frei (Entscheidung 010).
-- Muss zu daten/gebaeude.md ("Lager-Kästen" und "Kapazitäts-Upgrade") passen.

local ConfigTypes = require(script.Parent.Parent.Types.ConfigTypes)

type OreId = ConfigTypes.OreId
type Cost = ConfigTypes.Cost

export type BinId = "bin_iron" | "bin_copper" | "bin_coal" | "bin_crystal" | "bin_titanium"

export type CapacityLevel = {
	level: number,
	capacity: number,
	cost: Cost, -- Kosten, um AUF diese Stufe zu kommen (Stufe 1 = Kaufpreis des Kastens)
}

export type BinDef = {
	id: BinId,
	ore: OreId,
	displayName: string,
	cost: Cost, -- leere Tabelle = gratis
	ownedAtStart: boolean,
	-- Index = Stufe. Stufe 1 ist die Start-Kapazität nach dem Kauf.
	levels: { CapacityLevel },
}

export type BinsConfig = {
	MAX_LEVEL: number,
	order: { BinId },
	byId: { [BinId]: BinDef },
	byOre: { [OreId]: BinId },
}

-- Kapazitäts-Staffel ist für alle Kästen gleich, bezahlt wird mit dem Erz des Kastens selbst.
local CAPACITIES = { 100, 250, 500, 1000, 2500 }
local UPGRADE_COSTS = { 0, 50, 100, 200, 400 } -- Stufe 1 hat keinen Upgrade-Preis

local function buildLevels(ore: OreId, buyCost: Cost): { CapacityLevel }
	local levels: { CapacityLevel } = {}
	for level, capacity in CAPACITIES do
		local cost: Cost
		if level == 1 then
			cost = buyCost
		else
			cost = { [ore] = UPGRADE_COSTS[level] }
		end
		table.insert(levels, { level = level, capacity = capacity, cost = cost })
	end
	return levels
end

local function bin(id: BinId, ore: OreId, displayName: string, cost: Cost, ownedAtStart: boolean): BinDef
	return {
		id = id,
		ore = ore,
		displayName = displayName,
		cost = cost,
		ownedAtStart = ownedAtStart,
		levels = buildLevels(ore, cost),
	}
end

local Bins: BinsConfig = {
	MAX_LEVEL = #CAPACITIES,
	order = { "bin_iron", "bin_copper", "bin_coal", "bin_crystal", "bin_titanium" },
	byId = {
		bin_iron = bin("bin_iron", "iron_ore", "Eisen-Kasten", {}, true), -- steht schon
		bin_copper = bin("bin_copper", "copper_ore", "Kupfer-Kasten", { iron_ore = 40 }, false),
		bin_coal = bin("bin_coal", "coal", "Kohle-Kasten", { iron_ore = 60, copper_ore = 30 }, false),
		bin_crystal = bin("bin_crystal", "crystal", "Kristall-Kasten", { copper_ore = 100, coal = 50 }, false),
		bin_titanium = bin("bin_titanium", "titanium_ore", "Titan-Kasten", { coal = 150, crystal = 60 }, false),
	},
	byOre = {
		iron_ore = "bin_iron",
		copper_ore = "bin_copper",
		coal = "bin_coal",
		crystal = "bin_crystal",
		titanium_ore = "bin_titanium",
	},
}

return Bins
