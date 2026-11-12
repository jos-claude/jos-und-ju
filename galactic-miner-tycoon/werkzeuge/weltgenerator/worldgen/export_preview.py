"""Schreibt Vorschau-Daten fuer den Browser-Renderer (preview/)."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from .world import CELL, HALF, N, RGB, TERRAIN_MATERIALS, VOID, Enum, World


def _plain(v):
    if isinstance(v, RGB):
        return list(v)
    if isinstance(v, Enum):
        return v.value
    if isinstance(v, dict):
        return {str(k): _plain(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [_plain(x) for x in v]
    if isinstance(v, np.ndarray):
        return v.tolist()
    if isinstance(v, (np.floating,)):
        return float(v)
    if isinstance(v, (np.integer,)):
        return int(v)
    return v


def export(world: World, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    h = np.where(world.h <= VOID, np.nan, world.h).astype(np.float32)
    with open(out_dir / "terrain.bin", "wb") as f:
        f.write(h.tobytes())                                  # float32 N*N (NaN = kein Terrain)
        f.write(world.mat.astype(np.uint8).tobytes())          # u8 N*N
        f.write(world.water.astype(np.uint8).tobytes())        # u8 N*N
        f.write(world.strata_off.astype(np.uint8).tobytes())   # u8 N*N
        f.write(world.depth.astype(np.uint8).tobytes())        # u8 N*N
    templates = {}
    for t in world.templates.values():
        templates[t.name] = {
            "category": t.category,
            "variants": [{r: list(c) for r, c in v.items()} for v in t.variants],
            "parts": [
                {
                    "shape": p.shape, "size": list(map(float, p.size)), "pos": list(map(float, p.pos)),
                    "rot": [float(x) for x in np.asarray(p.rot).ravel()], "role": p.role, "material": p.material,
                    "transparency": p.transparency, "reflectance": p.reflectance,
                    "castShadow": p.cast_shadow, "light": p.light,
                }
                for p in t.parts
            ],
        }
    placements: dict[str, list] = {}
    for (name, x, y, z, ry, rx, rz, s, v) in world.placements:
        placements.setdefault(name, []).extend([round(x, 2), round(y, 2), round(z, 2), round(ry, 4), round(rx, 4), round(rz, 4), round(s, 4), v])
    scene = {
        "grid": {"n": N, "cell": CELL, "origin": -HALF},
        "materials": TERRAIN_MATERIALS,
        "meta": _plain(world.meta),
        "waterLevels": world.water_levels,
        "terrainOps": _plain(world.terrain_ops),
        "templates": templates,
        "placements": placements,
    }
    (out_dir / "scene.json").write_text(json.dumps(scene))
