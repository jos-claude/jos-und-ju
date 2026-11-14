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


def cyl(p0, p1, diam, role, mat="Plaster", **kw):
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    v = p1 - p0
    L = float(np.linalg.norm(v))
    return PartDef("Cylinder", (L, diam, diam), tuple((p0 + p1) / 2), basis_x(v), role, mat, **kw)


def ball(c, d, role, mat="Plaster", **kw):
    return PartDef("Ball", (d, d, d), tuple(np.asarray(c, float)), np.eye(3), role, mat, **kw)


def ell(c, size, role, rot=None, mat="Plastic", **kw):   # SpecialMesh: Material wird ohnehin nicht gezeigt
    return PartDef("Ellipsoid", tuple(size), tuple(np.asarray(c, float)), np.eye(3) if rot is None else rot, role, mat, **kw)


def block(c, size, role, rot=None, mat="Plaster", **kw):
    return PartDef("Block", tuple(size), tuple(np.asarray(c, float)), np.eye(3) if rot is None else rot, role, mat, **kw)


def wedge(c, size, role, rot=None, mat="Plaster", **kw):
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
# Review: gedaempfte, matte Farben (L 0,55-0,80, Saettigung <= 0,6); jede Pflanze mit dunklerer Unterseite
# Runde 1: Kronen ~15-20 % satter (Zielbild: kraeftiges Tuerkis und Gelbgruen)
CROWNS = [C("#3FC9C4"), C("#BEE04C"), C("#78D6AF"), C("#60ABDE"), C("#F196A3"), C("#F1D161")]
CROWN_W = [35, 35, 15, 7, 5, 3]
CROWNS_E = [C("#A8D2EA"), C("#BCAEE8"), C("#C4CCE0")]
TRUNKS = [C("#7E5A68"), C("#6E5262")]
NOODLE = [C("#E8D27E"), C("#6CC6BC"), C("#94D8BC"), C("#EBA6BE")]
NOODLE_W = [34, 31, 27, 8]
CRYSTAL = [(C("#8EE8D8"), C("#B4F2E6")), (C("#A8D8F2"), C("#C8E6F8")), (C("#CFA0F0"), C("#E2C4F6")),
           (C("#F2A0D6"), C("#F8C4E6")), (C("#B2A0F0"), C("#CEC2F6"))]
CRYSTAL_W = [30, 25, 20, 10, 15]
LANTERN = [C("#FFC76B"), C("#FF8FB8"), C("#6DEBDD")]
MUSHROOM = [C("#A98CD8"), C("#EE9CB8"), C("#F2AE86"), C("#79C9C0")]
ORGAN = [C("#E99AA2"), C("#E8CF86"), C("#8ED6B4")]
MOSS = [C("#B0D98A"), C("#8FD6B5"), C("#B8AAD6")]
CACTUS = [C("#94CDB8"), C("#AC9CD2")]
PEBBLE = {"Sandstone": C("#F4A9C4"), "Limestone": C("#F9E7A3"), "Slate": C("#A99BE0"), "Rock": C("#C48BBE"),
          "Mud": C("#D9795F"), "Salt": C("#FCEFEA")}
PEBBLE_KEYS = list(PEBBLE)
TUFT = [C("#A8C878"), C("#94BE86"), C("#BCCB7C")]
FLOWER = [C("#FFE36B"), C("#FF9FB5"), C("#FFFFFF")]


def cooler(c, f=0.22):
    """Dunklere, etwas kuehlere Unterseite (eingebauter Kontaktschatten)."""
    r, g, b = darker(c, f)
    return (int(r * 0.94), int(g * 0.97), min(255, int(b * 1.06)))


# Gesteins-Kiesel: Material und Farbe des Bands darueber (12 % dunkler, 15 % entsaettigt)
ROCKS = {"Sandstone": "#EEA0A2", "Limestone": "#F1CF94", "Slate": "#D2AACE", "Mud": "#EC8E74", "Rock": "#CDA49E"}


def band_pebble_color(hexc):
    r, g, b = C(hexc)
    l = (r + g + b) / 3
    r, g, b = (l + (r - l) * 0.85, l + (g - l) * 0.85, l + (b - l) * 0.85)
    return (int(r * 0.88), int(g * 0.88), int(b * 0.88))


