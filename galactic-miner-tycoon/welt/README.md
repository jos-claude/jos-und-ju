# Welt Insel 1 – Einzel-Skript `BuildIsland1.luau`

- **Status:** Vorschlag. Die Welt ist gebaut und in Studio getestet, das Design ist noch nicht von Jos/Ju abgestimmt.
- **Branch:** `claude/laughing-brahmagupta-uhrczr` (Weltgenerator, Builder, Himmel). Ein Zwischenstand liegt schon auf `main`.
- **Erzeugt von:** `werkzeuge/weltgenerator/` (`python3 generate.py` → `python3 bundle.py`). **Nicht von Hand ändern**, außer den Skybox-IDs im Einstellungs-Block.

`BuildIsland1.luau` ist der WorldBuilder (`src/ServerStorage/WorldBuilder`) mit allen Daten in **einer Datei** (ca. 2,3 MB). Er baut dasselbe wie der Rojo-Weg in `../technik/weltgenerator.md`.

## Benutzen (Studio, Edit-Modus)
1. Datei als **ModuleScript** nach `ServerStorage` legen und `BuildIsland1` nennen. Für die Befehlsleiste ist sie zu groß.
2. In der Befehlsleiste (frische Kopie, damit kein alter `require`-Stand benutzt wird):
   ```lua
   local c = game.ServerStorage.BuildIsland1:Clone(); c.Parent = game.ServerStorage; require(c).Build(); c:Destroy()
   ```
   Wird der Code ohne `script` ausgeführt (z. B. per `loadstring`), baut er sofort.
3. Dauert ca. 6 s. Danach den Place speichern. `Lighting.Technology` einmal von Hand setzen (z. B. ShadowMap), Skripte dürfen das nicht. Falls kein Gras wächst: `Workspace.Terrain.Decoration` einschalten.

Mehrfach ausführen ist ungefährlich (idempotent):

| Was | Wohin |
|---|---|
| Gelände | `Workspace.Terrain` (wird vorher gelöscht und neu geschrieben) |
| Deko (Felsen, Pflanzen, Kristalle, Nebel, Randwand) | `Workspace.Island1/<Kategorie>/Chunk_x_z` (alter Ordner wird gelöscht) |
| Licht, Atmosphere, Bloom, Farbkorrektur, Sonnenstrahlen, Sky | `Lighting` (eigene `World*`-Effekte werden ersetzt, fremde nach `ServerStorage.WorldBuilderBackup` verschoben) |
| Baseplate | bleibt, wird nur **ausgeblendet** (Transparency 1, keine Kollision) |
| SpawnLocation | wird auf den Spawn gesetzt |

## Maße
- Spielfläche: Kreis mit **Radius 2000 Studs** um (0, 0). Erze bis r 1900, dahinter das Randgebirge.
- Terrain-Raster: −2304 … +2304 in X und Z, 4-Stud-Voxel.
- **Basis-Plateau:** Oberfläche auf **y ≈ 0**, flach und hindernisfrei bis r 150.
- **Spawn:** (0, 0.6, 20), Blick Richtung Nordosten (Azimut 40°: Saturn-Tor, Vulkan, Saturn).
- Die Start-Halle von Ju liegt bei x ≈ 0, z 30–58 und bleibt frei.
- Höhen: Ebenen −30 bis +60, Tafelberge bis ca. 140, Regenbogen-Kämme bis ca. 210, Randgebirge bis ca. 320.
- Ringe (passend zu den Erzen): A Pfirsichebene 0–250, B Tafelberge und Felsnadeln 250–600, C Lava/Dünen 600–1100, D Regenbogenland 1100–1600, E Silberhochland 1600–2000.
- Umfang: ca. 12 Mio. Terrain-Zellen, ca. 1 000 Terrain-Zusatzformen, ca. 22 350 Deko-Teile, 44 PointLights, nur 66 durchsichtige Glas-Teile (Handy-freundlich).
- Bauzonen (eben, frei, erreichbar) für den Erz-Spawn: `WorldBuilder.IsBuildZone(x, z)` und `WorldBuilder.GetBuildZoneCells(minR, maxR)`.

## Farben (Terrain-Materialien, eine gemeinsame Geologie)
Nach der Review `../referenz/welt-review-insel-1.md`: Boden, Schutt, Sand und Felsbänder stammen sichtbar aus denselben Gesteinen. Der Boden ist ihre Mischfarbe, die Berge wachsen aus einem Korall-Sockel. Die Gesteinsbänder sind 13 Bänder in 4 warmen Farbfamilien (ohne Mint und Weiß).

| Material | Verwendung | Farbe |
|---|---|---|
| Ground | Hauptboden | #F8B68C |
| Sand | Flussbetten, Dünen, Fächer, Windfahnen | #F7D5A6 |
| Mud | Korall-Sockel der Berge, Bodenflecken | #EC8E74 |
| Rock | Schutthalden | #CDA49E |
| Sandstone / Limestone / Slate | Gesteinsbänder (Rosa, Butter, Mauve) | #EEA0A2 / #F1CF94 / #D2AACE |
| Salt / Concrete | Sinterterrassen, Geoden | #F8ECE2 / #B2E0D0 |
| Basalt / CrackedLava | Lavaströme am Vulkan | #4A3D50 / #FFB07A |
| Grass / LeafyGrass | Wiesen und Moos (animiertes Terrain-Gras) | #B2D08E / #86C2A6 |
| Snow / Ice / Glacier | Ring E und Gipfel | #F6F0F2 / #CFE6EE / #A9D8E8 |
| Wasser | Teiche, Terrassen | #5FE3D6 (Transparenz 0,35) |

Deko: kein SmoothPlastic mehr. Kronen sind matt und wolkig mit kühlerer Unterseite, die Stämme aus dunklem Holz. Kristalle aus Glas, nur die Riesen-Kristalle sind durchsichtig. Kiesel und Brocken bekommen Material und Farbe des Felses, von dem sie stammen.

Licht: goldene Stunde mit Sonne auf Azimut 250°, Höhe 30° (ClockTime 15,8956, GeographicLatitude 40,73), passend zur Skybox. Leichter Dunst in Staubfarbe (Atmosphere Density 0,28, Haze 1,5, Farbe #F2BFA6) plus flacher Bodennebel in Mulden und Becken.

## Himmel
Die 6 Skybox-Bilder liegen in `../assets/himmel/`. Hochladen und die IDs im Block `MODULES["Settings"]` ganz oben in `BuildIsland1.luau` eintragen (bzw. in `src/ServerStorage/WorldBuilder/Settings.luau`), dann `Build({ terrain = false, props = false })`. Schritte: `../assets/himmel/README.md`.

## Mehr
- Design-Vorgabe: `../referenz/welt-design-insel-1.md`
- Technik und Rojo-Weg: `../technik/weltgenerator.md`
- Einzelne Deko-Modelle zum Wiederverwenden: `../assets/modelle/umwelt/*.rbxm`
- Vorschau-Bilder: `../referenz/bilder/welt/vorschau-insel-1/`
