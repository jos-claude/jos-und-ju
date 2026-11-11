# Entscheidung 005: Jeder Planet bekommt einen eigenen Place

- **Status:** Beschlossen
- **Datum:** 11.11.2026
- **Von:** Ju (ersetzt 004)

## Frage
Alles in einem Place oder pro Planet ein eigener Place?

## Entscheidung
**Jeder Planet ist ein eigener Place** innerhalb desselben Spiels (einer Universe). Die Raketenreise wechselt per Teleport den Place.

## Warum
Jeder Planet bleibt klein, lädt schnell und kann einzeln gebaut werden.

## Folgen
- Spielstände müssen über alle Places derselben Universe funktionieren (gleicher DataStore, siehe `../technik/datenspeicherung.md`).
- `TravelService` nutzt `TeleportService`; Daten wie Rohstoffe und Rakete müssen beim Teleport mitkommen.
- Jeder Place braucht eigene Place-ID, Team Create und ein eigenes Rojo-Projekt (gemeinsamer Code in `Shared`). Für M1 genügt der Heimatplanet.
- Zu prüfen: `../spiel/06-planeten.md`, `../technik/architektur.md`, `../technik/zusammenarbeit-roblox-studio.md`.
