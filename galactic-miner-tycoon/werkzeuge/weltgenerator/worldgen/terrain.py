"""Grundgelaende: Ringprofil mit Stufen (Schichtstufen), Grund-Rauschen, Washes, Randgebirge, Rand, Schwebfelsen."""
from __future__ import annotations

import math

import numpy as np
from scipy.ndimage import gaussian_filter1d

from .ctx import Ctx
from .world import HALF
from .layout import BALCONY_AZ, PLATEAU_R, ang_diff, pol, sh, sr
from .noise import smoothstep as ss

# Runde 2 (Entscheidung 022): Kamm bei r ~990 (alt 1972), Balkon/Hochland-Hoehen mit dem Profil halbiert
RIM_R = 996.0
RIM_RC_MIN, RIM_RC_MAX = 984.0, 1010.0     # Kammlinie (alt 1955-2015)
BALCONY_FLOOR = 25.0
BENCH_E2 = sh(30.0)
RIM_H = 0.68                               # Randgebirge 32 % niedriger (wirkt bei halbem Radius sonst uebermaechtig)


def ring_fields(c: Ctx):
    """Verwischter Radius (Ring-Grenzen mit Domain-Warping, +-40 Studs, Wellenlaenge 130) und Sektor C-Nordost."""
    # Ring-Grenzen verwischt fuer Materialien; fuer Hoehen ein weicherer Warp,
    # sonst staucht der Warp das Profil und verdoppelt stellenweise die Neigung. Runde 2: alles x 0,5
    pr = ss(PLATEAU_R + 4, PLATEAU_R + 50, c.r)
    w = c.nz.fbm("ringwarp", c.x, c.z, sr(260), 3) * sr(150.0)
    c.rw_mat = c.r + np.clip(w, -sr(80), sr(80)) * pr
    wh = c.nz.fbm("ringwarph", c.x, c.z, sr(620), 2) * sr(160.0)
    c.rw = c.r + np.clip(wh, -sr(75), sr(75)) * pr
    azj = c.az + c.nz.fbm("sectorjit", c.x, c.z, sr(400), 2) * 25.0
    d1 = ang_diff(azj, 30.0)          # Mitte des Nordost-Sektors (300..120)
    c.wNE = 1.0 - ss(90.0, 110.0, np.abs(d1))
    c.sector_ne = c.wNE > 0.5


def _scarp(rw, rk, hk, g):
    """Schichtstufe: steil (g=1, Wand + Schutthalde) oder sanfte Rampe (g=0). hk>0: aussen hoeher."""
    habs = abs(hk)
    w_sharp = habs / math.tan(math.radians(62)) + 10.0
    w_gentle = habs / math.tan(math.radians(12.0))  # Rampe: kurz und befahrbar (<= 20 Grad), spart Bauflaeche (Runde 2: 12 statt 8,5)
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


# Runde 2: Die umlaufenden Schichtstufen (s0 Basaltplateau C-Nordost, s1/s1b C -> D, s2 D -> Hochland E, s4 E1 -> E2)
# entfallen: bei halbem Radius kostet ein Stufenring doppelt so viel Bauflaeche je Ring (Ring B-E fielen unter 35 %),
# und bei Profil-Hoehen x 0,3 waeren sie nur noch 3-8 Studs hoch. Ihre Hoehe steckt jetzt in flachen Rampen
# (<= ~5 Grad) in profile(). Die Mechanik bleibt fuer spaetere Inseln.
SCARPS = []  # (Radius, Hoehe, Name, nur Nordost-Sektor C)


