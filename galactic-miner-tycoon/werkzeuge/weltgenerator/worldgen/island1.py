"""Insel 1 (Heimatplanet) nach referenz/welt-design-insel-1.md.

Ablauf: Grundgelaende -> Washes -> Landmarken/Becken/Felder/Berge -> Hochland + Rand -> Materialien
-> Pruefungen (Bauzonen, Flood-Fill, Wasser) -> Deko (Oekologie-Karten, Inseln) -> Licht/Meta.
"""
from __future__ import annotations

import time

import numpy as np

from . import cameras, checks, compose, ecology, fields, lighting, materials, placement, terrain
from .ctx import Ctx
from .layout import STRATA_BASE, SUN_AZ, SUN_EL
from .world import RGB, World

SEED = 1


def build_zone_raster(c, build, cell=16):
    """Bauzonen als grobes Raster fuer den Erz-Spawn: eine 16x16-Zelle zaehlt, wenn alle 4x4-Spalten Bauzone sind.
    Ring E nur bis r 1900 (Randgebirge ist Grenze)."""
    k = int(cell // 4)
    n = build.shape[0] // k
    b = build[: n * k, : n * k].reshape(n, k, n, k).all(axis=(1, 3))
    xs = -2304 + cell / 2 + cell * np.arange(n)
    X, Z = np.meshgrid(xs, xs)
    b &= np.hypot(X, Z) <= 1900
    return {"cell": cell, "n": n, "origin": -2304.0, "mask": b}


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
    zoneA = (c.rw > 185) & (c.rw < 255) & ~c.mask("claimed") & (c.wash_dist > 5)
    zoneB = (c.rw > 270) & (c.rw < 600) & ~c.mask("claimed") & (c.wash_dist > 5)
    zoneD = (c.rw > 1150) & (c.rw < 1560) & ~c.mask("claimed") & (c.wash_dist > 5)
    fields.outcrops(c, zoneA, 0.05, (2.0, 4.0), "outA")
    fields.outcrops(c, zoneB, 0.04, (2.5, 5.0), "outB")
    fields.outcrops(c, zoneD, 0.03, (3.0, 6.0), "outD")
    fields.low_floating_stones(c, 30)
    terrain.foothills(c, 10)
    terrain.rim(c)
    terrain.floating_rocks(c)
    log("Rand, Balkone, Schwebfelsen")
    from .landforms import check_ops
    thin = check_ops(c.ops)
    c.thin_ops = thin
    if thin:
        print(f"  WARNUNG: {len(thin)} Zusatzformen duenner als Durchmesser 8 (werden in Roblox klumpig): "
              + ", ".join(sorted({o['op'] + '/' + o['material'] for o in thin})))
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
        log(f"Oekologie-Karten, {len(p.islands)} Deko-Inseln")
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
    w.preview = {"cameras": cameras.make(c), "map": cameras.map_data(c)}
    w.build_zones = build_zone_raster(c, res["build"])
    return w
