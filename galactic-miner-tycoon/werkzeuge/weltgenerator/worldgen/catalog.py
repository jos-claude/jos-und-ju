"""Deko-Katalog (Vorgabe 5.2): Vorlagen aus einfachen Teilen, mehrere Formvarianten je Art.

Konventionen: Fusspunkt (0, 0, 0) liegt auf dem Boden, +Y nach oben. Cylinder-Achse = lokales X (Roblox).
Keile (WedgePart) nur dort, wo die Ausrichtung egal ist (Kiesel, Kelchblaetter). Kristallspitzen sind um 45 Grad
gedrehte Bloecke (Dachfirst), damit die Keil-Ausrichtung keine Rolle spielt.
Farben kommen aus den Varianten (je Rolle); hoechstens 6 Grundfarben je Art (+ kuehle Ring-E-Varianten).
"""
from __future__ import annotations

import math

import numpy as np

from .world import PartDef, Template, angles, rot_y, rot_z

UP = np.array([0.0, 1.0, 0.0])


def C(h):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def lighter(c, f=0.25):
    return tuple(int(v + (255 - v) * f) for v in c)


def darker(c, f=0.2):
    return tuple(int(v * (1 - f)) for v in c)


def basis_x(d):
    d = np.asarray(d, float)
    d = d / np.linalg.norm(d)
    ref = UP if abs(d @ UP) < 0.95 else np.array([1.0, 0.0, 0.0])
    zc = np.cross(d, ref)
    zc /= np.linalg.norm(zc)
    yc = np.cross(zc, d)
    return np.column_stack([d, yc, zc])


def basis_y(d):
    """Drehung, deren Y-Achse in Richtung d zeigt."""
    d = np.asarray(d, float)
    d = d / np.linalg.norm(d)
    ref = np.array([1.0, 0.0, 0.0]) if abs(d[0]) < 0.9 else np.array([0.0, 0.0, 1.0])
    xc = np.cross(d, ref)
    xc /= np.linalg.norm(xc)
    zc = np.cross(xc, d)
    return np.column_stack([xc, d, zc])


def cyl(p0, p1, diam, role, mat="SmoothPlastic", **kw):
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    v = p1 - p0
    L = float(np.linalg.norm(v))
    return PartDef("Cylinder", (L, diam, diam), tuple((p0 + p1) / 2), basis_x(v), role, mat, **kw)


def ball(c, d, role, mat="SmoothPlastic", **kw):
    return PartDef("Ball", (d, d, d), tuple(np.asarray(c, float)), np.eye(3), role, mat, **kw)


def ell(c, size, role, rot=None, mat="SmoothPlastic", **kw):
    return PartDef("Ellipsoid", tuple(size), tuple(np.asarray(c, float)), np.eye(3) if rot is None else rot, role, mat, **kw)


def block(c, size, role, rot=None, mat="SmoothPlastic", **kw):
    return PartDef("Block", tuple(size), tuple(np.asarray(c, float)), np.eye(3) if rot is None else rot, role, mat, **kw)


def wedge(c, size, role, rot=None, mat="SmoothPlastic", **kw):
    return PartDef("Wedge", tuple(size), tuple(np.asarray(c, float)), np.eye(3) if rot is None else rot, role, mat, **kw)


def rot_axis(axis, ang):
    a = np.asarray(axis, float)
    a = a / np.linalg.norm(a)
    K = np.array([[0, -a[2], a[1]], [a[2], 0, -a[0]], [-a[1], a[0], 0]])
    return np.eye(3) + math.sin(ang) * K + (1 - math.cos(ang)) * K @ K


def tilt_dir(azr, tilt):
    """Einheitsvektor, tilt (rad) von der Senkrechten in Richtung azr (rad, lokal)."""
    return np.array([math.sin(tilt) * math.cos(azr), math.cos(tilt), math.sin(tilt) * math.sin(azr)])


