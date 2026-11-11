# Zusammenarbeit in Roblox Studio

Hintergrund: `../entscheidungen/002-zusammenarbeit-roblox-studio.md` (Vorschlag, noch zu bestätigen). Einrichtung: `../checklisten/roblox-studio-setup.md`.

## Wer arbeitet womit?
| Arbeit | Wo | Wie |
|---|---|---|
| Code (Luau) | `src/` im Repo | Datei bearbeiten → Rojo zeigt es in Studio |
| Welt, Modelle, Beleuchtung | Roblox Studio | Team Create |
| UI-Layout | Roblox Studio | Team Create |
| Konzept, Daten, Aufträge | Repo (Markdown) | Git |

## Regeln
1. **Ein Bereich, ein Bearbeiter.** Welche Welt-Zonen/Modelle wer baut, steht im Auftrag. Nie gleichzeitig am selben Model/Script.
2. Scripts nur in `src/` ändern (sonst überschreibt Rojo sie wieder).
3. Neue Modelle in `../assets/asset-liste.md` eintragen.
4. Vor dem Arbeiten `git pull`, danach `git push`.

## Place-Daten (bitte eintragen, sobald vorhanden)
- Place-ID (Heimatplanet): 81903956971405
- Universe-ID: 10775982291
- Roblox-Account Jos: _ · Roblox-Account Ju: _
