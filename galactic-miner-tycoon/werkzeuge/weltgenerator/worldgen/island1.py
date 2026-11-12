"""Insel 1 (Heimatplanet) nach referenz/welt-design-insel-1.md.

Ablauf: Grundgelaende -> Washes -> Landmarken/Becken/Felder/Berge -> Hochland + Rand -> Materialien
-> Pruefungen (Bauzonen, Flood-Fill, Wasser) -> Deko (Oekologie-Karten, Inseln) -> Licht/Meta.
"""
from __future__ import annotations

import time

import numpy as np

from . import cameras, compose, fields, lighting, materials, terrain
from .ctx import Ctx
from .layout import STRATA_BASE, SUN_AZ, SUN_EL
from .world import RGB, World

SEED = 1


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
    fields.outcrops(c, zoneA, 0.08, (2.0, 4.0), "outA")
    fields.outcrops(c, zoneB, 0.06, (2.5, 5.0), "outB")
    fields.outcrops(c, zoneD, 0.05, (3.0, 6.0), "outD")
    fields.low_floating_stones(c, 50)
    terrain.rim(c)
    terrain.floating_rocks(c)
    log("Rand, Balkone, Schwebfelsen")
    materials.assign(c)
    materials.apply_overrides(c)
    log("Materialien")
    w = World(seed=seed)
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
    w.preview = {"cameras": cameras.make(c)}
    return w
