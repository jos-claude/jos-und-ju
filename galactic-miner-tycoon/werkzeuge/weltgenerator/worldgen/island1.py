"""Insel 1 (Heimatplanet). PLATZHALTER: nur ein Minimal-Gelaende zum Testen der Pipeline.

Die echte Welt entsteht nach referenz/welt-design-insel-1.md.
"""
from __future__ import annotations

import numpy as np

from .noise import Noise, smoothstep
from .world import MAT, RGB, STRATA_FLAG, Enum, PartDef, Template, World, angles


def build(seed: int) -> World:
    w = World(seed=seed)
    nz = Noise(seed)
    x, z = World.coords()
    r = np.hypot(x, z)
    hills = nz.fbm("hills", x, z, 300, 4) * 12
    h = hills * smoothstep(180, 320, r)
    mesa = smoothstep(120, 100, np.hypot(x - 300, z + 300))
    h = h + np.round(mesa * 60 / 12) * 12
    w.h = np.where(r < 2100, h, -9999.0)
    w.mat[:] = MAT["Ground"]
    w.mat[mesa > 0.05] = STRATA_FLAG
    w.finalize_depth()
    w.meta.update({
        "name": "Insel 1 (Platzhalter)", "seed": seed,
        "layers": {"topDepth": 5, "subDepth": 14, "bedrock": "Sandstone", "subsoil": {"Ground": "Mud"}},
        "strata": {"base": 0, "bands": [["Sandstone", 24], ["Limestone", 8], ["Slate", 24]]},
        "materialColors": {"Ground": RGB("#F2A07C"), "Sandstone": RGB("#F4A9C4"), "Limestone": RGB("#F9E7A3"), "Slate": RGB("#A99BE0"), "Mud": RGB("#D9795F")},
        "water": {"WaterColor": RGB("#5FE3D6")},
        "lighting": {"Lighting": {"ClockTime": 16.5, "Technology": Enum("Technology", "ShadowMap")}},
        "spawn": [0, 0, 20],
    })
    w.add_template(Template("TestBall", "Flora", [PartDef("Ball", (6, 6, 6), (0, 3, 0))], [{"main": (63, 208, 208)}]))
    w.place("TestBall", 20, float(w.height_at(20, 20)), 20)
    return w
