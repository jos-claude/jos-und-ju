"""Flaechige Formen: Vulkan + Lavafelder (Ring C Nordost), Duenen + Wave (Ring C Suedwest), Hochland E, Felsbaenke."""
from __future__ import annotations

import math

import numpy as np

from .ctx import Ctx
from .landforms import TAN, claim, op_ball, op_cyl, set_mat, set_strata_top
from .layout import LEE_DIR, ang_diff, pol
from .noise import smoothstep as ss
from .waterforms import snap4_down


# ------------------------------------------------------------------ Vulkan
def volcano(c: Ctx, cx, cz, top, crater_d, west_az=None, name="volcano", small=False):
    nz = c.nz
    base = float(np.percentile(c.H[c.win(cx, cz, 300 if not small else 60)], 40))
    Hv = top - base
    Rv = Hv / TAN(25.0 if not small else 24.0)
    Rc = crater_d / 2
    pad = Rv * 1.35 + 40
    sl = c.win(cx, cz, pad)
    x, z = c.local(sl)
    dx, dz = x - cx, z - cz
    rho = np.hypot(dx, dz)
    ang = np.degrees(np.arctan2(dx, -dz)) % 360
    lob = 1 + 0.13 * nz.fbm(name + "lob", cx + 80 * np.sin(np.radians(ang)), cz - 80 * np.cos(np.radians(ang)), 70, 3)
    Rv_a = Rv * lob
    if west_az is not None:
        spur = ss(26, 6, np.abs(ang_diff(ang, west_az)))
        Rv_a = Rv_a * (1 + spur * (TAN(25) / TAN(15) - 1))
    q = np.clip((rho - Rc) / (Rv_a - Rc), 0, 1)
    cone = base + Hv * (1 - q) ** 1.3
    # Radiale Erosionsrinnen
    rills = nz.ridged(name + "rill", ang * 6.0, rho * 0.02, 14, 2, sharp=2.0)
    cone = cone - rills * (4.0 if not small else 1.2) * ss(0.05, 0.4, q) * (1 - ss(0.75, 1.0, q))
    # Krater (Innenneigung <= 25 Grad, flacher Boden)
    dep = 18.0
    wall = dep / TAN(24.0)
    rf = max(Rc - wall, Rc * 0.25)
    crater = top - dep * (1 - ss(rf, Rc, rho))
    rimbump = 2.0 * np.exp(-((rho - Rc) / 6.0) ** 2)
    if west_az is not None:
        notch = ss(12, 4, np.abs(ang_diff(ang, west_az)))
        rimbump = rimbump - notch * 5.0 * np.exp(-((rho - Rc) / 14.0) ** 2)
    hv = np.where(rho < Rc, crater, cone) + rimbump
    hv = np.where(q < 0.999, hv, -1e9)
    Hl = c.H[sl]
    new = np.maximum(Hl, hv)
    c.H[sl] = new
    body = (hv > Hl + 0.5) & (rho < Rv_a)
    c.mask("volcano")[sl] |= body
    set_mat(c, sl, body, "Basalt")
    ash = body & (nz.fbm(name + "ash", ang * 3.0, rho * 0.05, 9, 3) > 0.25) & (rho > Rc + 10)
    set_mat(c, sl, ash, "Ground" if not small else "Mud")
    set_mat(c, sl, rho < rf + 2, "CrackedLava")
    c.obstacle[sl] |= body & (q < 0.82)
    claim(c, sl, rho < Rv_a * 1.05 + 10)
    c.feat["volcano"].append({"x": cx, "z": cz, "top": top, "Rc": Rc, "Rv": Rv, "base": base, "small": small,
                              "floor": top - dep})
    for k in range(3 if not small else 1):
        a = (west_az or 0) + 90 + 110 * k + c.u(-20, 20) if not small else 0
        rr = Rc + 2 if not small else 0
        px, pz = cx + rr * math.sin(math.radians(a)), cz - rr * math.cos(math.radians(a))
        c.feat["spring"].append({"x": px, "z": pz, "kind": "volcano" if not small else "cone"})
    return base


