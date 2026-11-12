--!strict
-- Spitzhacke für den Handabbau, verbessert in der Schmiede (Raum 2, Entscheidung 016).
-- Muss zu daten/upgrades.md ("Spitzhacke") passen.
-- Welche Stufe welches Erz abbauen kann und der Härte-Malus stehen in Ores.luau
-- (minPickaxeLevel, handHardness). Titan geht nie von Hand (Entscheidung 020).
-- Vorkommen werden durch Handabbau nicht leer (Entscheidung 020).

local ConfigTypes = require(script.Parent.Parent.Types.ConfigTypes)

type Cost = ConfigTypes.Cost

export type PickaxeLevel = {
	level: number,
	displayName: string,
	orePerHit: number, -- vor dem Härte-Malus
	swingSeconds: number, -- Zeit pro Schlag
	cost: Cost, -- Kosten, um AUF diese Stufe zu kommen (Stufe 1: Start, leer)
}

export type PickaxeConfig = {
	START_LEVEL: number,
	MAX_LEVEL: number,
	levels: { PickaxeLevel },
}

local levels: { PickaxeLevel } = {
	{ level = 1, displayName = "Rost-Spitzhacke", orePerHit = 1, swingSeconds = 1.0, cost = {} },
	{ level = 2, displayName = "Eisen-Spitzhacke", orePerHit = 2, swingSeconds = 1.0, cost = { iron_ore = 30 } },
	{
		level = 3,
		displayName = "Stahl-Spitzhacke",
		orePerHit = 3,
		swingSeconds = 0.9,
		cost = { iron_ore = 80, copper_ore = 30 },
	},
	{
		level = 4,
		displayName = "Kristall-Spitzhacke",
		orePerHit = 4,
		swingSeconds = 0.8,
		cost = { copper_ore = 150, coal = 60 },
	},
	{
		level = 5,
		displayName = "Titan-Spitzhacke",
		orePerHit = 6,
		swingSeconds = 0.7,
		cost = { coal = 120, crystal = 80 },
	},
}

local Pickaxe: PickaxeConfig = {
	START_LEVEL = 1,
	MAX_LEVEL = #levels,
	levels = levels,
}

return Pickaxe