def profile(rw, wNE, gs=None, wig=None):
    """Radiales Hoehenprofil (y). gs: Schaerfe der Stufen (None = alle sanft, fuer Wash-Boeden)."""
    # Grosse ebene Flaechen, Hoehenwechsel gebuendelt in Schichtstufen (wie Colorado-Plateau)
    # Runde 2: Plateau-Rand bleibt bei r ~120 (Basis), der Rest x 0,5 in Radius und Hoehe
    h = sh(-6.0) * ss(PLATEAU_R + 6, PLATEAU_R + 50, rw) - sh(4.0) * ss(sr(300), sr(560), rw)
    h = h + sh(2.0) * (1.0 - wNE) * ss(sr(600), sr(780), rw)          # C-Suedwest: Duenenland
    h = h + sh(12.0) * wNE * ss(300.0, 380.0, rw) * (1.0 - ss(520.0, 600.0, rw))   # C-Nordost: Basaltplateau (alte s0/s1b)
    h = h - sh(4.0 + 12.0 * (1.0 - wNE)) * ss(540.0, 640.0, rw)        # D-Becken (mit alter Stufe s1)
    h = h + sh(8.0 + 20.0) * ss(640.0, 900.0, rw)                      # Hochland E1 (mit alter Steilstufe s2)
    h = h + sh(4.0 + 10.0) * ss(860.0, 960.0, rw)                      # E2 (mit alter Stufe s4)
    for k, (rk, hk, name, ne) in enumerate(SCARPS):
        g = 0.0 if gs is None else gs[k]
        off = 0.0 if wig is None else wig[k]
        dh, _, _ = _scarp(rw, rk + off, hk, g)
        h = h + dh * (wNE if ne else 1.0)
    return h


def base_terrain(c: Ctx):
    ring_fields(c)
    x, z, rw = c.x, c.z, c.rw
    nz = c.nz
    gs, wig = [], []
    for k, (rk, hk, name, ne) in enumerate(SCARPS):
        gname = name.rstrip("b")
        g = ss(-0.2, -0.05, nz.fbm("scarpg" + gname, x, z, sr(260), 3))
        gs.append(g)
        wig.append(nz.fbm("scarpw" + gname, x, z, sr(70) + 10, 3) * sr(30.0))
    c.scarp_g = gs
    c.scarp_wig = wig
    h = profile(rw, c.wNE, gs, wig)
    # Stufen-Waende merken (fuer Material + Deko)
    sc = c.mask("scarp")
    for k, (rk, hk, name, ne) in enumerate(SCARPS):
        _, t, w = _scarp(rw, rk + wig[k], hk, gs[k])
        wall = (gs[k] > 0.5) & (t > 0.05) & (t < 0.95)
        if ne:
            wall &= c.wNE > 0.5
        sc |= wall
    c.obstacle |= sc
    # Grund-Rauschen (Vorgabe 2.5), Amplituden leicht gedaempft wegen Bauzonen-Neigung <= 6 Grad
    # Amplituden gegenueber Vorgabe 2.5 reduziert, sonst liegt zu viel Flaeche ueber 6 Grad (Bauzonen-Regel)
    n = (nz.fbm("o1", x, z, 300, 1) * 3.0 + nz.fbm("o2", x, z, 90, 1) * 0.7
         + nz.fbm("o3", x, z, 28, 1) * 0.08)
    # Runde 2: Wellenlaengen des Grundrauschens bleiben (Objekt-Massstab), die Ring-Grenzen x 0,5
    amp = 1.0 - 0.6 * (1.0 - ss(PLATEAU_R + 30, sr(300) + 20, rw))         # Plateau-Rand ruhiger
    amp = amp * (1.0 - 0.4 * ss(sr(1200), sr(1260), rw) * (1.0 - ss(sr(1430), sr(1470), rw)))  # D-Becken x0.6
    amp = amp * ss(PLATEAU_R, PLATEAU_R + 40, c.r)                       # Plateau eben
    micro = nz.fbm("plateau", x, z, 40, 2) * 0.45 * (1.0 - ss(PLATEAU_R, PLATEAU_R + 40, c.r))
    micro = micro + (nz.fbm("microw", x, z, 85, 2) * 1.6 + nz.fbm("microw2", x, z, 34, 1) * 0.3) \
        * ss(PLATEAU_R + 2, PLATEAU_R + 40, c.r) * (1.0 - ss(sr(380), sr(520), c.r))
    macro = (nz.fbm("macrorel", x, z, 120, 2) * 1.6 + nz.fbm("macrorel2", x, z, 65, 1) * 0.5) \
        * ss(PLATEAU_R + 25, PLATEAU_R + 60, c.r) \
        * (1.0 - 0.6 * ss(sr(1550), sr(1700), c.r))        # Ring E: Boden dort schon fleckig (Slate/Rock), Bauflaechen schonen
    c.H = h + n * amp + micro + macro
    c.base_smooth = h  # ohne Rauschen (fuer Washes)


