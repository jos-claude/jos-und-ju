"""Grundgelaende: Ringprofil mit Stufen (Schichtstufen), Grund-Rauschen, Washes, Randgebirge, Rand, Schwebfelsen."""
from __future__ import annotations

import math

import numpy as np
from scipy.ndimage import gaussian_filter1d

from .ctx import Ctx
from .layout import BALCONY_AZ, ang_diff, pol
from .noise import smoothstep as ss

RIM_R = 1940.0
BALCONY_FLOOR = 50.0
BENCH_E2 = 30.0


def ring_fields(c: Ctx):
    """Verwischter Radius (Ring-Grenzen mit Domain-Warping, +-80 Studs, Wellenlaenge 250) und Sektor C-Nordost."""
    w = c.nz.fbm("ringwarp", c.x, c.z, 260, 3) * 150.0
    c.rw = c.r + np.clip(w, -80, 80) * ss(150, 300, c.r)
    azj = c.az + c.nz.fbm("sectorjit", c.x, c.z, 400, 2) * 25.0
    d1 = ang_diff(azj, 30.0)          # Mitte des Nordost-Sektors (300..120)
    c.wNE = 1.0 - ss(90.0, 110.0, np.abs(d1))
    c.sector_ne = c.wNE > 0.5


def _scarp(rw, rk, hk, g):
    """Schichtstufe: steil (g=1, Wand + Schutthalde) oder sanfte Rampe (g=0). hk>0: aussen hoeher."""
    habs = abs(hk)
    w_sharp = habs / math.tan(math.radians(62)) + 10.0
    w_gentle = habs / math.tan(math.radians(4.2))
    w = w_gentle + (w_sharp - w_gentle) * g
    t = np.clip((rw - rk) / w + 0.5, 0.0, 1.0)
    gentle = t * t * (3 - 2 * t)
    # steile Form: Schutthalde (unten, konkav), Wand, gerundete Kante
    talus = 0.32 * (np.clip(t / 0.42, 0, 1) ** 1.7)
    wall = np.clip((t - 0.42) / 0.48, 0, 1)
    sharp = np.where(t < 0.42, talus, 0.32 + 0.63 * wall + 0.05 * ss(0.9, 1.0, t))
    if hk > 0:
        p = gentle + (sharp - gentle) * g
        return hk * p, t, w
    # Abfall nach aussen: Profil spiegeln (Schutthalde liegt aussen unten)
    tm = 1.0 - t
    gentle_m = tm * tm * (3 - 2 * tm)
    talus_m = 0.32 * (np.clip(tm / 0.42, 0, 1) ** 1.7)
    wall_m = np.clip((tm - 0.42) / 0.48, 0, 1)
    sharp_m = np.where(tm < 0.42, talus_m, 0.32 + 0.63 * wall_m + 0.05 * ss(0.9, 1.0, tm))
    p = gentle_m + (sharp_m - gentle_m) * g
    return -habs * (1.0 - p), t, w


SCARPS = [  # (Radius, Hoehe, Name)
    (1110.0, -10.0, "s1"),
    (1455.0, 12.0, "s2"),
    (1562.0, 14.0, "s3"),
    (1776.0, 14.0, "s4"),
]


def profile(rw, wNE, gs=None, wig=None):
    """Radiales Hoehenprofil (y). gs: Schaerfe der Stufen (None = alle sanft, fuer Wash-Boeden)."""
    cl = -8.0 + 10.0 * wNE
    h = -6.0 * ss(165, 262, rw) - 4.0 * ss(300, 560, rw)
    h = h + (cl + 10.0) * ss(560, 730, rw)
    h = h + (-8.0 - cl) * ss(960, 1090, rw)
    h = h - 6.0 * ss(1135, 1270, rw)
    h = h + 2.0 * ss(1475, 1540, rw)
    h = h + 6.0 * ss(1580, 1680, rw)
    h = h + 2.0 * ss(1690, 1760, rw)
    h = h + 4.0 * ss(1795, 1880, rw)
    for k, (rk, hk, name) in enumerate(SCARPS):
        g = 0.0 if gs is None else gs[k]
        off = 0.0 if wig is None else wig[k]
        dh, _, _ = _scarp(rw, rk + off, hk, g)
        h = h + dh
    return h


