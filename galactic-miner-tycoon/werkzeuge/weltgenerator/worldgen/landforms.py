"""Felsformen: Tafelberge/Buttes/Spitzen, Massive mit Canyons, Danxia-Kaemme, Hoodoos, Finnen, Bogen, Tunnel."""
from __future__ import annotations

import math

import numpy as np
from scipy.spatial import cKDTree

from .ctx import Ctx
from .materials import MAT, band_boundaries, s_smooth
from .noise import smoothstep as ss
from .world import angles, rot_y

TAN = lambda deg: math.tan(math.radians(deg))  # noqa: E731
MIN_OP_R = 4.0      # Zusatzformen duenner als Durchmesser 8 werden bei 4-Stud-Voxeln klumpig oder verschwinden
MIN_HAT_R = 6.0


def check_ops(ops):
    """Warnungen fuer zu duenne Terrain-Zusatzformen (Radius < 4 bzw. Block-Kante < 8, Luft ausgenommen)."""
    thin = []
    for o in ops:
        if o["material"] == "Air":
            continue
        if o["op"] in ("Ball", "Cylinder") and o["r"] < MIN_OP_R - 1e-6:
            thin.append(o)
        elif o["op"] in ("Block", "Wedge") and min(o["size"]) < 2 * MIN_OP_R - 1e-6:
            thin.append(o)
    return thin


# ------------------------------------------------------------------ Hilfen
def cf(x, y, z, R=None):
    R = np.eye(3) if R is None else np.asarray(R)
    return [float(x), float(y), float(z)] + [float(v) for v in R.ravel()]


def op_cyl(c: Ctx, x, y, z, h, r, mat, R=None, tag=None):
    c.ops.append({"op": "Cylinder", "cf": cf(x, y, z, R), "height": float(h), "r": float(r), "material": mat})


def op_ball(c: Ctx, x, y, z, r, mat):
    c.ops.append({"op": "Ball", "c": [float(x), float(y), float(z)], "r": float(r), "material": mat})


def op_block(c: Ctx, x, y, z, size, mat, R=None):
    c.ops.append({"op": "Block", "cf": cf(x, y, z, R), "size": [float(s) for s in size], "material": mat})


def set_mat(c: Ctx, sl, sel, name, keep_strata=False):
    if not hasattr(c, "mat_override"):
        c.mat_override = np.zeros(c.H.shape, np.uint8)
        c.override_keep_strata = np.zeros(c.H.shape, bool)
    v = c.mat_override[sl]
    v[sel] = MAT[name] + 1
    if keep_strata:
        c.override_keep_strata[sl] |= sel


def set_strata_top(c: Ctx, sl, sel, name):
    if not hasattr(c, "strata_top"):
        c.strata_top = np.zeros(c.H.shape, np.uint8)
    v = c.strata_top[sl]
    v[sel] = MAT[name] + 1


def claim(c: Ctx, sl, sel):
    c.mask("claimed")[sl] |= sel


SOFT = ("wash", "wash_floor", "dune", "fan", "playa", "canyon_floor")


def clear_soft(c: Ctx, sl, sel):
    """Fels ueberdeckt weiche Boeden (Wash-Sand usw.)."""
    for name in SOFT:
        if name in c.masks:
            c.masks[name][sl] &= ~sel


def is_free(c: Ctx, x, z, rad, wash_margin=20.0, allow=None):
    sl = c.win(x, z, rad)
    lx, lz = c.local(sl)
    circ = (lx - x) ** 2 + (lz - z) ** 2 < rad * rad
    if not circ.any():
        return False
    if (c.mask("claimed")[sl] & circ).any():
        return False
    if (c.wash_dist[sl][circ] < wash_margin).any():
        return False
    if c.void[sl][circ].any():
        return False
    return True


def poly_sdf(x, z, vx, vz):
    """Exakter Abstand zu einem konvexen Polygon (negativ innen)."""
    n = len(vx)
    dmin = np.full(x.shape, 1e9)
    inside = np.ones(x.shape, bool)
    for i in range(n):
        ax, az_ = vx[i], vz[i]
        bx, bz = vx[(i + 1) % n], vz[(i + 1) % n]
        ex, ez = bx - ax, bz - az_
        wx, wz = x - ax, z - az_
        t = np.clip((wx * ex + wz * ez) / (ex * ex + ez * ez), 0, 1)
        dx, dz = wx - ex * t, wz - ez * t
        dmin = np.minimum(dmin, np.hypot(dx, dz))
        cross = ex * wz - ez * wx
        inside &= cross > 0
    return np.where(inside, -dmin, dmin)


