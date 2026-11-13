--!strict
-- Regeln für die Kauffelder (Schritt 5 und 6, spiel/14-ui-und-bedienung.md "Kaufflächen").
-- Preise stehen NICHT hier, sondern in Drills.luau, Rooms.luau, Pickaxe.luau und Backpack.luau.
-- Hier steht nur, was die Kauffelder gerade anbieten dürfen.

export type ShopConfig = {
	-- Bis zu dieser Stufe kann man in der Schmiede jetzt kaufen. Die nächste Stufe wird mit
	-- Name und Preis angezeigt, aber als "später" (Auftrag Schritt 6: "ausbauen kommt später").
	-- Zum Freischalten einfach die Zahl erhöhen (höchstens Pickaxe.MAX_LEVEL / Backpack.MAX_LEVEL).
	FORGE_MAX_PICKAXE_LEVEL: number,
	FORGE_MAX_BACKPACK_LEVEL: number,

	-- Bohrer kann man nur kaufen, wenn noch ein freies Vorkommen da ist (ein Bohrer pro
	-- Vorkommen, Entscheidung 020). Sonst läge ein bezahlter Bohrer nutzlos herum.
	DRILL_NEEDS_FREE_NODE: boolean,

	-- Bohrer ohne Band füllen offline ihren Puffer (spiel/03, Vorschlag zu Entscheidung 011).
	-- Höchstens bis der Puffer voll ist.
	OFFLINE_FILLS_DRILL_BUFFER: boolean,
}

local Shop: ShopConfig = {
	FORGE_MAX_PICKAXE_LEVEL = 2,
	FORGE_MAX_BACKPACK_LEVEL = 1,
	DRILL_NEEDS_FREE_NODE = true,
	OFFLINE_FILLS_DRILL_BUFFER = true,
}

return Shop
