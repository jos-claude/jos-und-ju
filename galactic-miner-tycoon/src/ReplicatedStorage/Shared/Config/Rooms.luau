--!strict
-- Räume der Basis: 6 Stück, feste Kosten (Entscheidungen 016 und 018).
-- Muss zu daten/gebaeude.md ("Räume") und spiel/16-raeume-und-spitzhacke.md passen.
-- Welches Erz mit welchem Raum erscheint, steht in Ores.luau (unlockRoom).

local ConfigTypes = require(script.Parent.Parent.Types.ConfigTypes)

type Cost = ConfigTypes.Cost

export type RoomId = "start_hall" | "forge" | "machine_hall" | "garage" | "research_lab" | "rocket_hangar"

export type RoomDef = {
	id: RoomId,
	number: number, -- Raum-Nummer 1 bis 6, bestimmt die Reihenfolge
	displayName: string,
	cost: Cost, -- leere Tabelle = gratis
	ownedAtStart: boolean,
}

export type RoomsConfig = {
	order: { RoomId },
	byId: { [RoomId]: RoomDef },
	byNumber: { [number]: RoomId },
}

local Rooms: RoomsConfig = {
	order = { "start_hall", "forge", "machine_hall", "garage", "research_lab", "rocket_hangar" },
	byId = {
		-- Lager, Bohrer kaufen.
		start_hall = { id = "start_hall", number = 1, displayName = "Start-Halle", cost = {}, ownedAtStart = true },
		-- Spitzhacke und Rucksack verbessern, Teleportfeld zur Lobby.
		forge = { id = "forge", number = 2, displayName = "Schmiede", cost = { iron_ore = 50 }, ownedAtStart = false },
		-- Förderbänder kaufen, Bohrer aufwerten.
		machine_hall = {
			id = "machine_hall",
			number = 3,
			displayName = "Maschinenhalle",
			cost = { iron_ore = 100, copper_ore = 15 },
			ownedAtStart = false,
		},
		-- Rover kaufen und verbessern. Absichtlich ohne Kristall (Kristall erscheint erst mit ihr).
		garage = {
			id = "garage",
			number = 4,
			displayName = "Garage",
			cost = { iron_ore = 150, copper_ore = 60, coal = 20 },
			ownedAtStart = false,
		},
		-- Techbaum. Absichtlich ohne Titan (Titan erscheint erst mit ihm, Entscheidung 018).
		research_lab = {
			id = "research_lab",
			number = 5,
			displayName = "Forschungslabor",
			cost = { iron_ore = 250, copper_ore = 120, coal = 60, crystal = 20 },
			ownedAtStart = false,
		},
		-- Rakete bauen und betreten (die Rakete kostet extra).
		rocket_hangar = {
			id = "rocket_hangar",
			number = 6,
			displayName = "Raketen-Hangar",
			cost = { copper_ore = 600, coal = 300, crystal = 150, titanium_ore = 50 },
			ownedAtStart = false,
		},
	},
	byNumber = {
		[1] = "start_hall",
		[2] = "forge",
		[3] = "machine_hall",
		[4] = "garage",
		[5] = "research_lab",
		[6] = "rocket_hangar",
	},
}

return Rooms