# ---------------------------------------------------------------- Washes
WASH_RMAX, WASH_DR = sr(2000.0), 2.0      # Mittellinie in 2-Stud-Schritten (vorher 4 bis r 2000)


def wash_lines(c: Ctx):
    """Mittellinien der 6 Washes (fest +- Jitter), Maeander als seitlicher Versatz."""
    lines = []
    rs = np.arange(0.0, WASH_RMAX, WASH_DR)
    for k, a0 in enumerate(c.L.washes):
        phi = c.u(0, 2 * math.pi)
        # Runde 2 (Offen aus Runde 1: kurviger): Maeander-Wellenlaenge 500 -> 210, zwei Wellen ueberlagert; seitlich
        # +-14 + 26 (Rauschen) statt +-21 + 55 -> bei halbem Radius ein staerker gewundener Lauf
        phi2 = c.u(0, 2 * math.pi)
        lat = 14.0 * np.sin(2 * math.pi * rs / 210.0 + phi) + 6.0 * np.sin(2 * math.pi * rs / 95.0 + phi2) \
            + 26.0 * c.nz.fbm(f"washlat{k}", rs, np.full_like(rs, 1000.0 * k), sr(800), 2)
        lat *= ss(PLATEAU_R, PLATEAU_R + 70, rs)
        az = a0 + np.degrees(lat / np.maximum(rs, 25.0))
        # die vier Washes mit Balkon biegen am Ende zum Balkon ab
        for b in BALCONY_AZ:
            if abs(ang_diff(b, a0)) < 16:
                az = az + ang_diff(b, az) * ss(sr(1550), sr(1840), rs)
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
    ri = np.clip((r / WASH_DR).astype(int), 0, int(WASH_RMAX / WASH_DR) - 1)
    for k, (rs, azl) in enumerate(c.wash_lines):
        # Bodenprofil entlang des Wash: sanftes Profil (ohne Stufen), stark geglaettet
        px = rs * np.sin(np.radians(azl))
        pz = -rs * np.cos(np.radians(azl))
        iz, ix = c.idx(px, pz)
        prof = profile(c.rw[iz, ix], c.wNE[iz, ix])
        prof = gaussian_filter1d(prof, 44.0 / WASH_DR, mode="nearest")
        # Runde 2: 2-3,2 tief (vorher 2-4); mit Ufer 10 bleibt die Uferneigung <= ~24 Grad -> Boden von der Basis
        # aus erreichbar (Flood-Fill <= 25 Grad), sonst zaehlt der Wash-Boden nicht als Bauzone
        depth = 2.6 + 0.6 * c.nz.fbm(f"washdep{k}", rs, np.full_like(rs, 7.0 * k), sr(300), 2) * 2
        depth = np.clip(depth, 2.0, 3.2) * ss(PLATEAU_R + 4, PLATEAU_R + 50, rs) * (1.0 - ss(sr(1830), sr(1890), rs))
        # Runde 2: in Ring B/C flache Sand-Mulden statt Rinnen (1,1-1,5 tief, Ufer <= ~5 Grad): Wege wie im
        # Zielbild und die Ufer bleiben Bauzone; nach aussen (r 440-620) werden sie zu echten Washes
        shallow = 1.0 - ss(440.0, 620.0, rs)
        depth = depth * (1.0 - 0.55 * shallow)
        floor = prof - depth
        # Runde 2 (Offen aus Runde 1: schmaler): Breite 38-60 Studs (halbe Breite 19-30) statt 50-90, wechselnd.
        # Boden bleibt >= 24 breit (Bauzonen-Pruefung verlangt Flecken >= 20 breit, Erz darf in den Washes liegen)
        hw = (23.0 + 6.0 * ss(sr(250), sr(1100), rs)) * (1.0 + 0.25 * c.nz.fbm(f"washw{k}", rs, np.full_like(rs, 3.0 * k), sr(260), 2) * 2.0)
        hw = np.clip(hw, 21.0, 31.0) * (0.75 + 0.25 * ss(PLATEAU_R, PLATEAU_R + 50, rs))
        # Zelle -> seitlicher Abstand zur Linie
        a_here = azl[ri]
        lat = r * np.sin(np.radians(ang_diff(az, a_here)))
        d = np.abs(lat)
        ok = (np.abs(ang_diff(az, a_here)) < 45) & (r > PLATEAU_R) & (r < sr(1900))
        hwc = hw[ri]
        fl = floor[ri]
        dep = depth[ri]
        shc = shallow[ri]
        bank = 10.0 + 8.0 * shc
        tb = np.clip((d - (hwc - bank)) / bank, 0.0, 1.0)
        prof_b = tb * tb * (3 - 2 * tb) * (1.0 - shc) + (tb * (1.15 - 0.15 * tb)) * shc     # innen fast linear
        cut = fl + dep * prof_b + np.maximum(0.0, d - hwc) * np.tan(np.radians(33.0 - 28.0 * shc))
        # Geflochtene Nebenarme: flache Rinnen neben dem Hauptbett, die sich wieder vereinen
        # Runde 2: Nebenarme erst ab Ring C (in Ring B zerschnitten sie die knappen Bauflaechen)
        for j in range(2):
            r0 = 300.0 + 260.0 * j + c.u(0, 100)
            L = c.u(sr(220), sr(380))
            side = 1 if c.u() < 0.5 else -1
            off = side * (hw[ri] + c.u(12, 20)) * np.sin(np.pi * np.clip((r - r0) / L, 0, 1)) ** 0.8
            da = np.abs(lat - off)
            arm = (r > r0) & (r < r0 + L)
            armcut = fl + 1.2 + dep * 0.6 * ss(4, 9, da) + np.maximum(0.0, da - 9) * math.tan(math.radians(25))
            cut = np.where(arm, np.minimum(cut, armcut), cut)
            c.mask("wash_arm")[:] |= ok & arm & (da < 8) & (dep > 0.5)
        sel = ok & (d < hwc + 110)
        H[sel] = np.minimum(H[sel], cut[sel])
        inner = ok & (d < hwc) & (dep > 0.5)
        wash_m |= inner
        floor_m |= ok & (d < hwc - bank) & (dep > 0.5)
        # Kiesinseln im Bett (Ground, laenglich, leicht erhaben)
        bars = ok & (d < hwc - bank * 0.6) & (dep > 0.5) & (c.nz.fbm(f"bars{k}", lat / 8.0, r / 45.0, 1.0, 2) > 0.33)
        c.mask("wash_bar")[:] |= bars
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
    # Runde 2: Kammlinie, Massive und Gipfel entlang des (halb so langen) Kranzes x 0,5; Hoehen x RIM_H (0,7)
    rc = RIM_R + nz.fbm("rimrc", px, pz, sr(600), 3) * sr(80.0) + nz.fbm("rimrc2", px, pz, sr(160), 2) * sr(20.0)
    rc = np.clip(rc, RIM_RC_MIN, RIM_RC_MAX)
    # Massive mit Gipfeln und Saetteln unterschiedlicher Hoehe (Review: keine gleichmaessige Wand)
    massif = ss(-0.25, 0.3, nz.fbm("rimmacro", px, pz, sr(650), 2))
    # Review: ruhigere Grate (sharp 1,3, Zacken halbiert) und weiche Terrassen -> "Mega-Tafelberge" derselben Familie
    peaks = np.clip(nz.ridged("rimpk", px, pz, sr(230) + 20, 3, sharp=1.3), 0, 1)
    teeth = nz.ridged("rimteeth", px, pz, 45, 2, sharp=1.3)
    # Runde 1: Zacken 7 -> 3 (ruhigere Kronen wie im Zielbild)
    hc = RIM_H * (118.0 + 125.0 * massif + 120.0 * peaks ** 1.8 * (0.25 + 0.75 * massif)) + 2.0 * teeth
    step = 20.0
    k = np.floor(hc / step)
    f = np.clip((hc - k * step) / step, 0, 1)
    hc = k * step + step * ss(0.55, 0.95, f)          # flache Kronen-Stufen, weiche Kanten
    hc = np.clip(hc, RIM_H * 110.0, RIM_H * 330.0)
    # Balkon-Kerben
    notch = np.full(r.shape, 1e9)
    for b in BALCONY_AZ:
        lb = RIM_R * np.abs(np.radians(ang_diff(az, b)))
        notch = np.minimum(notch, lb)
    hc = np.minimum(hc, BALCONY_FLOOR + np.maximum(0.0, notch - 30.0) * math.tan(math.radians(52)))
    rc = np.where(notch < 50, np.maximum(rc, RIM_R + 12.0 - np.maximum(0, notch - 30) * 0.4), rc)
    c.rim_rc, c.rim_hc = rc, hc
    H = c.H
    hb = H
    # Innenseite: gestufte Wand mit Rinnen und Spornen; Sporne laufen als Grate ins Hochland
    # Runde 1: breitere, flachere Rinnen (Skala 55 -> 140, Amplitude 22 -> 9) und breitere Simse: liest sich als gestufte
    # Mega-Tafelberge statt als feine Riffelwand. Vorschlag war Stufe 26 / Wand 6 / Sims 14; das schiebt den Wandfuss
    # ~65 Studs nach innen (Ring E verliert ~14 % Bauzone). Darum 28 / 4 / 10: Verhaeltnis 0,5 bleibt innerhalb der
    # Schutthalde (Fuss bei 0,525 x Wandhoehe) -> keine Bauflaeche verloren.
    # Runde 2: Stufen 24 / Wand 4 / Sims 6 (mittlere Neigung 2,4:1 statt 2:1 bei 28/4/10, engere Simse ->
    # der niedrigere Kamm frisst weniger Bauflaeche von Ring E); Sporne 25 statt 55 lang
    gully = nz.ridged("rimgully", px, pz, 100, 2, sharp=1.6)
    t = rc - r
    spur = np.maximum(0.0, nz.ridged("rimspur", px, pz, sr(190) + 15, 2, sharp=3.0) - 0.35) / 0.65
    spur_len = 25.0 * spur ** 1.5
    t_eff = np.maximum(0.0, t + 5.0 * nz.fbm("rimledge", x, z, 40, 2) + 7.0 * (gully - 0.5) * ss(0, 50, t))
    t_spur = np.maximum(0.0, t - spur_len)
    drop = np.minimum(_staircase(t_eff, 24.0, 4.0, 6.0), _staircase(t_spur, 24.0, 4.0, 6.0) + spur_len * 0.9)
    h_in = hc - drop
    tfoot = np.maximum(1.0, (hc - hb) / 2.6)
    tal_h = 0.13 * (hc - hb)
    tal_l = tal_h / math.tan(math.radians(31))
    tq = np.clip((t - tfoot + 0.35 * tal_l) / tal_l, 0, 1)
    h_tal = hb + tal_h * (1.0 - tq) ** 1.4
    inner = (t >= 0) & (t < sr(460))
    tal_ok = (t > tfoot - 0.4 * tal_l) & (tq < 1.0)
    newh = np.maximum(H, np.maximum(h_in, np.where(tal_ok, h_tal, -1e9)))
    # Aussenseite: steile Abbruchkante (70-80 Grad) mit Simsen
    to = r - rc
    drop_o = _staircase(np.maximum(0.0, to + 3.0 * nz.fbm("rimout", x, z, 30, 2)), 40.0, 4.5, 5.0)
    h_out = hc - drop_o
    # Unterseite: umgekehrter Kegel (Runde 2: halbe Groesse)
    bottom = -60.0 - 0.9 * np.maximum(0.0, sr(2080.0) - r) + nz.fbm("bottom", x, z, 60, 3) * 28.0
    bottom = np.minimum(bottom, -50.0)
    outer = to >= 0
    H2 = np.where(inner, newh, H)
    H2 = np.where(outer, h_out, H2)
    void = outer & (h_out < bottom + 10.0)
    c.H = H2
    c.void |= void | (r > sr(2250))
    # Material-Masken
    rim_m = c.mask("rim")
    rim_m |= (inner & (newh > hb + 3.0)) | (outer & ~void)
    tal_m = c.mask("rim_talus")
    tal_m |= inner & tal_ok & (h_tal >= h_in - 0.5) & (h_tal > hb + 0.8)
    deep = (r > sr(1890)) & ~c.void
    c.bottom = np.where(deep, np.minimum(bottom, c.H - 20.0), c.bottom)
    c.obstacle |= rim_m | tal_m
    c.feat["rim_rc"] = rc
    rim_arches(c)
    _balconies(c)


