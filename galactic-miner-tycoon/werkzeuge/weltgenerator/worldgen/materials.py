"""Materialien, Schichtband-Versatz (Kanal S), Tiefen und Wasser -> World-Kanaele."""
from __future__ import annotations

import math

import numpy as np

from .ctx import Ctx
from .layout import DIP_DEG, LEE_DIR, STRATA_BASE, STRATA_PERIOD
from .noise import smoothstep as ss
from .world import CELL, MAT, N, STRATA_FLAG, VOID, World

# Schichtband-Stapel, Periode 240, y_eff = y + STRATA_BASE + S (Review "ein Gesteinsstapel, drei Zustaende"):
# 13 Baender, 4 warme Farbfamilien (Rose, Lavendel-Rose, Korall, Butter), mindestens 8 Studs, kein Mint und kein Weiss.
BANDS = [
    ("Mud", 16), ("Sandstone", 28), ("Limestone", 10), ("Slate", 24), ("Sandstone", 20), ("Limestone", 8),
    ("Mud", 12), ("Sandstone", 26), ("Limestone", 8), ("Slate", 28), ("Limestone", 12), ("Sandstone", 24), ("Mud", 24),
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
        "Basalt": "Basalt", "CrackedLava": "Basalt", "Salt": "Salt", "Snow": "Slate", "Ice": "Glacier",
        "Glacier": "Glacier", "Slate": "Slate", "Rock": "Rock", "Limestone": "Limestone", "Sandstone": "Sandstone",
        "Concrete": "Salt",
    },
}

# Review-Palette: Boden = Mischfarbe der Gesteine, Schutt (Rock) verbindet Fels und Boden, Akzente nur bei Leben
MATERIAL_COLORS = {
    "Ground": "#F8B68C", "Sand": "#F7D5A6", "Mud": "#EC8E74", "Sandstone": "#EEA0A2", "Limestone": "#F1CF94",
    "Slate": "#D2AACE", "Rock": "#CDA49E", "Salt": "#F8ECE2", "Concrete": "#B2E0D0", "Basalt": "#4A3D50",
    "CrackedLava": "#FFB07A", "Grass": "#B2D08E", "LeafyGrass": "#86C2A6", "Snow": "#F6F0F2", "Ice": "#CFE6EE",
    "Glacier": "#A9D8E8",
}


def s_smooth(c: Ctx, x=None, z=None):
    """Glatter Teil des Schichtversatzes: 3 Grad Fall nach Azimut 70 + sanfte Faltung."""
    if x is None:
        x, z = c.x, c.z
    a = math.radians(LEE_DIR)
    u = x * math.sin(a) - z * math.cos(a)
    return math.tan(math.radians(DIP_DEG)) * u + c.nz.fbm("fold", x, z, 700, 2) * 8.0


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


