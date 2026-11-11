# Roblox Studio – Einrichtung (einmalig)

Siehe Hintergrund in `../technik/zusammenarbeit-roblox-studio.md` und `../entscheidungen/002-zusammenarbeit-roblox-studio.md`.

## Place anlegen
- [ ] Einen Place „Galactic Miner Tycoon“ in Roblox Studio anlegen (einer von uns)
- [ ] **Team Create** aktivieren und den anderen einladen
- [ ] Place-ID und Universe-ID in `../technik/zusammenarbeit-roblox-studio.md` eintragen

## Rojo (Code aus dem Repo in den Place)
- [ ] Rojo installieren (Aftman/Rokit oder Rojo-Plugin in Studio)
- [ ] Repo klonen, `galactic-miner-tycoon/` öffnen
- [ ] `rojo serve` starten, in Studio mit dem Rojo-Plugin verbinden
- [ ] Test: Spiel starten – in der Ausgabe erscheint „Server started“ und „Client started“

## Git
- [ ] Beide haben Zugriff auf das GitHub-Repo
- [ ] Vor jedem Arbeiten `git pull`, nach jeder Arbeit `git push` (siehe Haupt-`CLAUDE.md`)

## Faustregeln für gleichzeitiges Arbeiten
- [ ] Wir haben uns abgesprochen, wer welchen Bereich der Welt baut (steht im Auftrag)
- [ ] Scripts bearbeiten wir nur in den Dateien in `src/`, nicht direkt in Studio

## Rojo starten – Schritt für Schritt (getestet am 11.11.2026, Rojo 7.7.1, Windows)
1. Terminal öffnen (PowerShell) und in den Spielordner wechseln: `cd C:\Users\<Name>\Projects\JosUndJu\galactic-miner-tycoon`
2. Server starten: `rojo serve`. Wird `rojo` nicht gefunden, das Terminal ganz neu öffnen oder den vollen Pfad nutzen: `& "$env:LOCALAPPDATA\Programs\rojo\rojo.exe" serve`
3. Es erscheint „Rojo server listening … Port 34872“. Das Terminal offen lassen.
4. In Studio den Place öffnen, **Plugins → Rojo → Connect**, bei Rückfrage bestätigen.
5. Danach stehen `Shared`, `Server` und `Client` aus `src/` in Studio. Scripts nur im Repo bearbeiten, nicht in Studio.
6. Beenden mit `Strg+C` im Terminal.

Das Studio-Plugin installiert man mit `rojo plugin install`. Die Datei `default.project.json` baut mit dieser Rojo-Version fehlerfrei.
