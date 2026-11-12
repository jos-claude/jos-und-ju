"""Mulden mit und ohne Wasser: Teiche, Sinterterrassen, Salzpfannen, Geoden, Krater, Schwemmfaecher.

Wasser-Regel (wie im WorldBuilder): Wasser steht nur in Voxeln, deren Unterkante >= Terrain-Oberkante ist.
Darum liegen alle Wasserboeden genau auf einem Vielfachen von 4 (volle Voxel) und der Spiegel darueber.
"""
from __future__ import annotations

import math

import numpy as np

from .ctx import Ctx
from .landforms import TAN, claim, set_mat
from .noise import smoothstep as ss


def snap4_down(y):
    return math.floor(y / 4.0) * 4.0


def _ellipse(c, x, z, cx, cz, a, b, rot, wob=0.08, name="ell", scale=30):
    cr, sr = math.cos(rot), math.sin(rot)
    lx = (x - cx) * cr + (z - cz) * sr
    lz = -(x - cx) * sr + (z - cz) * cr
    q = np.hypot(lx / a, lz / b)
    th = np.arctan2(lz, lx)
    q = q * (1 + wob * c.nz.fbm(name, cx + 50 * np.cos(th), cz + 50 * np.sin(th), scale, 2))
    return q


def pond(c: Ctx, cx, cz, diam, depth, rot=None, floor_mat="Mud", bank_mat="LeafyGrass", ring_mat="Grass",
         shore=None, name="pond"):
    R = diam / 2
    rot = rot if rot is not None else c.u(0, math.pi)
    pad = R * 1.3 + 40
    sl = c.win(cx, cz, pad)
    x, z = c.local(sl)
    q = _ellipse(c, x, z, cx, cz, R * 1.12, R / 1.12, rot, 0.12, name)
    Hl = c.H[sl]
    if shore is None:
        shore = float(np.percentile(Hl[q < 1.2], 50))
    F = snap4_down(shore - depth - 0.3)
    W = F + depth
    bank = depth / TAN(11.0)
    rr = R * q  # radialer Abstand in Studs (ungefaehr)
    inner = R - rr                      # > 0 innen
    hb = F + (W + 0.6 - F) * ss(bank, 0.0, inner)        # Boden -> Ufer
    lev = np.maximum(W + 0.6, Hl)
    out = np.clip(-inner / 26.0, 0, 1)                    # aussen sanft an das Gelaende angleichen
    hring = (W + 0.6) * (1 - ss(0, 1, out)) + Hl * ss(0, 1, out)
    hn = np.where(inner > 0, hb, np.where(out < 1, np.maximum(hring, np.minimum(Hl, W + 0.6 + out * 30)), Hl))
    c.H[sl] = hn
    wet = (inner > 0) & (hn < W - 0.05)
    c.wl[sl] = np.where(wet, W, c.wl[sl])
    set_mat(c, sl, (inner > bank * 0.4), floor_mat)
    wob = 9.0 * c.nz.fbm(name + "g", x, z, 30, 3)
    set_mat(c, sl, (inner <= bank * 0.4) & (inner > -6 + wob * 0.5), bank_mat)
    set_mat(c, sl, (inner <= -6 + wob * 0.5) & (inner > -24 + wob * 1.6), ring_mat)
    c.mask("pond")[sl] |= inner > -4
    c.obstacle[sl] |= inner > -2
    claim(c, sl, inner > -30)
    c.feat["water"].append({"x": cx, "z": cz, "R": R, "W": W, "kind": name})
    return W