# ------------------------------------------------------------------ Farben (Vorgabe 5.2)
CROWNS = [C("#3FD0D0"), C("#A6E04A"), C("#6FE3B0"), C("#5EB8F2"), C("#FF9FB5"), C("#FFE36B")]
CROWN_W = [35, 35, 15, 7, 5, 3]
CROWNS_E = [C("#9AD5F0"), C("#B8A8F0"), C("#C7D3E8")]
TRUNKS = [C("#C97A86"), C("#B8707A")]
NOODLE = [C("#F4E27A"), C("#5FD3C8"), C("#8FE3C0"), C("#F7A8C8")]
NOODLE_W = [34, 31, 27, 8]
CRYSTAL = [(C("#7FF3E0"), C("#B0FFF2")), (C("#9BD8FF"), C("#C8ECFF")), (C("#D58BFF"), C("#ECC0FF")),
           (C("#FF7FD0"), C("#FFB4E6")), (C("#A58CFF"), C("#CBBEFF"))]
CRYSTAL_W = [30, 25, 20, 10, 15]
LANTERN = [C("#FFC76B"), C("#FF8FB8"), C("#6DEBDD")]
MUSHROOM = [C("#B58CF0"), C("#FF9CC2"), C("#FFB88A"), C("#7FD8CF")]
ORGAN = [C("#F28BA0"), C("#F4D87A"), C("#7FE0B0")]
MOSS = [C("#A8E070"), C("#7FE0B0"), C("#B79BE8")]
CACTUS = [C("#8FE3C0"), C("#B592F0")]
PEBBLE = {"Sandstone": C("#F4A9C4"), "Limestone": C("#F9E7A3"), "Slate": C("#A99BE0"), "Rock": C("#C48BBE"),
          "Mud": C("#D9795F"), "Salt": C("#FCEFEA")}
PEBBLE_KEYS = list(PEBBLE)
TUFT = [C("#A6DC6E"), C("#8CCF7C"), C("#C4DB72")]
FLOWER = [C("#FFE36B"), C("#FF9FB5"), C("#FFFFFF")]


def _weighted(variants, weights):
    return variants, weights


# ------------------------------------------------------------------ Arten
def balloon_tree(rng, k):
    """Ballon-Baum: 1-3 Staemme aus Segmenten (S-Kurve), Kugelkrone 0,42 x Hoehe, Knoten, Wurzel."""
    H = 24.0
    n_st = [1, 1, 2, 2, 2, 3, 1, 2][k % 8]
    side = k % 3 == 0 and n_st < 3
    parts = []
    d0 = rng.uniform(1.5, 2.1)
    parts.append(ell((0, 0.25, 0), (2.6 * d0 * (1.2 if n_st > 1 else 1), 0.9 * d0, 2.6 * d0), "trunk", collide=False))
    nseg = 4 if n_st < 3 else 3
    spread = rng.uniform(0, 2 * math.pi)
    for si in range(n_st):
        az = spread + si * 2 * math.pi / n_st + rng.uniform(-0.4, 0.4)
        tilt = math.radians(rng.uniform(4, 10) if n_st == 1 else rng.uniform(10, 20))
        hs = H * (0.62 if si == 0 else rng.uniform(0.45, 0.58))
        seg = hs / nseg
        p = np.array([math.cos(az) * 0.4 * (si > 0), 0.0, math.sin(az) * 0.4 * (si > 0)])
        d = tilt_dir(az, tilt)
        sgn = 1 if rng.uniform() < 0.5 else -1
        for j in range(nseg):
            ang = math.radians(rng.uniform(6, 14)) * sgn * (1 if j % 2 == 0 else -1)
            axis = np.cross(d, UP) if abs(d @ UP) < 0.999 else np.array([1.0, 0, 0])
            if np.linalg.norm(axis) < 1e-6:
                axis = np.array([math.cos(az + 1.57), 0, math.sin(az + 1.57)])
            d = rot_axis(axis, ang) @ d
            q = p + d * seg
            dia = d0 * (1.0 - 0.35 * (j + 0.5) / nseg) * (1.0 if si == 0 else 0.8)
            parts.append(cyl(p - d * 0.3, q, dia, "trunk", collide=(j == 0 and dia >= 1.6)))
            p = q
            if side and si == 0 and j == 2:
                # Zweitballon an einem kurzen Seitenast
                sd = tilt_dir(az + math.pi * rng.uniform(0.6, 1.0), math.radians(40))
                s1 = p + sd * seg * 0.9
                parts.append(cyl(p, s1, dia * 0.7, "trunk"))
                cr2 = H * 0.42 * rng.uniform(0.5, 0.65)
                parts.append(ball(s1 + sd * cr2 * 0.42, cr2, "crown2"))
        cr = H * (0.42 if si == 0 else rng.uniform(0.3, 0.38))
        if n_st < 3:
            parts.append(ball(p + d * 0.3, 1.25 * d0, "knot"))
        parts.append(ball(p + d * cr * 0.44, cr, "crown" if si == 0 else "crown2"))
    variants = []
    for ci, cc in enumerate(CROWNS + CROWNS_E):
        tr = TRUNKS[ci % 2] if ci < 6 else C("#9C8FB8")
        c2 = CROWNS[(ci + 2) % 6] if ci < 6 and rng.uniform() < 0.3 else lighter(cc, 0.18)
        variants.append({"trunk": tr, "knot": darker(tr, 0.1), "crown": cc, "crown2": c2})
    return Template(f"BalloonTree_{k}", "Flora", parts, variants)