# ------------------------------------------------------------------ Arten
def crown(center, D, role, rng, full=True, mat="Sand"):
    """Wolkenform: Hauptkugel + 1 Nebenkugel (leicht unterhalb, ueberlappend) + dunklere Unterseiten-Kugel.
    Runde 3: 3 statt 4 Kugeln (rundere Ballon-Kronen wie im Zielbild, Teile sparen)."""
    center = np.asarray(center, float)
    parts = [ball(center, D, role, mat)]
    if full:
        a0 = rng.uniform(0, 2 * math.pi)
        for i in range(1):
            a = a0 + i * rng.uniform(2.2, 3.4)
            d = D * rng.uniform(0.55, 0.7)
            off = (D + d) / 2 * rng.uniform(0.65, 0.75)
            parts.append(ball(center + np.array([math.cos(a) * off, -D * rng.uniform(0.08, 0.18), math.sin(a) * off]), d, role, mat))
    parts.append(ball(center - np.array([0, D * 0.25, 0]), D * 0.8, role + "_under", mat))
    return parts


def balloon_tree(rng, k):
    """Ballon-Baum: duenne, dunkle Holzstaemme (gleicher Durchmesser je Stamm), Wurzeln, Wolken-Krone mit Unterseite."""
    H = 24.0
    n_st = [1, 1, 2, 1, 2, 1, 2, 3][k % 8]
    parts = []
    d0 = rng.uniform(0.95, 1.35)
    nseg = 4 if n_st < 3 else 3
    spread = rng.uniform(0, 2 * math.pi)
    # Wurzeln: Runde 3 nur noch 1 kurzer Zylinder (40 Grad geneigt, halb im Boden), Teile sparen
    for i in range(1):
        a = spread + i * 2.09 + rng.uniform(-0.3, 0.3)
        dr = np.array([math.cos(a) * math.cos(math.radians(40)), -math.sin(math.radians(40)), math.sin(a) * math.cos(math.radians(40))])
        L = rng.uniform(1.5, 2.5)
        p0 = np.array([0.0, 0.5, 0.0])
        parts.append(cyl(p0, p0 + dr * L, d0 * 0.6, "trunk", "Wood"))
    for si in range(n_st):
        az = spread + si * 2 * math.pi / n_st + rng.uniform(-0.4, 0.4)
        tilt = math.radians(rng.uniform(4, 10) if n_st == 1 else rng.uniform(12, 22))
        hs = H * (0.62 if si == 0 else rng.uniform(0.45, 0.56))
        seg = hs / nseg
        p = np.array([math.cos(az) * 0.3 * (si > 0), -0.4, math.sin(az) * 0.3 * (si > 0)])
        d = tilt_dir(az, tilt)
        sgn = 1 if rng.uniform() < 0.5 else -1
        dia = d0 * (1.0 if si == 0 else 0.8)
        for j in range(nseg):
            ang = math.radians(rng.uniform(5, 13)) * sgn * (1 if j % 2 == 0 else -1)
            axis = np.cross(d, UP)
            if np.linalg.norm(axis) < 1e-6:
                axis = np.array([math.cos(az + 1.57), 0, math.sin(az + 1.57)])
            d = rot_axis(axis, ang) @ d
            q = p + d * seg
            parts.append(cyl(p, q + d * 0.15, dia, "trunk", "Wood", collide=(j == 0 and si == 0)))
            if abs(math.degrees(ang)) > 10 and j < nseg - 1:
                parts.append(ball(q, dia * 1.12, "trunk", "Wood"))       # Gelenk nur bei Knick > 10 Grad
            p = q
        Dc = H * (0.42 if si == 0 else rng.uniform(0.3, 0.36))
        parts += crown(p + d * Dc * 0.45, Dc, "crown" if si == 0 else "crown2", rng, full=(si == 0))
    variants = []
    for ci, cc in enumerate(CROWNS + CROWNS_E):
        tr = TRUNKS[ci % 2]
        c2 = lighter(cc, 0.12) if ci >= 6 or rng.uniform() > 0.3 else CROWNS[(ci + 2) % 6]
        variants.append({"trunk": tr, "crown": cc, "crown_under": cooler(cc), "crown2": c2, "crown2_under": cooler(c2)})
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
        # Runde 3 (Teile sparen): 2 statt 3 Segmente je Ranke, Endkugel bleibt
        prof = [(0.0, 0.0), (0.12, 0.62), (0.46, 0.8)] if (i + k) % 2 == 0 else \
               [(0.0, 0.0), (0.18, 0.52), (0.48, 0.62)]
        pts = [o * a * hh + UP * b * hh for a, b in prof]
        pts[0] = pts[0] - UP * 0.6                              # unterster Teil halb im Boden
        for j in range(2):
            parts.append(cyl(pts[j], pts[j + 1], (1.4 - 0.22 * j) * (0.9 if i else 1.0), "base" if j == 0 else "main", "Plaster"))
        if i == 0:
            parts.append(ball(pts[2], 1.6, "tip", "Plaster"))
    variants = [{"main": cc, "base": cooler(cc, 0.18), "tip": lighter(cc, 0.2)} for cc in NOODLE]
    return Template(f"Noodle_{k}", "Flora", parts, variants)