def base_terrain(c: Ctx):
    ring_fields(c)
    x, z, rw = c.x, c.z, c.rw
    nz = c.nz
    gs, wig = [], []
    for k, (rk, hk, name) in enumerate(SCARPS):
        g = ss(-0.04, 0.16, nz.fbm("scarpg" + name, x, z, 230, 3))
        gs.append(g)
        wig.append(nz.fbm("scarpw" + name, x, z, 70, 3) * 30.0)
    c.scarp_g = gs
    c.scarp_wig = wig
    h = profile(rw, c.wNE, gs, wig)
    # Stufen-Waende merken (fuer Material + Deko)
    sc = c.mask("scarp")
    for k, (rk, hk, name) in enumerate(SCARPS):
        _, t, w = _scarp(rw, rk + wig[k], hk, gs[k])
        wall = (gs[k] > 0.5) & (t > 0.05) & (t < 0.95)
        sc |= wall
    # Grund-Rauschen (Vorgabe 2.5), Amplituden leicht gedaempft wegen Bauzonen-Neigung <= 6 Grad
    n = (nz.fbm("o1", x, z, 300, 1) * 6.0 + nz.fbm("o2", x, z, 80, 1) * 2.0
         + nz.fbm("o3", x, z, 24, 1) * 0.55 + nz.fbm("o4", x, z, 9, 1) * 0.12)
    amp = 1.0 - 0.6 * (1.0 - ss(200, 300, rw))         # Ring A ruhiger
    amp = amp * (1.0 - 0.4 * ss(1200, 1260, rw) * (1.0 - ss(1430, 1470, rw)))  # D-Becken x0.6
    amp = amp * ss(150, 215, c.r)                       # Plateau eben
    micro = nz.fbm("plateau", x, z, 40, 2) * 0.45 * (1.0 - ss(150, 215, c.r))
    c.H = h + n * amp + micro
    c.base_smooth = h  # ohne Rauschen (fuer Washes)


# ---------------------------------------------------------------- Washes
def wash_lines(c: Ctx):
    """Mittellinien der 6 Washes (fest +- Jitter), Maeander als seitlicher Versatz."""
    lines = []
    rs = np.arange(0.0, 2000.0, 4.0)
    for k, a0 in enumerate(c.L.washes):
        phi = c.u(0, 2 * math.pi)
        lat = 21.0 * np.sin(2 * math.pi * rs / 500.0 + phi) + 55.0 * c.nz.fbm(f"washlat{k}", rs, np.full_like(rs, 1000.0 * k), 800, 2)
        lat *= ss(120, 300, rs)
        az = a0 + np.degrees(lat / np.maximum(rs, 50.0))
        # die vier Washes mit Balkon biegen am Ende zum Balkon ab
        for b in BALCONY_AZ:
            if abs(ang_diff(b, a0)) < 16:
                az = az + ang_diff(b, az) * ss(1550, 1840, rs)
        lines.append((rs, az))
    c.wash_lines = lines


def carve_washes(c: Ctx, regen=True):
    if regen:
        wash_lines(c)
    x, z, r, az = c.x, c.z, c.r, c.az
    best = np.full(r.shape, 1e9)
    wid = np.full(r.shape, -1, np.int16)
    floor_m = c.mask("wash_floor")
    wash_m = c.mask("wash")
    H = c.H
    ri = np.clip((r / 4.0).astype(int), 0, 499)
    for k, (rs, azl) in enumerate(c.wash_lines):
        # Bodenprofil entlang des Wash: sanftes Profil (ohne Stufen), stark geglaettet
        px = rs * np.sin(np.radians(azl))
        pz = -rs * np.cos(np.radians(azl))
        iz, ix = c.idx(px, pz)
        prof = profile(c.rw[iz, ix], c.wNE[iz, ix])
        prof = gaussian_filter1d(prof, 18.0, mode="nearest")
        depth = 3.0 + 0.9 * c.nz.fbm(f"washdep{k}", rs, np.full_like(rs, 7.0 * k), 300, 2) * 2
        depth = np.clip(depth, 2.0, 4.0) * ss(170, 290, rs) * (1.0 - ss(1830, 1890, rs))
        floor = prof - depth
        hw = 50.0 + 30.0 * ss(250, 1100, rs)
        # Zelle -> seitlicher Abstand zur Linie
        a_here = azl[ri]
        lat = r * np.sin(np.radians(ang_diff(az, a_here)))
        d = np.abs(lat)
        ok = (np.abs(ang_diff(az, a_here)) < 45) & (r > 150) & (r < 1900)
        hwc = hw[ri]
        fl = floor[ri]
        dep = depth[ri]
        bank = 14.0
        cut = fl + dep * ss(hwc - bank, hwc, d) + np.maximum(0.0, d - hwc) * math.tan(math.radians(33))
        sel = ok & (d < hwc + 160)
        H[sel] = np.minimum(H[sel], cut[sel])
        inner = ok & (d < hwc) & (dep > 0.5)
        wash_m |= inner
        floor_m |= ok & (d < hwc - bank) & (dep > 0.5)
        closer = ok & (d - hwc < best)
        best[closer] = (d - hwc)[closer]
        wid[closer] = k
        c.feat["wash"].append({"k": k, "rs": rs, "az": azl, "hw": hw, "floor": floor})
    c.wash_dist = best          # < 0 innerhalb eines Wash
    c.wash_id = wid


