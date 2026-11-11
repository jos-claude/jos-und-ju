# 02 – Heimatplanet (Tycoon-Basis)

- **Status:** abgestimmt für M1 (11.11.2026, Ju). Zahlen dürfen später angepasst werden.
- **Zuletzt geändert:** 11.11.2026
- **Mindmap-Ast:** Home Planet Tycoon / Base Building

## Worum geht es?
Der Startplanet. Der Spieler baut wie in Satisfactory eine immer größere Basis, mit Lager, Räumen und vielen Bohrern auf zufällig verteilten Erzvorkommen. Bezahlt wird mit Erzen (006, 009).

## Beschlossen
- Jeder Spieler hat seine eigene Basis (008). Der Heimatplanet ist ein eigener Place (005).
- **Auf dem Heimatplaneten gibt es keine Gefahren** (010).
- Die Basis besteht aus **Räumen**, die Erze kosten. In den Räumen gibt es Upgrades (Raumschiff, Geschwindigkeit, Stärke u. a.).
- Zur Basis gehört ein **Lager** mit einem Kasten pro Erz (Glaswand, Füllstand sichtbar). Die Kästen sind das Inventar (010).
- **Erzvorkommen** liegen verteilt auf der Karte. Man platziert Bohrer darauf (010).

## Beschlossen (011)
- Jeder Spieler hat seine eigene Karte, einmal zufällig erzeugt und gespeichert.
- Mindestradius pro Erz und Spawn nach Fortschritt.

## Festlegung für M1 (Zahlen änderbar)
- **Aufbau:** Basis mit Lager in der Mitte. Rundherum die offene Landschaft mit den Vorkommen.
- **Verteilung:** Position zufällig, aber jedes Erz hat einen **Mindestradius** um die Basis (Entscheidung 011, Radien in `../daten/ressourcen.md`). Seltene Erze erscheinen nie nah an der Basis.
- **Spawn nach Fortschritt:** Vorkommen sind am Anfang nicht alle da. Sie erscheinen nach und nach mit dem Fortschritt des Spielers (Regeln in `../daten/ressourcen.md`).
- **Räume:** Raum 2: 50 Eisen. Raum 3: 100 Eisen + 15 Kupfer. Weitere in `../daten/gebaeude.md`.
- **Lager** steht in Raum 1. Die Kästen für weitere Erze kauft man dort.

## Beschlossen (012)
- Vorerst 6 Räume, später änderbar.
- Bohrer sind aufwertbar.

## Offene Fragen
- [ ] Wie viele Vorkommen pro Erz?

## Verknüpft mit
`03`, `04`, `14-ui-und-bedienung.md`, `../technik/architektur.md` (PlotService, BuildService)
