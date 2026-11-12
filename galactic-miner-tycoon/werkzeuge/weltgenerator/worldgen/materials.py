"""Materialien, Schichtband-Versatz (Kanal S), Tiefen und Wasser -> World-Kanaele."""
from __future__ import annotations

import math

import numpy as np

from .ctx import Ctx
from .layout import DIP_DEG, LEE_DIR, STRATA_BASE, STRATA_PERIOD
from .noise import smoothstep as ss
from .world import CELL, MAT, N, STRATA_FLAG, VOID, World

# Schichtband-Stapel (Vorgabe 4.2), Periode 240, y_eff = y + 48 + S
BANDS = [
    ("Mud", 16), ("Sandstone", 24), ("Limestone", 8), ("Slate", 24), ("Salt", 4), ("Sandstone", 28),
    ("Limestone", 10), ("Concrete", 4), ("Rock", 32), ("Limestone", 10), ("Slate", 30), ("Salt", 6),
    ("Sandstone", 28), ("Mud", 16),
]
BAND_LUT = np.zeros(STRATA_PERIOD, np.uint8)
BAND_TOPS = []  # (Grenze oben, Material darunter)
_p = 0
for _m, _t in BANDS:
    BAND_LUT[_p:_p + _t] = MAT[_m]
    _p += _t
    BAND_TOPS.append((_p, _m, _t))
assert _p == STRATA_PERIOD

LAYERS = {
    "topDepth": 5, "subDepth": 14, "bedrock": "Rock",
    "subsoil": {
        "Ground": "Mud", "Grass": "Ground", "LeafyGrass": "Mud", "Sand": "Sandstone", "Mud": "Mud",
        "Basalt": "Basalt", "CrackedLava": "Basalt", "Salt": "Limestone", "Snow": "Slate", "Ice": "Glacier",
        "Glacier": "Glacier", "Slate": "Slate", "Rock": "Rock", "Limestone": "Limestone", "Sandstone": "Sandstone",
        "Concrete": "Salt",
    },
}

MATERIAL_COLORS = {
    "Ground": "#F2A07C", "Sand": "#F6CF96", "Mud": "#D9795F", "Sandstone": "#F4A9C4", "Limestone": "#F9E7A3",
    "Slate": "#A99BE0", "Rock": "#C48BBE", "Salt": "#FCEFEA", "Concrete": "#A9E5D2", "Basalt": "#3B3245",
    "CrackedLava": "#FFB07A", "Grass": "#9BE06B", "LeafyGrass": "#4FC9B0", "Snow": "#F2F6FF", "Ice": "#BFE6F5",
    "Glacier": "#A9D8E8",
}


def s_smooth(c: Ctx, x=None, z=None):
    """Glatter Teil des Schichtversatzes: 3 Grad Fall nach Azimut 70 + sanfte Faltung."""
    if x is None:
        x, z = c.x, c.z
    a = math.radians(LEE_DIR)
    u = x * math.sin(a) - z * math.cos(a)
    return math.tan(math.radians(DIP_DEG)) * u + c.nz.fbm("fold", x, z, 700, 2) * 14.0


def band_at(y_eff):
    return BAND_LUT[np.floor(y_eff).astype(np.int64) % STRATA_PERIOD]


def band_boundaries(y_lo, y_hi, s_val, min_band=6):
    """Bandgrenzen (y) zwischen y_lo und y_hi bei Versatz s_val. Gibt (y, Material darunter, Dicke) zurueck."""
    out = []
    k0 = math.floor((y_lo + s_val + STRATA_BASE) / STRATA_PERIOD) - 1
    for k in range(k0, k0 + 4):
        for top, m, t in BAND_TOPS:
            y = top + k * STRATA_PERIOD - s_val - STRATA_BASE
            if y_lo <= y <= y_hi and t >= min_band:
                out.append((y, m, t))
    out.sort()
    return out


def slope_deg(H):
    gz, gx = np.gradient(H, CELL)
    return np.degrees(np.arctan(np.hypot(gx, gz)))