# ---------------------------------------------------------------- Randgebirge, Balkone, Rand
def _staircase(t, step_h, wall_w, ledge_w):
    p = wall_w + ledge_w
    k = np.floor(t / p)
    f = np.clip((t - k * p) / wall_w, 0.0, 1.0)
    f = f * f * (3 - 2 * f)
    return step_h * (k + f)


def rim(c: Ctx):
    x, z, r, az = c.x, c.z, c.r, c.az
    nz = c.nz
    th = np.radians(az)
    px, pz = RIM_R * np.sin(th), -RIM_R * np.cos(th)       # Projektion auf den Kammkreis
    rc = RIM_R + nz.fbm("rimrc", px, pz, 320, 3) * 30.0
    peaks = nz.ridged("rimpk", px, pz, 170, 3, sharp=2.2)
    hc = 178.0 + 150.0 * np.clip(peaks, 0, 1) ** 1.5 + nz.fbm("rimhc", px, pz, 520, 2) * 40.0
    hc = np.clip(hc, 165.0, 318.0)
    # Balkon-Kerben
    notch = np.full(r.shape, 1e9)
    for b in BALCONY_AZ:
        lb = RIM_R * np.abs(np.radians(ang_diff(az, b)))
        notch = np.minimum(notch, lb)
    hc = np.minimum(hc, BALCONY_FLOOR + np.maximum(0.0, notch - 36.0) * math.tan(math.radians(52)))
    rc = np.where(notch < 60, np.maximum(rc, 1998.0 - np.maximum(0, notch - 36) * 0.4), rc)
    c.rim_rc, c.rim_hc = rc, hc
    H = c.H
    hb = H
    # Innenseite: Stufen-Wand (Baender) mit Rinnen und Spornen
    gully = nz.ridged("rimgully", px, pz, 55, 2, sharp=1.6)
    t = rc - r
    t_eff = np.maximum(0.0, t + 6.0 * nz.fbm("rimledge", x, z, 40, 2) + 22.0 * (gully - 0.5) * ss(0, 60, t))
    drop = _staircase(t_eff, 34.0, 9.0, 13.0)
    h_in = hc - drop
    tfoot = np.maximum(1.0, (hc - hb) / 1.45)
    tal_h = 0.24 * (hc - hb)
    tal_l = tal_h / math.tan(math.radians(31))
    tq = np.clip((t - tfoot + 0.35 * tal_l) / tal_l, 0, 1)
    h_tal = hb + tal_h * (1.0 - tq) ** 1.4
    inner = (t >= 0) & (t < 460)
    tal_ok = (t > tfoot - 0.4 * tal_l) & (tq < 1.0)
    newh = np.maximum(H, np.maximum(h_in, np.where(tal_ok, h_tal, -1e9)))
    # Aussenseite: steile Abbruchkante (70-80 Grad) mit Simsen
    to = r - rc
    drop_o = _staircase(np.maximum(0.0, to + 3.0 * nz.fbm("rimout", x, z, 30, 2)), 40.0, 4.5, 5.0)
    h_out = hc - drop_o
    bottom = -95.0 - 0.9 * np.maximum(0.0, 2050.0 - r) + nz.fbm("bottom", x, z, 90, 3) * 45.0
    bottom = np.minimum(bottom, -80.0)
    outer = to >= 0
    H2 = np.where(inner, newh, H)
    H2 = np.where(outer, h_out, H2)
    void = outer & (h_out < bottom + 10.0)
    c.H = H2
    c.void |= void | (r > 2250)
    # Material-Masken
    rim_m = c.mask("rim")
    rim_m |= (inner & (newh > hb + 3.0)) | (outer & ~void)
    tal_m = c.mask("rim_talus")
    tal_m |= inner & tal_ok & (h_tal >= h_in - 0.5) & (h_tal > hb + 0.8)
    deep = (r > 1890) & ~c.void
    c.bottom = np.where(deep, np.minimum(bottom, c.H - 20.0), c.bottom)
    c.obstacle |= rim_m | tal_m
    c.feat["rim_rc"] = rc
    _balconies(c)


