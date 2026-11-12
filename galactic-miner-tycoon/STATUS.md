# Status – Galactic Miner Tycoon

## Stand 12.11.2026, abends (Nachtrag von Jos' Claude)
| Bereich | Stand | Wo |
|---|---|---|
| Planeten-Physik (Entscheidung 019) | **im Play gemessen:** Schwerkraft 60, Sprung 12 Studs / 1,23 s, Trägheit (Anlaufen ca. 0,6 s, 2 Studs Nachrutschen), Landestaub | `src/…/MovementService`, `MovementController` |
| Code M1 (Ju) | Schritt 1 bis 4 fertig (12.11. spät): Greybox-Halle, Lager mit Eisen-Kasten, Eisen-Vorkommen aus dem Seed, Handabbau mit E halten, Abladefeld, HUD. Nächstes: Schritt 5 (erster Bohrer) | `checklisten/code-fortschritt.md` |
| 3D-Modelle v3 (Förderband, Erzbrocken, Lager-Kasten, Basis) | fertig auf `main`, **Import in Studio offen** (Upload-Ordner muss in Studio freigegeben werden) | `assets/modelle/`, `assets/asset-liste.md` |
| Welt Insel 1 (WorldBuilder) | **im Place gebaut (12.11., 21:45)** und im Play getestet – Gelände noch **Platzhalter** (Ebene, eine Mesa), echtes Design baut Jos' Cloud-Chat (Runde 2). Plateau-Oberfläche liegt bei y = 2,0. Himmel-Bilder fertig (`assets/himmel/`), Upload offen. Einspielen ohne Jus Rojo: `rojo serve worldbuilder.project.json` (nur `ServerStorage.WorldBuilder`) | `technik/weltgenerator.md` |
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