RIM_ARCH_AZ = (70.0, 120.0, 300.0)


def rim_arches(c: Ctx):
    """Runde 1: drei Felsfenster im Kamm (Luft-Zylinder r 18-26, Achse radial), 14+ Studs Fels darueber.
    Von innen sieht man durch das Fenster den Himmel hinter dem Rand (Bogen-Silhouette wie im Zielbild)."""
    from .landforms import op_cyl
    rng = np.random.default_rng(c.seed * 4001 + 17)     # eigener Zufall: aendert den Rest der Welt nicht
    for a0 in RIM_ARCH_AZ:
        best = None
        # hoechste Kammstelle im Umkreis +-6 Grad: dort ist der Bogen am deutlichsten und bleibt dick genug
        for da in np.linspace(-6, 6, 13):
            a = a0 + da
            iz, ix = c.idx(*pol(a, RIM_R))
            hc = float(c.rim_hc[iz, ix])
            if best is None or hc > best[1]:
                best = (a, hc, float(c.rim_rc[iz, ix]))
        a, hc, rc = best
        rr = float(rng.uniform(16.0, 22.0))
        x, z = pol(a, rc + 2.0)
        # Oberkante nach dem niedrigsten Kammpunkt ueber dem Fenster (Kamm ist zackig): >= 14 Studs Fels darueber
        sl = c.win(x, z, rr)
        lx, lz = c.local(sl)
        disk = (lx - x) ** 2 + (lz - z) ** 2 < rr * rr
        h_low = float(np.percentile(c.H[sl][disk], 15)) if disk.any() else hc
        yc = min(hc, h_low) - 14.0 - rr
        if yc - rr < BALCONY_FLOOR:          # zu niedriger Kamm: kein Fenster
            continue
        d = np.array([math.sin(math.radians(a)), 0.0, -math.cos(math.radians(a))])
        xc = np.array([0.0, 1.0, 0.0])
        zc = np.cross(xc, d)
        R = np.column_stack([xc, d, zc])     # lokale Y-Achse = radial
        op_cyl(c, x, yc, z, 130.0, rr, "Air", R)
        c.feat["rim_arch"].append({"az": a, "x": x, "z": z, "y": yc, "r": rr})