def make_poly(c: Ctx, cx, cz, R, aspect, rot, nv=None, jitter=0.07):
    rng = c.rng
    nv = int(nv or rng.integers(7, 10))
    ang = np.linspace(0, 2 * math.pi, nv, endpoint=False) + rng.uniform(-0.18, 0.18, nv) * (1 + 2 * jitter) + rng.uniform(0, 6.3)
    ang = np.sort(ang)
    rad = R * (1.0 + rng.uniform(-jitter, jitter, nv))
    sx, sz = math.sqrt(aspect), 1.0 / math.sqrt(aspect)
    px, pz = rad * np.cos(ang) * sx, rad * np.sin(ang) * sz
    cr, sr = math.cos(rot), math.sin(rot)
    vx = cx + px * cr - pz * sr
    vz = cz + px * sr + pz * cr
    # Reihenfolge so, dass "innen" = links (cross > 0) fuer unser Koordinatensystem
    area = 0.5 * np.sum(vx * np.roll(vz, -1) - np.roll(vx, -1) * vz)
    if area < 0:
        vx, vz = vx[::-1], vz[::-1]
    return vx, vz


# ------------------------------------------------------------------ Tafelberg / Butte
def apron(q, qa):
    """Konkaves Schutt-Profil 0..1: steiler oberer Teil (bis qa, ~30-40 Grad), dann langer flacher Fuss (<= ~5 Grad),
    der in den Boden auslaeuft. q = 0 am Fels, 1 am Fuss."""
    up = 0.18 + 0.82 * np.clip(1.0 - q / qa, 0, 1) ** 1.4
    lo = 0.18 * np.clip(1.0 - (q - qa) / (1.0 - qa), 0, 1) ** 1.1
    return np.where(q < qa, up, lo)


def gfan_of(g):
    """Breiter Schuttkegel unter einer Rinne (g = schmale Rinnen-Funktion 0..1)."""
    return np.clip(g * 1.6, 0, 1) ** 0.5


def set_talus_q(c: Ctx, sl, sel, q):
    """Relative Lage auf der Halde (0 = oben am Fels, 1 = Fuss) fuer das Zerfasern der Unterkante."""
    if not hasattr(c, "talus_q"):
        c.talus_q = np.full(c.H.shape, np.nan, np.float32)
    v = c.talus_q[sl]
    v[sel] = q[sel]


def flat_s(c: Ctx, sl, sel, sval):
    """Konstanter Schichtversatz in einem Bereich (waagerechte Baender)."""
    c.S_local[sl] = np.where(sel, sval, c.S_local[sl])
    c.S_local_w[sl] = np.where(sel, 1.0, c.S_local_w[sl])


