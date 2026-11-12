# 3D-Modelle

Hier liegen die Blender-Modelle (`.blend`) und die Exporte für Roblox (`.fbx`). Die Modelle sind nach den Referenzbildern in `../../referenz/bilder/` gebaut. Liste und Status: `../asset-liste.md`.

## Einheiten und Ausrichtung
- **1 Blender-Einheit = 1 Stud.** Boden bei z = 0, Vorderseite zeigt nach −Y (wie beim Bohrer).
- Pro Modell gibt es **ein Objekt pro Material**, z. B. `OreBin_Orange`, `OreBin_Fill_OreRock`. In Roblox wird jedes davon eine MeshPart mit einer Farbe. Der mittlere Namensteil ist eine Gruppe, die man getrennt ein-/ausblenden kann (z. B. `Lid`, `Fill`, `Door`, `Shutter`).

## Dateien
| Datei | Modell(e) | Größe (Studs, ca.) | Hinweis |
|---|---|---|---|
| `conveyor_straight.fbx` | `ConveyorStraight` | 12 × 4,3 × 3,6 | Gerades Band wie im Bild, Fluss in +X |
| `conveyor_segment.fbx` | `ConveyorSegment` | 4 × 4,3 × 3,6 | 4-Stud-Stück zum Aneinanderreihen (`belt_segment`) |
| `conveyor_curve.fbx` | `ConveyorCurve` | 8 × 8 | Rechtskurve 90° (rein von −Y, raus nach +X) |
| `conveyor_curve_left.fbx` | `ConveyorCurveLeft` | 8 × 8 | Linkskurve (gespiegelt) |
| `conveyor_end.fbx` | `ConveyorEnd` | 8 × 4,3 × 5,3 | Bandende mit Trichter |
| `ore_chunk.fbx` | `OreChunkA/B/C` | ca. 1–1,5 | Erzbrocken (Eisen) |
| `ore_bin.fbx` | `OreBin` | 9,1 × 6 × 8,6 | Lager-Kasten; `Lid` = Deckel, `Fill` = Erzhaufen, `GaugeFill` = Anzeige |
| `base_hall.fbx` | `BaseHall` | 18 × 16 × 14 | Start-Halle (Raum 1); `Door` = Tür |
| `base_room.fbx` | `BaseRoom` | 9 × 11 × 9,4 | Gesperrter Raum; `Shutter` = Rolltor. Steht bei x = ±13, y = −0,5 neben der Halle |
| `conveyor.blend`, `ore_bin.blend`, `base.blend` | alle oben | – | Blender-Dateien zum Weiterbearbeiten |

Füllstand: `OreBin_Fill_*` und `OreBin_GaugeFill_*` haben ihren Boden am Kastenboden. Im Spiel per Höhe (Größe in Y) skalieren.

## In Roblox Studio importieren
1. Studio öffnen, den Place öffnen.
2. **Datei → Import 3D**, eine `.fbx` wählen. Im Importfenster „Import Only As Model“ anlassen. Einheit: Stud (falls gefragt).
3. Nach dem Import die neuen Modelle markieren und den Inhalt von `StudioModelSetup.luau` in die **Command Bar** kopieren und ausführen. Das setzt Farben, Neon/Glas, verankert die Teile und korrigiert die Größe.
4. Fertige Modelle nach `ReplicatedStorage.Assets` ziehen und per Rechtsklick → **Save to File** als `.rbxm` nach `src/ReplicatedStorage/Assets/` im Repo speichern (sonst löscht Rojo sie beim Sync).

## Neu bauen (Blender-Skripte)
Die Modelle entstehen komplett aus den Skripten in `blender-skripte/` – Maße ändern, Skript neu laufen lassen, fertig:

```
blender -b -P blender-skripte/build_conveyor.py
blender -b -P blender-skripte/build_ore_bin.py
blender -b -P blender-skripte/build_base.py
```

Mit `-- --render` am Ende entstehen zusätzlich Vorschaubilder in `vorschau/`.