def foothills(c: Ctx, n=8):
    """Vorberge/Massive vor dem Randgebirge, die die Kammlinie ueberschneiden (Slate/Rock, keine Baender)."""
    rng = c.rng
    done = 0
    for _ in range(600):
        if done >= n:
            break
        a = rng.uniform(0, 360)
        if min(abs(ang_diff(a, b)) for b in BALCONY_AZ) < 9 or min(abs(ang_diff(a, w)) for w in c.L.washes) < 8:
            continue
        # Runde 1: Abstand zur oertlichen Kammlinie statt fester Radius (vorher r 1870-1915): Vorberge ueberschneiden
        # immer den Kamm und ragen nicht weit in die Bauflaechen von Ring E
        px, pz = pol(a, RIM_R)
        rc = float(np.clip(RIM_R + c.nz.fbm("rimrc", np.array(px), np.array(pz), sr(600), 3) * sr(80.0)
                           + c.nz.fbm("rimrc2", np.array(px), np.array(pz), sr(160), 2) * sr(20.0), RIM_RC_MIN, RIM_RC_MAX))
        # Runde 2: naeher am Kamm (35-60 statt 55-95), kleiner und flacher (Ring E ist nur noch 150 tief)
        r = rc - rng.uniform(35, 60)
        x0, z0 = pol(a, r)
        if c.mask("claimed")[c.idx(x0, z0)]:
            continue
        if any(math.hypot(x0 - f["x"], z0 - f["z"]) < 170 for f in c.feat["foothill"]):
            continue
        R = rng.uniform(30, 55)
        hgt = rng.uniform(25, 55)
        sl = c.win(x0, z0, R * 1.6)
        x, z = c.local(sl)
        th = np.arctan2(z - z0, x - x0)
        q = np.hypot(x - x0, z - z0) / R * (1 + 0.22 * c.nz.fbm("fh%d" % done, x, z, 40, 3))
        prof = np.where(q < 1.4, hgt * np.clip(1 - q / 1.4, 0, 1) ** 1.25, -1e9)
        prof = prof + c.nz.ridged("fhr%d" % done, x, z, 35, 2) * 6 * np.clip(1 - q, 0, 1)
        base = float(np.percentile(c.H[sl], 40))
        hn = np.where(prof > -1e8, base + prof, -1e9)
        c.H[sl] = np.maximum(c.H[sl], hn)
        m = hn > c.H[sl] - 0.01
        m &= q < 1.35
        c.mask("rim")[sl] |= m & (prof > 2)
        c.mask("foothill")[sl] |= m & (prof > 2)
        c.obstacle[sl] |= m & (prof > 4)
        c.feat["foothill"].append({"x": x0, "z": z0, "R": R})
        done += 1
    return done


