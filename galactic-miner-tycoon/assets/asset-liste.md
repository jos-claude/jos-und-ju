# Asset-Liste

| Name | Art | Datei | Roblox-ID | Quelle | Gebaut von | Status |
|---|---|---|---|---|---|---|
| Eisen-Bohrer (`drill_iron`) | Modell (15 Teile, ca. 2.100 Dreiecke) | `modelle/drill_iron.blend`, `modelle/drill_iron.fbx` | – | selbst (Blender, nach `referenz/bilder/gebaeude/bohrer-01.jpg`) | Ju (mit Claude) | in Studio importiert, liegt in `ServerStorage.GMT_Models.drill_iron` (14.11.); das Spiel nutzt es für jeden aufgestellten Bohrer |
| Förderband gerade (`ConveyorStraight`) | Modell (7 Teile, ca. 2.500 Dreiecke) | `modelle/conveyor_straight.fbx/.glb`, `modelle/conveyor.blend` | – | selbst (Blender, nach `referenz/bilder/gebaeude/foerderband-01.jpg`) | Jos (mit Claude) | v3 fertig, Import in Studio offen |
| Förderband-Segment 4 Studs (`ConveyorSegment`, `belt_segment`) | Modell (6 Teile, ca. 600 Dreiecke) | `modelle/conveyor_segment.glb/.fbx` | – | selbst (Blender) | Jos (mit Claude) | v3 fertig, Import in Studio offen |
| Förderband-Kurve rechts/links (`ConveyorCurve`, `ConveyorCurveLeft`) | Modell (6 Teile, ca. 2.500 Dreiecke) | `modelle/conveyor_curve.glb/.fbx`, `modelle/conveyor_curve_left.glb/.fbx` | – | selbst (Blender) | Jos (mit Claude) | v3 fertig, Import in Studio offen |
| Förderband-Ende mit Trichter (`ConveyorEnd`) | Modell (8 Teile, ca. 2.400 Dreiecke) | `modelle/conveyor_end.glb/.fbx` | – | selbst (Blender) | Jos (mit Claude) | v3 fertig, Import in Studio offen |
| Erzbrocken Eisen (`OreChunkA/B/C`) | Modell (je 1 Teil, 20 Dreiecke) | `modelle/ore_chunk.glb/.fbx` | – | selbst (Blender) | Jos (mit Claude) | v3 fertig, Import in Studio offen |
| Lager-Kasten (`OreBin`, `bin_*`) | Modell (21 Teile, ca. 9.000 Dreiecke, Deckel/Erzhaufen/Anzeige getrennt) | `modelle/ore_bin.glb/.fbx`, `modelle/ore_bin.blend` | – | selbst (Blender, nach `referenz/bilder/gebaeude/lager-kasten-01.jpg`) | Jos (mit Claude) | v3 fertig, Import in Studio offen |
| Start-Halle (`BaseHall`) | Modell (11 Teile, ca. 4.000 Dreiecke, Tür getrennt) | `modelle/base_hall.fbx/.glb`, `modelle/base.blend` | – | selbst (Blender, nach `referenz/bilder/gebaeude/basis-01.jpg`) | Jos (mit Claude) | v3 fertig, Import in Studio offen |
| Gesperrter Raum (`BaseRoom`) | Modell (11 Teile, ca. 2.200 Dreiecke, Rolltor getrennt) | `modelle/base_room.fbx/.glb` | – | selbst (Blender) | Jos (mit Claude) | v3 fertig, Import in Studio offen |
| Skybox Insel 1 (`sky_Bk/Dn/Ft/Lf/Rt/Up`) | 6 Bilder 1024² | `himmel/sky_*.png` | – (Upload offen, IDs in `src/ServerStorage/WorldBuilder/Settings.luau`) | selbst (Python, `werkzeuge/weltgenerator/render_sky.py`) | Jos (mit Claude) | fertig, Upload in Studio offen |
| Umwelt-Deko Insel 1 (`BalloonTree`, `Crystal*`, `Boulder`, `Noodle`, `Mushroom`, `OrganPipe`, `Lantern`, `Mist` u. a.) | 97 Modelle aus Roblox-Parts (je 1–13 Teile, mehrere Farbvarianten, matte Materialien) | `modelle/umwelt/*.rbxm` | – (reine Parts, kein Upload nötig) | selbst (Generator `werkzeuge/weltgenerator`, nach `referenz/bilder/welt/heimatplanet-02-orange.jpg`) | Jos (mit Claude) | fertig, werden vom WorldBuilder gebaut; einzeln per „Insert from File…“ nutzbar |
| Spitzhacke, 5 Stufen (`PickaxeRust`, `PickaxeIron`, `PickaxeSteel`, `PickaxeCrystal`, `PickaxeTitan`) | Modell (je ca. 10–14 Teile, höchstens 1.500 Dreiecke) | Bauplan: `modelle/bauplaene/spitzhacke.md` | – | selbst (Blender-Skript, geplant `build_pickaxe.py`) | Jos (mit Claude) | Bauplan (Vorschlag), Blender-Bau offen |
| Schmiede-Einrichtung (`ForgeAnvilStation`, `ForgeBackpackBench`, `ForgeTeleporter`, `ForgeFurnace` + Deko) | 9 Modelle, zusammen höchstens ca. 16.000 Dreiecke | Bauplan: `modelle/bauplaene/schmiede-einrichtung.md` | – | selbst (Blender-Skript, geplant `build_forge.py`) | Jos (mit Claude) | Bauplan (Vorschlag), Blender-Bau offen |

## Roblox-Asset-IDs der importierten Modelle (13.11.2026)
Hochgeladen von Claude (Ju) über Open Cloud auf das Konto des Place-Besitzers (Ju). In Studio liegen die Modelle in `ServerStorage.GMT_Models`. Hochgeladene Modelle lassen sich über Open Cloud nicht löschen, nur im Creator Dashboard.

| Modell | Asset-ID |
|---|---|
| ConveyorSegment | 116413465941420 |
| ConveyorStraight | 79562193567287 |
| ConveyorCurve | 134336095953676 |
| ConveyorCurveLeft | 89114707761972 |
| ConveyorEnd | 116431496040310 |
| OreChunkA/B/C (zusammen) | 126940783580041 |
| OreBin | 83143021088022 |
| BaseHall | 113729453111097 |
| BaseRoom | 103778311952310 |