def mesa(c: Ctx, cx, cz, diam, height, stage="mesa", aspect=None, rot=None, nsteps=None, talus=1.0,
         top_patch=None, base=None, record=True, gully=True, nv=None, rough=None):
    """Geschichteter Tafelberg wie im Referenzbild: gestapelte Stufen mit flachen Baenken und fast senkrechten
    Waenden, jede Stufenkante ein abgerundetes Polygon. Stufen liegen auf Bandgrenzen (je Stufe 1-2 Streifen)."""
    rng = c.rng
    R = diam / 2.0
    aspect = aspect if aspect is not None else (rng.uniform(1.0, 1.55) if stage == "mesa" else rng.uniform(1.0, 1.25))
    rot = rot if rot is not None else rng.uniform(0, math.pi)
    # Review: lange, konkave Schutt-Schuerze, Laenge 0,6-0,9 x Wandhoehe, Hoehe 0,25-0,35 x Wandhoehe
    tal_l = talus * height * rng.uniform(0.5, 0.65)
    pad = R * math.sqrt(aspect) + tal_l * 1.6 + 16
    sl = c.win(cx, cz, pad)
    x, z = c.local(sl)
    # kleine Formen (Buttes, kleine Mesas): unregelmaessiger Grundriss mit senkrechten Rippen und Rinnen
    small = stage == "butte" or R < 50
    if rough is None:
        rough = small
    rr = min(R * (0.12 if rough else 0.22), 6.0 if rough else 12.0)
    vx, vz = make_poly(c, cx, cz, max(R - rr, R * 0.5), aspect, rot, nv=nv or (int(rng.integers(6, 9)) if rough else None),
                       jitter=0.17 if rough else 0.07)
    d = poly_sdf(x, z, vx, vz) - rr
    d = d + c.nz.fbm("mesaedge", x, z, 70, 2) * 1.3 + (c.nz.fbm("mesaedge2", x, z, 22, 2) * 2.2 if rough else 0.0)
    Hl = c.H[sl]
    if base is None:
        foot = d < 0
        base = float(np.percentile(Hl[foot], 35)) if foot.any() else float(c.h_at(cx, cz))
    sc = float(s_smooth(c, np.array(cx), np.array(cz)))
    if nsteps is None:
        nsteps = (int(rng.integers(2, 5)) if R >= 50 else int(rng.integers(2, 4))) if stage == "mesa" else int(rng.integers(1, 3))
    bounds = band_boundaries(base + height * 0.6, base + height * 1.15, sc, min_band=4)
    top = min(bounds, key=lambda b: abs(b[0] - (base + height)))[0] if bounds else base + height
    # aufeinanderfolgende Bandgrenzen von unten nach oben; Stufen < 7 Studs zusammenlegen
    lows = [b[0] for b in band_boundaries(base + 0.14 * height, top - 6.5, sc, min_band=4)]
    levels = []
    last = base
    for y in lows:
        if y - last >= 7.0 and top - y >= 7.0:
            levels.append(y)
            last = y
    while len(levels) > nsteps - 1:          # gleichmaessig ausduennen
        gaps = [levels[i + 1] - levels[i - 1] if 0 < i < len(levels) - 1 else 1e9 for i in range(len(levels))]
        levels.pop(int(np.argmin(gaps)) if len(levels) > 2 else 0)
    levels = levels + [top]
    s = -d
    big = (stage == "mesa" and R > 42 and gully) or rough
    if big:
        th = np.arctan2(z - cz, x - cx)
        per = 2 * math.pi * R * (1 + aspect) / 2
        k = max(5, int(round(per / (rng.uniform(13, 19) if rough else rng.uniform(20, 35)))))
        # unregelmaessige Abstaende (starke Phasen-Verzerrung), je Rinne eigene Tiefe; ~20 % fallen aus, nur jede
        # zweite bekommt einen Schuttkegel/Faecher -> kein Strahlenkranz
        ph = k * th + rng.uniform(0, 6.3) + 2.2 * c.nz.fbm("gul", x, z, 70, 2)
        gi = np.mod(np.floor(ph / (2 * math.pi) + 0.5), k)
        hs = np.mod(np.sin(gi * 12.9898 + cx * 0.0137 + cz * 0.0071) * 43758.5453, 1.0)   # ohne rng (Reihenfolge bleibt)
        keep = (hs > 0.2).astype(float)
        has_fan = (np.mod(hs * 7.31, 1.0) < 0.5).astype(float)
        cosv = np.maximum(0.0, np.cos(ph))
        g = cosv ** (4 if rough else 8) * keep * (0.55 + 0.6 * np.mod(hs * 3.7, 1.0))
        gw = cosv ** 2 * keep * has_fan      # breite, flache Schuttkegel nur unter einem Teil der Rinnen
        rmin0 = R / math.sqrt(aspect)
        g = g * ss(0.3 * rmin0, 0.65 * rmin0, np.hypot(x - cx, z - cz))   # Rinnen nur am Rand, keine Loecher oben
        gd = rng.uniform(3.0, 4.5) if rough else rng.uniform(3.0, 6.0)
    else:
        g = np.zeros_like(s)
        gw = g
        gd = 0.0
    h = np.full(s.shape, base)
    inset = 0.0
    prev = base
    insvar = 1.0 + 0.15 * c.nz.fbm("insv", x, z, 90, 2)
    rmin = R / math.sqrt(aspect)
    wws = [max(1.2, (lv - p) * TAN(8)) for lv, p in zip(levels, [base] + levels[:-1])]     # Waende >= 82 Grad
    if stage == "mesa" and not small:
        inss = [rng.uniform(9, 16) for _ in levels[:-1]]
        budget = 0.62 * rmin - sum(wws)
    elif stage == "mesa":
        inss = [rng.uniform(4, 8) for _ in levels[:-1]]
        budget = 0.4 * rmin - sum(wws)
    else:
        inss = [rng.uniform(2, 4) for _ in levels[:-1]]
        budget = 0.3 * rmin - sum(wws)
    if inss and sum(inss) > budget:                # Oberseite bleibt breit (keine Spitze)
        f = max(budget, 0.0) / sum(inss)
        inss = [v * f for v in inss]
    for i, lv in enumerate(levels):
        dh = lv - prev
        ww = wws[i]
        s_eff = s - g * gd * (1.0 + 0.6 * i / max(1, len(levels) - 1))
        ramp = np.clip((s_eff - inset * insvar) / ww, 0, 1)
        h = h + dh * ramp
        prev = lv
        inset = inset + ww + (inss[i] if i < len(levels) - 1 else 0)
    roof = rng.uniform(0.3, 0.9) if stage == "mesa" else 0.2
    h = h + roof * ss(inset, inset + 30, s)
    mesa_h = np.where(s > -1, h, -1e9)
    # Schutt-Schuerze (Rock): oben steil (~32-40 Grad), langer flacher Fuss (<= 5 Grad), Unterkante zerfasert in den
    # Boden (materials.py). Laenge ~0,6-0,8 x Wandhoehe. Unter jeder Rinne ein Schuttkegel mit Mini-Faecher aus Sand.
    T = max(4.0, height * rng.uniform(0.14, 0.19) * min(1.0, talus * 1.4))
    L1, L2 = 1.25 * T, 0.18 * T / TAN(3.0)
    tal_l = L1 + L2
    qa = L1 / tal_l
    gfan = gfan_of(g) * (gw > 0)
    gs = 0.5 + 0.5 * c.nz.fbm("talcone", x, z, 80, 2)
    # Kegel unter den Rinnen breit und flach (sonst entstehen radiale Grate, die den flachen Fuss zerschneiden)
    tl = tal_l * (1.0 + 0.06 * gs + 0.14 * gw)
    Tg = T * (1.0 + 0.05 * gs + 0.06 * gw)
    q_raw = (d + 0.06 * tl) / tl
    q = np.clip(q_raw, 0, 1)
    tal = base + Tg * apron(q, qa)
    # Liegt das Gelaende hinter dem Fuss tiefer als base (Hanglage), laeuft der Fuss mit 3,5 Grad weiter, bis er das
    # Gelaende trifft: keine Stufe am Haldenende (sonst gehen dort Bauflaechen verloren). Nicht in Washes/Wasser.
    ext = np.clip(q_raw - 1.0, 0, None) * tl
    soft = c.mask("wash")[sl] | ~np.isnan(c.wl[sl]) if hasattr(c, "wl") else c.mask("wash")[sl]
    tal = np.where(q_raw < 1, tal, np.where((ext < 1.5 * tl + 20) & ~soft, base - ext * TAN(3.5), -1e9))
    new = np.maximum(Hl, np.maximum(mesa_h, tal))
    body = (mesa_h >= tal) & (mesa_h > Hl + 0.5)
    tmask = (tal > mesa_h) & (tal > Hl + 0.25) & (q_raw < 1)
    c.H[sl] = new
    c.mask("mesa")[sl] |= body
    c.mask("talus")[sl] |= tmask
    set_talus_q(c, sl, tmask, q)
    c.mask("minifan")[sl] |= tmask & (gfan > 0.45) & (q > qa * 0.8)
    clear_soft(c, sl, body | tmask)
    # Hindernis nur am steilen oberen Teil; der flache Fuss bleibt Bauzone
    q12 = qa
    c.obstacle[sl] |= body | (tmask & (q < q12))
    claim(c, sl, d < tal_l + 18)
    if top_patch:
        topsel = body & (s > inset - 2) & (c.nz.fbm("toppatch", x, z, 40, 2) > -0.1)
        set_strata_top(c, sl, topsel, top_patch)
    # Schichten innerhalb der Mesa waagerecht (konstanter Versatz): keine 4-Stud-Treppen in den Baendern
    flat_s(c, sl, d < tal_l + 6, sc)
    if record:
        c.feat["mesa"].append({"x": cx, "z": cz, "R": R * math.sqrt(aspect), "Rmin": R / math.sqrt(aspect), "base": base,
                               "top": top, "talus": tal_l, "stage": stage, "levels": levels, "rot": rot,
                               "top_inset": inset, "aspect": aspect, "R0": R})
    return top