def _prism(base, d, b, L, role, mat="Glass", tr=0.0, collide=False, light=None, core=False, tip_mat=None, tip=True):
    """Kristall-Prisma: Glas-Block + Dachfirst-Spitze (45 Grad gedrehter Block, hellere Farbe), optional Neon-Kern.
    Handy-Budget: nur Riesen-/Landmarken-Kristalle sind durchsichtig (tr > 0) und haben einen Neon-Kern; kleine und
    mittlere sind undurchsichtiges Glas (Transparency 0 = guenstig), Leitwirkung ueber hellere Spitzen."""
    R = basis_y(d)
    spin = rot_axis(d, 0.6)
    R = spin @ R
    c = np.asarray(base, float) + d * L / 2
    body = block(c, (b, L, b), role, R, mat, transparency=tr, collide=collide, light=light if not core else None,
                 cast_shadow=False, reflectance=0.08 if mat == "Glass" else 0.0)
    out = [body]
    if tip:
        tipR = R @ angles(math.pi / 4, 0, 0)
        tc = np.asarray(base, float) + d * L
        tm = tip_mat or mat
        out.append(block(tc, (b, b * 0.72, b * 0.72), role + "_tip", tipR, tm, transparency=tr if tm != "Neon" else 0.0,
                         cast_shadow=False, reflectance=0.08 if tm == "Glass" else 0.0))
    if core:
        out.append(block(np.asarray(base, float) + d * L * 0.45, (b * 0.45, L * 0.8, b * 0.45), "core", R, "Neon",
                         transparency=0.25, cast_shadow=False, light=light))
    return out


def crystal(rng, k, size="small", lit=False):
    """Kristall-Cluster: 3-5 Prismen faecherfoermig (10-35 Grad)."""
    if size == "small":
        b, L = rng.uniform(0.7, 1.1), rng.uniform(3.5, 5.5)
    elif size == "medium":
        b, L = rng.uniform(1.6, 2.6), rng.uniform(8, 14)
    else:
        b, L = rng.uniform(5, 8), rng.uniform(38, 60)
    n = (2 + k % 2) if size == "small" else 3 + k % 3        # Runde 3: kleine Kristalle 2-3 statt 3-5 Prismen
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
            light = {"range": 22 if size != "giant" else 55, "brightness": 1.2 if size != "giant" else 1.5, "role": "core"}
        giant = size == "giant"
        # Lit-Kristalle (mittel): Spitze des Hauptprismas aus Neon -> Bloom nur dort; sonst undurchsichtiges Glas
        # Runde 1 (Teile sparen): Dachfirst-Spitze nur am Hauptprisma (ausser Riesen-Kristallen)
        parts += _prism(base, d, bi, Li, "c1" if i % 2 == 0 else "c2", tr=0.35 if giant else 0.0,
                        collide=(size != "small" and i == 0), light=light, core=(giant and i == 0),
                        tip_mat="Neon" if (lit and not giant and i == 0) else None, tip=(giant or i == 0))
    # 1-2 Fussbrocken in Gesteinsfarbe: der Kristall waechst aus dem Fels
    for j in range(1 if size == "small" else 1 + k % 2):     # Runde 3: kleine Kristalle nur 1 Fussbrocken
        a = az0 + 2.5 + j * 2.0
        rr = b * (1.1 + 0.4 * j)
        fs = b * rng.uniform(1.2, 1.8)
        parts.append(block((math.cos(a) * rr, fs * 0.2, math.sin(a) * rr), (fs, fs * 0.7, fs * 0.9), "foot",
                           angles(rng.uniform(-0.4, 0.4), rng.uniform(0, 3), rng.uniform(-0.4, 0.4)), "Rock"))
    variants = [{"c1": a, "c2": bb, "c1_tip": lighter(a, 0.3), "c2_tip": lighter(bb, 0.3), "core": lighter(a, 0.15),
                 "foot": C("#B8908A")} for a, bb in CRYSTAL]
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
        for p in _prism(np.array([0, -0.1 * Li, 0]), d, bi, Li, "c1" if i % 2 == 0 else "c2", mat="Glass", tr=0.0, collide=i == 0):
            p.reflectance = 0.15
            parts.append(p)
    variants = [{"c1": C("#C7D3E8"), "c2": C("#E4ECF8"), "c1_tip": C("#EEF3FB"), "c2_tip": C("#F4F8FD")},
                {"c1": C("#BFE6F5"), "c2": C("#E2F5FC"), "c1_tip": C("#E8F7FC"), "c2_tip": C("#F2FBFE")}]
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
    parts = [cyl((0, -0.3, 0), p1, 0.55, "stem", "Plaster"), cyl(p1, p2, 0.5, "stem", "Plaster")]
    for i in range(3):
        a = az + i * 2.094
        rot = rot_y(-a) @ angles(math.radians(-35), 0, 0)
        parts.append(wedge(p2 + np.array([math.cos(a) * D * 0.25, -D * 0.15, math.sin(a) * D * 0.25]),
                           (0.4, 1.0, rng.uniform(1.6, 2.4)), "sepal", rot, "Plaster"))
    light = {"range": 14, "brightness": 0.6, "role": "lamp"} if lit else None
    parts.append(ball(p2 + d2 * D * 0.45, D, "lamp", "Neon", transparency=0.35, light=light, cast_shadow=False))
    variants = [{"stem": C("#86C49A"), "sepal": lighter(cc, 0.1) if i != 2 else C("#A8C878"), "lamp": cc}
                for i, cc in enumerate(LANTERN)]
    return Template(f"Lantern{'Lit' if lit else ''}_{k}", "Flora", parts, variants)


