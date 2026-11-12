# Code-Fortschritt M1 (Wiedereinstieg bei Abbruch)

Zweck: Wenn ein Chat mitten in der Arbeit abbricht (Usage-Limit), steht hier, **was fertig ist und was als Nächstes kommt**. Der Chat aktualisiert diese Datei nach **jedem Schritt**, committet und pusht.

- **Zuletzt geändert:** 12.11.2026 (Schritt 1 bis 4 fertig, als Nächstes Schritt 5)
- **Konzept:** `../spiel/`, `../daten/`, Entscheidungen 005 bis 020. Nicht ohne Rückfrage ändern.

## Schritte (kleine Scheiben, in dieser Reihenfolge)
| # | Schritt | Status | Commit | Beweis |
|---|---|---|---|---|
| 1 | Config als Luau aus `../daten/` (Erze, Kästen, Bohrer, Räume, Spitzhacke, Rucksack), alte Credits-Config entfernen | fertig | `47f2d24` | Studio (Edit): alle 10 Shared-Skripte per Rojo da, Länge gleich (ohne CR); `Currencies` weg; 67 Prüfungen der Config-Werte gegen `daten/` per loadstring: 0 Fehler; keine Fehler im Log. `--!strict` nicht maschinell geprüft (kein luau-analyze installiert) |
| 2 | Daten pro Welt (Welt-ID), Standard-Welt, Speichern/Laden mit Mock im Studio | fertig | `85ccc9c` + Fix Mock-Prüfung | Playtest von Ju (12.11.2026): Mock lädt und speichert. Studio (Edit): Skripte per Rojo da, Länge gleich; Selbsttest 23/23 (Standard-Welt, Speichern→neu Laden gleiche Werte, 2. Spieler eigene Welt, fehlende Felder ergänzt, neuere Version abgelehnt, Lesefehler → nichts geschrieben, Studio → immer Mock, echter DataStore in Studio verweigert); keine Fehler im Log |
| 3 | Spielobjekte auf der Welt von Jos (WorldBuilder, `../technik/weltgenerator.md`): Lager mit Eisen-Kasten (Platzhalter), Eisen-Vorkommen nach Ring mit Seed (ResourceNodeService). Die Welt und ihre Modelle gehören Jos, nicht neu bauen | fertig | `624cd75` | Edit: alle neuen Skripte per Rojo da, kompilieren; Platzierung: gleicher Seed → gleiche Positionen, erste 3 bleiben gleich, wenn später 6 da sind; 200 Seeds: immer 6 Vorkommen, 0 Regelverstöße, Radius 15,9–199,9, kleinster Abstand 24,2. Play (Mock): `Workspace.GMT_Gameplay` mit `GMT_PH_StartHall`, `GMT_PH_Storage` (Eisen-Kasten 0/100), 3 Vorkommen (Radius 189,8 / 137,7 / 50,3), Unterkante je 0,4 unter Boden y = 0 (Raycast), Prompt da; Positionen im Edit aus Seed 2098410383 neu berechnet = identisch; keine Fehler eigener Skripte. Gelände von Jos war noch nicht gebaut → steht auf der Baseplate |
| 4 | Handabbau mit Spitzhacke (Tragevorrat 10), Erz in den Kasten legen | fertig | siehe Git-Log „Schritt 4 fertig“ (Code: `c510c1d`) | Play (Mock, echte Taste E gehalten): Tragen 1→10 im Abstand 1,00–1,02 s, Stopp bei 10, Zahl orange + Hinweis „Voll!“; aufs Abladefeld gelaufen → Kasten 10/100, Tragen 0/10, Füllstand im Glas 0,92 Studs, Schild „EISEN 10/100“. Gefühl gemessen: Ton 0,07 s nach Tastendruck, „+1“ 0,06 s danach, Felsen staucht auf 0,88 und federt auf 1,0, Tonhöhe steigt mit dem Füllstand (0,94 → 1,06), Splitter-Emitter da, alle 3 Töne geladen; keine Fehler eigener Skripte. **Nur statisch geprüft:** Kasten-Limit 100 (voller Kasten, Rest bleibt in der Hand), „zu weit weg“, „zu hart“. Halle für den WorldBuilder-Spawn (0, 0, 20) nach z = 44 verschoben |
| 5 | Erster Bohrer kaufen und auf Vorkommen setzen, Puffer, Erz holen | offen | – | – |
| 6 | Raum 2 (Schmiede) kaufen, Rucksack und Spitzhacke verbessern | offen | – | – |
| 7 | Vorkommen erscheinen nach Fortschritt, Kupfer-Kasten, Bänder, Garage/Rover, Tutorial, Lobby (später, in eigenen Runden) | offen | – | – |

Status: offen / in Arbeit / fertig (mit Beweis).

## Wiedereinstieg
1. `git pull`, diese Datei lesen, den ersten Schritt mit Status „in Arbeit“ oder „offen“ nehmen.
2. Im Repo nachsehen, was davon schon existiert (`git log`, `src/`), bevor etwas neu gebaut wird.
3. Nach jedem Schritt: Status hier eintragen, committen, pushen.

## Notizen des letzten Chats
_(hier trägt der Chat Besonderheiten, Probleme und offene Fragen ein)_

- 12.11.2026 (Ju-Chat): Schritt 1 Dateien geschrieben (`Config/Ores, Bins, Drills, Rooms, Pickaxe, Backpack`, `Types/ConfigTypes`, `Resources` um Kohle/Titan ergänzt, `Currencies` gelöscht); in Studio geprüft, fertig. Offene Fragen dazu: Upgrade-Kosten der anderen Bohrer ("Kleinigkeit vom nächsten Erz" ist nicht beziffert, fehlt im Code), Rundung der Preise (`math.round`).
- 12.11.2026 (Ju-Chat, Schritt 3): Gelände von Insel 1 war im Place noch nicht gebaut (`ServerStorage.WorldBuilder` fehlte, Jus Rojo lief noch vom Nachmittag). Spielobjekte stehen deshalb auf der alten Baseplate; der Raycast findet später automatisch das Terrain. Neue Dateien: `Config/BaseLayout`, `Modules/NodePlacement` (Shared), `Server/Modules/Ground, Greybox, GameplayFolder, PlayerState, Remotes`, `Services/BaseService, ResourceNodeService`; `DataService` um `GetPlayTimeSeconds`/`GetPlayersInWorld` ergänzt. Halle und Lager entstehen beim Serverstart (nicht im Edit sichtbar).
- 12.11.2026 (Ju-Chat, Schritt 4): `PickaxeService` (Server prüft jeden Schlag), Abladefeld in `BaseService`, `HudController` und `PickaxeController` (Client) geschrieben, kompilieren in Studio. Play-Test bestanden, Schritt 4 fertig. Bedienung: am Erz E halten (Handy: Prompt-Knopf halten), aufs grüne Feld „ABLADEN“ laufen. Feel-Zahlen in `CONFIG` oben in `PickaxeController` und `HudController`. Offen: Schlag-Animation der Figur (kein Animations-Asset, nur der Felsen bewegt sich), Rundung beim Härte-Malus (jetzt kaufmännisch, mind. 1). Nächster Schritt: 5 (erster Bohrer).
- Schritt 2: Code geschrieben (`Server/Modules/WorldData, SaveStore, WorldRepository`, `Services/DataService`); Edit-Selbsttest bestanden (23/23). Nächster Schritt: Playtest mit Jus Erlaubnis, dann Status auf fertig.