def spire(c: Ctx, cx, cz, base_d, tip_d, height, base=None):
    rb, rt = base_d / 2, tip_d / 2
    pad = rb * 2.2 + 6
    sl = c.win(cx, cz, pad)
    x, z = c.local(sl)
    rho = np.hypot(x - cx, z - cz) * (1 + 0.12 * c.nz.fbm("spire", x, z, 9, 2))
    Hl = c.H[sl]
    if base is None:
        base = float(Hl[rho < rb].min()) if (rho < rb).any() else float(c.h_at(cx, cz))
    q = np.clip((rho - rt) / (rb - rt), 0, 1)
    # leicht gestuft: harte Baender bilden Simse
    prof = (1 - q) ** 0.75
    prof = np.round(prof * 9) / 9 * 0.35 + prof * 0.65
    hs = base + height * prof
    hs = np.where(rho < rb, hs, -1e9)
    tal_r = rb * 1.6 + 2
    tq = np.clip((rho - rb * 0.6) / (tal_r - rb * 0.6), 0, 1)
    tal = base + rb * 0.55 * (1 - tq) ** 1.5
    tal = np.where(tq < 1, tal, -1e9)
    new = np.maximum(Hl, np.maximum(hs, tal))
    body = (hs >= tal) & (hs > Hl + 0.5)
    tm = (tal > hs) & (tal > Hl + 0.3)
    c.H[sl] = new
    c.mask("spire")[sl] |= body
    c.mask("talus")[sl] |= tm
    clear_soft(c, sl, body | tm)
    c.obstacle[sl] |= body | tm
    claim(c, sl, rho < tal_r + 14)
    flat_s(c, sl, rho < tal_r, float(s_smooth(c, np.array(cx), np.array(cz))))
    c.feat["spire"].append({"x": cx, "z": cz, "R": rb, "base": base, "top": base + height})
    return base + height