def noodle(rng, k):
    """Nudelpflanze: 2-3 eingerollte Ranken (Farnschnecke), Endkugel."""
    H = 7.0
    n = 3 if k % 3 == 2 else 2
    parts = []
    az0 = rng.uniform(0, 2 * math.pi)
    for i in range(n):
        az = az0 + i * 2 * math.pi / n + rng.uniform(-0.3, 0.3)
        o = np.array([math.cos(az), 0, math.sin(az)])
        hh = H * rng.uniform(0.75, 1.15)
        prof = [(0.0, 0.0), (0.1, 0.5), (0.34, 0.86), (0.52, 0.66)] if (i + k) % 2 == 0 else \
               [(0.0, 0.0), (0.16, 0.42), (0.42, 0.72), (0.5, 0.48)]
        pts = [o * a * hh + UP * b * hh for a, b in prof]
        for j in range(3):
            parts.append(cyl(pts[j], pts[j + 1], (1.4 - 0.18 * j) * (0.9 if i else 1.0), "main"))
        if i == 0:
            parts.append(ball(pts[3], 1.6, "tip"))
    variants = [{"main": cc, "tip": lighter(cc, 0.35)} for cc in NOODLE]
    return Template(f"Noodle_{k}", "Flora", parts, variants)


def _prism(base, d, b, L, role, mat="Neon", tr=0.15, collide=False, light=None):
    """Kristall-Prisma: Block + Dachfirst-Spitze (45 Grad gedrehter Block)."""
    R = basis_y(d)
    spin = rot_axis(d, 0.6)
    R = spin @ R
    c = np.asarray(base, float) + d * L / 2
    body = block(c, (b, L, b), role, R, mat, transparency=tr, collide=collide, light=light, cast_shadow=False)
    tipR = R @ angles(math.pi / 4, 0, 0)
    tc = np.asarray(base, float) + d * L
    tip = block(tc, (b, b * 0.72, b * 0.72), role, tipR, mat, transparency=tr, cast_shadow=False)
    return [body, tip]


def crystal(rng, k, size="small", lit=False):
    """Kristall-Cluster: 3-5 Prismen faecherfoermig (10-35 Grad)."""
    if size == "small":
        b, L = rng.uniform(0.7, 1.1), rng.uniform(3.5, 5.5)
    elif size == "medium":
        b, L = rng.uniform(1.6, 2.6), rng.uniform(8, 14)
    else:
        b, L = rng.uniform(5, 8), rng.uniform(38, 60)
    n = 3 + k % 3
    parts = []
    az0 = rng.uniform(0, 2 * math.pi)
    for i in range(n):
        if i == 0:
            d = tilt_dir(az0, math.radians(rng.uniform(2, 9)))
            bi, Li = b, L
        else:
            d = tilt_dir(az0 + i * 2 * math.pi / (n - 1) + rng.uniform(-0.4, 0.4), math.radians(rng.uniform(14, 35)))
            bi, Li = b * rng.uniform(0.55, 0.85), L * rng.uniform(0.45, 0.8)
        base = np.array([math.cos(az0 + i) * b * 0.5 * (i > 0), -0.12 * Li, math.sin(az0 + i) * b * 0.5 * (i > 0)])
        light = None
        if lit and i == 0:
            light = {"range": 22 if size != "giant" else 55, "brightness": 1.2 if size != "giant" else 1.5, "role": "c1"}
        parts += _prism(base, d, bi, Li, "c1" if i % 2 == 0 else "c2", tr=rng.uniform(0.1, 0.25),
                        collide=(size != "small" and i == 0), light=light)
    variants = [{"c1": a, "c2": bb} for a, bb in CRYSTAL]
    name = {"small": "CrystalS", "medium": "CrystalM", "giant": "CrystalG"}[size] + ("Lit" if lit else "") + f"_{k}"
    return Template(name, "Crystal", parts, variants)


