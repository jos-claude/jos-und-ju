"""Schreibt die Welt als Luau-Datenmodule fuer den WorldBuilder (Rojo synchronisiert sie nach ServerStorage)."""
from __future__ import annotations

import re
import shutil
from pathlib import Path

import numpy as np

from . import codec
from .world import CELL, HALF, HMIN, HQ, N, RGB, TERRAIN_MATERIALS, VOID, Enum, World

HEADER = "-- AUTOMATISCH ERZEUGT vom Weltgenerator (werkzeuge/weltgenerator). Nicht von Hand aendern.\n"
_IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


class Raw(str):
    """Luau-Ausdruck, der unveraendert geschrieben wird (z. B. Color3.fromRGB(...))."""


def color3(rgb) -> Raw:
    r, g, b = (int(round(c)) for c in rgb)
    return Raw(f"Color3.fromRGB({r}, {g}, {b})")


def num(v: float, digits: int = 3) -> str:
    if isinstance(v, (bool, np.bool_)):
        return "true" if v else "false"
    if isinstance(v, (int, np.integer)):
        return str(int(v))
    s = f"{float(v):.{digits}f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def luau(v, indent: int = 0) -> str:
    pad = "\t" * indent
    if isinstance(v, (Raw, Enum)):
        return str(v)
    if isinstance(v, RGB):
        return str(color3(v))
    if v is None:
        return "nil"
    if isinstance(v, (bool, np.bool_)):
        return "true" if v else "false"
    if isinstance(v, (int, float, np.integer, np.floating)):
        return num(v, 4)
    if isinstance(v, str):
        return '"' + v.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'
    if isinstance(v, (list, tuple)):
        if all(isinstance(x, (int, float, np.integer, np.floating)) and not isinstance(x, bool) for x in v):
            return "{" + ", ".join(num(x, 4) for x in v) + "}"
        inner = ",\n".join(pad + "\t" + luau(x, indent + 1) for x in v)
        return "{\n" + inner + ",\n" + pad + "}" if v else "{}"
    if isinstance(v, dict):
        if not v:
            return "{}"
        items = []
        for k, x in v.items():
            key = k if _IDENT.match(str(k)) else "[" + luau(str(k)) + "]"
            items.append(pad + "\t" + key + " = " + luau(x, indent + 1))
        return "{\n" + ",\n".join(items) + ",\n" + pad + "}"
    raise TypeError(f"kann {type(v)} nicht als Luau schreiben")


def _write(path: Path, body: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(HEADER + body, encoding="utf-8")


def export(world: World, out_dir: Path):
    data_dir = out_dir / "Data"
    if data_dir.exists():
        shutil.rmtree(data_dir)
    data_dir.mkdir(parents=True)

    # --- Pruefungen (der Builder schreibt Wasser nur ueber Land) ---
    bad = (world.water > 0) & (world.h <= VOID)
    if bad.any():
        print(f"WARNUNG: {int(bad.sum())} Wasser-Spalten ohne Terrain werden entfernt")
        world.water[bad] = 0
    bad = (world.mat == 0) & (world.h > VOID)
    if bad.any():
        print(f"WARNUNG: {int(bad.sum())} Terrain-Spalten ohne Material (Index 0) -> Ground")
        world.mat[bad] = 3  # Ground

    # --- Terrain-Kanaele ---
    h = world.h
    q = np.where(h <= VOID, 0, np.clip(np.round((h - HMIN) * HQ), 1, 65535)).astype(np.int64)
    channels = {
        "H": codec.encode_heights(q),
        "M": codec.encode_rle(world.mat),
        "W": codec.encode_rle(world.water),
        "S": codec.encode_rle(world.strata_off),
        "D": codec.encode_rle(world.depth),
    }
    chunk_counts = {}
    total = 0
    for name, raw in channels.items():
        parts = codec.to_base64_chunks(raw)
        chunk_counts[name] = len(parts)
        for k, s in enumerate(parts, 1):
            _write(data_dir / "Terrain" / f"{name}_{k:02d}.luau", f'return "{s}"\n')
            total += len(s)

    meta = dict(world.meta)
    # surfaceOffset: Roblox zeigt die Oberflaeche einer vollen Zelle 2 Studs ueber der Zellgrenze (in Studio gemessen)
    meta["grid"] = {"n": N, "cell": CELL, "origin": -HALF, "hmin": HMIN, "hq": HQ,
                    "surfaceOffset": world.meta.get("surfaceOffset", 2.0)}
    meta["materials"] = TERRAIN_MATERIALS
    meta["chunks"] = chunk_counts
    meta["waterLevels"] = list(world.water_levels)
    _write(data_dir / "Meta.luau", "return " + luau(meta) + "\n")

    # --- Zusatzformen aus Terrain (Boegen, schwebende Felsen ...) ---
    _write(data_dir / "TerrainOps.luau", "return " + luau(world.terrain_ops) + "\n")

    # --- Deko-Vorlagen ---
    templates = {}
    for t in world.templates.values():
        parts = []
        for p in t.parts:
            r = p.rot
            e = {
                "shape": p.shape,
                "size": [round(float(x), 3) for x in p.size],
                "cf": [round(float(x), 3) for x in p.pos] + [round(float(x), 5) for x in r.ravel()],
                "role": p.role,
                "material": p.material,
            }
            if p.transparency:
                e["transparency"] = p.transparency
            if p.reflectance:
                e["reflectance"] = p.reflectance
            if not p.cast_shadow:
                e["castShadow"] = False
            if p.collide:
                e["collide"] = True
            if p.light:
                e["light"] = p.light
            if getattr(p, "particles", None):
                e["particles"] = p.particles
            parts.append(e)
        variants = [{role: color3(c) for role, c in v.items()} for v in t.variants]
        templates[t.name] = {"category": t.category, "parts": parts, "variants": variants}
        if getattr(t, "extra", None):
            templates[t.name].update(t.extra)
    _write(data_dir / "Templates.luau", "return " + luau(templates) + "\n")

    # --- Platzierungen (je Vorlage ein flaches Zahlenfeld, 8 Werte pro Objekt) ---
    by_t: dict[str, list] = {}
    for (name, x, y, z, ry, rx, rz, s, v) in world.placements:
        by_t.setdefault(name, []).append((x, y, z, ry, rx, rz, s, v))
    lines = []
    count = 0
    groups = []
    for name, items in by_t.items():
        for i in range(0, len(items), 1000):
            groups.append((name, items[i:i + 1000]))
    for name, items in groups:
        flat = []
        for (x, y, z, ry, rx, rz, s, v) in items:
            flat += [num(x, 2), num(y, 2), num(z, 2), num(ry, 3), num(rx, 3), num(rz, 3), num(s, 3), str(v + 1)]
        count += len(items)
        rows = [", ".join(flat[i:i + 64]) for i in range(0, len(flat), 64)]
        lines.append(f'\t{{ template = "{name}", items = {{\n\t\t' + ",\n\t\t".join(rows) + "\n\t} },")
    # in mehrere Module teilen (je ~150 KB)
    modules, cur, size = [], [], 0
    for ln in lines:
        if cur and size + len(ln) > 150_000:
            modules.append(cur)
            cur, size = [], 0
        cur.append(ln)
        size += len(ln)
    if cur:
        modules.append(cur)
    for k, mod in enumerate(modules, 1):
        _write(data_dir / "Placements" / f"P_{k:02d}.luau", "return {\n" + "\n".join(mod) + "\n}\n")
    return {"terrain_b64_chars": total, "placements": count, "templates": len(templates), "placement_modules": len(modules)}