def _balconies(c: Ctx):
    H = c.H
    for i, b in enumerate(BALCONY_AZ):
        cx, cz = pol(b, 1960.0)
        sl = c.win(cx * 0.95, cz * 0.95, 190)
        x, z = c.local(sl)
        r = np.hypot(x, z)
        az = np.degrees(np.arctan2(x, -z)) % 360
        lb = 1960.0 * np.radians(ang_diff(az, b))
        alb = np.abs(lb)
        hl = H[sl]
        # Rampe von der Hochflaeche (r 1835) hinauf zur Plattform (<= 12 Grad)
        ramp_t = np.clip((r - 1835.0) / 115.0, 0, 1)
        ramp_h = BENCH_E2 + (BALCONY_FLOOR - BENCH_E2) * ramp_t
        corridor = (alb < 34 + 0.2 * np.maximum(0, 1950 - r)) & (r > 1835) & (r < 1952)
        hl = np.where(corridor, np.minimum(np.maximum(hl, ramp_h - 0.5), ramp_h + 0.4 * ss(24, 34, alb)), hl)
        plat = (alb < 31) & (r >= 1950) & (r < 1993)
        hl = np.where(plat, BALCONY_FLOOR + 0.3 * c.nz.fbm("balc", x, z, 12, 1), hl)
        para = (alb < 33) & (r >= 1993) & (r < 1998)
        hl = np.where(para, BALCONY_FLOOR + 4.0, hl)
        H[sl] = hl
        m = c.mask("balcony")
        m[sl] |= plat | para
        c.mask("ramp")[sl] |= corridor
        c.void[sl] &= ~(plat | para)
        c.bottom[sl] = np.where(plat | para, np.minimum(np.nan_to_num(c.bottom[sl], nan=-150.0), -150.0), c.bottom[sl])
        c.feat["balcony"].append({"az": b, "x": cx, "z": cz, "y": BALCONY_FLOOR})


# ---------------------------------------------------------------- Schwebende Felsen (Hoehenkarte + Tiefe)
def floating_rocks(c: Ctx):
    rng = c.rng
    rocks = []
    big = [(60.0, 2400.0, 152.0, 150.0), (300.0, 2300.0, 72.0, 150.0)]
    for a, rr, y, R in big:
        x0, z0 = pol(a, rr)
        rocks.append((x0, z0, y, R, True))
    arch = [(18, 2330, 30), (100, 2250, -60), (165, 2300, 110), (222, 2420, -20), (338, 2280, 160)]
    lim = 2304 - 8
    for a, rr, ybase in arch:
        ax, azz = pol(a + c.u(-5, 5), rr + c.u(-40, 40))
        n = int(rng.integers(10, 14))
        for k in range(n):
            for _ in range(30):
                big_one = k == 0
                R = c.u(45, 70) if big_one else (c.u(22, 40) if k < 4 else c.u(10, 22))
                ang = c.u(0, 2 * math.pi)
                dist = 0 if big_one else c.u(60, 260)
                x0, z0 = ax + dist * math.cos(ang), azz + dist * math.sin(ang)
                r0 = math.hypot(x0, z0)
                if r0 - R * 1.25 < 2150 or abs(x0) + R * 1.25 > lim or abs(z0) + R * 1.25 > lim:
                    continue
                if any(math.hypot(x0 - q[0], z0 - q[1]) < (R + q[3]) * 1.15 for q in rocks):
                    continue
                y = ybase + c.u(-110, 110) * (0.4 if big_one else 1.0)
                y = float(np.clip(y, -195, 230))
                rocks.append((x0, z0, y, R, False))
                break
    for (x0, z0, y, R, is_big) in rocks:
        sl = c.win(x0, z0, R * 1.35)
        x, z = c.local(sl)
        dx, dz = x - x0, z - z0
        rho = np.hypot(dx, dz)
        th = np.arctan2(dz, dx)
        nn = c.nz.fbm("flt", x0 + 40 * np.cos(th), z0 + 40 * np.sin(th), 30, 2)
        Rt = R * (1.0 + 0.32 * nn + 0.08 * c.nz.fbm("flt2", x, z, 14, 2))
        q = rho / Rt
        inside = q < 1.0
        top = y + 0.12 * R * (1 - q ** 2) + 1.5 * c.nz.fbm("fltt", x, z, 18, 2) - 2.5 * ss(0.85, 1.0, q)
        thick = R * (1.5 if not is_big else 0.95)
        bot = y - thick * (1.0 - np.clip(q, 0, 1) ** 1.4) ** 0.75 - 4.0 * np.abs(c.nz.fbm("fltb", x, z, 20, 2)) - 3.0
        cur_void = c.void[sl]
        set_ = inside & (cur_void | (top > c.H[sl]))
        c.H[sl] = np.where(set_, top, c.H[sl])
        c.bottom[sl] = np.where(set_, np.minimum(bot, top - 6.0), c.bottom[sl])
        c.void[sl] = np.where(set_, False, cur_void)
        c.mask("float")[sl] |= set_
        c.feat["float"].append({"x": x0, "z": z0, "y": y, "R": R, "big": is_big})
