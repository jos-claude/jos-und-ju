# 3D-Modelle

Hier liegen die Blender-Modelle (`.blend`) und die Exporte für Roblox (`.fbx` und `.glb`). Gebaut nach den Referenzbildern in `../../referenz/bilder/gebaeude/`. Liste und Status: `../asset-liste.md`. Vorschaubilder: `vorschau/`.

## Stand (12.11.2026)
| Modell | Datei | Stand |
|---|---|---|
| Förderband: gerade, Segment, Kurve rechts/links, Ende mit Trichter | `conveyor_*.fbx/.glb`, `conveyor.blend` | **v3 – fertig zum Import.** Gegen das Referenzbild geprüft und überarbeitet (Proportionen, Kurve, Trichter, Beine). |
| Erzbrocken A/B/C | `ore_chunk.fbx/.glb` | **v3 – fertig zum Import.** |
| Lager-Kasten | `ore_bin.fbx/.glb`, `ore_bin.blend` | **v3 – fertig zum Import.** Überarbeitet (Glas, Erzhaufen, Trichter, Schild, Streben, Anzeige). |
| Basis: Start-Halle + gesperrter Raum | `base_hall.fbx/.glb`, `base_room.fbx/.glb`, `base.blend` | **v3 – fertig zum Import.** Überarbeitet (Höhe, Dachrand mit Fase, Rolltore, Antenne, Raumtiefe, Warnstreifen). |

**Look:** flache Farben ohne Texturen (Comic-Stil), mit kräftigem Kontrast (Wunsch von Jos, 12.11.2026). Ein Versuch mit Texturen wurde verworfen.

## Einheiten und Ausrichtung
- **1 Blender-Einheit = 1 Stud.** Boden bei z = 0, Vorderseite zeigt nach −Y (wie beim Bohrer).
- Pro Modell gibt es **ein Objekt pro Farbe**, z. B. `OreBin_Orange`, `OreBin_Fill_OreRock`. In Roblox wird jedes davon eine MeshPart mit einer Farbe. Der mittlere Namensteil ist eine Gruppe, die man getrennt ein-/ausblenden kann (`Lid`, `Fill`, `GaugeFill`, `Door`, `Shutter`).

## Dateien
| Datei | Modell(e) | Größe (Studs, ca.) | Hinweis |
|---|---|---|---|
| `conveyor_straight` | `ConveyorStraight` | 8 × 5 × 2,95 | Gerades Band wie im Bild (2 Segmente), Fluss in +X |
| `conveyor_segment` | `ConveyorSegment` | 4 × 5 × 2,95 | 4-Stud-Stück zum Aneinanderreihen (`belt_segment`), gerade Enden |
| `conveyor_curve` | `ConveyorCurve` | 8,5 × 8,5 | Rechtskurve 90° im 8 × 8-Raster: rein bei x = −2 von −Y, raus bei y = +2 nach +X |
| `conveyor_curve_left` | `ConveyorCurveLeft` | 8,5 × 8,5 | Linkskurve (gespiegelt) |
| `conveyor_end` | `ConveyorEnd` | 6,3 × 5 × 4,4 | Bandende mit Trichter, Fluss in +X |
| `ore_chunk` | `OreChunkA/B/C` | 0,7–1,1 | Erzbrocken (Eisen) |
| `ore_bin` | `OreBin` | 9,35 × 6,6 × 8,7 | Lager-Kasten; `Lid` = Deckel, `Fill` = Erzhaufen, `GaugeFill` = Anzeige |
| `base_hall` | `BaseHall` | 17,7 × 17 × 17 | Start-Halle (Raum 1) mit Verbindungsgängen; `Door` = Tür |
| `base_room` | `BaseRoom` | 9,7 × 10,5 × 9,4 | Gesperrter Raum; `Shutter` = Rolltor. Steht bei x = ±13, y = −0,2 neben der Halle |

Band-Oberkante liegt bei 2,75 Studs (knapp unter dem Ausgang des Bohrers bei 2,85).

Füllstand: `OreBin_Fill_*` und `OreBin_GaugeFill_*` haben ihren Boden am Kastenboden. Im Spiel per Höhe skalieren.

## In Roblox Studio importieren
1. Place öffnen, **Datei → Import 3D**, eine `.fbx` (oder `.glb`) wählen. Mehrere Dateien nacheinander.
2. Die neuen Modelle markieren und den Inhalt von **`StudioModelSetup.luau`** in die **Command Bar** kopieren und ausführen. Das färbt alle Teile, setzt Neon/Glas, verankert alles, sortiert die Teile in Modelle und korrigiert die Größe (falls der Import in Metern kam).
3. Fertige Modelle nach **`ServerStorage.GMT_Models`** legen (nicht nach `ReplicatedStorage.Assets`: Rojo löscht dort alles, was nicht als Datei in `src/` liegt). Eine Ansicht zum Anschauen steht in `Workspace.GMT_ModelShowcase`.

## Neu bauen
Alles entsteht aus den Skripten in `blender-skripte/`:

```
blender -b -P blender-skripte/build_conveyor.py
blender -b -P blender-skripte/build_ore_bin.py
blender -b -P blender-skripte/build_base.py
```

Mit `-- --render` am Ende entstehen zusätzlich Vorschaubilder in `vorschau/`. Farben stehen in `blender-skripte/gmt_materials.py`, Formen in den `build_*.py`, gemeinsame Bausteine in `gmt_lib.py`.
