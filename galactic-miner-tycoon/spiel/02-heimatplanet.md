# 02 – Heimatplanet (Tycoon-Basis)

- **Status:** Richtung beschlossen (Entscheidung 009), Zahlen sind Vorschlag
- **Zuletzt geändert:** 11.11.2026
- **Mindmap-Ast:** Home Planet Tycoon / Base Building

## Worum geht es?
Der Startplanet. Der Spieler baut wie in Satisfactory eine immer größere Basis. Sie wächst Raum für Raum und Bohrer für Bohrer. Bezahlt wird mit Rohstoffen (Entscheidungen 006, 009).

## Beschlossen
- Jeder Spieler hat seine eigene Basis (008). Der Heimatplanet ist ein eigener Place (005).
- Die Basis besteht aus **Räumen**. Neue Räume kosten Rohstoffe.
- In den Räumen gibt es Upgrades: Raumschiff, Spielergeschwindigkeit, Stärke u. a.
- Erzvorkommen liegen um die Basis. **Je seltener das Erz, desto weiter weg.**

## Vorschlag (Zahlen noch nicht bestätigt)
- **Aufbau:** Raum 1 ist die Start-Halle mit der Kiste und einem Eisenvorkommen direkt davor. Die Erzfelder liegen draußen in Ringen um die Basis, nach Entfernung sortiert (siehe `../daten/ressourcen.md`).
- **Feste Bohrer-Slots** auf jedem Erzfeld (kein freies Platzieren), z. B. 4 pro Feld.
- **Räume:** Kosten steigen. Raum 2: 50 Eisen. Raum 3: 100 Eisen + 15 Kupfer. Weitere in `../daten/gebaeude.md`.
- Welche Räume welches Upgrade enthalten, siehe `../daten/upgrades.md`.

## Offene Fragen
- [ ] Wie sieht der Planet aus: Basis in der Mitte, Erzfelder drumherum?
- [ ] Wie viele Räume am Ende?
- [ ] Sind die Erzfelder gefährlich oder nur weit weg?
- [ ] Gibt es Gebäude-Level (Bohrer aufwerten statt neu bauen)?

## Verknüpft mit
`03`, `04`, `14-ui-und-bedienung.md`, `../technik/architektur.md` (PlotService, BuildService)