def mushroom(rng, k):
    sh = rng.uniform(5, 10)
    sd = rng.uniform(1.4, 2.4)
    cd = rng.uniform(5, 8)
    lean = rng.uniform(0, 6.28)
    top = np.array([math.cos(lean) * 0.5, sh, math.sin(lean) * 0.5])
    parts = [cyl((0, -0.5, 0), top, sd, "stem", "Plaster", collide=sd >= 2.0)]
    dc = cd * 0.8
    cc_ = top + UP * dc * 0.2                                # Hut = Kugel, Mitte knapp ueber dem Stielende
    parts.append(ball(cc_, dc, "cap", "Plaster"))
    parts.append(cyl(top - UP * 0.05, top + UP * 0.3, dc * 0.92, "gill", "Plaster"))   # Lamellen dunkler (Schatten)
    for i in range(2 + k % 2):
        a = rng.uniform(0, 6.28)
        el = math.radians(rng.uniform(30, 65))
        parts.append(ball(cc_ + np.array([math.cos(a) * math.cos(el), math.sin(el), math.sin(a) * math.cos(el)]) * dc * 0.48,
                          rng.uniform(0.6, 1.0), "spot", "Plaster"))
    variants = [{"stem": C("#EDE2D2"), "cap": cc, "gill": cooler(cc, 0.3), "spot": C("#FFF1DC")} for cc in MUSHROOM]
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
        parts.append(cyl((x, -0.5, z), (x, hs[i], z), d, "tube", "Plaster", collide=d >= 2.0))
        if i < 3:
            parts.append(cyl((x, hs[i] - 1.2, z), (x, hs[i] + 0.05, z), max(0.6, d - 0.6), "hole", "Plaster"))
    variants = [{"tube": cc, "hole": darker(cc, 0.4)} for cc in ORGAN]
    return Template(f"OrganPipe_{k}", "Flora", parts, variants)


def steam_vent(rng, k):
    parts = []
    y = 0.0
    for i, d in enumerate((10, 7, 4)):
        parts.append(cyl((0, y - (0.6 if i == 0 else 0), 0), (0, y + 1.5, 0), d, "sinter", "Limestone", collide=i == 0))
        y += 1.5
    steam = {"kind": "steam", "rate": 5, "lifetime": [4, 7], "size": [3, 12], "speed": [5, 9], "spread": 12,
             "color": "#F4EEF8", "transparency": [0.55, 1.0], "pulse": [25, 40]}
    parts.append(cyl((0, y - 0.05, 0), (0, y + 0.25, 0), 3.0, "water", "Glass", transparency=0.3, particles=steam, cast_shadow=False))
    for i in range(4):
        a = i * 1.57 + rng.uniform(-0.3, 0.3)
        parts.append(ball((math.cos(a) * 5.4, 0.2, math.sin(a) * 5.4), rng.uniform(1.4, 2.2), "stone", "Limestone"))
    variants = [{"sinter": C("#EFE3D2"), "water": C("#7FE0D6"), "stone": C("#E6D8C4")}]
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
        parts.append(block((base + p1) / 2, (0.32, L1, 0.32), "blade", basis_y(d1), "Grass", cast_shadow=False))
        parts.append(block((p1 + p2) / 2, (0.3, L2, 0.3), "tip", basis_y(d2), "Grass", cast_shadow=False))
    variants = [{"blade": C("#8CCFB0"), "tip": C("#E8D68A")}, {"blade": C("#82C2A4"), "tip": C("#E2D294")}]
    return Template(f"Reeds_{k}", "Flora", parts, variants)


