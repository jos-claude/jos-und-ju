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


def make_poly(c: Ctx, cx, cz, R, aspect, rot, nv=None):
    rng = c.rng
    nv = int(nv or rng.integers(7, 10))
    ang = np.linspace(0, 2 * math.pi, nv, endpoint=False) + rng.uniform(-0.18, 0.18, nv) + rng.uniform(0, 6.3)
    ang = np.sort(ang)
    rad = R * (1.0 + rng.uniform(-0.07, 0.07, nv))
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
def mesa(c: Ctx, cx, cz, diam, height, stage="mesa", aspect=None, rot=None, nsteps=None, talus=1.0,
         top_patch=None, base=None, record=True, gully=True):
    """Geschichteter Tafelberg. Stufen liegen auf Bandgrenzen (Oberseiten zeigen das Band)."""
    rng = c.rng
    R = diam / 2.0
    aspect = aspect if aspect is not None else (rng.uniform(1.0, 1.6) if stage == "mesa" else rng.uniform(1.0, 1.3))
    rot = rot if rot is not None else rng.uniform(0, math.pi)
    tal_l = talus * height * (rng.uniform(0.30, 0.42) if stage == "mesa" else rng.uniform(0.32, 0.45))
    pad = R * math.sqrt(aspect) + tal_l * 1.7 + 16
    sl = c.win(cx, cz, pad)
    x, z = c.local(sl)
    rr = min(R * 0.18, 10.0)
    vx, vz = make_poly(c, cx, cz, max(R - rr, R * 0.5), aspect, rot)
    d = poly_sdf(x, z, vx, vz) - rr
    d = d + c.nz.fbm("mesaedge", x, z, 38, 3) * 3.2
    Hl = c.H[sl]
    if base is None:
        foot = d < 0
        base = float(np.percentile(Hl[foot], 35)) if foot.any() else float(c.h_at(cx, cz))
    sc = float(s_smooth(c, np.array(cx), np.array(cz)))
    # Stufen auf Bandgrenzen
    if nsteps is None:
        nsteps = int(rng.integers(3, 7)) if stage == "mesa" else int(rng.integers(2, 4))
    bounds = band_boundaries(base + height * 0.55, base + height * 1.12, sc, min_band=6)
    top = min(bounds, key=lambda b: abs(b[0] - (base + height)))[0] if bounds else base + height
    lows = [b[0] for b in band_boundaries(base + 0.18 * height, top - 6, sc, min_band=4)]
    chosen = []
    for y in sorted(lows, key=lambda v: rng.uniform()):
        if all(abs(y - q) >= 7 for q in chosen) and abs(top - y) >= 7:
            chosen.append(y)
        if len(chosen) >= nsteps - 1:
            break
    levels = sorted(chosen) + [top]
    # Einrueckung je Stufe
    s = -d
    if gully:
        th = np.arctan2(z - cz, x - cx)
        per = 2 * math.pi * R * (1 + aspect) / 2
        k = max(5, int(round(per / rng.uniform(19, 28))))
        g = np.maximum(0.0, np.cos(k * th + rng.uniform(0, 6.3) + 1.2 * c.nz.fbm("gul", x, z, 60, 2))) ** 6
        gd = rng.uniform(3.0, 7.0)
    else:
        g = np.zeros_like(s)
        gd = 0.0
    h = np.full(s.shape, base)
    inset = 0.0
    prev = base
    dS = s_smooth(c, x, z) - sc        # Oberseiten folgen der Schichtneigung
    for i, lv in enumerate(levels):
        dh = lv - prev
        ww = max(2.2, dh * TAN(10) + 1.5)
        s_eff = s - g * gd * (1.0 + 0.9 * i / max(1, len(levels) - 1))
        ramp = np.clip((s_eff - inset) / ww, 0, 1)
        h = h + dh * ramp
        prev = lv
        ins = rng.uniform(4, 14) if stage == "mesa" else rng.uniform(1.5, 5)
        ins *= 1.0 + 0.35 * c.nz.fbm("ins%d" % i, x, z, 45, 2)
        inset = inset + ww + (ins if i < len(levels) - 1 else 0)
    roof = rng.uniform(0.5, 2.0) if stage == "mesa" else 0.4
    h = h + roof * ss(inset, inset + 30, s) - dS * (s > 0)
    mesa_h = np.where(s > -1, h, -1e9)
    # Schutthalde (Mud) mit Schuttkegeln unter den Rinnen
    T = tal_l * TAN(31) * 0.85
    gs = np.maximum(0.0, np.cos(k * th + 0.0)) ** 2 if gully else np.zeros_like(s)
    gs = 0.5 * gs + 0.5 * (c.nz.fbm("talcone", x, z, 30, 2) * 0.5 + 0.5)
    tl = tal_l * (1.0 + 0.3 * gs)
    Tg = T * (1.0 + 0.22 * gs)
    q = np.clip((d + 0.15 * tl) / tl, 0, 1)
    tal = base + Tg * (1 - q) ** 1.55 + c.nz.fbm("talus", x, z, 14, 2) * 0.6
    tal = np.where(q < 1, tal, -1e9)
    new = np.maximum(Hl, np.maximum(mesa_h, tal))
    body = (mesa_h >= tal) & (mesa_h > Hl + 0.5)
    tmask = (tal > mesa_h) & (tal > Hl + 0.25)
    c.H[sl] = new
    c.mask("mesa")[sl] |= body
    c.mask("talus")[sl] |= tmask
    clear_soft(c, sl, body | tmask)
    foot = (d < tl * 0.9)
    c.obstacle[sl] |= body | tmask
    claim(c, sl, d < tl + 18)
    # Oberseite: Staub- oder Grasflecken
    if top_patch:
        topsel = body & (s > inset - 2) & (c.nz.fbm("toppatch", x, z, 22, 3) > -0.05)
        set_strata_top(c, sl, topsel, top_patch)
    if record:
        c.feat["mesa"].append({"x": cx, "z": cz, "R": R * math.sqrt(aspect), "Rmin": R / math.sqrt(aspect), "base": base,
                               "top": top, "talus": tal_l, "stage": stage, "levels": levels, "rot": rot})
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


