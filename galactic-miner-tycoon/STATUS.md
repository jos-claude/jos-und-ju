# Status – Galactic Miner Tycoon

## Stand 12.11.2026, abends (Nachtrag von Jos' Claude)
| Bereich | Stand | Wo |
|---|---|---|
| Planeten-Physik (Entscheidung 019) | **im Play gemessen:** Schwerkraft 60, Sprung 12 Studs / 1,23 s, Trägheit (Anlaufen ca. 0,6 s, 2 Studs Nachrutschen), Landestaub | `src/…/MovementService`, `MovementController` |
| Code M1 (Ju) | Schritt 1 bis 6 fertig (13.11.): Greybox-Halle, Lager mit Eisen-Kasten, Eisen-Vorkommen aus dem Seed, Handabbau (E), Abladefeld, HUD, **Kauffelder, Bohrer kaufen/aufstellen/abholen (F), Schmiede (Raum 2) mit Spitzhacke 2 und Rucksack 1**, alles im Play mit Mock belegt. Nächstes: Schritt 7 in eigenen Runden | `checklisten/code-fortschritt.md` |
| 3D-Modelle v3 (Förderband, Erzbrocken, Lager-Kasten, Basis) | fertig auf `main`, **Import in Studio offen** (Upload-Ordner muss in Studio freigegeben werden) | `assets/modelle/`, `assets/asset-liste.md` |
| Welt Insel 1 (WorldBuilder) | Stand „Deko Runde 3“ **im Place gebaut (12.11., 22:10)** und im Play getestet (Plateau y ≈ 0, Sonne passt). **Neu (Stimmigkeits-Runde nach Jos’ Feedback, Vorschlag):** eine gemeinsame Geologie für Boden und Berge, matte Deko statt Plastik, Terrain-Moos, Sonne 30° (Skybox neu gerendert), ca. 22 350 Teile, nur 66 durchsichtige Glas-Teile. Analyse: `referenz/welt-review-insel-1.md`. **Noch neu einspielen** (Rojo `worldbuilder.project.json` oder `welt/BuildIsland1.luau`, frische Kopie wegen require-Cache) und **Studio-Screenshot schicken** (Farben der Vorschau sind außer Ground geschätzt). Skybox-Upload offen; `Lighting.Technology` von Hand auf ShadowMap; ggf. `Terrain.Decoration` an. | `technik/weltgenerator.md`, `welt/README.md`, Bilder: `referenz/bilder/welt/vorschau-insel-1/` |
| Spitzhacke + Schmiede-Einrichtung (14.11.) | **Spitzhacke v2 in Blender gebaut** (Jos' Claude, nach Higgsfield-Bildern): 5 Stufen, 704 bis 1.148 Dreiecke, `pickaxe.glb/.fbx`, Vorschau und Shop-Icons. Schmiede-Einrichtung weiter als Bauplan, jetzt mit Higgsfield-Bild. **Neu:** Liste weiterer Basis-Modelle mit 10 Higgsfield-Bildern (`basis-modelle-liste.md`). Alles **Vorschlag, wartet auf OK von Jos und Ju**, danach Import in Studio und Auftrag an Ju (Einbau, Vitrine, Licht). | `assets/modelle/bauplaene/`, `referenz/bilder/ausruestung/`, `referenz/bilder/raeume/` |
| Abstimmung Jos ↔ Ju im Place | Auftrag 001 (wer baut was) | `auftraege/offen/001-jos-an-ju-welt-modelle-abstimmen.md` |

(Der Abschnitt darunter ist der ältere Stand vom 11.11.)

**Stand:** 11.11.2026 · **Phase:** 0 – Fundament (Struktur & Vision)

## Wo stehen wir?
- [x] Ordnerstruktur angelegt
- [x] Erste Mindmap als Referenz abgelegt (`referenz/mindmap.md`)
- [x] Konzept-Gerüst (`spiel/`) aus der Mindmap abgeleitet – **alles noch Entwurf**
- [ ] Vision und Kernschleife von Jos und Ju bestätigt
- [ ] Erster spielbarer Prototyp (siehe `checklisten/meilensteine.md`)

## Nächste Schritte
1. Vision + Spielablauf gemeinsam durchgehen und abstimmen (`spiel/00-vision.md`, `spiel/01-spielablauf.md`).
2. Offene Kernfragen unten beantworten und als Entscheidung festhalten.
3. Roblox-Studio-Zusammenarbeit klären (Rojo oder nur Team Create) – `entscheidungen/002-zusammenarbeit-roblox-studio.md`.
4. Ersten Auftrag verteilen (z. B. Heimatplanet-Prototyp).

## Offene Kernfragen
1. Was bedeutet **„Hub & Hazard“** in der Mindmap genau? (`spiel/09-hub-und-gefahren.md`)
2. Gibt es eine **dritte Währung** neben Credits und Gems? (Mindmap zeigt ein drittes Symbol.) (`spiel/10-wirtschaft-und-waehrungen.md`)
3. **Ein Place oder mehrere?** Planeten als Zonen im selben Place – oder Teleport zu eigenen Places? (`entscheidungen/004-ein-place.md`)
4. **Singleplayer-Basis oder gemeinsame Basis** mehrerer Spieler? (`spiel/13-multiplayer.md`)
5. Wer von uns macht was (Aufgabenverteilung Jos / Ju)?
