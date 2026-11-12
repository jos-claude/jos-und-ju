# Weltgenerator (Insel 1)

Erzeugt die Welt des Heimatplaneten als **Daten** und baut sie in Roblox Studio mit dem `WorldBuilder` auf. Design-Vorgabe: `../../referenz/welt-design-insel-1.md`. Anleitung für Studio: `../../technik/weltgenerator.md`.

```
worldgen/ (Python)  ──►  src/ServerStorage/WorldBuilder/Data/*.luau  ──►  Studio: WorldBuilder.Build()
        │
        └──────────►  out/preview/ (terrain.bin, scene.json)  ──►  preview/ (three.js)  ──►  Screenshots
```

Eine Quelle, zwei Ausgaben: Was die Vorschau zeigt, baut der WorldBuilder in Studio.

## Benutzen
```bash
python3 generate.py              # Welt erzeugen (Luau + Vorschau), ca. 10-15 s, druckt die Pruefwerte
python3 generate.py --no-luau    # nur Vorschau
python3 generate.py --seed 7     # anderer Seed (Aufbau/Slots bleiben, Details aendern sich)
python3 generate.py --debugmap   # zusaetzlich schnelle Draufsicht out/debug_top.png (PIL)
npm install                      # einmalig (three.js für die Vorschau)
node preview/shoot.js            # alle Kamera-Presets + Karte -> out/shots/*.png (Playwright, SwiftShader, 1600x900)
node preview/shoot.js hero karte # nur bestimmte Bilder
node preview/shoot.js spawn_040_grau  # Graustufen-Kontrolle + Helligkeit je Terrain-Material (.json, Ausgabe im Terminal)
```
Interaktiv: `out/` und `preview/` ueber einen beliebigen statischen Server aus diesem Ordner ausliefern und `preview/index.html` oeffnen (Maus = OrbitControls).

## Module (`worldgen/`)
| Modul | Inhalt |
|---|---|
| `layout.py` | fester Aufbau: Landmarken-Slots L0-L10, 6 Washes, Ringe, Sonne, Wind, Spawn (Seed verschiebt nur in den Toleranzen) |
| `ctx.py`, `fastnoise.py` | Arbeitskontext (Raster, Masken, Merkmal-Listen), schnelles Rauschen (numba: fbm, ridged, Voronoi) |
| `terrain.py` | Ringprofil mit Schichtstufen, Grundrauschen, Washes (mit Nebenarmen/Kiesinseln), Randgebirge, Balkone, Rand/Unterseite, Schwebfelsen, Vorberge |
| `landforms.py` | Tafelberge/Buttes (Stufen auf Bandgrenzen), Felsnadeln, Danxia-Kaemme, Finnen mit Fenstern, Bogen, Hoodoos |
| `waterforms.py` | Teiche, Sinterterrassen, Salzpfannen, Geoden, Krater, Schwemmfaecher (Wasserboeden auf Vielfachen von 4) |
| `fields.py` | Vulkan + Lavazungen, Duenen, Wave, Hochland E, Felsbaenke, Lufteinsprengsel |
| `compose.py` | Reihenfolge und Platzierung aller Landformen (Sichtachsen, Gruppen, Slots) |
| `materials.py` | Bandstapel (13 Baender, >= 8 Studs, `STRATA_BASE` 4 = Korall-Sockel auf Bodenhoehe), Bodenmaterial: Ground (Staub = Mischfarbe), Korall-Flecken (Mud), Sand in Washes/Faechern/Windfahnen (Lee, Az 70), Schutt (Rock) mit zerfasertem Rand, Ring-E-Uebergang; Kanaele S/D/W |
| `ecology.py` | Feuchte F, Mineral M, Schatten S (Vorgabe 5.1) |
| `catalog.py`, `placement.py` | Deko-Vorlagen und Platzierung in Dichte-Inseln. Regeln (Review Stufe 1): matte Materialien (`Plaster`, `Sand`, `Wood`, `Grass`, Gestein, `Glass`, `Neon` nur fuer Lichter), **kein SmoothPlastic**, `Ellipsoid` nur fuer Nebel/Wolken; Kronen als Wolkenform mit dunklerer Unterseite; Moos ist **Terrain** (LeafyGrass/Grass-Flecken), Gras in Hainen kommt von `Terrain.Decoration`; Kiesel im Material des naechsten Felsens (Band in halber Wandhoehe), Brocken-Gruppen (`Boulder`) als mittlere Groesse; Hindernis-Deko nur in Deko-Inseln oder am Fels |
| `checks.py` | Bauzonen je Ring, Flood-Fill, Wasser, Mulden, Plateau |
| `lighting.py`, `cameras.py` | Licht/Atmosphaere-Meta (Sonne Az 250 / El 30 ueber `ClockTime`/`GeographicLatitude`, aus `sky.solve_roblox_sun`), Vorschau-Kameras und Kartendaten |
| `export_luau.py`, `export_preview.py`, `codec.py`, `world.py` | Datenmodell und Ausgabe |