def crystal_titan(rng, k):
    """Titan-Kristalle (Ring E): Silber-Prismen, wenig Leuchten (Glass)."""
    b, L = rng.uniform(1.4, 2.4), rng.uniform(7, 12)
    parts = []
    az0 = rng.uniform(0, 2 * math.pi)
    for i in range(4):
        d = tilt_dir(az0 + i * 1.7, math.radians(5 if i == 0 else rng.uniform(15, 30)))
        bi, Li = (b, L) if i == 0 else (b * 0.7, L * rng.uniform(0.5, 0.75))
        for p in _prism(np.array([0, -0.1 * Li, 0]), d, bi, Li, "c1" if i % 2 == 0 else "c2", mat="Glass", tr=0.2, collide=i == 0):
            p.reflectance = 0.25
            parts.append(p)
    variants = [{"c1": C("#C7D3E8"), "c2": C("#E4ECF8")}, {"c1": C("#BFE6F5"), "c2": C("#E2F5FC")}]
    return Template(f"CrystalTitan_{k}", "Crystal", parts, variants)


def lantern(rng, k, lit=False):
    H = 10.0
    l1, l2 = H * rng.uniform(0.35, 0.45), H * rng.uniform(0.3, 0.4)
    az = rng.uniform(0, 6.28)
    d1 = tilt_dir(az, math.radians(4))
    d2 = tilt_dir(az, math.radians(12))
    p1 = d1 * l1
    p2 = p1 + d2 * l2
    D = rng.uniform(2.4, 3.4)
    parts = [cyl((0, -0.2, 0), p1, 0.55, "stem"), cyl(p1, p2, 0.5, "stem")]
    for i in range(3):
        a = az + i * 2.094
        rot = rot_y(-a) @ angles(math.radians(-35), 0, 0)
        parts.append(wedge(p2 + np.array([math.cos(a) * D * 0.25, -D * 0.15, math.sin(a) * D * 0.25]),
                           (0.4, 1.0, rng.uniform(1.6, 2.4)), "sepal", rot))
    light = {"range": 14, "brightness": 0.6, "role": "lamp"} if lit else None
    parts.append(ball(p2 + d2 * D * 0.45, D, "lamp", "Neon", transparency=0.3, light=light, cast_shadow=False))
    variants = [{"stem": C("#7FCF9A"), "sepal": lighter(cc, 0.2) if i != 2 else C("#A8E070"), "lamp": cc}
                for i, cc in enumerate(LANTERN)]
    return Template(f"Lantern{'Lit' if lit else ''}_{k}", "Flora", parts, variants)


def mushroom(rng, k):
    sh = rng.uniform(5, 10)
    sd = rng.uniform(1.4, 2.4)
    cd = rng.uniform(5, 8)
    lean = rng.uniform(0, 6.28)
    top = np.array([math.cos(lean) * 0.5, sh, math.sin(lean) * 0.5])
    parts = [cyl((0, -0.3, 0), top, sd, "stem", collide=sd >= 2.0)]
    capR = basis_y(top / np.linalg.norm(top) * 0.3 + UP * 0.7)
    parts.append(ell(top + UP * cd * 0.12, (cd, cd * 0.48, cd), "cap", capR))
    parts.append(cyl(top - UP * 0.05, top + UP * 0.25, cd * 0.85, "gill"))
    for i in range(2 + k % 2):
        a = rng.uniform(0, 6.28)
        rr = cd * rng.uniform(0.15, 0.32)
        parts.append(ball(top + np.array([math.cos(a) * rr, cd * 0.32 - rr * 0.25, math.sin(a) * rr]), rng.uniform(0.6, 1.1), "spot"))
    variants = [{"stem": C("#F6EEDC"), "cap": cc, "gill": lighter(cc, 0.45), "spot": C("#FFF3D6")} for cc in MUSHROOM]
    return Template(f"Mushroom_{k}", "Flora", parts, variants)


