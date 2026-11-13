--!strict
-- Erze auf Insel 1 (Heimatplanet). Muss zu daten/ressourcen.md passen.
-- Ringe: Entscheidung 020 · Erscheinen nach Fortschritt: Entscheidung 016 ·
-- Härte-Malus und "Titan nur mit Bohrern": Entscheidung 020 (Spitzhacke: daten/upgrades.md).

local ConfigTypes = require(script.Parent.Parent.Types.ConfigTypes)

export type OreId = ConfigTypes.OreId

export type OreDef = {
	id: OreId,
	displayName: string,
	tier: number,

	-- Ring um die Basis, in dem Vorkommen erscheinen dürfen (Studs).
	minRadius: number,
	maxRadius: number,

	-- Handabbau: Faktor auf "Erz pro Schlag" der Spitzhacke.
	-- nil = kann nicht von Hand abgebaut werden (Titan, nur mit Bohrern).
	handHardness: number?,
	-- Mindest-Stufe der Spitzhacke für den Handabbau. nil = gar nicht von Hand.
	minPickaxeLevel: number?,

	-- Wann Vorkommen erscheinen.
	unlockRoom: number, -- Raum, mit dem die ersten Vorkommen kommen (1 = Spielstart)
	initialNodes: number, -- so viele erscheinen sofort
	nodeIntervalSeconds: number, -- danach +1 Vorkommen alle ... Sekunden Spielzeit
	maxNodes: number, -- höchstens so viele Vorkommen
}

export type OresConfig = {
	ISLAND_RADIUS: number,
	order: { OreId },
	byId: { [OreId]: OreDef },
}

local Ores: OresConfig = {
	-- Radius der Insel in Studs (flache Plattform, Entscheidung 015).
	ISLAND_RADIUS = 1000, -- Entscheidung 022 (halbe Insel)

	-- Reihenfolge = Fortschritt (Stufe 1 bis 5).
	order = { "iron_ore", "copper_ore", "coal", "crystal", "titanium_ore" },

	byId = {
		iron_ore = {
			id = "iron_ore",
			displayName = "Eisenerz",
			tier = 1,
			minRadius = 10,
			maxRadius = 100,
			handHardness = 1.0,
			minPickaxeLevel = 1,
			unlockRoom = 1,
			initialNodes = 3,
			nodeIntervalSeconds = 5 * 60,
			maxNodes = 6,
		},
		copper_ore = {
			id = "copper_ore",
			displayName = "Kupfererz",
			tier = 2,
			minRadius = 125,
			maxRadius = 350,
			handHardness = 0.8,
			minPickaxeLevel = 2,
			unlockRoom = 2,
			initialNodes = 2,
			nodeIntervalSeconds = 5 * 60,
			maxNodes = 8,
		},
		coal = {
			id = "coal",
			displayName = "Kohle",
			tier = 3,
			minRadius = 300,
			maxRadius = 550,
			handHardness = 0.6,
			minPickaxeLevel = 3,
			unlockRoom = 3,
			initialNodes = 2,
			nodeIntervalSeconds = 5 * 60,
			maxNodes = 6,
		},
		crystal = {
			id = "crystal",
			displayName = "Kristall",
			tier = 4,
			minRadius = 550,
			maxRadius = 800,
			handHardness = 0.4,
			minPickaxeLevel = 4,
			unlockRoom = 4,
			initialNodes = 1,
			nodeIntervalSeconds = 10 * 60,
			maxNodes = 5,
		},
		titanium_ore = {
			id = "titanium_ore",
			displayName = "Titanerz",
			tier = 5,
			minRadius = 800,
			maxRadius = 1000,
			handHardness = nil, -- nur mit Bohrern (Entscheidung 020)
			minPickaxeLevel = nil,
			unlockRoom = 5,
			initialNodes = 1,
			nodeIntervalSeconds = 10 * 60,
			maxNodes = 4,
		},
	},
}

return Ores