## Datenformat (muss zu `src/ServerStorage/WorldBuilder/init.luau` passen)
**Koordinaten:** Roblox-Welt, Y nach oben. Basis = (0, 0). Azimut 0° = Norden = −Z, 90° = Osten = +X. Das Basis-Plateau liegt auf **y = 0** (Oberkante der alten Baseplate).

**Raster:** `N = 1152` Spalten je Achse, `CELL = 4` Studs (= Roblox-Voxel), Karte von −2304 bis +2304. Spalte `[iz, ix]` hat ihre Mitte bei `x = −2304 + 2 + 4·ix`, `z = −2304 + 2 + 4·iz`.

| Kanal | Typ | Bedeutung |
|---|---|---|
| `H` | Höhe (Studs, auf 1/4 Stud gerundet) | Oberkante des Terrains. `VOID` (−512) = kein Terrain (Weltraum) |
| `M` | u8 | Material-Index in `TERRAIN_MATERIALS` (Bits 0–4). Bit 5 (`STRATA_FLAG` = 32): Spalte zeigt **Gesteinsschichten nach Höhe**. Bei Schicht-Spalten heißt Index 0 „oberste Schicht ist auch Band“, sonst liegt das Material als Deckschicht oben. |
| `W` | u8 | Wasser: 0 = keins, sonst Index (1-basiert) in `water_levels` (Wasseroberfläche in Studs). Wasser füllt von der Terrain-Oberkante bis zu dieser Höhe. |
| `S` | u8 | Versatz der Schichtbänder in Studs (0 … Periode−1). Damit lassen sich Bänder neigen, falten und mit Rauschen ausfransen. |
| `D` | u8 | Fülltiefe unter der Oberkante in 4-Stud-Schritten (siehe `World.finalize_depth`, verhindert Löcher in Steilwänden; für die Unterseite der Plattform größer setzen). |

**Material je Voxel** (Voxelmitte `yc`, Tiefe `d = h − yc`):
- Schicht-Spalte: Deckschicht wenn `topIndex ≠ 0 und d < topDepth`, sonst `bands[floor(yc + S + strata.base) mod Periode]`.
- Normale Spalte: `d < topDepth` → Material aus `M`; `d < subDepth` → `layers.subsoil[Material]` (sonst `bedrock`); tiefer → `layers.bedrock`.
- Belegung (Occupancy) der obersten Voxel: `clamp((h − yUnten) / 4, 0, 1)`.

**Zusatzformen** (`world.terrain_ops`, nach der Höhenkarte ausgeführt, `material = "Air"` schneidet aus):
`{"op": "Ball", "c": [x,y,z], "r": r, "material": m}`, `{"op": "Block", "cf": [12 Zahlen], "size": [x,y,z], ...}`, `{"op": "Cylinder", "cf": [...], "height": h, "r": r, ...}` (Achse = Y), `{"op": "Wedge", "cf": [...], "size": [...], ...}`. `cf` = Roblox-CFrame-Komponenten `x, y, z, R00 … R22`.

**Deko:** `Template(name, category, parts, variants)`; jedes `PartDef` hat Form (`Block`, `Ball` = Kugel mit gleichen Seiten, `Cylinder` = **Achse entlang X** wie in Roblox, `Wedge` = Roblox-Keil, `Ellipsoid` = Block mit Kugel-Mesh), Größe, Lage relativ zum Fußpunkt, Drehmatrix, Farbrolle, Material, Transparenz, Licht. Varianten liefern die Farben je Rolle. `world.place(name, x, y, z, ry, rx, rz, s, variant)` setzt ein Objekt: Drehung wie `CFrame.Angles(0, ry, 0) * CFrame.Angles(rx, 0, rz)`, Maßstab `s` skaliert Größe und Lage aller Teile.

**Meta** (`world.meta`, wird zu `Data/Meta.luau`): `name`, `seed`, `layers`, `strata`, `materialColors`, `water` (Terrain-Wasser-Eigenschaften), `lighting` (`Lighting`, `Atmosphere`, `Bloom`, `ColorCorrection`, `SunRays`, `DepthOfField`, `Sky` → jeweils Eigenschaften), `sun` (`azimuth`, `elevation`, `direction` = Einheitsvektor zur Sonne, zum Pruefen mit `Lighting:GetSunDirection()`), `spawn`, `terrain` (`Decoration = true`, `GrassLength`: Wunsch an den Builder, `workspace.Terrain.Decoration`/`GrassLength` zu setzen - animiertes Gras auf `Grass`), `grid.surfaceOffset` (Builder senkt Hoehen/Wasser um diesen Wert, siehe export_luau). Farben als `RGB("#RRGGBB")`, Enums als `Enum("Technology", "ShadowMap")`.