def _balconies(c: Ctx):
    H = c.H
    # Runde 2: Plattform r 974-996 (vorher 1950-1993), Rampe r 918-974 von y 15 auf 25 (~10 Grad)
    RB = RIM_R - 6.0
    R0, R1, R2, R3 = sr(1835.0), RB - 6.0, RB + 16.0, RB + 20.0
    for i, b in enumerate(BALCONY_AZ):
        cx, cz = pol(b, RB)
        sl = c.win(cx * 0.95, cz * 0.95, 110)
        x, z = c.local(sl)
        r = np.hypot(x, z)
        az = np.degrees(np.arctan2(x, -z)) % 360
        lb = RB * np.radians(ang_diff(az, b))
        alb = np.abs(lb)
        hl = H[sl]
        # Rampe von der Hochflaeche hinauf zur Plattform (<= 12 Grad)
        ramp_t = np.clip((r - R0) / (R1 - R0), 0, 1)
        ramp_h = BENCH_E2 + (BALCONY_FLOOR - BENCH_E2) * ramp_t
        corridor = (alb < 30 + 0.2 * np.maximum(0, R1 - r)) & (r > R0) & (r < R1 + 2)
        hl = np.where(corridor, np.minimum(np.maximum(hl, ramp_h - 0.5), ramp_h + 0.4 * ss(20, 30, alb)), hl)
        plat = (alb < 28) & (r >= R1) & (r < R2)
        hl = np.where(plat, BALCONY_FLOOR + 0.3 * c.nz.fbm("balc", x, z, 12, 1), hl)
        para = (alb < 30) & (r >= R2) & (r < R3)
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
    # Runde 2: alles hinter die neue Kante (r ~1040) gezogen und ~0,6 x so gross; das Raster endet bei +-1152
    big = [(60.0, 1170.0, 110.0, 80.0), (300.0, 1165.0, 55.0, 80.0)]
    for a, rr, y, R in big:
        x0, z0 = pol(a, rr)
        rocks.append((x0, z0, y, R, True))
    # Archipel 0 liegt vom Balkon Az 45 aus gesehen vor Saturn (Postkarte Ring E)
    arch = [(40, 1190, 118), (100, 1110, -40), (165, 1125, 78), (222, 1230, -15), (338, 1160, 112)]
    lim = HALF - 8
    for a, rr, ybase in arch:
        ax, azz = pol(a + c.u(-5, 5), rr + c.u(-20, 20))
        n = int(rng.integers(8, 12))
        for k in range(n):
            for _ in range(30):
                big_one = k == 0
                R = c.u(28, 42) if big_one else (c.u(14, 24) if k < 4 else c.u(8, 14))
                ang = c.u(0, 2 * math.pi)
                dist = 0 if big_one else c.u(35, 150)
                x0, z0 = ax + dist * math.cos(ang), azz + dist * math.sin(ang)
                r0 = math.hypot(x0, z0)
                if r0 - R * 1.25 < sr(2150) or abs(x0) + R * 1.35 > lim or abs(z0) + R * 1.35 > lim:
                    continue
                if any(math.hypot(x0 - q[0], z0 - q[1]) < (R + q[3]) * 1.15 for q in rocks):
                    continue
                y = ybase + c.u(-80, 80) * (0.4 if big_one else 1.0)
                y = float(np.clip(y, -140, 165))
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