def pearl_cactus(rng, k, pearls=False):
    D = rng.uniform(4, 5.5)
    parts = [ball((0, D * 0.36, 0), D, "main", "Sand", collide=False)]
    for i in range(3):
        a = rng.uniform(0, 6.28)
        d = D * rng.uniform(0.5, 0.7)
        y = rng.uniform(0.3, 0.9) * D
        r = (D + d) * 0.4
        parts.append(ball((math.cos(a) * r, y, math.sin(a) * r), d, "main" if i else "under", "Sand"))
    if pearls:
        for i in range(4):
            a = rng.uniform(0, 6.28)
            parts.append(ball((math.cos(a) * D * 0.45, D * rng.uniform(0.6, 0.95), math.sin(a) * D * 0.45), 0.45, "pearl", "Neon",
                              cast_shadow=False))
    variants = [{"main": cc, "under": cooler(cc, 0.15), "pearl": C("#FF9FD0")} for cc in CACTUS]
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
        parts.append(cyl(pts[i], pts[i + 1], 0.9 - 0.08 * i, "main", "Limestone", cast_shadow=False))
    return Template(f"Fossil_{k}", "Feature", parts, [{"main": C("#EAD9BC")}])


def pebble(rng, k, mat):
    """Kiesel im Material des Bands darueber: Kugel (35 % versenkt), Keil oder gedrehter Block."""
    sh = k % 3
    if sh == 0:
        parts = [ball((0, 0.3, 0), 2.0, "main", mat, cast_shadow=False)]
    elif sh == 1:
        parts = [wedge((0, 0.45, 0), (2.0, 1.4, 2.6), "main", rot_y(1.1), mat, cast_shadow=False)]
    else:
        parts = [block((0, 0.35, 0), (1.8, 1.3, 2.0), "main", angles(0.3, 0.7, 0.2), mat, cast_shadow=False)]
    return Template(f"Pebble_{mat}_{k}", "Rock", parts, [{"main": band_pebble_color(ROCKS[mat])}])


def boulder(rng, k):
    """Mittelgrosser Brocken (2-8 Studs) aus Schutt: 2-3 gedrehte Bloecke/Keile (Low-Poly)."""
    parts = []
    for i in range(2 + k % 2):
        sz = np.array([rng.uniform(2.2, 3.2), rng.uniform(1.4, 2.4), rng.uniform(2.0, 3.0)]) * (1.0 if i == 0 else 0.7)
        off = np.array([rng.uniform(-0.8, 0.8), sz[1] * 0.3, rng.uniform(-0.8, 0.8)]) * (i > 0)
        R = angles(rng.uniform(-0.35, 0.35), rng.uniform(0, 3.1), rng.uniform(-0.35, 0.35))
        if i == 1:
            parts.append(wedge(off + np.array([0, sz[1] * 0.35, 0]), sz, "main", R, "Rock", collide=False))
        else:
            parts.append(block(off + np.array([0, sz[1] * 0.3, 0]), sz, "main", R, "Rock", collide=i == 0))
    return Template(f"Boulder_{k}", "Rock", parts, [{"main": C("#BE9690")}, {"main": C("#C99E94")}, {"main": C("#B58C92")}])


def boulder_soft(base: Template, k):
    """Runde 3: Leitstueck der Feld-Gruppen - wie Boulder, aber ohne Kollision (auch der Hauptblock), kniehoch."""
    from dataclasses import replace
    parts = [replace(q, collide=False) for q in base.parts]
    return Template(f"BoulderSoft_{k}", "Rock", parts, base.variants)


def lava_rock(rng, k):
    """Runde 3: Lava-Brocken (Ring C, Vulkan/Lavafelder): dunkler Basalt-Brocken + gluehender Neon-Keil im Spalt."""
    sz = np.array([rng.uniform(3.4, 4.6), rng.uniform(2.2, 3.0), rng.uniform(3.0, 4.0)])
    yaw = rng.uniform(0, math.pi)
    R = angles(rng.uniform(-0.2, 0.2), yaw, rng.uniform(-0.2, 0.2))
    parts = [block((0, sz[1] * 0.32, 0), tuple(sz), "main", R, "Basalt")]
    if k % 2 == 0:
        s2 = sz * np.array([0.6, 0.75, 0.65])
        a = yaw + rng.uniform(0.8, 1.6)
        parts.append(wedge((math.cos(a) * sz[0] * 0.45, s2[1] * 0.35, math.sin(a) * sz[0] * 0.45), tuple(s2), "main",
                           rot_y(-a), "Basalt"))
    # gluehende Naht quer ueber die Oberseite (Keil ragt ~1/4 seiner Hoehe aus dem Brocken)
    parts.append(wedge((0.0, sz[1] * 0.32 + sz[1] * 0.42, 0.0), (sz[0] * 0.3, sz[1] * 0.5, sz[2] * 0.95), "glow", R, "Neon",
                       cast_shadow=False))
    return Template(f"LavaRock_{k}", "Rock", parts, [{"main": C("#3E3440"), "glow": C("#FF8A3D")},
                                                     {"main": C("#463A48"), "glow": C("#FF9A4A")}])


