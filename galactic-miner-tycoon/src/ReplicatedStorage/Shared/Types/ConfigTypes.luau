--!strict
-- Gemeinsame Typen für die Config-Dateien in Shared/Config.

-- Die fünf Erze von Insel 1 (daten/ressourcen.md).
export type OreId = "iron_ore" | "copper_ore" | "coal" | "crystal" | "titanium_ore"

-- Kosten: Erz-ID → Menge. Bezahlt wird mit Erzen aus den Lager-Kästen (Entscheidung 006).
-- Beispiel: { iron_ore = 150, copper_ore = 60, coal = 20 }
export type Cost = { [string]: number }

return {}
