--!strict
-- Bohrer: werden auf ein Vorkommen gesetzt, ein Bohrer pro Vorkommen (Entscheidung 020).
-- Muss zu daten/gebaeude.md ("Bohrer") und daten/upgrades.md ("Bohrer-Upgrades") passen.
-- Kaufpreis: Preis(n) = Basispreis × 1,15^n, n = schon gekaufte Bohrer dieses Erzes.

local ConfigTypes = require(script.Parent.Parent.Types.ConfigTypes)

type OreId = ConfigTypes.OreId
type Cost = ConfigTypes.Cost

export type DrillId = "drill_iron" | "drill_copper" | "drill_coal" | "drill_crystal" | "drill_titanium"

export type DrillLevel = {
	level: number,
	rateFactor: number, -- mal Grundrate
	buffer: number, -- so viel Erz fasst der Puffer, dann stoppt der Bohrer
	upgradeCost: Cost, -- Kosten, um AUF diese Stufe zu kommen (Stufe 1: leer)
}

export type DrillDef = {
	id: DrillId,
	ore: OreId,
	displayName: string,
	baseCost: Cost, -- Preis des ersten Bohrers dieses Erzes
	baseRate: number, -- Erz pro Sekunde auf Stufe 1
	requiresBin: string?, -- Kasten, der vorher gekauft sein muss
	levels: { DrillLevel },
}

export type DrillsConfig = {
	PRICE_GROWTH: number,
	MAX_LEVEL: number,
	order: { DrillId },
	byId: { [DrillId]: DrillDef },
	byOre: { [OreId]: DrillId },
	getPrice: (drillId: DrillId, ownedCount: number) -> Cost,
}

-- Staffel für alle Bohrer (daten/upgrades.md).
local RATE_FACTORS = { 1.0, 1.5, 2.0, 2.5, 3.0 }
local BUFFERS = { 50, 75, 100, 150, 200 }

-- Upgrade-Kosten der anderen Erze: Kaufpreis × Faktor (Stufe 2 bis 5).
local UPGRADE_MULTIPLIERS = { 0, 1.25, 2.5, 5, 10 }

-- Eisen-Bohrer: Upgrade-Kosten stehen ausdrücklich in daten/upgrades.md.
local IRON_UPGRADE_COSTS: { Cost } = {
	{},
	{ iron_ore = 25 },
	{ iron_ore = 50, copper_ore = 10 },
	{ iron_ore = 100, copper_ore = 30 },
	{ iron_ore = 200, copper_ore = 60, coal = 20 },
}

local function roundCost(cost: Cost, factor: number): Cost
	local result: Cost = {}
	for oreId, amount in cost do
		result[oreId] = math.round(amount * factor)
	end
	return result
end

local function buildLevels(baseCost: Cost, explicitUpgradeCosts: { Cost }?): { DrillLevel }
	local levels: { DrillLevel } = {}
	for level = 1, #RATE_FACTORS do
		local upgradeCost: Cost
		if explicitUpgradeCosts then
			upgradeCost = explicitUpgradeCosts[level]
		elseif level == 1 then
			upgradeCost = {}
		else
			-- OFFEN (Frage an Ju): "ab Level 3 zusätzlich eine Kleinigkeit vom nächsten Erz"
			-- ist in daten/upgrades.md nicht beziffert und fehlt hier deshalb noch.
			upgradeCost = roundCost(baseCost, UPGRADE_MULTIPLIERS[level])
		end
		table.insert(levels, {
			level = level,
			rateFactor = RATE_FACTORS[level],
			buffer = BUFFERS[level],
			upgradeCost = upgradeCost,
		})
	end
	return levels
end

local function drill(
	id: DrillId,
	ore: OreId,
	displayName: string,
	baseCost: Cost,
	baseRate: number,
	requiresBin: string?,
	explicitUpgradeCosts: { Cost }?
): DrillDef
	return {
		id = id,
		ore = ore,
		displayName = displayName,
		baseCost = baseCost,
		baseRate = baseRate,
		requiresBin = requiresBin,
		levels = buildLevels(baseCost, explicitUpgradeCosts),
	}
end

local PRICE_GROWTH = 1.15

local byId: { [DrillId]: DrillDef } = {
	-- Nicht mehr gratis (Entscheidung 016). Der Eisen-Kasten steht schon, darum keine Voraussetzung.
	drill_iron = drill("drill_iron", "iron_ore", "Eisen-Bohrer", { iron_ore = 20 }, 1.0, nil, IRON_UPGRADE_COSTS),
	drill_copper = drill("drill_copper", "copper_ore", "Kupfer-Bohrer", { iron_ore = 40 }, 0.8, "bin_copper"),
	drill_coal = drill("drill_coal", "coal", "Kohle-Bohrer", { iron_ore = 40, copper_ore = 20 }, 0.6, "bin_coal"),
	drill_crystal = drill(
		"drill_crystal",
		"crystal",
		"Kristall-Bohrer",
		{ copper_ore = 60, coal = 30 },
		0.4,
		"bin_crystal"
	),
	drill_titanium = drill(
		"drill_titanium",
		"titanium_ore",
		"Titan-Bohrer",
		{ coal = 80, crystal = 40 },
		0.3,
		"bin_titanium"
	),
}

local Drills: DrillsConfig = {
	PRICE_GROWTH = PRICE_GROWTH,
	MAX_LEVEL = #RATE_FACTORS,
	order = { "drill_iron", "drill_copper", "drill_coal", "drill_crystal", "drill_titanium" },
	byId = byId,
	byOre = {
		iron_ore = "drill_iron",
		copper_ore = "drill_copper",
		coal = "drill_coal",
		crystal = "drill_crystal",
		titanium_ore = "drill_titanium",
	},
	-- Preis des nächsten Bohrers, wenn schon `ownedCount` Bohrer dieses Erzes gekauft sind.
	-- Gerundet auf ganze Erze (wie in daten/balance/spielzeit-simulation.ps1).
	getPrice = function(drillId: DrillId, ownedCount: number): Cost
		return roundCost(byId[drillId].baseCost, PRICE_GROWTH ^ ownedCount)
	end,
}

return Drills