def assign(c: Ctx):
    x, z, H = c.x, c.z, c.H
    nz = c.nz
    rw = c.rw
    top = c.top
    sl = slope_deg(np.where(c.void, np.nan, H))
    sl = np.nan_to_num(sl, nan=0.0)
    c.slope = sl
    rwd = rw + nz.fbm("matring", x, z, 70, 3) * 60.0
    pA = nz.fbm("patchA", x, z, 90, 4)
    pB = nz.fbm("patchB", x, z, 55, 4)
    pC = nz.fbm("patchC", x, z, 140, 3)
    G, SAND, MUD = MAT["Ground"], MAT["Sand"], MAT["Mud"]
    # Grundboden je Ring
    top[:] = G
    ringA = rwd < 250
    ringB = (rwd >= 250) & (rwd < 600)
    ringC = (rwd >= 600) & (rwd < 1100)
    ringD = (rwd >= 1100) & (rwd < 1600)
    ringE = rwd >= 1600
    # A: Korall, Sand-Flecken 8 %, Mud 2 %
    top[ringA & (pA > 0.30)] = SAND
    top[ringA & (pB < -0.40)] = MUD
    # B: Ground, Sand 10 %, Mud 9 %
    top[ringB & (pA > 0.24)] = SAND
    top[ringB & (pB < -0.30)] = MUD
    # C Nordost: Asche (Basalt) mit Korall-Inseln; C Suedwest: Sand mit Korall
    ne = c.wNE + nz.fbm("nedither", x, z, 40, 2) * 0.5 > 0.5
    top[ringC & ne & (pC < -0.08)] = MAT["Basalt"]
    top[ringC & ne & (pB < -0.25)] = MUD
    top[ringC & ~ne] = SAND
    top[ringC & ~ne & (pC > 0.25)] = G
    # D: Ground, Sand, Mud
    top[ringD & (pA > 0.12)] = SAND
    top[ringD & (pB < -0.33)] = MUD
    # E: Schiefer/Fels lavendelgrau, Staub, Sand
    top[ringE] = MAT["Slate"]
    top[ringE & (pC > 0.18)] = MAT["Rock"]
    top[ringE & (pA < -0.38)] = G
    top[ringE & (pB > 0.40)] = SAND
    # Washes: Sand mit Kies-Streifen (laengs)
    wf = c.mask("wash")
    streak = nz.fbm("gravel", x * 1.0, z * 1.0, 26, 3)
    top[wf] = SAND
    top[c.mask("wash_floor") & (streak > 0.33) & (rwd > 250)] = G
    for name, m in [("talus", MUD), ("fan", SAND)]:
        if name in c.masks:
            top[c.masks[name]] = m
    # Strata: Landformen + steile Hange
    st = c.strata
    for name in ("scarp", "rim", "mesa", "ridge", "spire", "fin", "wave", "outcrop", "hoodoo_foot", "float", "canyon_wall"):
        if name in c.masks:
            st |= c.masks[name]
    st |= (sl > 40.0)
    for name in ("talus", "rim_talus", "no_strata", "volcano", "lava", "basalt_cells", "playa", "terrace", "pond",
                 "geode", "crater_floor", "ramp", "wash_floor"):
        if name in c.masks:
            st &= ~c.masks[name]
    if "rim_talus" in c.masks:
        top[c.masks["rim_talus"]] = MAT["Rock"]
    c.strata_slope = sl


def apply_overrides(c: Ctx):
    """Materialien, die Landformen in c.mat_override (Index+1) eingetragen haben."""
    ov = getattr(c, "mat_override", None)
    if ov is not None:
        m = ov > 0
        c.top[m] = (ov[m] - 1).astype(np.uint8)
        c.strata[m & ~getattr(c, "override_keep_strata", np.zeros_like(m))] = False


def finalize(c: Ctx, w: World):
    H = c.H
    void = c.void
    sl = c.strata_slope
    # Schichtversatz S
    S = s_smooth(c) + c.nz.fbm("bandnoise", c.x, c.z, 22, 2) * 2.2
    S = S * (1 - c.S_local_w) + c.S_local * c.S_local_w
    S_int = np.mod(np.round(S), STRATA_PERIOD).astype(np.int64)
    st = c.strata & ~void
    # flache Schicht-Spalten: Deckmaterial = Band direkt unter der Oberflaeche (kein Flackern der Voxelmitte)
    flat = st & (sl < 32.0)
    yb = H - 1.5 + S_int + STRATA_BASE
    band_below = BAND_LUT[np.floor(yb).astype(np.int64) % STRATA_PERIOD]
    explicit_top = getattr(c, "strata_top", None)  # Schnee, Gras, Staub auf Schichtfelsen
    code = np.where(st, STRATA_FLAG, 0).astype(np.int64)
    topidx = np.where(flat, band_below, 0).astype(np.int64)
    if explicit_top is not None:
        topidx = np.where(st & (explicit_top > 0), explicit_top - 1, topidx)
    mat = np.where(st, code | topidx, c.top.astype(np.int64))
    mat = np.where(void, 0, mat)
    w.mat = mat.astype(np.uint8)
    w.strata_off = np.where(st, S_int, 0).astype(np.uint8)
    hq = np.round(H * 4.0) / 4.0
    w.h = np.where(void, VOID, hq)
    # Wasser
    wl = np.where(void, np.nan, c.wl)
    levels = {}
    wat = np.zeros((N, N), np.uint8)
    has = ~np.isnan(wl)
    if has.any():
        vals = np.round(wl[has] * 4) / 4
        uniq = np.unique(vals)
        if len(uniq) > 250:
            raise RuntimeError(f"zu viele Wasserspiegel: {len(uniq)}")
        for i, v in enumerate(uniq):
            levels[float(v)] = i + 1
            w.add_water_level(float(v))
        idx = np.searchsorted(uniq, vals) + 1
        wat[has] = idx.astype(np.uint8)
    w.water = wat
    # Fuelltiefe
    w.finalize_depth(extra=12.0, min_depth=12.0)
    bot = c.bottom
    hasb = ~np.isnan(bot) & ~void
    need = np.ceil((hq - bot) / CELL)
    d = w.depth.astype(np.int64)
    d = np.where(hasb, np.maximum(d, need), d)
    w.depth = np.clip(d, 1, 255).astype(np.uint8)
    w.depth[void] = 1
    w.terrain_ops = list(c.ops)