**Erweiterungen der Deko-Daten** (der Builder ignoriert unbekannte Felder; was er dafuer tun soll, steht dabei):
- `PartDef.particles` (in `Templates.luau` als `particles = {...}` am Teil): Wunsch nach einem **ParticleEmitter** an diesem Teil, z. B. Dampf `{kind="steam", rate, lifetime={min,max}, size={start,end}, speed={min,max}, spread, color="#RRGGBB", transparency={start,end}, pulse={min,max}}` (`pulse` = alle 25-40 s kurz staerker). Benutzt von `SteamVent_*` (`kind="steam"`) und `MistEmitter` (`kind="mist"`, ruhige Nebel-Partikel in den Nebelbecken, unsichtbares Traegerteil).
- Vorlagen `Boulder_*` (Kategorie `Rock`, 2-3 gedrehte Bloecke/Keile aus `Rock`) und `Pebble_<Material>_*` (Kugel/Keil/Block im Material des Bands: `Sandstone`, `Limestone`, `Slate`, `Mud`, `Rock`; Farbe = Bandfarbe 12 % dunkler, 15 % entsaettigt).
- Vorlagen `Mist_*` (Kategorie `Mist`): Bodennebel-Schwaden aus 2-3 flachen Ellipsoiden (Hoehe <= 0,15 x Breite, Transparenz 0,88-0,94, ohne Schatten/Kollision), 2-8 Studs ueber Mulden, Teichen, Salzpfannen, Terrassen, Oasen, Nebelbecken und am Fuss des Randgebirges; nie auf dem Plateau (r < 150) oder in Washes.
- Vorlage `EdgeBarrier` (Kategorie `Barrier`): unsichtbare Wand (Transparency 1, CanCollide true), 64 Stueck im Ring r 2008, Hoehe -60 bis 700. Funktioniert mit dem bestehenden Builder.
- Kategorien der Vorlagen: `Flora`, `Crystal`, `Rock`, `Feature`, `Landmark`, `Sky` (Wolken unter der Plattform, Nebelkugeln), `Mist` (Bodennebel), `Barrier`. Fuer Streaming sollen die Modelle in Chunk-Modelle je 200 x 200 Studs (nach x/z der Platzierung) sortiert werden.

**Budgets** (der Generator warnt bei Ueberschreitung): hoechstens 25 000 Teile (Handys), <= 120 PointLights, Terrain-Daten < 3 MB Base64. Terrain-Zusatzformen nicht duenner als Durchmesser 8 (Radius >= 4, Block-Kante >= 8), sonst werden sie bei 4-Stud-Voxeln klumpig oder verschwinden; der Generator meldet zu duenne Formen.

**Bauzonen** (`Data/BuildZones.luau`, fuer den Erz-Spawn):
```lua
return { cell = 16, n = 288, origin = -2304, maxRadius = 1900, rows = { "0001110...", ... } }
```
`rows[iz]` ist eine Zeichenkette mit `n` Zeichen; Zeichen `ix` (1-basiert) = `"1"`: die ganze 16x16-Zelle ist Bauzone (Neigung <= 6 Grad, keine Landform, keine Hindernis-Deko, kein Wasser > 0,5, zusammenhaengende Flecken >= 40x40 Studs, per Neigung <= 25 Grad von der Basis erreichbar, r <= 1900). Zellmitte: `x = origin + (ix - 0.5) * cell`, `z = origin + (iz - 0.5) * cell`; die Hoehe per Raycast holen.

**Vorschau** (`out/preview/scene.json`): zusaetzlich `preview.cameras` (Kamera-Presets) und `preview.map` (Ringe, Washes, Landmarken fuer die Karte). Die Vorschau rendert das Terrain nach derselben Voxel-Regel wie der Builder (inkl. weicher Materialmischung zwischen Nachbar-Voxeln), Zusatzformen als Koerper (Luft-Formen als Ausschnitt), Deko mit echten Formen, Neon + Bloom, Licht nach `meta.lighting`, Dunst nach Atmosphere. Der orange Block in der Mitte ist nur der Platzhalter der Start-Halle (nicht in den Luau-Daten).

**Vorschau ehrlich halten** (Review 2f): Roblox-Materialien sind Textur x Farbe, die Textur dunkelt ab. `preview/main.js` multipliziert deshalb jede Farbe mit einem **Albedo-Faktor je Material** (`ALBEDO`, linear). Ground ist gemessen (Studio-Screenshot 2026-11-12: `#F2A07C` wurde zu ~`#BB6B4A`, Faktor ~0,56/0,55/0,49), alle anderen Faktoren sind **Schaetzungen** und muessen mit Studio-Screenshots nachkalibriert werden. Dazu kommt eine feine Koernung (`GRAIN`) auf Terrain und matten Teilen (nur in der Naehe). Glanz hat nur `SmoothPlastic`/`Plastic`; `Ellipsoid`-Teile (SpecialMesh) werden ohne Textur gezeigt, wie in Roblox. `node preview/shoot.js spawn_040_grau` rendert die Graustufen-Kontrolle und misst ueber ein Material-ID-Bild die mittlere Helligkeit je Terrain-Material (Ziel: Boden und Fels hoechstens 0,10 auseinander).