def wind_streaks(c: Ctx, top):
    """Sand-Windfahnen im Lee der Tafelberge: Laenge 3-6 x Breite (max. 420), Breite 0,6 x, Ende zerfasert."""
    import math as _m
    from .layout import LEE_DIR
    a = _m.radians(LEE_DIR)
    dx, dz = _m.sin(a), -_m.cos(a)
    avoid = c.void.copy()
    for name in ("mesa", "talus", "ridge", "spire", "fin", "wash", "playa", "terrace", "pond", "volcano", "lava", "rim"):
        if name in c.masks:
            avoid |= c.masks[name]
    avoid |= ~np.isnan(c.wl)
    for k, m in enumerate(c.feat.get("mesa", [])):
        wdt = 2.0 * m["Rmin"]
        L = min(420.0, wdt * c.rng.uniform(3.0, 5.0))
        x0, z0 = m["x"] + dx * m["Rmin"] * 0.6, m["z"] + dz * m["Rmin"] * 0.6
        sl = c.win(x0 + dx * L / 2, z0 + dz * L / 2, L / 2 + wdt)
        x, z = c.local(sl)
        al = (x - x0) * dx + (z - z0) * dz
        ac = (x - x0) * -dz + (z - z0) * dx + c.nz.fbm("streakw%d" % k, x, z, 90, 2) * wdt * 0.25
        t = np.clip(al / L, 0, 1)
        hw = 0.3 * wdt * (1 - t) ** 0.6 * (0.7 + 0.3 * np.sin(np.pi * np.clip(al / (0.25 * L), 0, 1)))
        fray = c.nz.fbm("streakf%d" % k, x, z, 16, 2) * 0.5 + 0.5
        m_ = (al > 0) & (al < L) & (np.abs(ac) < hw) & (fray > 0.25 + 0.7 * t) & ~avoid[sl]
        v = top[sl]
        v[m_] = MAT["Sand"]
        c.mask("windstreak")[sl] |= m_


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
    G, SAND, MUD, ROCK = MAT["Ground"], MAT["Sand"], MAT["Mud"], MAT["Rock"]
    top[:] = G
    # Ring E: Uebergang Ground -> Slate fleckig ueber ~300 Studs
    ringE = (rwd + nz.fbm("ringEmix", x, z, 120, 3) * 220.0 >= 1640) & ~c.void
    # Korall-Bodenflecken (Mud) auf ~22 % der Ebenen: Flecken 80-300 Studs, bevorzugt in Mulden, Rand zerfasert
    from scipy import ndimage as ndi
    hs = ndi.gaussian_filter(np.where(c.void, 0.0, H), 8)
    conc = np.clip(ndi.laplace(hs) * 25.0, -1, 1)
    cor = nz.fbm("coral", x, z, 210, 3) + 0.35 * conc + 0.22 * nz.fbm("coralfray", x, z, 14, 2)
    plains = ~ringE & (c.r > 160) & ~c.void
    thr = np.quantile(cor[plains], 0.78) if plains.any() else 1.0
    top[_clean(plains & (cor > thr), 1, 2, 30)] = MUD
    # Ring C Suedwest: Duenenfeld = Sand (weich begrenzt)
    dune = c.masks.get("dune_zone")
    if dune is not None:
        top[_clean(dune, 6, 8, 400)] = SAND
    # Ring E: Slate (jetzt Lavendel-Rose), grosse Rock-Zonen (Schutt), Schnee in Mulden
    rockE = ringE & (nz.fbm("rockE", x, z, 500, 2) > 0.12)
    top[ringE] = MAT["Slate"]
    top[_clean(rockE, 6, 8, 600)] = ROCK
    if "snow" in c.masks:
        top[_clean(c.masks["snow"] & ringE, 4, 6, 120)] = MAT["Snow"]
    snowfoot = ringE & (c.r > 1800) & (sl < 12) & (nz.fbm("snowfoot", x, z, 140, 3) > 0.05)
    top[_clean(snowfoot, 4, 6, 200)] = MAT["Snow"]
    # Sand: Washes (Band mit weichem, geschwungenem Rand), Faecher, Canyonboeden
    wm = (c.wash_dist < -2.0 + 3.0 * nz.fbm("washedge", x, z, 90, 2)) | c.masks.get("wash_arm", np.zeros_like(c.void))
    top[_clean(wm, 3, 5, 120)] = SAND
    if "wash_bar" in c.masks:
        top[_clean(c.masks["wash_bar"], 1, 2, 12)] = G
    if "fan" in c.masks:
        top[_clean(c.masks["fan"], 4, 5, 150)] = SAND
    # Windfahnen: heller Sand im Lee (Richtung 70) jedes Tafelbergs, zum Ende hin zerfasert
    wind_streaks(c, top)
    # Schutt (Rock): Halden; die untere Haelfte zerfasert in den Boden (Zellen 4-8 Studs)
    if "talus" in c.masks:
        tq = getattr(c, "talus_q", None)
        tal = c.masks["talus"]
        top[tal] = ROCK
        if tq is not None:
            f1, f2, cid = nz.voronoi("screefray", x, z, 6)
            cellr = (cid % 1000) / 1000.0
            fray = tal & ~np.isnan(tq) & (cellr < ss(0.45, 1.0, np.nan_to_num(tq, nan=0.0)) * 0.95)
            top[fray] = G
        if "minifan" in c.masks:
            top[c.masks["minifan"] & (nz.fbm("minifan", x, z, 10, 2) > -0.2)] = SAND
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
        # Schnee nur auf flachen Flaechen (< 35 Grad): keine weissen Zickzack-Streifen
        snowcap = rm & (H > 228.0 + 14.0 * nz.fbm("snowline", x, z, 120, 2)) & (sl < 35)
        top[snowcap] = MAT["Snow"]
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
    # Ufer dicht: trockene Nachbarn eines Wasserfelds liegen mindestens 0,25 ueber dem Spiegel
    if has.any():
        lv = np.array([np.nan] + list(w.water_levels))[wat]
        for _ in range(2):
            for dz, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nb_l = np.roll(np.roll(np.where(wat > 0, lv, -np.inf), dz, 0), dx, 1)
                leak = (wat == 0) & ~void & (w.h < nb_l + 0.25) & np.isfinite(nb_l)
                w.h = np.where(leak, np.ceil((nb_l + 0.25) * 4) / 4, w.h)
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
