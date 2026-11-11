# Entscheidung 002: Zusammenarbeit in Roblox Studio (Rojo + Git)

- **Status:** Beschlossen (11.11.2026, Ju)
- **Datum:** 11.11.2026
- **Von:** Claude (Vorschlag für Jos und Ju)

## Frage
Wie arbeiten Jos, Ju und ihre Claudes gemeinsam in **einem Place** in Roblox Studio, wenn die Claudes nur Dateien im Git-Repo bearbeiten können?

## Entscheidung (Vorschlag)
- **Code** (Luau-Scripts) liegt als Dateien in `src/` und wird mit **Rojo** in den Place synchronisiert. Die Claudes bearbeiten die Dateien, Studio zeigt die Änderungen live.
- **Welt, Modelle, UI-Layout** werden in **Roblox Studio** gebaut, gemeinsam über **Team Create** (der Place liegt auf Roblox).
- Wer baut was, steht in den Aufträgen – nie gleichzeitig am selben Script oder Model.

## Warum
Rojo macht Scripts git-fähig (Änderungen sichtbar, Konflikte lösbar, Claudes können Code schreiben). Modelle und Welt sind Binärdaten und gehören in Studio/Team Create.

## Alternativen
- Nur Team Create, kein Rojo: einfacher zu starten, aber die Claudes können keinen Code beitragen.

## Folgen
Siehe `../technik/zusammenarbeit-roblox-studio.md`, `../default.project.json`, `../src/`.
