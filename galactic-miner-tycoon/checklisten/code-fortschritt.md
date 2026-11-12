# Code-Fortschritt M1 (Wiedereinstieg bei Abbruch)

Zweck: Wenn ein Chat mitten in der Arbeit abbricht (Usage-Limit), steht hier, **was fertig ist und was als Nächstes kommt**. Der Chat aktualisiert diese Datei nach **jedem Schritt**, committet und pusht.

- **Zuletzt geändert:** 12.11.2026 (Anfangszustand, noch kein Schritt gebaut)
- **Konzept:** `../spiel/`, `../daten/`, Entscheidungen 005 bis 020. Nicht ohne Rückfrage ändern.

## Schritte (kleine Scheiben, in dieser Reihenfolge)
| # | Schritt | Status | Commit | Beweis |
|---|---|---|---|---|
| 1 | Config als Luau aus `../daten/` (Erze, Kästen, Bohrer, Räume, Spitzhacke, Rucksack), alte Credits-Config entfernen | fertig | `47f2d24` | Studio (Edit): alle 10 Shared-Skripte per Rojo da, Länge gleich (ohne CR); `Currencies` weg; 67 Prüfungen der Config-Werte gegen `daten/` per loadstring: 0 Fehler; keine Fehler im Log. `--!strict` nicht maschinell geprüft (kein luau-analyze installiert) |
| 2 | Daten pro Welt (Welt-ID), Standard-Welt, Speichern/Laden mit Mock im Studio | offen | – | – |
| 3 | Platzhalter-Insel (Greybox): flacher Boden, Start-Halle, Lager mit Eisen-Kasten, Eisen-Vorkommen mit Ring | offen | – | – |
| 4 | Handabbau mit Spitzhacke (Tragevorrat 10), Erz in den Kasten legen | offen | – | – |
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
- Schritt 2 begonnen.
