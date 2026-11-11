# Startplan – Was vor dem Bauen erledigt sein muss

- **Status:** Vorschlag (Reihenfolge und Zuständigkeiten bitte bestätigen)
- **Zuletzt geändert:** 11.11.2026
- **Ziel:** Alles Nötige klären und vorbereiten, damit **M1 – Heimatplanet-Prototyp** (`meilensteine.md`) in einem Rutsch gebaut werden kann.

**Wer:** `Ju` / `Jos` = Mensch (Studio, Bilder, Entscheidungen) · `Claude` = Dateien, Code, Blender · `beide` = gemeinsam.
Abhaken mit `[x]`. Phasen von oben nach unten abarbeiten; innerhalb einer Phase darf die Reihenfolge wechseln. Aufgaben an den anderen gehen als Auftrag nach `../auftraege/offen/`.

---

## Phase 1 – Entscheidungen (blockiert alles andere)

Ohne diese Antworten kann ich keinen Code und keine Zahlen festlegen. Ich schlage jeweils einen Standard vor: Wenn ihr einfach „ja“ sagt, gilt er und ich trage ihn in `../entscheidungen/` ein.

| # | Frage | Mein Vorschlag (Standard) | Wer entscheidet | Erledigt |
|---|---|---|---|---|
| 1 | Vision & Stimmung bestätigen (Zielgruppe 8–16, bunt-comichaft, kein Kampf) | ja, so übernehmen | beide | [x] |
| 2 | Singleplayer-Basis oder gemeinsame Basis? | **Jeder Spieler hat seine eigene Basis**, Koop später | beide | [x] |
| 3 | Ein Place, Planeten als Zonen? (`004`) | **Nein: jeder Planet ein eigener Place** (Entscheidung 005) | beide | [x] |
| 4 | Rojo + Team Create? (`002`) | ja | beide | [x] |
| 5 | Was ist „Hub & Hazard“? (`../ideen/hub-and-hazard-konzept.md`) | erst nach M3 klären, nicht für den Start nötig | beide | [x] |
| 6 | Dritte Währung? | **Keine Credits: Rohstoffe (Metall u. ä.) sind die Währung** (Entscheidung 006) | beide | [x] |
| 7 | Wer macht was (Aufgabenverteilung Jos / Ju)? | Jos (Max-Abo) übernimmt die umfangreichen Aufgaben, Ju die kleineren (Entscheidung 007) | beide | [x] |

## Phase 2 – Werkzeuge einrichten (einmalig, Mensch)

Das meiste steht schon in `roblox-studio-setup.md`. Hier nur die Reihenfolge und was ich dabei brauche.

- [ ] **Ju/Jos:** Roblox Studio installiert und eingeloggt
- [ ] **Ju/Jos:** Place „Galactic Miner Tycoon“ anlegen, Team Create an, den anderen einladen
- [x] **Ju/Jos:** Place-ID und Universe-ID an Claude geben (Claude trägt sie in `../technik/zusammenarbeit-roblox-studio.md` ein)
- [x] **Ju/Jos:** Rojo installieren und Test durchführen („Server started“ / „Client started“ in der Ausgabe) – *Rojo 7.7.1 + Studio-Plugin sind auf Jus PC installiert, Test bei Ju erfolgreich; Jos muss selbst installieren*
- [ ] **Ju/Jos:** Blender installiert (für die 3D-Modelle, siehe Phase 4)
- [ ] **Claude:** Prüfen, ob `default.project.json` zur Rojo-Version passt, und Anleitung Schritt für Schritt für Anfänger ergänzen

## Phase 3 – Konzept für M1 ausformulieren (Claude)

Nur die Dateien, die M1 braucht, werden „abgestimmt“. Der Rest bleibt Entwurf.

