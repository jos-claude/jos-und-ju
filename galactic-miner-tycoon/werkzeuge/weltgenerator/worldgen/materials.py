"""Materialien, Schichtband-Versatz (Kanal S), Tiefen und Wasser -> World-Kanaele."""
from __future__ import annotations

import math

import numpy as np

from .ctx import Ctx
from .layout import DIP_DEG, LEE_DIR, STRATA_BASE, STRATA_PERIOD
from .noise import smoothstep as ss
from .world import CELL, MAT, N, STRATA_FLAG, VOID, World

# Schichtband-Stapel, Periode 240, y_eff = y + 48 + S.
# Abweichung von Vorgabe 4.2 (Review Runde 1): duennere Baender (4-20) in mehr Wechseln, damit jede Mesa-Stufe
# 1-2 saubere Streifen zeigt und die Danxia-Kaemme viele Farben haben. Gleiche Materialien/Farben wie 4.1.
BANDS = [
    ("Mud", 10), ("Sandstone", 18), ("Limestone", 8), ("Slate", 16), ("Salt", 4), ("Sandstone", 14),
    ("Rock", 12), ("Limestone", 6), ("Slate", 20), ("Concrete", 4), ("Sandstone", 16), ("Mud", 6),
    ("Limestone", 10), ("Rock", 18), ("Salt", 6), ("Slate", 12), ("Sandstone", 20), ("Limestone", 6),
    ("Concrete", 6), ("Rock", 14), ("Mud", 14),
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
    "topDepth": 5, "subDepth": 14, "bedrock": "Slate",
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


def _clean(m, r_open=5, r_close=6, min_cells=180):
    """Morphologie: kleine Inseln/Loecher weg, Grenzen entlang weicher Kurven."""
    from scipy import ndimage as ndi
    yy, xx = np.mgrid[-r_close:r_close + 1, -r_close:r_close + 1]
    kc = xx * xx + yy * yy <= r_close * r_close
    yy, xx = np.mgrid[-r_open:r_open + 1, -r_open:r_open + 1]
    ko = xx * xx + yy * yy <= r_open * r_open
    m = ndi.binary_closing(m, structure=kc)
    m = ndi.binary_opening(m, structure=ko)
    lab, n = ndi.label(m)
    if n:
        sizes = ndi.sum(m, lab, index=np.arange(1, n + 1))
        keep = np.concatenate([[False], sizes >= min_cells])
        m = keep[lab]
    return m


def assign(c: Ctx):
    """Boden: Ground (Pfirsich) dominiert. Sand nur in Washes, Faechern, Duenen; Mud nur an Schutthalden und
    nassen Mulden. Ring E kuehl (Slate) mit grossen Rock-Zonen und Schnee in Mulden."""
    x, z, H = c.x, c.z, c.H
    nz = c.nz
    rw = getattr(c, "rw_mat", c.rw)
    top = c.top
    sl = slope_deg(np.where(c.void, np.nan, H))
    sl = np.nan_to_num(sl, nan=0.0)
    c.slope = sl
    rwd = rw + nz.fbm("matring", x, z, 260, 2) * 70.0
    G, SAND, MUD = MAT["Ground"], MAT["Sand"], MAT["Mud"]
    top[:] = G
    ringE = (rwd >= 1610) & ~c.void
    # Ring C Suedwest: Duenenfeld = Sand (weich begrenzt)
    dune = c.masks.get("dune_zone")
    if dune is not None:
        top[_clean(dune, 6, 8, 400)] = SAND
    # Ring E: Slate, grosse Rock-Zonen (Wellenlaenge 500), Schnee in Mulden
    rockE = ringE & (nz.fbm("rockE", x, z, 500, 2) > 0.12)
    top[ringE] = MAT["Slate"]
    top[_clean(rockE, 6, 8, 600)] = MAT["Rock"]
    if "snow" in c.masks:
        top[_clean(c.masks["snow"] & ringE, 4, 6, 200)] = MAT["Snow"]
    # Sand: Washes (Band mit weichem, geschwungenem Rand), Faecher, Canyonboeden
    wm = c.wash_dist < -2.0 + 3.0 * nz.fbm("washedge", x, z, 90, 2)
    top[_clean(wm, 3, 5, 120)] = SAND
    if "fan" in c.masks:
        top[_clean(c.masks["fan"], 4, 5, 150)] = SAND
    # Mud: Schutthalden
    if "talus" in c.masks:
        top[c.masks["talus"]] = MUD
    # Strata: Landformen + steile Hange
    st = c.strata
    for name in ("scarp", "mesa", "ridge", "spire", "fin", "wave", "outcrop", "hoodoo_foot", "float", "canyon_wall"):
        if name in c.masks:
            st |= c.masks[name]
    st |= (sl > 40.0) & ~ringE
    for name in ("talus", "rim_talus", "no_strata", "volcano", "lava", "basalt_cells", "playa", "terrace", "pond",
                 "geode", "crater_floor", "ramp", "wash_floor", "rim"):
        if name in c.masks:
            st &= ~c.masks[name]
    if "rim_talus" in c.masks:
        top[c.masks["rim_talus"]] = MAT["Rock"]
    if "rim" in c.masks:
        rm = c.masks["rim"]
        top[rm] = MAT["Slate"]
        top[rm & (nz.fbm("rimrock", x, z, 300, 2) > 0.2)] = MAT["Rock"]
        snowcap = rm & (H > 228.0 + 14.0 * nz.fbm("snowline", x, z, 120, 2)) & (sl < 58)
        top[snowcap] = MAT["Snow"]
        top[rm & (H > 255) & (sl < 70)] = MAT["Snow"]
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
    S = s_smooth(c) + c.nz.fbm("bandnoise", c.x, c.z, 80, 2) * 1.5 * 2.2
    S = S * (1 - c.S_local_w) + c.S_local * c.S_local_w
    S_int = np.mod(np.round(S), STRATA_PERIOD).astype(np.int64)
    st = c.strata & ~void
    # flache Schicht-Spalten: Deckmaterial = Band direkt unter der Oberflaeche (kein Flackern der Voxelmitte)
    flat = st & (sl < 32.0)
    S_sm = np.mod(np.round(s_smooth(c) * (1 - c.S_local_w) + c.S_local * c.S_local_w), STRATA_PERIOD)
    yb = H - 1.5 + S_sm + STRATA_BASE
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
