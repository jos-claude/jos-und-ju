# Entscheidung 021: Bohrer-Kauf, Offline-Puffer und Schmiede-Stufen (Schritt 5 und 6)

- **Status:** Beschlossen (Ju, 14.11.2026, Jos bitte gegenlesen). Zahlen sind änderbar.
- **Datum:** 14.11.2026
- **Von:** Ju

## Frage
Beim Bauen von Schritt 5 und 6 (`../checklisten/code-fortschritt.md`) waren vier Dinge im Konzept offen oder nur ein Vorschlag.

## Entscheidung
1. **Ein Bohrer ist nur kaufbar, wenn noch ein Vorkommen frei ist** (freie Vorkommen dieses Erzes minus gekaufte, noch nicht aufgestellte Bohrer). Sonst ist das Kauffeld grau.
2. **Bohrer ohne Band füllen offline ihren Puffer**, höchstens bis er voll ist (der Vorschlag aus `../spiel/03-abbau-und-automatisierung.md` zu Entscheidung 011 gilt damit).
3. **Schmiede vorerst nur Spitzhacke Stufe 2 und Rucksack Stufe 1.** Die nächste Stufe wird mit Name und Preis grau als „später“ angezeigt. Weitere Stufen werden später freigeschaltet.
4. **Lage der Schmiede:** vorerst als Greybox-Platzhalter rechts neben der Start-Halle (x 28 bis 60, z 30 bis 58, Tür nach Norden). Endgültige Lage und Aussehen kommen mit den Modellen von Jos (Schmiede, Spitzhacke usw.) in einer eigenen Runde.

## Warum
1. Sonst läge ein bezahlter Bohrer nutzlos herum (ein Bohrer pro Vorkommen, Entscheidung 020).
2. Offline-Ertrag ist beschlossen (011). Begrenzt durch den Puffer gibt es kein „unendlich Erz“.
3. Weitere Stufen brauchen Kupfer (Schritt 7) oder sollen erst nach dem Spieltest kommen.
4. Die Modelle macht Jos gerade, der Platzhalter ist leicht verschiebbar.

## Folgen
- Code: `../src/ReplicatedStorage/Shared/Config/Shop.luau` (Schalter `DRILL_NEEDS_FREE_NODE`, `OFFLINE_FILLS_DRILL_BUFFER`, `FORGE_MAX_PICKAXE_LEVEL`, `FORGE_MAX_BACKPACK_LEVEL`), `Config/BaseLayout.luau` (Lage der Schmiede).
- Freischalten weiterer Stufen = Zahl in `Shop.luau` erhöhen.
