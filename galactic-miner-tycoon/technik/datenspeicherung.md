# Datenspeicherung

Status: **Vorschlag**.

## Was pro Spieler gespeichert wird
- Credits, Gems
- Ressourcen-Bestände (Silos)
- Gebaute Gebäude und deren Level
- Freigeschaltete Planeten, Forschungen, Schiff-Upgrades
- Zeitpunkt des letzten Besuchs (für Offline-Einnahmen, falls gewünscht – `../spiel/01-spielablauf.md`)

## Regeln
- Gespeichert wird per DataStore im `DataService`, **nur serverseitig**.
- Datenformat hat eine **Versionsnummer** (`dataVersion`), damit alte Spielstände später migriert werden können.
- Automatisch speichern alle ~60 s und beim Verlassen.
- Neue Felder immer mit Standardwert ergänzen.
