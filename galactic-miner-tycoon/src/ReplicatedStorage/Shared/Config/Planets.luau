--!strict
-- Planeten. Platzhalter – muss zu daten/planeten.md passen.

export type PlanetDef = {
	id: string,
	displayName: string,
	resources: { string },
	hazards: { string },
	requiresEngineLevel: number,
}

local Planets: { [string]: PlanetDef } = {
	home = {
		id = "home",
		displayName = "Heimatplanet",
		resources = { "iron_ore", "copper_ore", "crystal" },
		hazards = {},
		requiresEngineLevel = 0,
	},
	lava = {
		id = "lava",
		displayName = "Lava-Planet",
		resources = { "obsidian" },
		hazards = { "heat", "eruption" },
		requiresEngineLevel = 1,
	},
	ice = {
		id = "ice",
		displayName = "Eis-Welt",
		resources = { "ice_crystal" },
		hazards = { "cold", "blizzard" },
		requiresEngineLevel = 2,
	},
	jungle = {
		id = "jungle",
		displayName = "Dschungel-Welt",
		resources = { "bio_fiber" },
		hazards = { "creatures", "toxic_plants" },
		requiresEngineLevel = 3,
	},
}

return Planets