def ridge(c: Ctx, p0, p1, bend, peaks, base=None, front=1, dip_deg=34.0, face_deg=62.0, back_deg=36.0,
          width_cap=None, gaps=(), name="ridge"):
    """Asymmetrischer Danxia-Kamm ("Haifischflosse"). peaks: [(t, Hoehe ueber Basis, Breite in t)].
    front=+1: Stirnseite auf der linken Seite der Laufrichtung p0->p1. gaps: [(t, Breite in Studs, Boden ueber Basis)]."""
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
    # Kammhoehe entlang t
    crest = np.zeros_like(t)
    for (tp, hp, wp) in peaks:
        crest = np.maximum(crest, hp * np.exp(-((t - tp) / wp) ** 2) ** 0.8)
    crest = crest * ss(-0.06, 0.08, t) * ss(1.06, 0.92, t)
    zack = c.nz.ridged(name + "zack", s / 1.0, np.zeros_like(s) + 7.0, 42, 2, sharp=2.0)
    crest = crest + (zack - 0.45) * 22.0 * np.clip(crest / 60, 0, 1)
    for (tg, wg, hg) in gaps:
        gw = wg / L
        crest = np.minimum(crest, hg + np.maximum(0, np.abs(t - tg) - gw / 2) * L * TAN(38))
    # Furchen auf der Stirnseite (alle 18-30 Studs), Rinnen auf der Rueckseite
    fur = np.maximum(0, np.cos(2 * math.pi * s / 24.0 + 1.3 * c.nz.fbm(name + "fur", x, z, 50, 2))) ** 5
    au = np.abs(u)
    front_h = crest - (au + fur * 6.0 * ss(0, 30, au)) * TAN(face_deg)
    bg = c.nz.ridged(name + "bg", x, z, 46, 3, sharp=1.8)
    back_h = crest - u * TAN(back_deg) - bg * 9.0 * ss(0, 40, u)
    hr = np.where(u < 0, front_h, back_h)
    # Schutthalde vor der Stirnseite
    foot_u = crest / TAN(face_deg)
    T = 0.22 * crest
    Ltal = T / TAN(30) + 4
    q = np.clip((au - foot_u + 0.35 * Ltal) / Ltal, 0, 1)
    tal = np.where((u < 0) & (q < 1), T * (1 - q) ** 1.5, -1e9)
    hrel = np.maximum(hr, tal)
    hrel = np.where(hrel > -0.5, hrel, -1e9)
    if width_cap is not None:
        hrel = np.minimum(hrel, crest * np.clip(1 - (au - width_cap) / 40, 0, 1) + 0 * au)
    hnew = base + hrel
    new = np.maximum(Hl, hnew)
    body = (hr >= tal) & (hnew > Hl + 0.5)
    tm = (tal > hr) & (hnew > Hl + 0.3)
    c.H[sl] = new
    c.mask("ridge")[sl] |= body
    c.mask("talus")[sl] |= tm
    clear_soft(c, sl, body | tm)
    c.obstacle[sl] |= body | tm
    claim(c, sl, (hnew > Hl - 1.0) & (hrel > -6))
    # lokal geneigte Schichten: Fall zur Rueckseite
    sc = float(s_smooth(c, np.array(mid[0]), np.array(mid[1])))
    w = ss(-6, 10, hrel) * ss(1.25, 0.95, np.abs(t - 0.5) * 2)
    loc = sc + TAN(dip_deg) * u
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
    """Fuss aus Hoehenkarte (Baender), Hals/Wulst/Hut als Zylinder-Zusatzformen (Ueberhang)."""
    rng = c.rng
    rf = rng.uniform(7, 10)
    hf = rng.uniform(8, 14) * min(1.0, total / 40 + 0.4)
    sl = c.win(x0, z0, rf * 2.2)
    x, z = c.local(sl)
    rho = np.hypot(x - x0, z - z0) * (1 + 0.12 * c.nz.fbm("hdf", x, z, 6, 1))
    Hl = c.H[sl]
    if base is None:
        base = float(Hl[rho < rf].min()) if (rho < rf).any() else float(c.h_at(x0, z0))
    q = np.clip(rho / (rf * 1.5), 0, 1)
    prof = np.where(rho < rf * 0.55, 1.0, (1 - np.clip((rho - rf * 0.55) / (rf * 0.95), 0, 1)) ** 1.6)
    hfoot = base + hf * prof
    tal = np.where(q < 1, base + rf * 0.35 * (1 - q) ** 1.4, -1e9)
    hfoot = np.where(rho < rf * 1.5, hfoot, -1e9)
    hn = np.maximum(hfoot, tal)
    c.H[sl] = np.maximum(Hl, hn)
    c.mask("hoodoo_foot")[sl] |= (hfoot >= tal) & (hfoot > Hl + 0.5)
    c.mask("talus")[sl] |= (tal > hfoot) & (tal > Hl + 0.3)
    c.obstacle[sl] |= rho < rf * 1.3
    y = base + hf - 1.5
    lean = rng.uniform(0, 2 * math.pi)
    lx, lz = math.cos(lean) * 0.04, math.sin(lean) * 0.04
    segs = []
    rest = total - hf
    neck_r = rng.uniform(2.7, 4.5)
    bulge_r = rng.uniform(4.6, 6.4)
    hat_r = rng.uniform(5.2, 8.0)
    hat_h = rng.uniform(3.0, 5.0)
    two = rest > 34 and rng.uniform() < 0.6
    if two:
        parts = [("neck", rest * 0.30, neck_r), ("bulge", rest * 0.22, bulge_r), ("neck", rest * 0.30, neck_r * 0.85)]
    else:
        parts = [("neck", rest * 0.45, neck_r), ("bulge", rest * 0.30, bulge_r), ("neck", rest * 0.12, neck_r * 0.9)]
    mats = [HOODOO_NECK[int(rng.integers(0, len(HOODOO_NECK)))], "Rock", "Sandstone"]
    k = 0
    cx, cz = x0, z0
    for kind, hgt, r in parts:
        hgt = max(hgt, 3.0)
        cy = y + hgt / 2
        cx += lx * hgt
        cz += lz * hgt
        mat = mats[k % len(mats)] if kind == "neck" else ("Slate" if rng.uniform() < 0.5 else "Rock")
        op_cyl(c, cx, cy, cz, hgt + 1.0, r, mat)
        if kind == "bulge":
            op_ball(c, cx, cy + hgt * 0.15, cz, r * 1.02, mat)
        y += hgt
        k += 1
    # Hut: harte Kalkstein-Kappe (Ueberhang)
    op_cyl(c, cx, y + hat_h / 2 - 0.5, cz, hat_h, hat_r, "Limestone")
    op_ball(c, cx, y + hat_h - 0.8, cz, hat_r * 0.72, "Limestone")
    top = y + hat_h
    c.feat["hoodoo"].append({"x": x0, "z": z0, "base": base, "top": top, "hat_r": hat_r, "foot_r": rf})
    return top
