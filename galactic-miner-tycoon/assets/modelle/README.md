# 3D-Modelle

Hier liegen die Blender-Modelle (`.blend`), die Exporte für Roblox (`.glb` mit Texturen, `.fbx` ohne eingebettete Texturen) und die Texturen (`texturen/`). Gebaut nach den Referenzbildern in `../../referenz/bilder/gebaeude/`. Liste und Status: `../asset-liste.md`.

## Stand (12.11.2026)
| Modell | Datei | Stand |
|---|---|---|
| Förderband: gerade, Segment, Kurve rechts/links, Ende mit Trichter | `conveyor_*.glb/.fbx`, `conveyor.blend` | **v2 – fertig zum Import.** Nach Prüfung gegen das Referenzbild überarbeitet (Proportionen, Kurve, Trichter, Beine, Farben) + Texturen. |
| Erzbrocken A/B/C | `ore_chunk.glb/.fbx` | **v2 – fertig zum Import.** |
| Lager-Kasten | `ore_bin.glb/.fbx`, `ore_bin.blend` | **v2 – fertig zum Import.** Überarbeitet (Glas, Erzhaufen, Trichter, Schild, Streben, Anzeige) + Texturen. |
| Basis: Start-Halle + gesperrter Raum | `base_hall.glb/.fbx`, `base_room.glb/.fbx`, `base.blend` | **v1 – Entwurf.** Hat schon die neuen Texturen; die Korrekturen aus der Prüfung (Höhe, Dachrand, Rolltore, Antenne, Raumtiefe, Farben) stehen noch aus. Kann zum Testen importiert werden, wird aber noch ersetzt. |

Der Stil folgt dem Wunsch von Jos: metallischer und etwas realistischer, mehr Kontrast, Comic-Look bleibt (kräftige Farben, dicke Formen, Fasen).

## Einheiten und Ausrichtung
- **1 Blender-Einheit = 1 Stud.** Boden bei z = 0, Vorderseite zeigt nach −Y (wie beim Bohrer).
- Pro Modell gibt es **ein Objekt pro Material**, z. B. `OreBin_Orange`, `OreBin_Fill_OreRock`. In Roblox wird jedes davon eine MeshPart. Der mittlere Namensteil ist eine Gruppe, die man getrennt ein-/ausblenden kann (`Lid`, `Fill`, `GaugeFill`, `Door`, `Shutter`).

## Dateien
| Datei | Modell(e) | Größte Ausdehnung (Studs) | Hinweis |
|---|---|---|---|
| `conveyor_straight` | `ConveyorStraight` | 8 × 5 × 2,95 | Gerades Band wie im Bild (2 Segmente), Fluss in +X |
| `conveyor_segment` | `ConveyorSegment` | 4 × 5 × 2,95 | 4-Stud-Stück zum Aneinanderreihen (`belt_segment`), gerade Enden |
| `conveyor_curve` | `ConveyorCurve` | 8,5 × 8,5 | Rechtskurve 90° im 8 × 8-Raster: rein bei x = −2 von −Y, raus bei y = +2 nach +X |
| `conveyor_curve_left` | `ConveyorCurveLeft` | 8,5 × 8,5 | Linkskurve (gespiegelt) |
| `conveyor_end` | `ConveyorEnd` | 6,3 × 5 × 4,4 | Bandende mit Trichter, Fluss in +X |
| `ore_chunk` | `OreChunkA/B/C` | ca. 0,7–1,1 | Erzbrocken (Eisen) |
| `ore_bin` | `OreBin` | 9,35 × 6,6 × 8,7 | Lager-Kasten; `Lid` = Deckel, `Fill` = Erzhaufen, `GaugeFill` = Anzeige |
| `base_hall` | `BaseHall` | 17,4 × 16 × 15 | Start-Halle (Raum 1); `Door` = Tür |
| `base_room` | `BaseRoom` | 9 × 11 × 9,4 | Gesperrter Raum; `Shutter` = Rolltor. Steht bei x = ±13, y = −0,5 neben der Halle |

Band-Oberkante liegt bei 2,75 Studs (knapp unter dem Ausgang des Bohrers bei 2,85).

Füllstand: `OreBin_Fill_*` und `OreBin_GaugeFill_*` haben ihren Boden am Kastenboden. Im Spiel per Höhe skalieren.

## Texturen (`texturen/`)
Kachelbare PBR-Texturen, 512 × 512, eine Kachel = 4 × 4 Studs. Pro Farbe eine `<Material>_color.jpg`, pro Typ Rauheit/Metall/Normal:
- `paint` – lackiertes Metall mit Kratzern und Abplatzern (leicht metallisch)
- `steel` – gebürsteter Stahl
- `tread` – Riffelblech (Rampe, Fußplatten)
- `rubber` – Gummiband mit Querrillen
- `rock` – Erz mit Rostflecken

## In Roblox Studio importieren
1. Place öffnen, **Datei → Import 3D**, eine **`.glb`** wählen (bringt die Texturen mit). Mehrere Dateien nacheinander.
2. Nach dem Import die neuen Modelle markieren und den Inhalt von **`StudioModelSetup.luau`** in die **Command Bar** kopieren und ausführen. Das sortiert die Teile in Modelle, setzt Neon/Glas, verankert alles und korrigiert die Größe (Import in Metern wird auf Studs umgerechnet). Texturen bleiben erhalten; Teile ohne Textur bekommen Farbe + Roblox-Material (Metal, DiamondPlate, Rubber …).
3. Fertige Modelle nach `ReplicatedStorage.Assets` ziehen und per Rechtsklick → **Save to File** als `.rbxm` nach `src/ReplicatedStorage/Assets/` im Repo speichern (sonst löscht Rojo sie beim Sync).

Falls `.glb` nicht klappt: die `.fbx` importieren. Dann gibt es keine Texturen, das Setup-Skript färbt die Teile und nimmt Roblox-Materialien.

## Neu bauen
Alles entsteht aus den Skripten in `blender-skripte/`:

```
python blender-skripte/make_textures.py        # nur nötig, wenn Texturen geändert werden (numpy + Pillow)
blender -b -P blender-skripte/build_conveyor.py
blender -b -P blender-skripte/build_ore_bin.py
blender -b -P blender-skripte/build_base.py
```

Mit `-- --render` am Ende entstehen zusätzlich Vorschaubilder in `vorschau/`. Farben und Material-Typen stehen in `blender-skripte/gmt_materials.py`, Formen in den `build_*.py`.
