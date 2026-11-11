# Entscheidung 001: Ein Oberordner pro Spiel

- **Status:** Beschlossen
- **Datum:** 11.11.2026
- **Von:** Jos

## Frage
Wie organisieren wir das Repo, wenn wir später mehrere Spiele machen?

## Entscheidung
Jedes Spiel bekommt einen eigenen Oberordner direkt im Repo-Hauptordner. Das erste Spiel heißt **Galactic Miner Tycoon** (`galactic-miner-tycoon/`). In diesem Ordner liegt alles zum Spiel: Konzept, Entscheidungen, Aufträge, Checklisten, Daten, Referenzen, Technik und Code.

## Warum
Alles, was zusammengehört, ist an einem Ort, und die Claudes finden die Vision und den Stand immer an derselben Stelle. Weitere Spiele stören sich nicht gegenseitig.

## Folgen
`spiel/` und `auftraege/` aus dem Repo-Hauptordner wurden in `galactic-miner-tycoon/` verschoben. Haupt-`CLAUDE.md` und Haupt-`README.md` wurden angepasst.
