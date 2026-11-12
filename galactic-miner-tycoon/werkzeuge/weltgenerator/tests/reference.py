"""Unabhaengige Referenz-Implementierung der README-Regeln (Voxel, Teile, Zusatzformen).

Absichtlich anders aufgebaut als der Luau-Builder: Es wird je Spalte direkt aus den Welt-Arrays gerechnet,
ohne 16x16-Bloecke, ohne Puffer, ohne Dekodierung.
"""
from __future__ import annotations

import math
from collections import OrderedDict

import numpy as np

from worldgen.world import CELL, HALF, HMIN, HQ, N, STRATA_FLAG, TERRAIN_MATERIALS, VOID, angles

ORIGIN_VOXEL = int(-HALF // CELL)  # -576


def quant_height(h):
    """Gespeicherte Hoehe: Viertel-Studs, mindestens q=1; <= VOID heisst kein Terrain."""
    if h <= VOID:
        return None
    q = max(1, min(65535, int(round((h - HMIN) * HQ))))
    return q / HQ + HMIN


def band_table(strata):
    table = []
    for name, width in strata["bands"]:
        table += [name] * int(width)
    return table


def column_material(world, ix, iz, h, yc):
    """Material im Voxel mit Mittelpunkt yc (README 'Material je Voxel')."""
    meta = world.meta
    layers, strata = meta["layers"], meta["strata"]
    code = int(world.mat[iz, ix])
    d = h - yc
    is_strata = bool(code & STRATA_FLAG)
    top_index = code & 31
    top = TERRAIN_MATERIALS[top_index]
    if is_strata:
        if top_index != 0 and d < layers["topDepth"]:
            return top
        bands = band_table(strata)
        return bands[int(math.floor(yc + int(world.strata_off[iz, ix]) + strata["base"])) % len(bands)]
    if d < layers["topDepth"]:
        return top
    if d < layers["subDepth"]:
        return layers["subsoil"].get(top, layers["bedrock"])
    return layers["bedrock"]


def expected_voxels(world):
    """-> (voxels {(vx,vy,vz): (material, occupancy)}, void_water_columns {(vx,vz): level})."""
    vox = {}
    void_water = {}
    cols = np.argwhere((world.h > VOID) | (world.water > 0))
    for iz, ix in cols.tolist():
        wi = int(world.water[iz, ix])
        wl = world.water_levels[wi - 1] if wi else None
        h = quant_height(float(world.h[iz, ix]))
        vxz = (ix + ORIGIN_VOXEL, iz + ORIGIN_VOXEL)
        if h is None:
            if wl is not None:
                void_water[vxz] = wl
            continue
        bottom = h - int(world.depth[iz, ix]) * CELL
        k0 = int(math.floor(bottom / CELL)) - 1
        k1 = int(math.ceil((max(h, wl if wl is not None else h)) / CELL)) + 1
        for k in range(k0, k1 + 1):
            yb = k * CELL
            if yb < h and yb + CELL > bottom:
                m = column_material(world, ix, iz, h, yb + CELL / 2)
                if m != "Air":
                    vox[(vxz[0], k, vxz[1])] = (m, min(1.0, (h - yb) / CELL))
            elif wl is not None and yb >= h and yb < wl:
                vox[(vxz[0], k, vxz[1])] = ("Water", min(1.0, (wl - yb) / CELL))
    return vox, void_water


# ---------------------------------------------------------------- Deko

def _place_matrix(p):
    (_, x, y, z, ry, rx, rz, s, v) = p
    # CFrame.new(x,y,z) * Angles(0,ry,0) * Angles(rx,0,rz)
    return np.array([x, y, z]), angles(0, ry, 0) @ angles(rx, 0, rz)


def expected_models(world):
    """-> OrderedDict category -> [Modell-Dict]; Reihenfolge: je Vorlage (Erstauftreten), darin Platzierungsreihenfolge."""
    groups = OrderedDict()
    for p in world.placements:
        groups.setdefault(p[0], []).append(p)
    cats = OrderedDict()
    unknown = []
    for name, items in groups.items():
        t = world.templates.get(name)
        if t is None:
            unknown.append(name)
            continue
        folder = cats.setdefault(t.category, [])
        for p in items:
            pos, rot = _place_matrix(p)
            s, variant = p[7], p[8]
            colors = t.variants[variant] if variant < len(t.variants) else t.variants[0]
            parts = []
            for d in t.parts:
                ppos = pos + rot @ (np.array(d.pos, float) * s)
                prot = rot @ np.asarray(d.rot, float)
                col = colors.get(d.role)
                col = (col[0] / 255, col[1] / 255, col[2] / 255) if col is not None else (1.0, 0.0, 1.0)
                e = {
                    "class": "WedgePart" if d.shape == "Wedge" else "Part",
                    "name": d.role,
                    "shape": {"Block": "Enum.PartType.Block", "Ball": "Enum.PartType.Ball", "Cylinder": "Enum.PartType.Cylinder"}.get(d.shape),
                    "size": [float(v) * s for v in d.size],
                    "cframe": [float(v) for v in ppos] + [float(v) for v in prot.ravel()],
                    "color": list(col), "material": f"Enum.Material.{d.material}",
                    "transparency": d.transparency, "reflectance": d.reflectance,
                    "castShadow": d.cast_shadow, "collide": d.collide,
                    "mesh": d.shape == "Ellipsoid", "light": None,
                }
                if d.light:
                    lc = d.light.get("color")
                    if lc is not None:
                        lcol = [lc[0] / 255, lc[1] / 255, lc[2] / 255]
                    else:
                        r = colors.get(d.light.get("role", d.role))
                        lcol = [r[0] / 255, r[1] / 255, r[2] / 255] if r is not None else [1.0, 1.0, 1.0]
                    e["light"] = {"range": min(60.0, d.light["range"] * s), "brightness": d.light["brightness"], "color": lcol}
                parts.append(e)
            folder.append({"name": name, "pivot": [float(v) for v in pos] + [float(v) for v in rot.ravel()], "parts": parts})
    return cats, unknown