def band_block(rng, k, mat):
    """Runde 1: Felsbrocken aus dem Schichtstapel (6-14 Studs bei s 0,7-1,5): zwei gestapelte Bloecke + Keil im
    Material und in der Farbe des Bands (Mittelgroesse zwischen Kiesel/Brocken und Tafelberg, Zielbild-Mittelfeld)."""
    base_c = C(ROCKS[mat])
    w, h, d = rng.uniform(7.5, 9.5), rng.uniform(3.6, 4.6), rng.uniform(6.0, 7.5)
    yaw = rng.uniform(0, math.pi)
    parts = [block((0, h * 0.42, 0), (w, h, d), "main", angles(rng.uniform(-0.06, 0.06), yaw, rng.uniform(-0.06, 0.06)), mat,
                   collide=True)]
    w2, h2, d2 = w * rng.uniform(0.6, 0.75), h * rng.uniform(0.75, 0.95), d * rng.uniform(0.6, 0.8)
    off = np.array([rng.uniform(-0.15, 0.15) * w, h * 0.92 + h2 * 0.42, rng.uniform(-0.12, 0.12) * d])
    parts.append(block(off, (w2, h2, d2), "upper", angles(rng.uniform(-0.08, 0.08), yaw + rng.uniform(-0.5, 0.5),
                                                          rng.uniform(-0.08, 0.08)), mat))
    a = yaw + rng.uniform(1.2, 2.0)
    ws = np.array([rng.uniform(3.5, 4.5), h * rng.uniform(0.8, 1.1), rng.uniform(4.0, 5.5)])
    parts.append(wedge((math.cos(a) * w * 0.5, ws[1] * 0.4, math.sin(a) * w * 0.5), tuple(ws), "main", rot_y(-a + math.pi / 2),
                       mat))
    variants = [{"main": darker(base_c, 0.06), "upper": lighter(base_c, 0.08)},
                {"main": darker(base_c, 0.12), "upper": base_c}]
    return Template(f"BandBlock_{mat}_{k}", "Rock", parts, variants)


# Runde 3: Koerper Kalk/Lavendel (unten/oben je ein Band), Hut Kalk-Creme
NEEDLE = [(C("#D2AACE"), C("#F1CF94"), C("#F6E2B4")), (C("#F1CF94"), C("#D8B2D4"), C("#F7E7C2")),
          (C("#DDB6DA"), C("#EEA0A2"), C("#F4D49A")), (C("#E9C68E"), C("#CDA6CC"), C("#F8E8C4"))]


def rock_needle(rng, k):
    """Runde 3: Hoodoo-Nadel wie im Zielbild (3 Teile): runder Schaft aus 2 Zylindern (oben 0,65 x so dick, anderes
    Band) + flacher, ueberstehender Kalk-Hut. 10-17 Studs."""
    H = rng.uniform(9, 15)
    b = rng.uniform(2.8, 3.6)
    h1 = H * rng.uniform(0.5, 0.62)
    lean = rng.uniform(0, 2 * math.pi)
    tilt = math.radians(rng.uniform(1, 4))
    top = np.array([math.cos(lean) * math.sin(tilt) * H, H, math.sin(lean) * math.sin(tilt) * H])
    mid = top * (h1 / H)
    parts = [cyl((0, -0.8, 0), mid + UP * 0.2, b, "body", "Limestone", collide=True),
             cyl(mid - UP * 0.1, top, b * 0.65, "body2", "Limestone")]
    th = rng.uniform(1.1, 1.6)
    parts.append(cyl(top - UP * 0.15, top + UP * th, b * rng.uniform(1.25, 1.5), "tip", "Limestone"))
    variants = [{"body": body, "body2": body2, "tip": tip} for body, body2, tip in NEEDLE]
    return Template(f"RockNeedle_{k}", "Rock", parts, variants)