def lava_tongue(c: Ctx, sx, sz, dir_deg, length, width, name="tongue"):
    """Lavazunge: erhaben (2-3), lappiger Rand, Basalt mit CrackedLava-Rissen (25-30 %)."""
    pts = []
    a = dir_deg
    px, pz = sx, sz
    step = 8.0
    for i in range(int(length / step)):
        pts.append((px, pz))
        a += c.nz.fbm(name + "dir", np.array(i * 0.1), np.array(3.0), 1.0, 1) * 9
        px += step * math.sin(math.radians(a))
        pz -= step * math.cos(math.radians(a))
    pts = np.array(pts)
    lo, hi = pts.min(0) - width, pts.max(0) + width
    sl = c.win((lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, max(hi[0] - lo[0], hi[1] - lo[1]) / 2 + 10)
    x, z = c.local(sl)
    from scipy.spatial import cKDTree
    tr = cKDTree(pts)
    d, i = tr.query(np.stack([x.ravel(), z.ravel()], 1))
    d = d.reshape(x.shape)
    t = (i / max(1, len(pts) - 1)).reshape(x.shape)
    hw = width / 2 * (0.6 + 0.6 * np.sin(math.pi * np.clip(t * 1.1, 0, 1)) ** 0.5) * (1 + 0.25 * c.nz.fbm(name + "w", x, z, 26, 2))
    inside = d < hw
    lobe = ss(hw, hw - 6, d)
    thick = 2.6 * lobe * (1 - 0.5 * t)
    Hl = c.H[sl]
    c.H[sl] = Hl + thick
    f1, f2, _ = c.nz.voronoi(name + "cr", x, z, 22)
    crack = inside & ((f2 - f1) < 3.2)
    set_mat(c, sl, inside, "Basalt")
    set_mat(c, sl, crack, "CrackedLava")
    c.mask("lava")[sl] |= inside
    c.obstacle[sl] |= inside


def lava_fields(c: Ctx):
    """Ring C Nordost: ~30 % Lavafeld (Basaltsaeulen-Zellen + Risse), Rest Asche-Ebene."""
    x, z = c.x, c.z
    zone = (c.wNE > 0.5) & (c.rw > 660) & (c.rw < 1060) & ~c.mask("claimed") & (c.wash_dist > 25)
    f = c.nz.fbm("lavazone", x, z, 230, 3) + 0.35 * c.nz.fbm("lavazone2", x, z, 80, 2)
    field = zone & (f > 0.13)
    # Oasen ausschneiden (werden spaeter bepflanzt)
    for o in c.feat.get("oasis_c", []):
        field &= np.hypot(x - o["x"], z - o["z"]) > o["R"] + 10
    f1, f2, cid = c.nz.voronoi("basaltcells", x, z, 15)
    off = ((cid % 7) / 6.0) * 2.6
    edge = ss(0.0, 3.0, f2 - f1)
    soft = ss(0.13, 0.2, f)
    c.H = np.where(field, c.H + off * soft * (0.45 + 0.55 * edge), c.H)
    cf1, cf2, _ = c.nz.voronoi("lavacrack", x, z, 46)
    crack = field & ((cf2 - cf1) < 3.0) & (f > 0.17)
    c.H = np.where(crack, c.H - 0.8, c.H)
    sl = (slice(None), slice(None))
    set_mat(c, sl, field, "Basalt")
    set_mat(c, sl, crack, "CrackedLava")
    c.mask("basalt_cells")[:] |= field
    c.obstacle |= field
    c.lava_field = field


# ------------------------------------------------------------------ Duenen
def dunes(c: Ctx):
    x, z = c.x, c.z
    a = math.radians(LEE_DIR)
    w = x * math.sin(a) - z * math.cos(a)       # windabwaerts (Richtung 70)
    v = x * math.cos(a) + z * math.sin(a)       # quer zum Wind (Kaemme ~ 340/160)
    zone = (c.wNE < 0.5) & (c.rw > 650) & (c.rw < 1075)
    zone &= ~c.mask("claimed")
    env = ss(-0.02, 0.22, c.nz.fbm("duneenv", x, z, 240, 3))
    env = env * ss(0, 40, c.wash_dist) * ss(640, 720, c.rw) * ss(1080, 1010, c.rw)
    lam = 112.0 + 18.0 * c.nz.fbm("dunelam", x, z, 600, 2)
    wb = w + 46.0 * c.nz.fbm("dunebend", v * 0.6, w * 0.15, 170, 3) + 14.0 * c.nz.fbm("dunebend2", x, z, 60, 2)
    t = np.mod(wb / lam, 1.0)
    ac = 0.77
    prof = np.where(t < ac, (t / ac) ** 1.15, (1 - t) / (1 - ac))
    Hd = 6.0 + 15.0 * ss(-0.3, 0.5, c.nz.fbm("duneh", x, z, 300, 2))
    dz = Hd * prof * env
    rip = 0.35 * np.sin(2 * math.pi * (w + 6 * c.nz.fbm("rip", x, z, 30, 2)) / 15.0) * ss(0.0, 0.3, env + 0.3)
    add = np.where(zone, dz + rip, 0.0)
    c.H = c.H + add
    m = zone & (env > 0.2)
    c.mask("dune")[:] |= m
    c.obstacle |= zone & (dz > 3.0)
    sl = (slice(None), slice(None))
    set_mat(c, sl, zone & (env > 0.05), "Sand")


def wave(c: Ctx, cx, cz, rx=170.0, rz=85.0, rot_deg=None, name="wave"):
    """'The Wave': geschwungene Sandstein-Rippen mit duennen Baendern entlang der Hoehenlinien."""
    rot = math.radians(rot_deg if rot_deg is not None else c.u(0, 180))
    sl = c.win(cx, cz, rx * 1.4)
    x, z = c.local(sl)
    cr, sr = math.cos(rot), math.sin(rot)
    lx = (x - cx) * cr + (z - cz) * sr
    lz = -(x - cx) * sr + (z - cz) * cr
    q = np.hypot(lx / rx, lz / rz) * (1 + 0.18 * c.nz.fbm(name + "o", x, z, 60, 2))
    mask = ss(1.0, 0.82, q)
    ph = lz + 34 * np.sin(lx / 55.0 + 1.3 * c.nz.fbm(name + "p", x, z, 120, 2)) + 10 * c.nz.fbm(name + "p2", x, z, 40, 2)
    lam = 62.0
    s = np.sin(2 * math.pi * ph / lam)
    rib = np.maximum(0.0, s) ** 0.8
    amp = 9.0 + 14.0 * ss(-0.4, 0.5, c.nz.fbm(name + "a", x, z, 90, 2))
    Hl = c.H[sl]
    base = float(np.percentile(Hl[q < 1], 40))
    hw = base + amp * rib * mask + 0.6 * c.nz.fbm(name + "m", x, z, 10, 1) * mask
    new = np.where(mask > 0.01, Hl * (1 - mask) + np.maximum(hw, base) * mask, Hl)
    c.H[sl] = new
    body = (mask > 0.3) & (rib > 0.05)
    c.mask("wave")[sl] |= body
    c.obstacle[sl] |= body & (rib > 0.25)
    set_mat(c, sl, (mask > 0.3) & ~body, "Sand")
    # duenne Baender entlang der Hoehenlinien: Versatz ~ 2,6 * Hoehe
    loc = c.S_local[sl]
    wgt = c.S_local_w[sl]
    sc = 30.0
    c.S_local[sl] = np.where(mask > wgt, sc + 2.6 * (new - base), loc)
    c.S_local_w[sl] = np.maximum(wgt, mask)
    claim(c, sl, q < 1.15)
    c.feat["wave"].append({"x": cx, "z": cz, "rx": rx, "rz": rz})


# ------------------------------------------------------------------ Hochland E
def highland(c: Ctx):
    x, z = c.x, c.z
    e = ss(1580, 1660, c.rw) * (c.r < 1890)
    waves = 4.0 * c.nz.fbm("ewave", x, z, 400, 2)
    c.H = c.H + waves * e
    # Nebelbecken: 3 flache Senken (-10)
    for k in range(3):
        for _ in range(40):
            a = c.u(0, 360)
            r = c.u(1680, 1800)
            px, pz = pol(a, r)
            if all(abs(ang_diff(a, b)) > 14 for b in c.L.washes) and all(abs(ang_diff(a, f["az"])) > 50 for f in c.feat["fogbasin"]):
                break
        R = c.u(125, 190)
        sl = c.win(px, pz, R * 1.2)
        lx, lz = c.local(sl)
        q = np.hypot(lx - px, lz - pz) / R * (1 + 0.15 * c.nz.fbm("fogb%d" % k, lx, lz, 80, 2))
        dip = 10.0 * (1 - ss(0.0, 1.0, q)) ** 1.0 * ss(1.0, 0.0, q)
        c.H[sl] = c.H[sl] - dip
        c.mask("fogbasin")[sl] |= q < 0.8
        c.feat["fogbasin"].append({"x": px, "z": pz, "R": R, "az": a})
    # Schnee in Mulden, Eisflecken
    curv = c.nz.fbm("snowcurv", x, z, 70, 3)
    snow = (e > 0.5) & (curv < -0.22) & ~c.mask("wash")
    sl = (slice(None), slice(None))
    set_mat(c, sl, snow, "Snow")
    for k in range(6):
        a, r = c.u(0, 360), c.u(1650, 1850)
        px, pz = pol(a, r)
        R = c.u(30, 60)
        s2 = c.win(px, pz, R * 1.3)
        lx, lz = c.local(s2)
        q = np.hypot(lx - px, lz - pz) / R * (1 + 0.25 * c.nz.fbm("ice%d" % k, lx, lz, 25, 2))
        ice = q < 1
        set_mat(c, s2, ice, "Ice")
        c.feat["ice"].append({"x": px, "z": pz, "R": R})


def outcrops(c: Ctx, zone, amount=0.08, height=(2.5, 5.0), name="outcrop"):
    """Niedrige Felsbaenke (Schichtfels schaut aus dem Boden), Ring A/B/D."""
    x, z = c.x, c.z
    f = c.nz.fbm(name, x, z, 70, 4) + 0.3 * c.nz.fbm(name + "2", x, z, 25, 2)
    thr = np.quantile(f[zone], 1 - amount) if zone.any() else 1.0
    lvl = ss(thr, thr + 0.035, f) * zone
    hgt = height[0] + (height[1] - height[0]) * ss(-0.3, 0.3, c.nz.fbm(name + "h", x, z, 120, 2))
    lvl2 = ss(thr + 0.09, thr + 0.12, f) * zone
    add = lvl * hgt + lvl2 * hgt * 0.8
    c.H = c.H + add
    m = (add > 0.6) & zone
    c.mask("outcrop")[:] |= m
    c.obstacle |= m


def low_floating_stones(c: Ctx, n=50):
    """Lufteinsprengsel (Ring D/E): kleine schwebende Felsen als Zusatzformen, >= 15 ueber Boden, >= 25 ueber Wegen."""
    placed = 0
    tries = 0
    while placed < n and tries < 4000:
        tries += 1
        a = c.u(0, 360)
        r = c.u(1180, 1840)
        px, pz = pol(a, r)
        if c.void[c.idx(px, pz)]:
            continue
        cl = c.mask("claimed")[c.idx(px, pz)]
        R = c.u(6, 15)
        g = float(c.h_at(px, pz))
        sl = c.win(px, pz, R + 6)
        gmax = float(c.H[sl].max())
        onwash = c.wash_dist[c.idx(px, pz)] < 10
        hov = c.u(20, 60) + (25 if onwash else 0)
        y = max(gmax + 15, g + hov)
        if any(math.hypot(px - f["x"], pz - f["z"]) < 40 for f in c.feat["lowfloat"]):
            continue
        # Form: Moosdeckel, Fels-Kegel nach unten, Spitze
        op_cyl(c, px, y, pz, 2.4, R, "Grass")
        op_cyl(c, px, y - 0.25 * R - 1.0, pz, 0.5 * R, R * 0.92, "Slate" if r > 1600 else "Sandstone")
        op_cyl(c, px, y - 0.62 * R - 1.0, pz, 0.35 * R, R * 0.62, "Rock")
        op_ball(c, px, y - 0.9 * R - 1.0, pz, R * 0.38, "Rock")
        c.feat["lowfloat"].append({"x": px, "z": pz, "y": y + 1.2, "R": R})
        placed += 1
