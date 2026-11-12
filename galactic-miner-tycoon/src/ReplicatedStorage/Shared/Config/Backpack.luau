--!strict
-- Rucksack: wie viel Erz man auf einmal trägt (Entscheidung 017, ersetzt "Stärke").
-- Gebaut und verbessert in der Schmiede (Raum 2). Fester Preis je Stufe.
-- Muss zu daten/upgrades.md ("Rucksack") passen. ID im Code: backpack.

local ConfigTypes = require(script.Parent.Parent.Types.ConfigTypes)

type Cost = ConfigTypes.Cost

export type BackpackLevel = {
	level: number,
	displayName: string,
	carryCapacity: number, -- Tragevorrat in Erz
	cost: Cost, -- Kosten, um AUF diese Stufe zu kommen (Stufe 0: Start, leer)
}

export type BackpackConfig = {
	START_LEVEL: number,
	MAX_LEVEL: number,
	-- Achtung: Stufe 0 gibt es (nur Hände). Deshalb levels[stufe] statt levels[index] benutzen.
	levels: { [number]: BackpackLevel },
}

local Backpack: BackpackConfig = {
	START_LEVEL = 0,
	MAX_LEVEL = 5,
	levels = {
		[0] = { level = 0, displayName = "Hände", carryCapacity = 10, cost = {} },
		[1] = { level = 1, displayName = "Stoff-Rucksack", carryCapacity = 25, cost = { iron_ore = 30 } },
		[2] = { level = 2, displayName = "Metall-Rucksack", carryCapacity = 40, cost = { iron_ore = 60 } },
		[3] = {
			level = 3,
			displayName = "Verstärkter Rucksack",
			carryCapacity = 60,
			cost = { iron_ore = 100, copper_ore = 20 },
		},
		[4] = {
			level = 4,
			displayName = "Profi-Rucksack",
			carryCapacity = 90,
			cost = { copper_ore = 60, coal = 20 },
		},
		[5] = {
			level = 5,
			displayName = "Titan-Rucksack",
			carryCapacity = 130,
			cost = { copper_ore = 150, coal = 60, crystal = 20 },
		},
	},
}

return Backpack