# ------------------------------------------------------------------ Danxia-Kamm
class Curve:
    def __init__(self, p0, p1, bend, n=256):
        p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
        d = p1 - p0
        nrm = np.array([-d[1], d[0]]) / (np.linalg.norm(d) + 1e-9)
        ctrl = (p0 + p1) / 2 + nrm * bend
        t = np.linspace(0, 1, n)[:, None]
        self.pts = (1 - t) ** 2 * p0 + 2 * (1 - t) * t * ctrl + t ** 2 * p1
        tan = np.gradient(self.pts, axis=0)
        self.tan = tan / np.linalg.norm(tan, axis=1)[:, None]
        self.nrm = np.stack([-self.tan[:, 1], self.tan[:, 0]], 1)
        seg = np.linalg.norm(np.diff(self.pts, axis=0), axis=1)
        self.s = np.concatenate([[0], np.cumsum(seg)])
        self.length = self.s[-1]
        self.tree = cKDTree(self.pts)

    def local(self, x, z):
        pts = np.stack([x.ravel(), z.ravel()], 1)
        _, i = self.tree.query(pts)
        v = pts - self.pts[i]
        u = np.sum(v * self.nrm[i], 1)
        a = np.sum(v * self.tan[i], 1)
        s = self.s[i] + np.where((i == 0) | (i == len(self.s) - 1), a, 0.0)
        return s.reshape(x.shape), u.reshape(x.shape), i.reshape(x.shape)


