# 02 – Heimatplanet (Tycoon-Basis)

- **Status:** Richtung beschlossen (Entscheidungen 009, 010), Zahlen sind Vorschlag
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

## Vorschlag (Zahlen noch nicht bestätigt)
- **Aufbau:** Basis mit Lager in der Mitte. Rundherum die offene Landschaft mit den Vorkommen.
- **Verteilung:** Die Position der Vorkommen ist zufällig, aber seltene Erze liegen eher weiter weg (Ringe um die Basis, siehe `../daten/ressourcen.md`). Eisen gibt es auch direkt an der Basis.
- **Räume:** Raum 2: 50 Eisen. Raum 3: 100 Eisen + 15 Kupfer. Weitere in `../daten/gebaeude.md`.
- **Lager** steht in Raum 1. Die Kästen für weitere Erze kauft man dort.

## Offene Fragen
- [ ] Zufällig neu bei jedem Spielstart oder pro Spieler einmal festgelegt und gespeichert? (Vorschlag: einmal pro Spieler, gespeichert)
- [ ] Hat jeder Spieler eine eigene Karte oder teilen sich alle im Place dieselbe? (Vorschlag: eigener Bereich pro Spieler)
- [ ] Wie viele Vorkommen pro Erz?
- [ ] Sind seltene Erze wirklich immer weiter weg, oder ganz zufällig?
- [ ] Wie viele Räume am Ende?
- [ ] Soll der Spieler die Bohrer später aufwerten können?

## Verknüpft mit
`03`, `04`, `14-ui-und-bedienung.md`, `../technik/architektur.md` (PlotService, BuildService)