- [x] `../spiel/02-heimatplanet.md`: Aufbau des Heimatplaneten festlegen (wo steht was, wie viele Bauplätze)
- [x] `../spiel/03-abbau-und-automatisierung.md`: Wie fördert ein Bohrer? (Rate pro Sekunde, wohin gehen die Rohstoffe)
- [x] `../spiel/10-wirtschaft-und-waehrungen.md`: Credits verdienen und ausgeben (Verkaufspreise, Gebäudepreise)
- [x] `../spiel/14-ui-und-bedienung.md`: HUD für M1 (Rohstoff-Anzeige, Kauf-Buttons, Handy-tauglich)
- [x] `../daten/gebaeude.md`: alle `_` durch konkrete Startwerte ersetzen
- [x] `../daten/ressourcen.md`: Verkaufspreise ergänzen
- [x] `../daten/upgrades.md`: erste Bohrer-Upgrades
- [x] Alle ausgefüllten Dateien den Nutzern zeigen und nur nach Bestätigung auf „abgestimmt“ setzen (11.11.2026, Ju; Jos soll gegenlesen)

## Phase 4 – Look festlegen und erste Modelle (beide)

- [ ] **Ju/Jos:** Referenzbilder mit den Prompts aus `../referenz/bild-prompts.md` erzeugen, zuerst: Rakete, Bohrer, Heimatplanet
- [ ] **beide:** Stil bestätigen (bunt-comichaft Low-Poly?), Eintrag in `../spiel/15-optik-und-audio.md` und `../entscheidungen/`
- [ ] **Ju/Jos:** Restliche M1-Bilder erzeugen: Förderband, Silo, Fabrik, Raketenstartplatz
- [ ] **Claude:** Bilder ablegen unter `../referenz/bilder/`, Modelle in Blender bauen
- [ ] **Claude + Ju/Jos:** Export-Weg klären (Blender → FBX → Studio-Import) und an einem Testmodell ausprobieren
- [ ] **Claude:** Jedes fertige Modell in `../assets/asset-liste.md` eintragen
- [ ] **Ju/Jos:** Modelle in Studio importieren und im Place platzieren

## Phase 5 – Code-Grundgerüst für M1 (Claude)

Vorhanden: `src/` mit Config (`Currencies`, `Planets`, `Resources`) und `DataService`. Fehlt für M1:

- [x] `Shared/Config/Buildings.luau` (aus `../daten/gebaeude.md`)
- [x] `Shared/Config/Upgrades.luau` (aus `../daten/upgrades.md`)
- [ ] `ResourceService` statt CurrencyService (Rohstoffe hinzufügen/abziehen, nur auf dem Server)
- [ ] `BuildService` (Kauf-Anfrage prüfen, Gebäude erscheinen lassen)
- [ ] `MiningService` (Bohrer fördern automatisch)
- [ ] Remotes festlegen (`../technik/remotes-und-netzwerk.md`)
- [ ] HUD im Client (Credits-Anzeige, Kauf-Buttons)
- [ ] `DataService` an Credits und Gebäude anbinden (Speichern/Laden, `../technik/datenspeicherung.md`)
- [ ] Namensregeln eingehalten (`../technik/namenskonventionen.md`)

## Phase 6 – Startklar-Check

- [ ] Phasen 1–5 abgehakt
- [ ] `STATUS.md` aktualisiert, Phase auf „1 – Prototyp M1“ gesetzt
- [ ] Erster Auftrag für M1 verteilt (Heimatplanet-Welt in Studio)
- [ ] Erst jetzt: M1 in `meilensteine.md` beginnen

---

## Kleines Roblox-Wörterbuch (für den Einstieg)

| Begriff | Bedeutung |
|---|---|
| **Place** | Eine Spielwelt-Datei auf Roblox, in der wir bauen |
| **Roblox Studio** | Das Programm zum Bauen und Testen |
| **Team Create** | Mehrere Leute bauen gleichzeitig im selben Place |
| **Rojo** | Brücke: Code aus dem Repo erscheint live in Studio |
| **Luau** | Die Programmiersprache von Roblox |
| **DataStore** | Roblox-Speicher für Spielstände |
| **Remote** | Verbindung zwischen Client (Spieler) und Server |

## Verknüpft mit
`meilensteine.md`, `roblox-studio-setup.md`, `../STATUS.md`, `../referenz/bild-prompts.md`