def organ_pipe(rng, k):
    n = 6
    parts = []
    hs = sorted([rng.uniform(6, 22) for _ in range(n)], reverse=True)
    hs[0] = rng.uniform(20, 28)
    pos = [(0, 0)]
    for i in range(1, n):
        a = rng.uniform(0, 6.28)
        r = rng.uniform(2.0, 3.6)
        pos.append((math.cos(a) * r, math.sin(a) * r))
    for i in range(n):
        d = rng.uniform(1.6, 3.2) if i else 3.2
        x, z = pos[i]
        parts.append(cyl((x, -0.3, z), (x, hs[i], z), d, "tube", collide=d >= 2.0))
        if i < 3:
            parts.append(cyl((x, hs[i] - 0.2, z), (x, hs[i] + 0.2, z), d + 0.4, "rim"))
    variants = [{"tube": cc, "rim": lighter(cc, 0.3)} for cc in ORGAN]
    return Template(f"OrganPipe_{k}", "Flora", parts, variants)


def moss(rng, k):
    D = 12.0
    hh = rng.uniform(2.0, 3.2)
    rot = rot_y(rng.uniform(0, 3))
    parts = [ell((0, hh * 0.3, 0), (D, hh, D * rng.uniform(0.7, 0.95)), "main", rot, cast_shadow=False)]
    a = rng.uniform(0, 6.28)
    parts.append(ell((math.cos(a) * D * 0.18, hh * 0.55, math.sin(a) * D * 0.18), (D * 0.4, hh * 0.9, D * 0.36), "main", rot,
                     cast_shadow=False))
    variants = [{"main": cc} for cc in MOSS]
    return Template(f"Moss_{k}", "Flora", parts, variants)


def steam_vent(rng, k):
    parts = []
    y = 0.0
    for i, d in enumerate((10, 7, 4)):
        parts.append(cyl((0, y - (0.4 if i == 0 else 0), 0), (0, y + 1.5, 0), d, "sinter", "Limestone", collide=i == 0))
        y += 1.5
    steam = {"kind": "steam", "rate": 5, "lifetime": [4, 7], "size": [3, 12], "speed": [5, 9], "spread": 12,
             "color": "#F4EEF8", "transparency": [0.55, 1.0], "pulse": [25, 40]}
    parts.append(cyl((0, y - 0.05, 0), (0, y + 0.25, 0), 3.0, "water", "Neon", transparency=0.2, particles=steam, cast_shadow=False))
    for i in range(4):
        a = i * 1.57 + rng.uniform(-0.3, 0.3)
        parts.append(ball((math.cos(a) * 5.4, 0.4, math.sin(a) * 5.4), rng.uniform(1.2, 2.0), "stone"))
    variants = [{"sinter": C("#F4EBDD"), "water": C("#7FF3E0"), "stone": C("#FCEFEA")}]
    t = Template(f"SteamVent_{k}", "Feature", parts, variants)
    return t


def reeds(rng, k):
    parts = []
    for i in range(3):
        a = i * 2.1 + rng.uniform(-0.4, 0.4)
        base = np.array([math.cos(a) * 0.5, 0, math.sin(a) * 0.5])
        L1, L2 = rng.uniform(2.5, 4.5), rng.uniform(2, 3.5)
        d1 = tilt_dir(0.0, math.radians(rng.uniform(2, 8)))
        d2 = tilt_dir(0.0, math.radians(rng.uniform(16, 30)))
        p1 = base + d1 * L1
        p2 = p1 + d2 * L2
        parts.append(block((base + p1) / 2, (0.32, L1, 0.32), "blade", basis_y(d1), cast_shadow=False))
        parts.append(block((p1 + p2) / 2, (0.3, L2, 0.3), "tip", basis_y(d2), cast_shadow=False))
    variants = [{"blade": C("#8FE3C0"), "tip": C("#F4E27A")}, {"blade": C("#7FD6A8"), "tip": C("#F7E89A")}]
    return Template(f"Reeds_{k}", "Flora", parts, variants)


