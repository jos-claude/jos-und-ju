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
python3 generate.py              # Welt erzeugen (Luau + Vorschau)
python3 generate.py --no-luau    # nur Vorschau
npm install                      # einmalig (three.js für die Vorschau)
```

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

**Meta** (`world.meta`, wird zu `Data/Meta.luau`): `name`, `seed`, `layers`, `strata`, `materialColors`, `water` (Terrain-Wasser-Eigenschaften), `lighting` (`Lighting`, `Atmosphere`, `Bloom`, `ColorCorrection`, `SunRays`, `DepthOfField`, `Sky` → jeweils Eigenschaften), `spawn`. Farben als `RGB("#RRGGBB")`, Enums als `Enum("Technology", "ShadowMap")`.