def copper_rock(rng, k):
    """Kupfer-Brocken: 2-3 gedrehte Bloecke/Keile, Patina als flache Scheiben."""
    D = rng.uniform(5, 7)
    parts = [block((0, D * 0.35, 0), (D, D * 0.75, D * 0.85), "rock", angles(0.2, rng.uniform(0, 3), 0.15), "Sandstone", collide=True)]
    for i in range(2):
        a = rng.uniform(0, 6.28)
        parts.append(wedge((math.cos(a) * D * 0.5, D * 0.25, math.sin(a) * D * 0.5), (D * 0.6, D * 0.5, D * 0.7), "rock",
                           rot_y(-a), "Sandstone"))
    for i in range(3):
        a = rng.uniform(0, 6.28)
        y = rng.uniform(0.35, 0.7) * D
        n = np.array([math.cos(a), 0.4, math.sin(a)])
        parts.append(cyl(np.array([math.cos(a) * D * 0.44, y, math.sin(a) * D * 0.44]),
                         np.array([math.cos(a) * D * 0.44, y, math.sin(a) * D * 0.44]) + n * 0.25, rng.uniform(1.2, 2.0),
                         "patina", "Plaster", cast_shadow=False))
    return Template(f"CopperRock_{k}", "Rock", parts, [{"rock": C("#C98A6E"), "patina": C("#52BCA2")}])


def tuft(rng, k):
    if k < 3:
        parts = []
        for i in range(3):
            a = i * 2.09 + rng.uniform(-0.4, 0.4)
            L = rng.uniform(1.3, 2.2)
            d = tilt_dir(a, math.radians(rng.uniform(8, 22)))
            base = np.array([math.cos(a) * 0.2, -0.15, math.sin(a) * 0.2])
            parts.append(wedge(base + d * L / 2, (0.16, L, 0.55), "main", basis_y(d) @ rot_y(a), "Grass", cast_shadow=False))
        variants = [{"main": cc} for cc in TUFT]
        return Template(f"GrassTuft_{k}", "Flora", parts, variants)
    parts = [block((0, 0.6, 0), (0.18, 1.3, 0.18), "stem", None, "Grass", cast_shadow=False),
             ball((0, 1.35, 0), 0.7, "bloom", "Plaster", cast_shadow=False)]
    variants = [{"stem": C("#8FD07A"), "bloom": cc} for cc in FLOWER]
    return Template(f"Flower_{k}", "Flora", parts, variants)


# ------------------------------------------------------------------ Grosse Einzelstuecke
def cloud():
    return Template("Cloud", "Sky", [ell((0, 0, 0), (100, 22, 80), "main", transparency=0.75, cast_shadow=False)],
                    [{"main": C("#D8C8F0")}])


def fog_ball():
    return Template("FogBall", "Sky", [ell((0, 0, 0), (100, 16, 80), "main", transparency=0.8, cast_shadow=False)],
                    [{"main": C("#EFE8FA")}])


def mist(rng, k):
    """Bodennebel-Schwade: 2-3 flache Ellipsoide uebereinander, leicht versetzt (Hoehe <= 0,15 x Breite)."""
    W = 60.0
    parts = []
    n = 2 + k % 2
    for i in range(n):
        w = W * (1.0 - 0.2 * i) * rng.uniform(0.85, 1.0)
        d = w * rng.uniform(0.55, 0.8)
        h = w * rng.uniform(0.09, 0.14)
        off = np.array([rng.uniform(-0.15, 0.15) * W, i * h * 0.55, rng.uniform(-0.15, 0.15) * W])
        parts.append(ell(off, (w, h, d), "main", rot_y(rng.uniform(0, 3.1)), transparency=round(rng.uniform(0.88, 0.94), 2),
                         cast_shadow=False))
    return Template(f"Mist_{k}", "Mist", parts, [{"main": C("#F4E8F4")}, {"main": C("#EDE4F7")}])


def mist_emitter():
    """Unsichtbares Teil mit ruhigen Nebel-Partikeln (Nebelbecken Ring E)."""
    pt = {"kind": "mist", "rate": 1.5, "lifetime": [12, 18], "size": [20, 40], "speed": [0.5, 1.5], "spread": 180,
          "color": "#F4E8F4", "transparency": [0.85, 1.0]}
    return Template("MistEmitter", "Mist", [block((0, 0, 0), (2, 2, 2), "main", None, "Plastic", transparency=1.0, cast_shadow=False,
                                                  particles=pt)],
                    [{"main": C("#F4E8F4")}])


def light_beam():
    """Lichtstrahl (Neon, Transparenz 0,85, Laenge 600) senkrecht nach oben."""
    parts = [cyl((0, 0, 0), (0, 600, 0), d, "main", "Neon", transparency=t, cast_shadow=False)
             for d, t in ((3.0, 0.4), (7.0, 0.75), (14.0, 0.9))]
    return Template("LightBeam", "Landmark", parts, [{"main": C("#BFF5FF")}, {"main": C("#E3B8FF")}])