def pearl_cactus(rng, k, pearls=False):
    D = rng.uniform(4, 5.5)
    parts = [ball((0, D * 0.42, 0), D, "main", collide=False)]
    for i in range(3):
        a = rng.uniform(0, 6.28)
        d = D * rng.uniform(0.5, 0.7)
        y = rng.uniform(0.3, 0.9) * D
        r = (D + d) * 0.4
        parts.append(ball((math.cos(a) * r, y, math.sin(a) * r), d, "main"))
    if pearls:
        for i in range(4):
            a = rng.uniform(0, 6.28)
            parts.append(ball((math.cos(a) * D * 0.45, D * rng.uniform(0.6, 0.95), math.sin(a) * D * 0.45), 0.45, "pearl", "Neon",
                              cast_shadow=False))
    variants = [{"main": cc, "pearl": C("#FF9FD0")} for cc in CACTUS]
    return Template(f"PearlCactus{'P' if pearls else ''}_{k}", "Flora", parts, variants)


def fossil(rng, k):
    """Ammonit: 5 Zylinder-Segmente als Spirale in der lokalen XY-Ebene (liegt flach an der Wand, Normale +Z)."""
    parts = []
    n = 6
    pts = []
    for i in range(n + 1):
        t = i / n
        ang = t * 1.6 * 2 * math.pi
        r = 5.0 * (1 - t) + 1.5 * t
        pts.append(np.array([math.cos(ang) * r, math.sin(ang) * r, 0.0]))
    for i in range(n):
        parts.append(cyl(pts[i], pts[i + 1], 0.9 - 0.08 * i, "main", cast_shadow=False))
    return Template(f"Fossil_{k}", "Feature", parts, [{"main": C("#F1E4C8")}])


def pebble(rng, k):
    sh = k % 4
    if sh == 0:
        parts = [ell((0, 0.45, 0), (2.4, 1.2, 1.8), "main", angles(0.15, 0.4, -0.1), "Slate", cast_shadow=False)]
    elif sh == 1:
        parts = [ell((0, 0.5, 0), (2.8, 1.5, 2.1), "main", rot_y(0.5), "Slate", cast_shadow=False)]
    elif sh == 2:
        parts = [wedge((0, 0.55, 0), (2.0, 1.4, 2.6), "main", rot_y(1.1), "Slate", cast_shadow=False)]
    else:
        parts = [block((0, 0.5, 0), (1.8, 1.3, 2.0), "main", angles(0.3, 0.7, 0.2), "Slate", cast_shadow=False)]
    variants = [{"main": PEBBLE[key]} for key in PEBBLE_KEYS]
    return Template(f"Pebble_{k}", "Rock", parts, variants)


def copper_rock(rng, k):
    D = rng.uniform(7, 10)
    parts = [ell((0, D * 0.35, 0), (D, D * 0.8, D * 0.9), "rock", rot_y(rng.uniform(0, 3)), "Slate", collide=True)]
    for i in range(2):
        a = rng.uniform(0, 6.28)
        parts.append(wedge((math.cos(a) * D * 0.42, D * 0.2, math.sin(a) * D * 0.42), (D * 0.5, D * 0.45, D * 0.6), "rock",
                           rot_y(-a), "Slate"))
    for i in range(4):
        a = rng.uniform(0, 6.28)
        y = rng.uniform(0.3, 0.75) * D
        rr = math.sqrt(max(0.0, (D * 0.5) ** 2 - (y - D * 0.35) ** 2)) * 0.95
        parts.append(ball((math.cos(a) * rr, y, math.sin(a) * rr), rng.uniform(1.0, 1.8), "patina", cast_shadow=False))
    return Template(f"CopperRock_{k}", "Rock", parts, [{"rock": C("#D98A62"), "patina": C("#3CC8A8")}])


