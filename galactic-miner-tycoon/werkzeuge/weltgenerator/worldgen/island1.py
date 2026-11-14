"""Insel 1 (Heimatplanet) nach referenz/welt-design-insel-1.md.

Ablauf: Grundgelaende -> Washes -> Landmarken/Becken/Felder/Berge -> Hochland + Rand -> Materialien
-> Pruefungen (Bauzonen, Flood-Fill, Wasser) -> Deko (Oekologie-Karten, Inseln) -> Licht/Meta.
"""
from __future__ import annotations

import time

import numpy as np

from . import cameras, checks, compose, ecology, fields, lighting, materials, placement, terrain
from .ctx import Ctx
from .layout import BUILD_MAX_R, PLATEAU_R, STRATA_BASE, SUN_AZ, SUN_EL, sr
from .world import HALF, RGB, World

SEED = 1


def build_zone_raster(c, build, cell=16):
    """Bauzonen als grobes Raster fuer den Erz-Spawn: eine 16x16-Zelle zaehlt, wenn alle 4x4-Spalten Bauzone sind.
    Ring E nur bis BUILD_MAX_R (Runde 2: r 950; Randgebirge ist Grenze)."""
    k = int(cell // 4)
    n = build.shape[0] // k
    b = build[: n * k, : n * k].reshape(n, k, n, k).all(axis=(1, 3))
    xs = -HALF + cell / 2 + cell * np.arange(n)
    X, Z = np.meshgrid(xs, xs)
    b &= np.hypot(X, Z) <= BUILD_MAX_R
    return {"cell": cell, "n": n, "origin": -HALF, "maxRadius": BUILD_MAX_R, "mask": b}


def build(seed: int = SEED, verbose: bool = True, deco: bool = True) -> World:
    t0 = time.time()

    def log(msg):
        if verbose:
            print(f"  [{time.time() - t0:5.1f} s] {msg}")

    c = Ctx(seed)
    terrain.base_terrain(c)
    log("Grundgelaende")
    counts = compose.build_landforms(c)
    log(f"Landformen {counts}")
    # Runde 2: Felsbaenke um das Plateau (r 130-170) (Radien x 0,5)
    zoneA = (c.rw > PLATEAU_R + 14) & (c.rw < PLATEAU_R + 55) & ~c.mask("claimed") & (c.wash_dist > 5)
    c.stage("outcrops")
    fields.outcrops(c, zoneA, 0.03, (2.0, 4.0), "outA")
    # Runde 3: Felsbaenke in Ring B und D aus (Anteil 0,02 -> 0): Ausgleich fuer die vielen kleinen Tafelberge
    c.stage("low_floating_stones")
    fields.low_floating_stones(c, 20)
    c.stage("foothills")
    terrain.foothills(c, 12)
    c.stage("rim")
    terrain.rim(c)
    c.stage("floating_rocks")
    terrain.floating_rocks(c)
    log("Rand, Balkone, Schwebfelsen")
    from .landforms import check_ops
    thin = check_ops(c.ops)
    c.thin_ops = thin
    if thin:
        print(f"  WARNUNG: {len(thin)} Zusatzformen duenner als Durchmesser 8 (werden in Roblox klumpig): "
              + ", ".join(sorted({o['op'] + '/' + o['material'] for o in thin})))
    c.stage("materials")
    materials.assign(c)
    materials.apply_overrides(c)
    log("Materialien")
    w = World(seed=seed)
    p = None
    if deco:
        ecology.compute(c)
        p = placement.Placer(c, w)
        placement.plan_islands(p)
        materials.apply_overrides(c)
        log(f"Oekologie-Karten, {len(p.islands)} Deko-Inseln, {len(c.feat.get('spring_pot', []))} Quelltoepfe")
    materials.finalize(c, w)
    w.ctx = c
    log("Kanaele")
    sx, _, sz = c.L.spawn
    w.meta.update({
        "name": "Insel 1 - Heimatplanet",
        "seed": seed,
        "layers": materials.LAYERS,
        "strata": {"base": STRATA_BASE, "bands": [[m, t] for m, t in materials.BANDS]},
        "materialColors": {k: RGB(v) for k, v in materials.MATERIAL_COLORS.items()},
        "water": {"WaterColor": RGB("#5FE3D6"), "WaterTransparency": 0.35, "WaterReflectance": 0.4,
                  "WaterWaveSize": 0.1, "WaterWaveSpeed": 6},
        "lighting": lighting.lighting_meta(),
        "sun": {"azimuth": SUN_AZ, "elevation": SUN_EL, "direction": lighting.sun_direction()},
        "spawn": [round(sx, 2), round(float(c.h_at(sx, sz)) + 0.5, 2), round(sz, 2)],
        # Review 2b: animiertes Terrain-Gras auf Grass (ersetzt die Gras-Bueschel in Hainen); Farbe = Grass-Terrainfarbe
        "terrain": {"Decoration": True, "GrassLength": 0.7},
    })
    if p is not None:
        placement.place_all(p)
        c.deco_zone = p.obstacle_mask()
    res = checks.analyse(w, c, getattr(c, "deco_zone", None))
    w.report = checks.report_lines(res)
    w.report.append(f"  Zusatzformen: {len(c.ops)}, davon zu duenn (< Durchmesser 8): {len(getattr(c, 'thin_ops', []))}")
    w.checks = res
    log("Pruefungen")
    if p is not None:
        w.report.append("Deko je Art (Objekte / Teile / Lichter):")
        for g in sorted(p.count, key=lambda k: -p.parts[k]):
            if g.startswith("_"):
                continue
            w.report.append(f"  {g:14s} {p.count[g]:5d} / {p.parts[g]:6d} / {p.lights[g]:3d}")
        c.deco_islands = p.islands
        total = sum(len(w.templates[q[0]].parts) for q in w.placements)
        if total > 25000:
            print(f"  WARNUNG: {total} Teile (Budget 25 000)")
        log("Deko gesetzt")
    c.deco_xz = np.array([(q[1], q[3]) for q in w.placements]) if w.placements else np.zeros((0, 2))
    w.preview = {"cameras": cameras.make(c), "map": cameras.map_data(c)}
    w.build_zones = build_zone_raster(c, res["build"])
    # Runde 2: Messwert der Schleife = Bauzonen-Anteil je Ring im 16er-Export (das liest der Erz-Spawn)
    from .layout import RING_EDGES, RING_NAMES
    bz = w.build_zones
    xs = bz["origin"] + bz["cell"] / 2 + bz["cell"] * np.arange(bz["n"])
    X, Z = np.meshgrid(xs, xs)
    R = np.hypot(X, Z)
    vals = []
    for i, k in enumerate(RING_NAMES):
        r1 = BUILD_MAX_R if k == "E" else RING_EDGES[i + 1]
        sel = (R >= RING_EDGES[i]) & (R < r1)
        vals.append(f"{k} {100 * bz['mask'][sel].mean():.1f} %")
    w.report.insert(6, "  Bauzonen im 16er-Export (Ziel >= 40 % je Ring): " + ", ".join(vals))
    return w