def terraces(c: Ctx, cx, cz, n_basins, width, length, down_az, name="terr", source=True):
    """Sinterterrassen am Hang: Becken als Plattformen mit Salz-Rand, Wasser 1,5-2,5 tief, Stufe 4."""
    rng = c.rng
    da = math.radians(down_az)
    dx, dz = math.sin(da), -math.cos(da)          # Richtung hangabwaerts
    px, pz = -dz, dx                               # quer zum Hang
    pad = max(width, length) * 0.9 + 60
    sl = c.win(cx, cz, pad)
    x, z = c.local(sl)
    a = (x - cx) * dx + (z - cz) * dz              # entlang (positiv = abwaerts)
    b = (x - cx) * px + (z - cz) * pz
    Hl = c.H[sl]
    top_y = float(np.percentile(Hl[(np.abs(a) < 30) & (np.abs(b) < 30)], 50))
    slope = TAN(10.0)
    # Unterlage: sanfter Hang (10 Grad) von oben (a=-L/2) nach unten (a=+L/2), seitlich ausgeblendet
    hill_top = top_y + slope * length * 0.5
    hill = hill_top - slope * (a + length / 2)
    qq = np.hypot(b / (width * 0.62), a / (length * 0.62)) * (1 + 0.16 * c.nz.fbm(name + "o", x, z, 70, 2))
    side = ss(1.35, 0.95, qq) * (1.0 - ss(0.0, length * 0.75, a - length * 0.45))
    under = Hl * (1 - side) + np.maximum(Hl, hill - 3.0) * side
    # Becken in Reihen
    rows = 3 if n_basins <= 9 else 4
    per_row = [n_basins // rows + (1 if i < n_basins % rows else 0) for i in range(rows)]
    basins = []
    hm = under.copy()
    lvl0 = snap4_down(hill_top - 6.0)
    k = 0
    for ri, cnt in enumerate(per_row):
        ar = -length * 0.42 + (ri + 0.5) * (length * 0.84 / rows)
        for j in range(cnt):
            br = (j + 0.5 - cnt / 2) * (width * 0.9 / cnt) + rng.uniform(-6, 6)
            aj = ar + rng.uniform(-10, 10)
            rx = min(width * 0.9 / cnt * 0.62, 40) * rng.uniform(0.75, 1.0)
            rz = rx * rng.uniform(0.55, 0.75)
            basins.append((aj, br, rx, rz))
            k += 1
    basins.sort(key=lambda t: t[0])
    # Hoehen von oben nach unten, je Becken eine Stufe (4)
    hmax = np.full(x.shape, -1e9)
    hcov = np.full(x.shape, -1e9)        # Becken + Rand (dort gilt nur das Becken, nicht der Hang)
    wl = np.full(x.shape, np.nan)
    salt = np.zeros(x.shape, bool)
    for i, (aj, br, rx, rz) in enumerate(basins):
        hill_here = hill_top - slope * (aj - rz * 0.6 + length / 2)
        F = snap4_down(hill_here - 2.6)
        dep = rng.uniform(1.5, 2.2)
        W = F + dep
        rim = W + rng.uniform(1.5, 2.0)          # helle Salt-Raender stehen 1,5-2 ueber dem Wasser
        la, lb = a - aj, b - br
        q = np.hypot(la / rz, lb / rx)
        th = np.arctan2(la, lb)
        q = q * (1 + 0.10 * np.sin(5 * th + i) + 0.06 * c.nz.fbm(name + "b%d" % i, x, z, 12, 2))
        rr = (1 - q) * min(rx, rz)                         # Abstand zum Rand (innen > 0)
        bank = dep / TAN(13.0)
        cup = np.where(rr > 0, F + (rim - F) * ss(bank, 0, rr), rim - np.maximum(0, -rr - 3.0) * TAN(62))
        cup = np.where(rr > -3.0, np.maximum(cup, np.where(rr > 0, cup, rim)), cup)
        notch = (np.abs(lb) < 3.0) & (la > 0) & (rr > -4) & (rr < 1)      # Ueberlauf-Kerbe hangabwaerts
        cup = np.where(notch, np.minimum(cup, W + 0.15), cup)
        newer = cup > hmax
        hmax = np.where(newer, cup, hmax)
        hcov = np.where(rr > -3.5, np.maximum(hcov, cup), hcov)
        wl = np.where(newer & (rr > 0), W, np.where(newer, np.nan, wl))
        salt |= (rr > -6) & (rr < 2.5)
        c.feat["basin"].append({"x": cx + dx * aj + px * br, "z": cz + dz * aj + pz * br, "W": W, "rx": rx, "rz": rz,
                                "group": name})
    hn = np.where(hcov > -1e8, hcov, np.maximum(hm, hmax))
    top_cover = (hcov > -1e8) & (hn >= hmax - 0.01)
    wl = np.where(top_cover & (hn < wl - 0.05), wl, np.nan)
    c.H[sl] = hn
    c.wl[sl] = np.where(~np.isnan(wl), wl, c.wl[sl])
    area = (hmax > -1e8) & top_cover
    set_mat(c, sl, area | (side > 0.45), "Salt")
    set_mat(c, sl, area & ~salt & np.isnan(wl), "Limestone")
    c.mask("terrace")[sl] |= area | (side > 0.3)
    c.obstacle[sl] |= area
    claim(c, sl, side > 0.05)
    src = (cx - dx * length * 0.5, cz - dz * length * 0.5)
    c.feat["spring"].append({"x": src[0], "z": src[1], "kind": "terrace", "group": name})
    c.feat["terrace"].append({"x": cx, "z": cz, "down": down_az, "w": width, "l": length, "name": name})


def playa(c: Ctx, cx, cz, diam, name="playa"):
    R = diam / 2
    rot = c.u(0, math.pi)
    sl = c.win(cx, cz, R * 1.5 + 70)
    x, z = c.local(sl)
    q = _ellipse(c, x, z, cx, cz, R * 1.2, R / 1.2, rot, 0.16, name, 60)
    Hl = c.H[sl]
    low = float(np.percentile(Hl[q < 1.0], 20))
    F = snap4_down(low - 1.0)
    rr = (1 - q) * R
    dry = F + 1.5
    hn = np.where(rr > 0, dry + 0.15 * c.nz.fbm(name + "m", x, z, 30, 2), Hl)
    rim = np.clip(-rr / 70.0, 0, 1)
    hn = np.where(rr <= 0, dry * (1 - ss(0, 1, rim)) + np.maximum(Hl, dry) * ss(0, 1, rim), hn)
    hn = np.where(rr <= 0, np.minimum(hn, Hl), hn)
    hn = np.where((rr <= 0) & (rr > -70), np.maximum(hn, dry), hn)
    spots = (c.nz.fbm(name + "s", x, z, 45, 3) > 0.12) & (rr > 12)
    hn = np.where(spots, F, hn)
    # Spot-Ufer weich: Nachbarn der Spots leicht absenken
    c.H[sl] = hn
    c.wl[sl] = np.where(spots, F + 1.0, c.wl[sl])
    set_mat(c, sl, rr > 0, "Salt")
    set_mat(c, sl, (rr <= 0) & (rr > -20), "Limestone")
    set_mat(c, sl, (rr <= -20) & (rr > -42), "Sand")
    c.mask("playa")[sl] |= rr > -42
    claim(c, sl, rr > -50)
    c.feat["playa"].append({"x": cx, "z": cz, "R": R, "F": F})


def geode(c: Ctx, cx, cz, diam, name="geode"):
    R = diam / 2
    dep = min(14.0, max(5.0, (R - 7) * TAN(19)))
    sl = c.win(cx, cz, R + 20)
    x, z = c.local(sl)
    q = _ellipse(c, x, z, cx, cz, R * 1.1, R / 1.1, c.u(0, 3), 0.1, name)
    Hl = c.H[sl]
    base = float(np.percentile(Hl[q < 1.0], 60))
    rr = (1 - q) * R
    wall = dep / TAN(19.0)
    bowl = base - dep * ss(0, wall, rr)
    rim = base + 1.5 * np.exp(-((rr + 4) / 6) ** 2)
    hn = np.where(rr > 0, np.minimum(Hl, bowl), np.maximum(Hl, rim * (rr > -14) + Hl * (rr <= -14)))
    c.H[sl] = hn
    set_mat(c, sl, rr > wall * 0.8, "Concrete" if c.u() < 0.5 else "Salt")
    set_mat(c, sl, (rr > 0) & (rr <= wall * 0.8), "Rock")
    c.mask("geode")[sl] |= rr > -8
    c.obstacle[sl] |= rr > -6
    claim(c, sl, rr > -20)
    c.feat["geode"].append({"x": cx, "z": cz, "R": R, "floor": base - dep})


def crater(c: Ctx, cx, cz, diam, water=False, name="crater"):
    R = diam / 2
    dep = min(26.0, 0.1 * diam)
    rimh = 0.04 * diam
    sl = c.win(cx, cz, R * 1.8 + 10)
    x, z = c.local(sl)
    q = _ellipse(c, x, z, cx, cz, R * 1.05, R / 1.05, c.u(0, 3), 0.07, name, 40)
    Hl = c.H[sl]
    base = float(np.median(Hl[q < 1.6]))
    rho = q * R
    wall = (dep + rimh) / TAN(22.0)
    rf = max(R - wall, R * 0.3)
    inner = base - dep + (dep + rimh) * ss(rf, R, rho)
    outer = base + rimh * np.exp(-((rho - R) / (0.32 * R)) ** 2 * 1.4)
    prof = np.where(rho < R, inner, outer)
    blend = ss(1.75 * R, 1.25 * R, rho)
    hn = Hl * (1 - blend) + (prof + (Hl - base) * 0.35) * blend
    if water:
        F = snap4_down(base - dep + 0.5)
        hn = np.where(rho < rf, np.minimum(hn, F), hn)
        W = F + 2.0
        wet = (rho < R) & (hn < W - 0.05)
        c.wl[sl] = np.where(wet, W, c.wl[sl])
        set_mat(c, sl, (rho < rf * 1.15), "Mud")
        set_mat(c, sl, (rho >= rf * 1.15) & (rho < rf + 12 + 8 * c.nz.fbm(name + "lg", x, z, 25, 2)), "LeafyGrass")
        c.feat["water"].append({"x": cx, "z": cz, "R": rf, "W": W, "kind": "crater"})
    c.H[sl] = hn
    c.mask("crater")[sl] |= rho < R * 1.2
    c.mask("crater_floor")[sl] |= rho < rf
    claim(c, sl, rho < R * 1.5)
    c.feat["crater"].append({"x": cx, "z": cz, "R": R, "base": base, "floor": base - dep})


def fan(c: Ctx, ax, az_, dir_deg, radius, open_deg=90.0, name="fan"):
    """Schwemmfaecher: Spitze am Schluchtausgang, Neigung ~3 Grad, Sand innen, Rinnen."""
    sl = c.win(ax, az_, radius + 20)
    x, z = c.local(sl)
    dx, dz = x - ax, z - az_
    rho = np.hypot(dx, dz)
    ang = np.degrees(np.arctan2(dx, -dz)) % 360
    da = np.abs((ang - dir_deg + 180) % 360 - 180)
    Hl = c.H[sl]
    apex = float(c.h_at(ax, az_))
    base_far = float(np.percentile(Hl[(rho < radius) & (da < open_deg / 2)], 40)) if ((rho < radius) & (da < open_deg / 2)).any() else apex
    rise = max(4.0, min(radius * TAN(3.0), apex - base_far + 3))
    shape = ss(open_deg / 2 + 12, open_deg / 2 - 18, da) * ss(radius, radius * 0.75, rho)
    conv = (1 - np.clip(rho / radius, 0, 1)) ** 1.25
    surf = base_far + rise * conv
    ch = np.zeros_like(rho)
    for k in range(int(c.rng.integers(3, 7))):
        ca = dir_deg + c.u(-open_deg / 2.5, open_deg / 2.5)
        wig = c.nz.fbm(name + "c%d" % k, rho, np.full_like(rho, 10.0 * k), 60, 2) * 20
        dd = np.abs(np.radians((ang - ca + 180) % 360 - 180) * rho + wig)
        ch = np.maximum(ch, ss(5.0, 0.0, dd) * ss(10, 30, rho))
    surf = surf - 1.6 * ch
    keep = c.mask("volcano")[sl] | c.mask("lava")[sl] | c.mask("mesa")[sl] | c.mask("ridge")[sl]
    shape = np.where(keep, 0.0, shape)
    add = (surf - Hl) * shape
    hn = Hl + np.maximum(add, 0)
    c.H[sl] = hn
    m = (shape > 0.35) & (add > 0.3)
    c.mask("fan")[sl] |= m & (rho < radius * 0.62)
    set_mat(c, sl, m & (rho < radius * 0.62), "Sand")
    set_mat(c, sl, m & (rho >= radius * 0.62), "Ground")
    c.feat["fan"].append({"x": ax, "z": az_, "dir": dir_deg, "R": radius, "open": open_deg})