def edge_barrier():
    """Unsichtbare Wand am Rand (r ~2008, Hoehe 700). Kann der Builder schon: Transparenz 1 + collide."""
    return Template("EdgeBarrier", "Barrier", [block((0, 330, 0), (200, 760, 4), "main", None, "Plastic", transparency=1.0,
                                                     collide=True, cast_shadow=False)], [{"main": (255, 255, 255)}])


def titan_vein_segment():
    return Template("TitanVein", "Landmark", [block((0, 0, 0), (1.2, 1.0, 1.8), "main", None, "Neon", transparency=0.05,
                                                    cast_shadow=False)],
                    [{"main": C("#9BE8FF")}])


BAND_BLOCK_MATS = ("Sandstone", "Slate", "Limestone")


def volcano_plume(k, rc, depth, rf):
    """Runde 1: Rauchfahne + Glutrand fuer den Vulkan (an die Kratergroesse angepasst, Fusspunkt = Kraterboden-Mitte).
    1 unsichtbares Traegerteil mit Rauch-Partikeln (kind "smoke") und PointLight, 8 Neon-Keile am oberen Kraterhang."""
    # Groesse 26 -> 85 (Vorschlag war 18 -> 55; im Zielbild ist die Fahne oben so breit wie der Kegel)
    # Runde 2 (Offen aus Runde 1: Vulkan praesenter): groessere, laengere Fahne (32 -> 100, 14-22 s, Rate 7; 100 = Partikel-Hoechstgroesse in Roblox)
    smoke = {"kind": "smoke", "rate": 7, "lifetime": [14, 22], "size": [32, 100], "speed": [10, 14], "spread": 8,
             "color": "#D9CCD6", "transparency": [0.3, 1.0]}
    light = {"range": 60, "brightness": 2.0, "role": "ember"}
    parts = [block((0, 3.0, 0), (4, 4, 4), "ember", None, "Plastic", transparency=1.0, cast_shadow=False,
                   particles=smoke, light=light)]
    t = 0.62                                                   # Lage auf dem Innenhang (0 = Boden, 1 = Kraterrand)
    rr = rf + (rc - rf) * t
    y = depth * (3 * t * t - 2 * t ** 3) + 2.2                 # Krater-Profil wie fields.volcano (smoothstep) + halbe Keilhoehe
    slope = math.atan(depth * 6 * t * (1 - t) / max(rc - rf, 1.0))
    for i in range(8):
        a = i * math.pi / 4 + 0.2
        # Keil: Unterseite liegt auf dem Hang, Schraege zeigt zur Kratermitte und nach oben (lokal +Z = hangaufwaerts)
        R = rot_y(math.pi / 2 - a) @ angles(-slope, 0, 0)
        parts.append(wedge((math.cos(a) * rr, y, math.sin(a) * rr), (rng_w(i), 4.0, (rc - rf) * 0.5), "glow", R, "Neon",
                           cast_shadow=False))
    return Template(f"VolcanoPlume_{k}", "Landmark", parts, [{"ember": C("#FF9A4A"), "glow": C("#FFB05A")}])


def rng_w(i):
    return 14.0 + 4.0 * ((i * 37) % 5) / 4.0


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
        "Boulder": [add(boulder(rng, k)) for k in range(4)],
        "LavaRock": [add(lava_rock(np.random.default_rng(4410 + k), k)) for k in range(3)],
        "SteamVent": [add(steam_vent(rng, k)) for k in range(2)],
        "Reeds": [add(reeds(rng, k)) for k in range(4)],
        "PearlCactus": [add(pearl_cactus(rng, k)) for k in range(3)] + [add(pearl_cactus(rng, 3, True))],
        "Fossil": [add(fossil(rng, k)) for k in range(2)],
        **{"Pebble_" + m: [add(pebble(rng, k, m)) for k in range(3)] for m in ROCKS},
        "CopperRock": [add(copper_rock(rng, k)) for k in range(3)],
        **{"BandBlock_" + m: [add(band_block(rng, k, m)) for k in range(3)] for m in BAND_BLOCK_MATS},
        "RockNeedle": [add(rock_needle(rng, k)) for k in range(4)],
        "Tuft": [add(tuft(rng, k)) for k in range(5)],
        "Cloud": [add(cloud())], "FogBall": [add(fog_ball())], "LightBeam": [add(light_beam())],
        "EdgeBarrier": [add(edge_barrier())], "TitanVein": [add(titan_vein_segment())],
        "Mist": [add(mist(rng, k)) for k in range(4)], "MistEmitter": [add(mist_emitter())],
    }
    groups["BoulderSoft"] = [add(boulder_soft(tp, k)) for k, tp in enumerate(groups["Boulder"])]
    return t, groups
