# Liste: Basis-Modelle, die Claude ohne weiteren Kontext bauen kann

- **Status:** Vorschlag (Jos' Claude, 14.11.2026). Nichts davon ist beschlossen. Jos und Ju wählen aus, was gebaut wird.
- **Auftrag von Jos (14.11.):** eine Liste der Raumstation-Modelle (= Basis, siehe Glossar), bei denen klar ist, wie sie nach unserem Konzept aussehen sollen, jeweils mit einem Higgsfield-Bild.
- **Bilder:** Higgsfield API, Modell `marketing-studio/image`, 2K, mit unseren Bildern als Stil-Vorlage. 13 Bilder (10 hier, 3 für die Spitzhacke) zusammen ca. 3,40 $. Alle beim ersten Versuch brauchbar. Die Prompts stehen in `../../../referenz/bilder/higgsfield-jobs-2026-11-14.json`.
- **Alle 10 Bilder auf einen Blick:** `../../../referenz/bilder/basis-modelle-uebersicht.jpg`
- **Bauweg für alle:** Blender-Skript mit `gmt_lib.py`, wie Förderband, Lager-Kasten und Spitzhacke. Alles ist mechanisch und aus Grundformen, deshalb kein Tripo (Skill `jos-3d-asset-routing`).

## A. Ohne weiteren Kontext baubar (Bild liegt vor)

| # | Modell (Name im Code) | Wofür (Konzept) | Bild | Bauweg | Teile / Dreiecke (Schätzung) | Vorschlag Priorität |
|---|---|---|---|---|---|---|
| 1 | Kauffeld `BuyPad` | Drauflaufen = kaufen (Entscheidung 021). 3 Zustände: kaufbar (Cyan), zu teuer (Orange), gesperrt (Grau mit Schloss) | `bilder/gebaeude/kauffeld-01.jpg` | neues Skript `build_buy_pad.py`. Zustände nur über Farbe der Neon-Kante, das schaltet Jus Code um | 6 Teile, ca. 800 | **P1** (steht überall in der Basis) |
| 2 | Lager-Kästen Kupfer, Kohle, Kristall, Titan (`bin_*`) | ein Kasten pro Erz (`daten/gebaeude.md`) | `bilder/gebaeude/lager-kasten-varianten-01.jpg` | `build_ore_bin.py` um Farbvarianten erweitern (Seitenfelder und Erz in der Erzfarbe) | wie `OreBin`, ca. 9.000 | **P1** (Kupfer kommt mit Schritt 7) |
| 3 | Bohrer Kupfer, Kohle, Kristall, Titan (`drill_copper` …) | ein Bohrer pro Erz, Körper bleibt orange, nur Akzente und Erz ändern sich | `bilder/gebaeude/bohrer-varianten-01.jpg` | Umfärben von `drill_iron`. **`drill_iron` hat Ju gebaut**, deshalb vorher mit Ju abstimmen, wer die Varianten macht | wie `drill_iron`, ca. 2.100 | **P1** (Kupfer), Rest P3 |
| 4 | Schmiede-Einrichtung (`ForgeAnvilStation`, `ForgeBackpackBench`, `ForgeTeleporter`, `ForgeFurnace`, Deko) | Raum 2 | `bilder/raeume/schmiede-01.jpg` | Bauplan steht schon: `schmiede-einrichtung.md` → `build_forge.py` | 9 Modelle, ca. 16.000 | **P1** |
| 5 | Rucksack, 5 Stufen (`Backpack1` … `Backpack5`) | Stoff, Metall, Verstärkt, Profi, Titan (`daten/upgrades.md`, Entscheidung 017). Wird größer, ab Stufe 4 mit Erz-Fenster | `bilder/ausruestung/rucksack-01.jpg` | neues Skript `build_backpack.py`, Prinzip wie bei der Spitzhacke („ein Gerüst, fünf Häute“). Hängt am Rücken (Attachment `BodyBackAttachment`) | je ca. 500 bis 1.200 | **P1** (Stufe 1), Rest P2 |
| 6 | Maschinenhalle-Einrichtung (`MachineBeltStation`, `MachineDrillStation`, Kran, Rohrwand, Palette, Werkzeugkiste) | Raum 3: Förderbänder kaufen, Bohrer aufwerten | `bilder/raeume/maschinenhalle-01.jpg` | neuer Bauplan wie bei der Schmiede, gleicher Stations-Rahmen | ca. 6 Modelle, ca. 14.000 | P2 |
| 7 | Band-Sammler `ConveyorMerger` (`belt_merger`) | 3 Bänder rein, 1 raus (Entscheidung 012, später) | `bilder/gebaeude/band-sammler-01.jpg` | `build_conveyor.py` erweitern (gleiche Bänder und Schienen) | 8 Teile, ca. 2.500 | P2 |
| 8 | Basis-Deko außen (Schüssel-Antenne, Solarpanel, Kisten, Fässer, Tank, Ventil, Signallampe, Geländer) | Basis lebendiger machen, auch für die Insel nutzbar | `bilder/gebaeude/basis-deko-01.jpg` | neues Skript `build_props.py`, 8 kleine Modelle | je 2 bis 8 Teile, je unter 1.000 | P2 |
| 9 | Garage-Einrichtung (Hebebühne, Rover-Upgrade-Station, Reifenstapel, Werkzeugwand, Zapfsäule, Ladestation) | Raum 4: Rover kaufen und verbessern | `bilder/raeume/garage-01.jpg` | neuer Bauplan wie bei der Schmiede. **Ohne den Rover selbst** (siehe B) | ca. 7 Modelle, ca. 12.000 | P3 |
| 10 | Forschungslabor-Einrichtung (Techbaum-Konsole, Probenbank, Kristall-Analysator, Server-Schrank) | Raum 5: Techbaum | `bilder/raeume/labor-01.jpg` | neuer Bauplan wie bei der Schmiede. Das Techbaum-Bild auf dem Bildschirm macht später die UI | ca. 5 Modelle, ca. 10.000 | P3 |

**Gemeinsamer Baustein:** Schmiede, Maschinenhalle und Garage nutzen denselben **Stations-Rahmen** (dunkler Sockel mit Warnstreifen, orange Rückwand mit Stahl-Kreuzstreben, Cyan-Leiste oben). Den baue ich einmal als Funktion in `gmt_lib.py`, dann sehen alle Räume gleich aus und die Skripte bleiben kurz.

**Was ich an den Bildern abweichend umsetzen würde (Vorschlag):**
- Rucksack: Die untere Reihe zeigt nicht die Seite, sondern wieder den Rücken. Die Tiefe nehme ich aus der Schräg-Ansicht.
- Labor: Der Bildschirm zeigt einen Techbaum. Im Modell wird er nur eine dunkle Fläche, den Inhalt zeigt die UI.
- Maschinenhalle: Auf dem Stapel Förderband-Teile ist ein gelbes X. Das lasse ich weg.

## B. Braucht noch Kontext (kein Bild gemacht)

| Modell | Was fehlt |
|---|---|
| Rover (Mondauto) | Aussehen und Bauweg. Fahrzeuge gehen laut Routing eher zu Tripo, unser Blockstil ginge aber auch in Blender. Größe, Sitz, sieht man den Spieler fahren? |
| Rakete und Raketen-Hangar (Raum 6) | Wächst die Rakete sichtbar, während man Erz hineinsteckt (Bau-Stufen)? Wie groß ist sie, gibt es eine Start-Animation? |
| Lobby-Raumschiff und Spielstand-Pad | Innenraum-Stil und Größe der Lobby (eigener Place, Entscheidung 014). Das Pad allein wäre wie das Kauffeld machbar. |
| Fabrik, Silo, Verarbeitung | Im Konzept noch nicht entworfen (`spiel/04-verarbeitung-und-lager.md`). |
| Schiff-Upgrades, Laserpickel, Scanner | Kommen erst in M3/M4 und sind noch leer (`daten/upgrades.md`). |

## Offene Fragen
- [ ] Welche Modelle aus A sollen gebaut werden, in welcher Reihenfolge? (Jos, Ju)
- [ ] Bohrer-Varianten: Macht Ju sie (er hat `drill_iron` gebaut) oder Jos' Claude?
- [ ] Für Rover und Rakete: Wer liefert die fehlenden Antworten aus Teil B?
