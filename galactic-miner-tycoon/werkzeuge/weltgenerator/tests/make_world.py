"""Synthetische Test-Welt fuer den WorldBuilder-Test (unabhaengig von generate.py / island1.py).

Die Welt ist fast ueberall VOID (schnell). Nur ausgewaehlte 16x16-Bloecke enthalten Terrain:
handgebaute Grenzfaelle plus ein paar Zufallsbloecke (Fuzz, feste Seeds).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from worldgen.world import (  # noqa: E402
    MAT, N, RGB, STRATA_FLAG, VOID, Enum, PartDef, Template, World, angles, rot_x, rot_y, rot_z,
)

G, SAND, ROCK, SNOW = MAT["Grass"], MAT["Sand"], MAT["Rock"], MAT["Snow"]
BLOCK = 16

LAYERS = {"topDepth": 6, "subDepth": 14, "bedrock": "Basalt",
          "subsoil": {"Grass": "Ground", "Sand": "Sandstone", "Snow": "Ice"}}
STRATA = {"base": 17, "bands": [["Sandstone", 60], ["Limestone", 20], ["Slate", 60], ["Basalt", 40], ["Sand", 60]]}
WATER_LEVELS = [10.5, 8.0, -20.0, 0.1, 100.25]


def put(w: World, ix, iz, h, mat=G, d=3, water=0, s=0, strata=False):
    w.h[iz, ix] = h
    w.mat[iz, ix] = (STRATA_FLAG | mat) if strata else mat
    w.depth[iz, ix] = d
    w.water[iz, ix] = water
    w.strata_off[iz, ix] = s


def fuzz_block(w: World, bx, bz, seed, density=1.0, water=True, strata=True):
    rng = np.random.default_rng(seed)
    for iz in range(bz * BLOCK, bz * BLOCK + BLOCK):
        for ix in range(bx * BLOCK, bx * BLOCK + BLOCK):
            if rng.random() > density:
                continue
            h = float(np.round(rng.uniform(-25, 40) * 4) / 4)
            mat = int(rng.integers(1, 22))
            st = strata and rng.random() < 0.3
            wl = int(rng.integers(0, 6)) if water and rng.random() < 0.4 else 0
            put(w, ix, iz, h, mat, int(rng.integers(1, 9)), wl, int(rng.integers(0, 240)), st)


def build_world() -> World:
    w = World(seed=42)
    for l in WATER_LEVELS:
        w.add_water_level(l)

    # --- Block (0,0): Ecke der Karte, Materialien, Klippen, Viertel-Studs, D=0, negative Hoehen ---
    for i in range(1, 16):                                   # Material 1..15, Reihe 0 (Zeile iz=0 -> Vorhersage Zeile 0)
        put(w, i - 1, 0, 5.25, i)
    for i in range(16, 22):                                  # Material 16..21
        put(w, i - 16, 1, -3.5, i)
    for iz in range(2, 6):                                   # Plateau mit Viertel-Studs
        for ix in range(16):
            put(w, ix, iz, [0, 0.25, 0.5, 0.75, 1.0, 3.25, 3.75, 4.0][(ix + iz) % 8])
    for iz in range(6, 10):                                  # Klippe 60.25 neben Plateau 0
        for ix in range(8):
            put(w, ix, iz, 60.25, ROCK, 20)
    put(w, 12, 7, 47.75, SNOW, 2)                            # Spitze, VOID drumherum
    put(w, 10, 10, 1.5, G, 0)                                # D=0, Teil-Voxel
    put(w, 11, 10, 4.0, G, 0)                                # D=0, genau auf Voxelgrenze -> nichts
    put(w, 12, 10, 3.9, G, 0)                                # 3.9 -> auf 3.75 gerundet
    put(w, 13, 10, 7.3, 0, 3)                                # Material-Index 0 (Air) ohne Schicht -> Luft
    put(w, 14, 10, 7.4, G, 3)                                # 7.4 -> 7.5
    for k, h in enumerate([-37.25, -0.25, -4.0, -3.75, -511.9, -9.5]):   # negative Hoehen (-511.9 -> q=1)
        put(w, k, 12, h, SAND, 4)

    # --- Block (1,0): Klippe ueber die Blockgrenze ix=15/16, Zufall ---
    for iz in range(0, 6):
        put(w, 15, iz, 40.0, ROCK, 12)
        put(w, 16, iz, -12.0, G, 4)
    fuzz_block(w, 1, 0, 2, density=0.6)
    fuzz_block(w, 2, 0, 3, density=1.0)
    fuzz_block(w, 0, 1, 4, density=1.0)

    # --- Block (30,40): groesste Hoehe, Block (31,40): kleinste Hoehe ---
    put(w, 30 * 16 + 3, 40 * 16 + 3, 15871.75, G, 255)       # q = 65535
    put(w, 31 * 16 + 3, 40 * 16 + 3, -511.75, SAND, 1)       # q = 1
    put(w, 31 * 16 + 4, 40 * 16 + 3, -511.75, SAND, 1, water=3)  # Wasser -20 ueber der Spalte (Wasser liegt ueber Terrain)

    # --- Block (50,10): Schichten ---
    bz0, bx0 = 10 * 16, 50 * 16
    cases = [  # (h, mat, strata, S, D)
        (0.0, 0, True, 0, 100), (100.75, 0, True, 1, 100), (-250.25, 0, True, 59, 100), (333.5, 0, True, 60, 100),
        (-100.0, 0, True, 95, 100), (12.0, 0, True, 119, 100), (-7.0, 0, True, 200, 100), (50.0, 0, True, 239, 100),
        (0.0, G, True, 0, 100), (100.75, SAND, True, 33, 100), (-250.25, ROCK, True, 150, 100), (30.0, SNOW, True, 239, 100),
        (6.0, G, True, 0, 100), (5.75, G, True, 0, 100), (6.25, G, True, 0, 100), (-1.0, SAND, True, 10, 3),
    ]
    for k, (h, m, st, s, d) in enumerate(cases):
        put(w, bx0 + k, bz0 + 2, h, m, d, 0, s, st)
    for k, (h, m, st, s, d) in enumerate(cases):             # dieselben ohne Schicht-Flag (Unterboden/Grundgestein)
        put(w, bx0 + k, bz0 + 4, h, m if m else G, d, 0, s, False)

    # --- Block (60,20): Wasser ueber Land ---
    bz0, bx0 = 20 * 16, 60 * 16
    wc = [  # (h, wasserindex)
        (3.0, 1), (10.5, 1), (10.75, 1), (12.0, 1), (8.0, 2), (7.75, 2), (-30.0, 3), (-20.0, 3), (0.0, 4), (0.05, 4),
        (-5.0, 5), (100.0, 5), (99.0, 5), (-100.0, 1), (1.0, 4), (9.0, 1),
    ]
    for k, (h, wi) in enumerate(wc):
        put(w, bx0 + k, bz0 + 1, h, SAND, 6, wi)
    for k in range(16):                                      # mit Schicht-Spalten und tiefem Boden
        put(w, bx0 + k, bz0 + 3, float(k) - 8, G, 30, 1, 5 * k, k % 2 == 0)

    # --- Block (40,40): Wasser ueber VOID, ganz allein im Block ---
    w.water[40 * 16 + 5, 40 * 16 + 5] = 1
    # --- Block (41,40): Wasser ueber VOID neben Land ---
    for k in range(4):
        put(w, 41 * 16 + k, 40 * 16 + 8, 6.0, G, 3)
    w.water[40 * 16 + 8, 41 * 16 + 7] = 5       # Stand 100.25 ueber der hoechsten Landspalte
    w.water[40 * 16 + 9, 41 * 16 + 7] = 3       # Stand -20 unter dem Land
    w.water[40 * 16 + 10, 41 * 16 + 7] = 1      # Stand 10.5

    # --- RLE: lange Laeufe (mehr als 127, Werte > 127), nur in VOID-Spalten ---
    w.strata_off[700, 100:500] = 200
    w.mat[701, 0:600] = STRATA_FLAG | 21
    w.depth[703, :] = 250

    # --- Ecke unten rechts (letzter Block, letzte Spalte) ---
    put(w, N - 1, N - 1, 2.0, G, 3)
    put(w, N - 2, N - 1, 2.25, ROCK, 3)
    put(w, N - 1, N - 2, -2.25, ROCK, 3)
    fuzz_block(w, 71, 71, 5, density=0.5)

    # --- Zusatzformen (inkl. Air-Schnitt, unbekannte Operation) ---
    rz = angles(0.3, 0.5, -0.2)
    cf = [12.5, -3.0, 8.25] + [round(float(v), 5) for v in rz.ravel()]
    ident = [100.0, 20.0, -40.0] + [1, 0, 0, 0, 1, 0, 0, 0, 1]
    w.terrain_ops = [
        {"op": "Ball", "c": [10.5, -3.0, 200.0], "r": 12.0, "material": "Rock"},
        {"op": "Ball", "c": [0.0, 0.0, 0.0], "r": 6.5, "material": "Air"},
        {"op": "Block", "cf": cf, "size": [20.0, 8.0, 12.5], "material": "Basalt"},
        {"op": "Block", "cf": ident, "size": [4.0, 4.0, 4.0], "material": "Air"},
        {"op": "Cylinder", "cf": [0.0, 50.0, 0.0] + [round(float(v), 5) for v in angles(0, 1.0, 0.5).ravel()], "height": 30.0, "r": 7.0, "material": "Sandstone"},
        {"op": "Wedge", "cf": cf, "size": [6.0, 6.0, 10.0], "material": "Ice"},
        {"op": "Wedge", "cf": ident, "size": [6.0, 6.0, 10.0], "material": "Air"},
        {"op": "Teapot", "c": [0, 0, 0], "material": "Rock"},   # unbekannt: wird uebersprungen
        {"op": "Ball", "c": [-5.0, -0.5, 3.0], "r": 0.5, "material": "Mud"},
    ]

    # --- Meta ---
    w.meta.update({
        "surfaceOffset": 0.0,  # Referenz rechnet ohne Roblox-Oberflaechenversatz
        "name": "Testwelt", "seed": 42, "layers": LAYERS, "strata": STRATA,
        "materialColors": {"Grass": RGB("#44AA33"), "Sand": RGB(200, 180, 120), "Rock": RGB("#777788")},
        "water": {"WaterColor": RGB("#3399CC"), "WaterTransparency": 0.9, "WaterWaveSize": 0.1, "WaterReflectance": 0.5, "WaterWaveSpeed": 8, "Decoration": False},
        "lighting": {
            "Lighting": {"ClockTime": 14.5, "Brightness": 3, "Technology": Enum("Technology", "Future"), "Ambient": RGB("#202040"),
                         "OutdoorAmbient": RGB(100, 110, 120), "GlobalShadows": True, "FogEnd": 4000, "ExposureCompensation": -0.25},
            "Atmosphere": {"Density": 0.3, "Color": RGB("#BBCCFF"), "Haze": 1.2, "Glare": 0.4},
            "Bloom": {"Intensity": 0.4, "Size": 24, "Threshold": 0.9},
            "ColorCorrection": {"Saturation": 0.1, "Contrast": 0.05, "TintColor": RGB("#FFEEDD")},
            "SunRays": {"Intensity": 0.2, "Spread": 0.8},
            "DepthOfField": {"FarIntensity": 0.2, "FocusDistance": 120, "InFocusRadius": 50, "NearIntensity": 0},
            "Sky": {"StarCount": 3000, "CelestialBodiesShown": True},
        },
        "spawn": [12.5, 3.25, -40.0],
    })

    # --- Vorlagen ---
    def pd(shape, size, pos=(0, 0, 0), rot=None, role="main", material="SmoothPlastic", **kw):
        return PartDef(shape, size, pos, np.eye(3) if rot is None else rot, role, material, **kw)

    w.add_template(Template("AllShapes", "Props", [
        pd("Block", (2, 3, 4), (0, 1.5, 0), role="main", material="Rock"),
        pd("Ball", (3, 3, 3), (1, 4, 0), role="accent", material="Glass", transparency=0.3, reflectance=0.1),
        pd("Cylinder", (6, 2, 2), (0, 1, 3), rot=rot_y(0.5), role="main", cast_shadow=False),
        pd("Wedge", (2, 2, 2), (-1, 0, -2), rot=rot_z(np.pi / 2), role="accent", collide=True),
        pd("Ellipsoid", (4, 2, 3), (0, 5, 1), rot=angles(0.2, -0.4, 0.1), role="glow", material="Neon",
           light={"range": 40, "brightness": 2, "role": "glow"}),
        pd("Block", (1, 1, 1), (3, 0.5, 3), role="nosuchrole"),                       # Rolle fehlt in Variante -> Magenta
        pd("Block", (0.5, 0.5, 0.5), (3, 2, 3), role="accent", light={"range": 12, "brightness": 1}),   # Licht ohne Rolle
        pd("Ball", (1, 1, 1), (3, 3, 3), role="main", light={"range": 20, "brightness": 1, "color": RGB(255, 0, 0)}),  # Licht mit "color"
    ], [
        {"main": RGB("#808080"), "accent": RGB(10, 200, 30), "glow": RGB("#FFCC00")},
        {"main": RGB("#201020"), "accent": RGB(250, 20, 30), "glow": RGB("#00CCFF")},
    ]))
    w.add_template(Template("Tree", "Flora", [
        pd("Cylinder", (8, 1.5, 1.5), (0, 4, 0), rot=rot_z(np.pi / 2), role="trunk", material="Wood"),
        pd("Ball", (6, 6, 6), (0, 9, 0), role="leaf", material="Grass"),
    ], [{"trunk": RGB("#553311"), "leaf": RGB("#22AA44")}, {"trunk": RGB("#442200"), "leaf": RGB("#DD9922")}, {"trunk": RGB("#111111"), "leaf": RGB("#FFFFFF")}]))
    w.add_template(Template("Pebble", "Props", [pd("Block", (1, 0.4, 0.8), (0, 0.2, 0), role="main", material="Slate")],
                            [{"main": RGB("#999999")}]))

    # --- Platzierungen ---
    w.place("AllShapes", 12.5, 3.25, -40.0)
    w.place("AllShapes", -100.75, -12.0, 250.5, ry=1.2, rx=0.3, rz=-0.7, s=2.5, variant=1)
    w.place("AllShapes", 55.0, 0.0, 55.0, ry=3.142, rx=-1.571, rz=0.0, s=0.5, variant=0)
    w.place("AllShapes", 5.0, 5.0, 5.0, ry=0.0, rx=0.0, rz=0.0, s=1.0, variant=7)         # Variante ausserhalb -> Variante 1
    w.place("Tree", 1000.5, 20.25, -999.75, ry=-2.5, s=1.75, variant=2)
    w.place("Tree", -2300.0, 0.0, 2300.0, ry=0.123, rx=0.1, rz=0.2, s=1.0, variant=0)
    w.place("Ghost", 1, 2, 3)                                                              # unbekannte Vorlage
    w.place("Pebble", 0.0, 0.0, 0.0)
    rng = np.random.default_rng(99)
    for i in range(3300):                                                                  # viele Objekte -> mehrere Platzierungs-Module
        w.place("Pebble", round(float(rng.uniform(-2000, 2000)), 2), round(float(rng.uniform(-10, 100)), 2),
                round(float(rng.uniform(-2000, 2000)), 2), round(float(rng.uniform(-3.14, 3.14)), 3),
                round(float(rng.uniform(-1.5, 1.5)), 3), round(float(rng.uniform(-1.5, 1.5)), 3),
                round(float(rng.uniform(0.3, 3)), 3), 0)
    w.place("AllShapes", 77.0, 1.0, 77.0, ry=0.5)                                          # nach den Pebbles: Gruppenreihenfolge
    return w