def ridge(c: Ctx, p0, p1, bend, peaks, base=None, front=1, dip_deg=13.0, face_deg=66.0, back_deg=34.0,
          width_cap=None, gaps=(), name="ridge"):
    """Danxia-Kamm als scharfgratige Haifischflosse: steile Stirnseite mit Rinnen alle 18-30 Studs und Rippen,
    Rueckseite ~34 Grad mit verzweigten Rinnen, gezackter Grat, Schutthalde vor der Stirn.
    peaks: [(t, Hoehe ueber Basis, Breite in t)]; gaps: [(t, Breite in Studs, Boden ueber Basis)]."""
    dip_deg = min(dip_deg, 15.0)
    cv = Curve(p0, p1, bend)
    L = cv.length
    hmax = max(p[1] for p in peaks)
    back_w = hmax / TAN(back_deg) + 40
    pad = L / 2 + back_w + 60
    mid = cv.pts[len(cv.pts) // 2]
    sl = c.win(mid[0], mid[1], pad)
    x, z = c.local(sl)
    s, u, _ = cv.local(x, z)
    t = s / L
    u = u * front           # u < 0 : Stirnseite
    Hl = c.H[sl]
    if base is None:
        base = float(np.percentile(c.H[c.win(mid[0], mid[1], 60)], 30))
    crest = np.zeros_like(t)
    for (tp, hp, wp) in peaks:
        crest = np.maximum(crest, hp * np.clip(1 - (np.abs(t - tp) / wp) ** 1.6, 0, 1) ** 0.45)
    crest = crest * ss(-0.04, 0.07, t) * ss(1.04, 0.93, t)
    zack = c.nz.ridged(name + "zack", s, np.zeros_like(s) + 7.0, 38, 2, sharp=1.3)
    fine = c.nz.ridged(name + "zack2", s, np.zeros_like(s) + 3.0, 13, 1, sharp=1.3)
    cf = np.clip(crest / 50, 0, 1)
    crest = crest + ((zack - 0.45) * 8.0 + (fine - 0.5) * 2.0) * cf
    for (tg, wg, hg) in gaps:
        gw = wg / L
        crest = np.minimum(crest, hg + np.maximum(0, np.abs(t - tg) - gw / 2) * L * TAN(40))
    au = np.abs(u)
    # Stirnseite: Rippen und Rinnen (Periode 18-30), Rinnen oben breiter
    per = 18.0 + 12.0 * (0.5 + 0.5 * c.nz.fbm(name + "per", x, z, 200, 1))
    ph = 2 * math.pi * s / per + 1.1 * c.nz.fbm(name + "fur", x, z, 70, 2)
    gully = (0.5 + 0.5 * np.cos(ph)) ** 3
    front_h = crest - (au + gully * 7.0 * ss(0, 18, au)) * TAN(face_deg)
    bg = c.nz.ridged(name + "bg", x, z, 42, 3, sharp=1.8)
    back_h = crest - u * TAN(back_deg) - bg * 10.0 * ss(0, 30, u)
    hr = np.where(u < 0, front_h, back_h)
    # Schutthalde vor der Stirnseite (Mud)
    foot_u = crest / TAN(face_deg)
    T = np.maximum(0.2 * crest, 1.0)
    L1, L2 = 1.25 * T, 0.18 * T / TAN(3.0)
    Ltal = L1 + L2
    qa_r = L1 / Ltal
    q = np.clip((au - foot_u + 0.2 * L1) / Ltal, 0, 1)
    tal = np.where((u < 0) & (q < 1), T * apron(q, qa_r), -1e9)
    hrel = np.maximum(hr, tal)
    hrel = np.where(hrel > -0.5, hrel, -1e9)
    hnew = base + hrel
    new = np.maximum(Hl, hnew)
    body = (hr >= tal) & (hnew > Hl + 0.5)
    tm = (tal > hr) & (hnew > Hl + 0.3)
    c.H[sl] = new
    c.mask("ridge")[sl] |= body
    c.mask("talus")[sl] |= tm
    set_talus_q(c, sl, tm, q)
    clear_soft(c, sl, body | tm)
    c.obstacle[sl] |= body | (tm & (q < qa_r))
    claim(c, sl, (hnew > Hl - 1.0) & (hrel > -6))
    # lokal geneigte Schichten (max. 15 Grad), Fall zur Rueckseite
    sc = float(s_smooth(c, np.array(mid[0]), np.array(mid[1])))
    w = ss(-6, 10, hrel) * ss(1.25, 0.95, np.abs(t - 0.5) * 2)
    loc = sc + TAN(dip_deg) * (s - L / 2) * (1 if front > 0 else -1)
    c.S_local[sl] = np.where(w > c.S_local_w[sl], loc, c.S_local[sl])
    c.S_local_w[sl] = np.maximum(c.S_local_w[sl], w)
    c.feat["ridge"].append({"curve": cv, "base": base, "front": front, "name": name, "peaks": peaks})
    return cv, base


# ------------------------------------------------------------------ Finne (duenne Wand) mit Fenstern
def fin(c: Ctx, p0, p1, thick, height, base=None, windows=1, win_size=(8.0, 12.0), name="fin", arch=None,
        mask_name="fin", tunnel=None):
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    d = p1 - p0
    L = float(np.linalg.norm(d))
    tx, tz = d / L
    nx, nz_ = -tz, tx
    mid = (p0 + p1) / 2
    pad = L / 2 + thick * 3 + 20
    sl = c.win(mid[0], mid[1], pad)
    x, z = c.local(sl)
    a = (x - mid[0]) * tx + (z - mid[1]) * tz
    u = (x - mid[0]) * nx + (z - mid[1]) * nz_
    Hl = c.H[sl]
    if base is None:
        base = float(np.percentile(c.H[c.win(mid[0], mid[1], 20)], 30))
    wob = c.nz.fbm(name + "w", x, z, 40, 2) * thick * 0.25
    half = thick / 2 * (1.0 + 0.6 * ss(height * 0.5, 0, np.zeros_like(u)))
    end = ss(L / 2 + 2, L / 2 - thick * 1.5, np.abs(a))
    topn = height * (0.85 + 0.15 * c.nz.fbm(name + "t", x, z, 30, 2)) * end ** 0.5
    side = np.clip(1 - (np.abs(u + wob) - half) / (thick * 0.9), 0, 1)
    hf = base + topn * side ** 0.35
    # breiter Fuss mit Schutt
    fq = np.clip(1 - (np.abs(u + wob) - half) / (thick * 1.6 + 6), 0, 1)
    foot = np.where((fq > 0) & (end > 0.02), base + height * 0.18 * fq ** 1.5 * end, -1e9)
    hf = np.where((side > 0) & (end > 0.02), hf, -1e9)
    hnew = np.maximum(hf, foot)
    new = np.maximum(Hl, hnew)
    body = (hf >= foot) & (hf > Hl + 1.0)
    tm = (foot > hf) & (foot > Hl + 0.3)
    c.H[sl] = new
    c.mask(mask_name)[sl] |= body
    c.mask("talus")[sl] |= tm
    clear_soft(c, sl, body | tm)
    c.obstacle[sl] |= body | tm
    claim(c, sl, np.abs(u) < thick * 2 + 12)
    flat_s(c, sl, np.abs(u) < thick * 2 + 8, float(s_smooth(c, np.array(mid[0]), np.array(mid[1]))))
    yaw = math.atan2(nx, nz_)  # lokales +Z zeigt quer zur Wand
    R = rot_y(yaw)
    out = []
    if windows:
        for k in range(windows):
            fa = (k + 1) / (windows + 1) + c.u(-0.1, 0.1)
            wx, wz = p0 + d * fa
            wy = base + height * c.u(0.3, 0.45) + win_size[1] / 2
            op_block(c, wx, wy, wz, (win_size[0], win_size[1], thick * 2.5 + 8), "Air", R)
            out.append((wx, wy, wz))
    c.feat[mask_name].append({"p0": p0, "p1": p1, "base": base, "height": height, "thick": thick})
    return base, R, out


def arch(c: Ctx, cx, cz, yaw_deg, span, clear, thick=16.0, wall_h=None):
    """Felsbogen: dicke Wand (Hoehenkarte) mit Luft-Zylinder + Luft-Quader als Oeffnung."""
    wall_h = wall_h or clear + 14
    L = span + 2 * 30
    ta = math.radians(yaw_deg)
    tx, tz = math.sin(ta), -math.cos(ta)
    p0 = (cx - tx * L / 2, cz - tz * L / 2)
    p1 = (cx + tx * L / 2, cz + tz * L / 2)
    base, R, _ = fin(c, p0, p1, thick, wall_h, windows=0, name="arch", mask_name="fin")
    rad = span / 2
    yc = base + clear - rad
    nx, nz_ = -tz, tx
    # Zylinder-Achse (lokal Y) quer zur Wand: R = Ry(yaw) * Rx(90)
    Rc = rot_y(math.atan2(nx, nz_)) @ angles(math.pi / 2, 0, 0)
    op_cyl(c, cx, yc, cz, thick * 3 + 10, rad, "Air", Rc)
    if yc > base - 2:
        hb = yc - (base - 3)
        op_block(c, cx, (yc + base - 3) / 2, cz, (span, hb, thick * 3 + 10), "Air", rot_y(math.atan2(nx, nz_)))
    c.feat["arch"].append({"x": cx, "z": cz, "base": base, "yaw": yaw_deg, "span": span, "clear": clear})
    return base


# ------------------------------------------------------------------ Hoodoo
HOODOO_NECK = ["Sandstone", "Slate", "Sandstone", "Rock"]


def hoodoo(c: Ctx, x0, z0, total, base=None):
    """Schlanker Hoodoo: Fuss aus Hoehenkarte (Baender), Koerper als Zylinder-Stapel mit Hals/Wulst,
    Segmentfarben = Schichtband der absoluten Hoehe (Baender laufen ueber alle Hoodoos durch),
    Hut aus hartem Kalkstein, nur wenig breiter als der Hals."""
    from .materials import BAND_LUT, STRATA_PERIOD
    from .layout import STRATA_BASE
    from .world import TERRAIN_MATERIALS
    rng = c.rng
    rf = rng.uniform(8.0, 10.5)
    hf = rng.uniform(6, 11) * min(1.0, total / 45 + 0.5)
    sl = c.win(x0, z0, rf * 2.4)
    x, z = c.local(sl)
    rho = np.hypot(x - x0, z - z0) * (1 + 0.1 * c.nz.fbm("hdf", x, z, 8, 1))
    Hl = c.H[sl]
    if base is None:
        base = float(Hl[rho < rf].min()) if (rho < rf).any() else float(c.h_at(x0, z0))
    q = np.clip(rho / (rf * 1.35), 0, 1)
    prof = np.where(rho < rf * 0.5, 1.0, (1 - np.clip((rho - rf * 0.5) / (rf * 0.9), 0, 1)) ** 1.5)
    hfoot = np.where(rho < rf * 1.4, base + hf * prof, -1e9)
    tal = np.where(q < 1, base + rf * 0.3 * (1 - q) ** 1.5, -1e9)
    hn = np.maximum(hfoot, tal)
    c.H[sl] = np.maximum(Hl, hn)
    c.mask("hoodoo_foot")[sl] |= (hfoot >= tal) & (hfoot > Hl + 0.5)
    c.mask("talus")[sl] |= (tal > hfoot) & (tal > Hl + 0.3)
    c.obstacle[sl] |= rho < rf * 1.15
    s_here = int(round(float(s_smooth(c, np.array(x0), np.array(z0))))) % STRATA_PERIOD
    hat_h = rng.uniform(3.5, 5.0)
    y0 = base + hf - 1.0
    y1 = base + total - hat_h
    r0 = rng.uniform(4.8, 6.0)                 # Roblox-Voxel 4 Studs: Hals mindestens Durchmesser 8
    nb = rng.choice([1.0, 1.5, 2.0])
    ph = rng.uniform(0, 2 * math.pi)
    seg_h = rng.uniform(4.5, 6.0)
    nseg = max(2, int(round((y1 - y0) / seg_h)))
    hseg = (y1 - y0) / nseg
    lean = rng.uniform(0, 2 * math.pi)
    lx, lz = math.cos(lean) * 0.035, math.sin(lean) * 0.035
    cx, cz = x0, z0
    rad = r0
    for i in range(nseg):
        tt = (i + 0.5) / nseg
        rad = r0 * (0.88 + 0.16 * math.sin(2 * math.pi * nb * tt + ph)) * (1.0 - 0.12 * tt)
        rad = max(rad, MIN_OP_R)
        yc = y0 + (i + 0.5) * hseg
        cx += lx * hseg
        cz += lz * hseg
        m = TERRAIN_MATERIALS[int(BAND_LUT[int(math.floor(yc + s_here + STRATA_BASE)) % STRATA_PERIOD])]
        op_cyl(c, cx, yc, cz, hseg + 0.8, rad, m)
    hat_r = max(MIN_HAT_R, rad + rng.uniform(1.5, 2.5))
    op_cyl(c, cx, y1 + hat_h / 2, cz, hat_h, hat_r, "Limestone")
    rb = max(MIN_OP_R, hat_r * 0.6)
    op_ball(c, cx, y1 + hat_h - rb + 1.4, cz, rb, "Limestone")
    top = y1 + hat_h + 1.0
    c.feat["hoodoo"].append({"x": x0, "z": z0, "base": base, "top": top, "hat_r": hat_r, "foot_r": rf})
    return top