def tuft(rng, k):
    if k < 3:
        parts = []
        for i in range(2):
            rot = rot_y(i * 1.9 + rng.uniform(-0.3, 0.3)) @ angles(rng.uniform(-0.25, 0.25), 0, rng.uniform(-0.2, 0.2))
            parts.append(wedge((0, 0.7, 0), (0.16, 1.5, 0.75), "main", rot, cast_shadow=False))
        variants = [{"main": cc} for cc in TUFT]
        return Template(f"GrassTuft_{k}", "Flora", parts, variants)
    parts = [block((0, 0.6, 0), (0.18, 1.3, 0.18), "stem", cast_shadow=False),
             ball((0, 1.35, 0), 0.7, "bloom", cast_shadow=False)]
    variants = [{"stem": C("#8FD07A"), "bloom": cc} for cc in FLOWER]
    return Template(f"Flower_{k}", "Flora", parts, variants)


# ------------------------------------------------------------------ Grosse Einzelstuecke
def cloud():
    return Template("Cloud", "Sky", [ell((0, 0, 0), (100, 22, 80), "main", transparency=0.75, cast_shadow=False)],
                    [{"main": C("#D8C8F0")}])


def fog_ball():
    return Template("FogBall", "Sky", [ell((0, 0, 0), (100, 16, 80), "main", transparency=0.8, cast_shadow=False)],
                    [{"main": C("#EFE8FA")}])


def light_beam():
    """Lichtstrahl (Neon, Transparenz 0,85, Laenge 600) senkrecht nach oben."""
    return Template("LightBeam", "Landmark", [cyl((0, 0, 0), (0, 600, 0), 7.0, "main", "Neon", transparency=0.85, cast_shadow=False)],
                    [{"main": C("#BFF5FF")}, {"main": C("#E3B8FF")}])


def edge_barrier():
    """Unsichtbare Wand am Rand (r ~2008, Hoehe 700). Kann der Builder schon: Transparenz 1 + collide."""
    return Template("EdgeBarrier", "Barrier", [block((0, 330, 0), (200, 760, 4), "main", transparency=1.0, collide=True,
                                                     cast_shadow=False)], [{"main": (255, 255, 255)}])


def titan_vein_segment():
    return Template("TitanVein", "Landmark", [block((0, 0, 0), (1.2, 1.0, 1.8), "main", None, "Neon", transparency=0.05,
                                                    cast_shadow=False)],
                    [{"main": C("#9BE8FF")}])


def build_catalog(rng):
    t = {}

    def add(tp):
        t[tp.name] = tp
        return tp
    groups = {
        "BalloonTree": [add(balloon_tree(rng, k)) for k in range(8)],
        "Noodle": [add(noodle(rng, k)) for k in range(6)],
        "CrystalS": [add(crystal(rng, k, "small")) for k in range(5)],
        "CrystalM": [add(crystal(rng, k, "medium")) for k in range(5)],
        "CrystalMLit": [add(crystal(rng, k, "medium", True)) for k in range(3)],
        "CrystalG": [add(crystal(rng, k, "giant", True)) for k in range(3)],
        "CrystalTitan": [add(crystal_titan(rng, k)) for k in range(3)],
        "Lantern": [add(lantern(rng, k)) for k in range(4)],
        "LanternLit": [add(lantern(rng, k, True)) for k in range(2)],
        "Mushroom": [add(mushroom(rng, k)) for k in range(4)],
        "OrganPipe": [add(organ_pipe(rng, k)) for k in range(4)],
        "Moss": [add(moss(rng, k)) for k in range(4)],
        "SteamVent": [add(steam_vent(rng, k)) for k in range(2)],
        "Reeds": [add(reeds(rng, k)) for k in range(4)],
        "PearlCactus": [add(pearl_cactus(rng, k)) for k in range(3)] + [add(pearl_cactus(rng, 3, True))],
        "Fossil": [add(fossil(rng, k)) for k in range(2)],
        "Pebble": [add(pebble(rng, k)) for k in range(4)],
        "CopperRock": [add(copper_rock(rng, k)) for k in range(3)],
        "Tuft": [add(tuft(rng, k)) for k in range(5)],
        "Cloud": [add(cloud())], "FogBall": [add(fog_ball())], "LightBeam": [add(light_beam())],
        "EdgeBarrier": [add(edge_barrier())], "TitanVein": [add(titan_vein_segment())],
    }
    return t, groups
