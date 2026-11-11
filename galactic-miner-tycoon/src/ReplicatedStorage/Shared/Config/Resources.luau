--!strict
-- Ressourcen und Rezepte. Platzhalter – muss zu daten/ressourcen.md passen.

export type ResourceDef = {
	id: string,
	displayName: string,
	kind: "raw" | "advanced",
	origin: string?, -- planet id, nur bei Rohstoffen
	recipe: { [string]: number }?, -- nur bei verarbeiteten Materialien
}

local Resources: { [string]: ResourceDef } = {
	iron_ore = { id = "iron_ore", displayName = "Eisenerz", kind = "raw", origin = "home" },
	copper_ore = { id = "copper_ore", displayName = "Kupfererz", kind = "raw", origin = "home" },
	crystal = { id = "crystal", displayName = "Kristall", kind = "raw", origin = "home" },
	obsidian = { id = "obsidian", displayName = "Obsidian", kind = "raw", origin = "lava" },
	ice_crystal = { id = "ice_crystal", displayName = "Eiskristall", kind = "raw", origin = "ice" },
	bio_fiber = { id = "bio_fiber", displayName = "Biofaser", kind = "raw", origin = "jungle" },

	iron_bar = { id = "iron_bar", displayName = "Eisenbarren", kind = "advanced", recipe = { iron_ore = 3 } },
	circuit = {
		id = "circuit",
		displayName = "Schaltkreis",
		kind = "advanced",
		recipe = { copper_ore = 2, crystal = 1 },
	},
	heat_plate = {
		id = "heat_plate",
		displayName = "Hitzeschild-Platte",
		kind = "advanced",
		recipe = { obsidian = 2, iron_bar = 1 },
	},
	coolant = {
		id = "coolant",
		displayName = "Kühlmittel",
		kind = "advanced",
		recipe = { ice_crystal = 2, crystal = 1 },
	},
	plasma_cell = {
		id = "plasma_cell",
		displayName = "Plasmazelle",
		kind = "advanced",
		recipe = { bio_fiber = 1, circuit = 1, coolant = 1 },
	},
}

return Resources
