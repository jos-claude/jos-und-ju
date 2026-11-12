"""Setzt alle Landformen nach dem festen Aufbau zusammen (Reihenfolge = Erosionsgeschichte)."""
from __future__ import annotations

import math

import numpy as np

from . import fields, landforms as lf, terrain, waterforms as wf
from .ctx import Ctx
from .layout import ang_diff, pol
from .noise import smoothstep as ss

# Sichtachsen von der Basis: hier keine hohen Formen (Mesas, Spitzen, Kaemme)
SIGHT = [(40.0, 6.5, 260, 980), (105.0, 4.0, 260, 1250), (140.0, 4.0, 260, 520), (198.0, 4.5, 260, 1380),
         (251.0, 4.0, 260, 1200), (297.0, 4.0, 260, 390)]


def sight_block(az, r):
    for a, w, r0, r1 in SIGHT:
        if r0 <= r <= r1 and abs(ang_diff(az, a)) < w + 600.0 / max(r, 120.0):
            return True
    return False


def gate_axis(c: Ctx):
    """Azimut (von der Basis) der Sichtachse Spawn -> Vulkan durch das Saturn-Tor."""
    sx, _, sz = c.L.spawn
    vx, vz = c.L.slots["L5"].xz
    return math.degrees(math.atan2(vx - sx, -(vz - sz))) % 360


def wash_az_at(c: Ctx, k, r):
    rs, az = c.wash_lines[k]
    return float(az[min(len(az) - 1, int(r / 4))])


def nudge(c: Ctx, az, r, need, span=8.0):
    """Verschiebt einen Slot innerhalb +-span Grad, bis der Abstand zum naechsten Wash >= need ist."""
    best, bestd = az, -1e9
    for da in sorted(np.linspace(-span, span, 33), key=abs):
        x, z = pol(az + da, r)
        d = float(c.wash_dist[c.idx(x, z)])
        if d >= need:
            return az + da
        if d > bestd:
            best, bestd = az + da, d
    return best


# ------------------------------------------------------------------ Washes mit Umweg
def setup_washes(c: Ctx):
    terrain.wash_lines(c)
    # Wash 0 (Az 40) laeuft im Bogen oestlich um den Vulkan herum
    rs, az = c.wash_lines[0]
    s5 = c.L.slots["L5"]
    vr = s5.r
    gate_az = gate_axis(c)
    w = ss(130, 220, rs) * (1 - ss(430, 560, rs))
    az = az + ang_diff(gate_az, az) * w
    bump = 360.0 * np.exp(-((rs - vr) / 330.0) ** 2)
    c.wash_lines[0] = (rs, az + np.degrees(bump / np.maximum(rs, 50)))
    # Wash 1 (Az 100) und Hauptkamm: Wash bleibt gerade (Durchbruch durch den Kamm)


def carve(c: Ctx):
    terrain.carve_washes(c, regen=False)


# ------------------------------------------------------------------ Landmarken
def landmarks(c: Ctx):
    S = c.L.slots
    rng = c.rng
    # L1 Saturn-Tor: zwei Mesas links/rechts vom Wash 0
    ga = gate_axis(c)
    sx, _, sz = c.L.spawn
    gdx, gdz = math.sin(math.radians(ga)), -math.cos(math.radians(ga))
    for key, side in (("L1a", -1), ("L1b", 1)):
        sl_ = S[key]
        if side < 0:   # breite, gestufte Mesa
            diam, top_y = 134.0, sl_.data["top"]
        else:          # schlanke Butte mit harter Kappe
            diam, top_y = 54.0, sl_.data["top"] + 8.0
        R = diam / 2 * (1.25 if side < 0 else 1.0)
        lat = side * (45.0 + R)
        along = sl_.r - 40
        x = sx + gdx * along - gdz * lat
        z = sz + gdz * along + gdx * lat
        az = math.degrees(math.atan2(x, -z)) % 360
        g = float(c.h_at(x, z))
        if side < 0:
            lf.mesa(c, x, z, diam, top_y - g, stage="mesa", aspect=1.5, rot=math.radians(az + 90), nsteps=6, talus=0.6,
                    top_patch="Grass", nv=8)
        else:
            t = lf.mesa(c, x, z, diam, top_y - g, stage="butte", aspect=1.3, nsteps=2, talus=0.5, nv=6, rough=True)
            m = c.feat["mesa"][-1]
            rtop = max(8.0, m["Rmin"] - m["top_inset"] - 3)
            # leicht ueberstehende, unregelmaessige Kalk-Kappe aus drei versetzten Scheiben
            for k in range(3):
                a = c.u(0, 2 * math.pi)
                off = c.u(1.5, 3.5)
                lf.op_cyl(c, x + math.cos(a) * off, t + 1.8 + k * 0.6, z + math.sin(a) * off, 4.5, rtop + c.u(0.5, 2.5), "Limestone")
        c.feat["landmark"].append({"key": key, "x": x, "z": z})
    # L2 Zwillingstuerme
    s2 = S["L2"]
    a = nudge(c, s2.az, s2.r, 60)
    cx, cz = pol(a, s2.r)
    ta = math.radians(a + 90)
    for k, (top, d) in enumerate(zip(s2.data["tops"], s2.data["diams"])):
        off = (k - 0.5) * (s2.data["gap"] + (s2.data["diams"][0] + s2.data["diams"][1]) / 2)
        x, z = cx + off * math.sin(ta), cz - off * math.cos(ta)
        lf.mesa(c, x, z, d, top - float(c.h_at(x, z)), stage="butte", aspect=1.1, nsteps=4, talus=0.45, gully=True)
    c.feat["landmark"].append({"key": "L2", "x": cx, "z": cz})
    # L5 Vulkan + Lavazungen + Kleinvulkane
    s5 = S["L5"]
    vx, vz = s5.xz
    fields.volcano(c, vx, vz, s5.data["top"], s5.data["crater"], west_az=238.0)
    c.feat["landmark"].append({"key": "L5", "x": vx, "z": vz})
    vsl = c.win(vx, vz, 330)
    own = np.zeros(c.H.shape, bool)
    own[vsl] = c.mask("volcano")[vsl]
    for k, da in enumerate((15, 70, 125, 335, 165)):
        a = da + rng.uniform(-12, 12)
        Rv = 230
        sx, sz = vx + Rv * 0.5 * math.sin(math.radians(a)), vz - Rv * 0.5 * math.cos(math.radians(a))
        fields.lava_tongue(c, sx, sz, a, rng.uniform(220, 460), rng.uniform(30, 50), name="tongue%d" % k, own=own)
    # L4 Bogen (Duenenland)
    s4 = S["L4"]
    ax, az_ = s4.xz
    fields_yaw = s4.az + 90 + rng.uniform(-20, 20)
    lf.arch(c, ax, az_, fields_yaw, s4.data["span"], s4.data["clear"], thick=17.0, wall_h=s4.data["clear"] + 16)
    lf.claim(c, *_circle(c, ax, az_, 120))
    c.feat["landmark"].append({"key": "L4", "x": ax, "z": az_})
    # L0 Abendbank: flacher Fels mit Rampe Richtung Basis
    s0 = S["L0"]
    bx, bz = s0.xz
    top = s0.data["top"]
    g = float(c.h_at(bx, bz))
    lf.mesa(c, bx, bz, 40, top - g, stage="butte", aspect=1.35, nsteps=2, talus=0.25, gully=False)
    _ramp(c, bx, bz, s0.az + 180 - 25, top, length=(top - g) / math.tan(math.radians(13)) + 12, width=12)
    c.feat["landmark"].append({"key": "L0", "x": bx, "z": bz, "top": top})


def _circle(c, x, z, rad):
    sl = c.win(x, z, rad)
    lx, lz = c.local(sl)
    return sl, (lx - x) ** 2 + (lz - z) ** 2 < rad * rad


def _ramp(c: Ctx, x0, z0, dir_deg, top, length, width):
    """Gerade Rampe vom Gelaende hinauf auf eine Oberseite (dir zeigt vom Fels weg)."""
    a = math.radians(dir_deg)
    dx, dz = math.sin(a), -math.cos(a)
    sl = c.win(x0 + dx * length / 2, z0 + dz * length / 2, length / 2 + width + 10)
    x, z = c.local(sl)
    along = (x - x0) * dx + (z - z0) * dz
    side = (x - x0) * -dz + (z - z0) * dx
    Hl = c.H[sl]
    t = np.clip(along / length, 0, 1)
    rh = top - (top - Hl) * t
    sel = (along > 0) & (along < length) & (np.abs(side) < width / 2)
    edge = ss(width / 2, width / 2 - 3, np.abs(side))
    hn = np.where(sel, np.maximum(Hl, Hl + (rh - Hl) * edge), Hl)
    c.H[sl] = hn
    c.mask("no_strata")[sl] |= sel
    lf.set_mat(c, sl, sel & (edge > 0.5), "Rock")


# ------------------------------------------------------------------ Hoodoo-Wald L3
def hoodoo_garden(c: Ctx):
    s3 = c.L.slots["L3"]
    rng = c.rng
    a0 = nudge(c, s3.az, s3.r, 10, 6)
    # Plateau-Rest am Aussenrand, davor Finnen, dann Hoodoo-Gruppen
    px, pz = pol(a0 + 2, 690)
    lf.mesa(c, px, pz, 170, 44, stage="mesa", aspect=1.6, rot=math.radians(a0 + 90), nsteps=3, talus=0.45)
    fins = 0
    for k in range(7):
        fa = a0 + (k - 3) * 3.6 + rng.uniform(-0.8, 0.8)
        fr = 585 + rng.uniform(-12, 8)
        L = rng.uniform(45, 100)
        p0 = pol(fa, fr - L / 2)
        p1 = pol(fa + rng.uniform(-2, 2), fr + L / 2)
        if c.wash_dist[c.idx((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2)] < 25:
            continue
        if fins >= 12:
            break
        lf.fin(c, p0, p1, rng.uniform(7, 10), rng.uniform(24, 52), windows=int(rng.integers(1, 3)), name="fin%d" % k)
        fins += 1
    groups = []
    tries = 0
    while len(groups) < 6 and tries < 2000:
        tries += 1
        ga = a0 + rng.uniform(-30, 28)
        gr = rng.uniform(385, 615)
        gx, gz = pol(ga, gr)
        if any(math.hypot(gx - q[0], gz - q[1]) < 112 for q in groups):
            continue
        if not lf.is_free(c, gx, gz, 26, wash_margin=10):
            continue
        groups.append((gx, gz, rng.uniform(40, 62)))
    count = 0
    area = sum(g[2] ** 2 for g in groups) or 1.0
    for gi, (gx, gz, grad) in enumerate(groups):
        n = int(round(96 * grad ** 2 / area)) + int(rng.integers(-2, 3))
        pts = []
        for _ in range(n * 30):
            if len(pts) >= n:
                break
            ang = rng.uniform(0, 2 * math.pi)
            rr = (grad + 8) * math.sqrt(rng.uniform(0, 1))
            hx, hz = gx + rr * math.cos(ang), gz + rr * math.sin(ang)
            if any(math.hypot(hx - p[0], hz - p[1]) < rng.uniform(22, 30) for p in pts):
                continue
            if c.wash_dist[c.idx(hx, hz)] < 10 or c.mask("claimed")[c.idx(hx, hz)]:
                continue
            pts.append((hx, hz))
        for k, (hx, hz) in enumerate(pts):
            tall = rng.uniform(30, 68) if rng.uniform() > 0.12 else rng.uniform(72, 90)
            if k == 0:
                tall = rng.uniform(70, 90)
            lf.hoodoo(c, hx, hz, tall)
            count += 1
        sl, circ = _circle(c, gx, gz, grad + 14)
        lf.claim(c, sl, circ)
        c.feat["hoodoo_group"].append({"x": gx, "z": gz, "R": grad})
    # Finnen mit Fenstern am Aussenrand jeder Gruppe (Erosionsfolge Plateau -> Finne -> Fenster -> Hoodoo)
    for gi, (gx, gz, grad) in enumerate(groups):
        ga = math.degrees(math.atan2(gx, -gz)) % 360
        gr = math.hypot(gx, gz)
        for k in range(2):
            if fins >= 12:
                break
            fa = ga + (k - 0.5) * math.degrees(38.0 / gr) * 2 + rng.uniform(-2, 2)
            L = rng.uniform(40, 85)
            r0 = gr + grad + rng.uniform(18, 30)
            p0, p1 = pol(fa, r0), pol(fa + rng.uniform(-2, 2), r0 + L)
            mx, mz = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
            if c.wash_dist[c.idx(mx, mz)] < 20 or c.wash_dist[c.idx(*p1)] < 15:
                continue
            lf.fin(c, p0, p1, rng.uniform(7, 10), rng.uniform(22, 48), windows=int(rng.integers(1, 3)), name="fin%d_%d" % (gi, k))
            fins += 1
    c.feat["landmark"].append({"key": "L3", "x": pol(a0, 500)[0], "z": pol(a0, 500)[1]})
    return count, fins


# ------------------------------------------------------------------ Tafelberg-Gruppen je Ring
RING_SPEC = {
    # n Berge, r-Bereich, Leit-Durchmesser, Hoehe ueber Umland
    "A": dict(n=4, r=(215, 300), lead=(70, 105), h=(26, 52)),
    "B": dict(n=10, r=(310, 590), lead=(90, 170), h=(45, 105)),
    "C": dict(n=8, r=(640, 1070), lead=(90, 160), h=(30, 85)),
    "D": dict(n=12, r=(1150, 1480), lead=(70, 160), h=(50, 120)),
    "E": dict(n=6, r=(1620, 1840), lead=(60, 120), h=(40, 95)),
}


def mesa_groups(c: Ctx, ring, sector=None):
    spec = RING_SPEC[ring]
    rng = c.rng
    placed = 0
    tries = 0
    r0, r1 = spec["r"]
    while placed < spec["n"] and tries < 900:
        tries += 1
        r = math.sqrt(rng.uniform(r0 * r0, r1 * r1))
        a = rng.uniform(0, 360)
        if sector and not sector(a, r):
            continue
        if sight_block(a, r):
            continue
        gx, gz = pol(a, r)
        lead_d = rng.uniform(*spec["lead"]) * (0.7 if rng.uniform() < 0.4 else 1.0)
        if not lf.is_free(c, gx, gz, lead_d * 0.62 + 14, wash_margin=18):
            continue
        hgt = rng.uniform(*spec["h"])
        lf.mesa(c, gx, gz, lead_d, hgt, stage="mesa", top_patch=_patch(c, ring))
        placed += 1
        # Begleiter (Rhythmus 1-2-1): Buttes, manchmal eine Spitze
        ncomp = int(rng.integers(1, 3))
        for k in range(ncomp):
            if placed >= spec["n"]:
                break
            for _ in range(20):
                ang = rng.uniform(0, 2 * math.pi)
                spire_ = rng.uniform() < 0.25
                d = rng.uniform(42, 75) if not spire_ else rng.uniform(12, 20)
                dist = lead_d / 2 + d / 2 + rng.uniform(36, 95)
                bx, bz = gx + dist * math.cos(ang), gz + dist * math.sin(ang)
                br = math.hypot(bx, bz)
                ba = math.degrees(math.atan2(bx, -bz)) % 360
                if br < r0 - 20 or br > r1 + 40 or sight_block(ba, br) or (sector and not sector(ba, br)):
                    continue
                if not lf.is_free(c, bx, bz, d * 0.7 + 12, wash_margin=16):
                    continue
                if spire_:
                    lf.spire(c, bx, bz, d, rng.uniform(3, 6), rng.uniform(34, 95) * (0.7 if ring == "A" else 1.0))
                else:
                    bh = min(d / rng.uniform(0.55, 0.95), spec["h"][1] * 1.1)
                    lf.mesa(c, bx, bz, d, bh, stage="butte")
                placed += 1
                break
    return placed


def _patch(c, ring):
    u = c.rng.uniform()
    if u < 0.15:
        return "Sand"
    if u < 0.27 and ring in ("A", "B"):
        return "Grass"
    if ring == "E" and u < 0.5:
        return "Snow"
    return None


def spires(c: Ctx, n=16):
    rng = c.rng
    placed = 0
    for _ in range(1500):
        if placed >= n:
            break
        r = rng.uniform(320, 1820)
        a = rng.uniform(0, 360)
        if sight_block(a, r):
            continue
        x, z = pol(a, r)
        d = rng.uniform(9, 20)
        if not lf.is_free(c, x, z, d + 26, wash_margin=30):
            continue
        lf.spire(c, x, z, d, rng.uniform(3, 6), rng.uniform(30, 110))
        placed += 1
    return placed


# ------------------------------------------------------------------ Kaemme Ring D
def ridges(c: Ctx):
    rng = c.rng
    S = c.L.slots
    s6 = S["L6"]
    # Hauptkamm L6: tangential, Stirnseite zur Basis, Wash 1 bricht durch eine Luecke
    a6, r6 = s6.az, s6.r
    L = s6.data["length"]
    cx, cz = pol(a6, r6)
    ta = math.radians(a6 + 90)
    tx, tz = math.sin(ta), -math.cos(ta)
    p0 = (cx - tx * L / 2, cz - tz * L / 2)
    p1 = (cx + tx * L / 2, cz + tz * L / 2)
    wa = wash_az_at(c, 1, r6)
    wx, wz = pol(wa, r6)
    tg = ((wx - p0[0]) * tx + (wz - p0[1]) * tz) / L
    peaks6 = []
    hs = s6.data["peaks"]
    base6 = -24.0
    pos = [0.16, 0.5, 0.84] if not (0.3 < tg < 0.7) else [0.14, 0.86, 0.5]
    for p, h in zip(sorted(pos), (hs[0] - base6, hs[1] - base6, hs[2] - base6)):
        peaks6.append((p, h, 0.3))
    gaps = []
    if 0.05 < tg < 0.95:
        gaps.append((tg, 120.0, 2.0))
    # Front zeigt zur Basis: Laufrichtung p0->p1 ist +90 Grad -> links = Richtung Basis
    lf.ridge(c, p0, p1, rng.uniform(-40, 40), peaks6, base=None, front=1, dip_deg=13, back_deg=40, gaps=gaps, name="L6")
    c.feat["landmark"].append({"key": "L6", "x": cx, "z": cz})
    others = [(300, 260, 120), (172, 300, 140), (352, 240, 105), (232, 330, 125), (22, 210, 95), (73, 280, 130)]
    for k, (a, L, h) in enumerate(others):
        r = rng.uniform(1220, 1430)
        a = a + rng.uniform(-4, 4)
        # Ausrichtung: radial wenn nah an einem Wash, sonst schraeg
        near = min(abs(ang_diff(a, wa_)) for wa_ in c.L.washes)
        if near < 14:
            a = a + math.copysign(14 - near + 2, ang_diff(a, min(c.L.washes, key=lambda q: abs(ang_diff(a, q)))))
            orient = a + rng.uniform(-12, 12)
        else:
            orient = a + 90 + rng.uniform(-35, 35)
        cx, cz = pol(a, r)
        if sight_block(a, r):
            a += 9
            cx, cz = pol(a, r)
        oa = math.radians(orient)
        tx, tz = math.sin(oa), -math.cos(oa)
        q0 = (cx - tx * L / 2, cz - tz * L / 2)
        q1 = (cx + tx * L / 2, cz + tz * L / 2)
        npk = int(rng.integers(1, 4))
        pk = [((i + 0.5) / npk + rng.uniform(-0.08, 0.08), h * rng.uniform(0.7, 1.0) if i else h, 0.7 / npk + 0.08) for i in range(npk)]
        lf.ridge(c, q0, q1, rng.uniform(-60, 60), pk, front=1 if rng.uniform() < 0.5 else -1,
                 dip_deg=rng.uniform(10, 15), face_deg=rng.uniform(62, 70), back_deg=rng.uniform(40, 46), name="ridge%d" % k)


def tunnels(c: Ctx, n=4):
    rng = c.rng
    done = 0
    for _ in range(400):
        if done >= n:
            break
        a, r = rng.uniform(0, 360), rng.uniform(1180, 1480)
        x, z = pol(a, r)
        if sight_block(a, r) or not lf.is_free(c, x, z, 70, wash_margin=40):
            continue
        yaw = rng.uniform(0, 180)
        L = rng.uniform(70, 110)
        ta = math.radians(yaw)
        p0 = (x - math.sin(ta) * L / 2, z + math.cos(ta) * L / 2)
        p1 = (x + math.sin(ta) * L / 2, z - math.cos(ta) * L / 2)
        thick = rng.uniform(40, 58)
        base, R, _ = lf.fin(c, p0, p1, thick, rng.uniform(46, 70), windows=0, name="tw%d" % done, mask_name="fin")
        th = rng.uniform(12, 16)
        lf.op_block(c, x, base + th / 2 - 0.5, z, (rng.uniform(18, 24), th, thick * 2.2 + 20), "Air", R)
        c.feat["tunnel"].append({"x": x, "z": z, "y": base, "R": R, "len": thick * 2.2 + 20, "h": th})
        done += 1
    return done


# ------------------------------------------------------------------ Massive mit Canyons
def massifs(c: Ctx):
    rng = c.rng
    specs = [(78.0, 760.0, 270.0, 48.0), (130.0, 1250.0, 330.0, 74.0), (293.0, 1420.0, 300.0, 64.0)]
    canyons = 0
    for k, (a, r, d, h) in enumerate(specs):
        a = nudge(c, a + rng.uniform(-4, 4), r, d / 2 + 30, 10)
        if sight_block(a, r):
            a += 8
        x, z = pol(a, r)
        for _ in range(200):
            if lf.is_free(c, x, z, d * 0.5, wash_margin=15):
                break
            a2, r2 = a + rng.uniform(-25, 25), r + rng.uniform(-110, 110)
            x, z = pol(a2, r2)
        else:
            continue
        lf.mesa(c, x, z, d, h, stage="mesa", aspect=1.25, nsteps=3, talus=0.5, top_patch="Sand")
        # 2 Durchgangs-Canyons + 1 kurzer Seitencanyon mit Oase am Ende
        base = c.feat["mesa"][-1]["base"]
        ang = rng.uniform(0, math.pi)
        _canyon(c, x, z, ang, d * 1.5, rng.uniform(40, 52), base, name="cyn%d" % k, offset=rng.uniform(-25, 25))
        canyons += 1
        ang = ang + math.pi / 2 * (1 if rng.uniform() < 0.5 else -1)
        ex, ez = x + math.cos(ang) * d * 0.28, z + math.sin(ang) * d * 0.28
        _canyon(c, (x + ex) / 2 + math.cos(ang) * d * 0.25, (z + ez) / 2 + math.sin(ang) * d * 0.25, ang, d * 0.55,
                40, base, name="side%d" % k, offset=0, bowl=(ex, ez))
        c.feat["oasis_canyon"].append({"x": ex, "z": ez, "R": 26, "y": base})
        canyons += 1
    return canyons


def _canyon(c: Ctx, cx, cz, ang, length, width, floor, name, offset=0.0, bowl=None):
    tx, tz = math.cos(ang), math.sin(ang)
    nx, nz_ = -tz, tx
    cx, cz = cx + nx * offset, cz + nz_ * offset
    sl = c.win(cx, cz, length / 2 + width + 40)
    x, z = c.local(sl)
    a = (x - cx) * tx + (z - cz) * tz
    u = (x - cx) * nx + (z - cz) * nz_
    u = u + 26 * c.nz.fbm(name, x, z, 140, 2) + 5 * c.nz.fbm(name + "s", x, z, 30, 2)
    hw = width / 2
    wall = np.maximum(0, np.abs(u) - hw)
    # Waende steil, oben breiter (Stufe)
    prof = floor + 0.5 + wall * math.tan(math.radians(76)) - np.maximum(0, wall - 16) * 2.2
    endf = ss(length / 2, length / 2 - 20, np.abs(a))
    if bowl is not None:
        # Kastencanyon: zum Massiv-Rand hin offen, innen endet er in einer runden Oasen-Mulde
        bx, bz = bowl
        db = np.hypot(x - bx, z - bz)
        a_b = (bx - cx) * tx + (bz - cz) * tz
        prof = np.minimum(np.where(a >= a_b, prof, 1e9), floor + 0.5 + np.maximum(0, db - 26) * math.tan(math.radians(70)))
        endf = np.where(a >= a_b, 1.0, 1.0)
    Hl = c.H[sl]
    cut = np.where(endf > 0, prof * endf + 1e4 * (1 - endf), 1e9)
    # nur durch das Massiv schneiden (kein Graben ins Umland -> keine geschlossene Senke)
    from scipy import ndimage as ndi
    rock = ndi.binary_dilation(c.mask("mesa")[sl] | c.mask("talus")[sl], iterations=3)
    cut = np.where(rock, cut, 1e9)
    hn = np.minimum(Hl, cut)
    changed = hn < Hl - 0.5
    c.H[sl] = hn
    floor_m = changed & (np.abs(u) < hw + 2)
    lf.set_mat(c, sl, floor_m, "Sand")
    c.mask("canyon_floor")[sl] |= floor_m
    c.mask("no_strata")[sl] |= floor_m
    c.mask("canyon_wall")[sl] |= changed & ~floor_m
    c.obstacle[sl] &= ~floor_m
    c.mask("mesa")[sl] &= ~floor_m
    c.mask("talus")[sl] &= ~floor_m
    c.feat["canyon"].append({"x": cx, "z": cz, "ang": ang, "len": length, "w": width})


# ------------------------------------------------------------------ Wasser und Mulden
def waters(c: Ctx):
    S = c.L.slots
    rng = c.rng
    sp = S["pond"]
    a = nudge(c, sp.az, sp.r, 40, 4)
    px, pz = pol(a, sp.r)
    wf.pond(c, px, pz, sp.data["diam"], sp.data["depth"], name="pond")
    ss_ = S["spring"]
    a = nudge(c, ss_.az, ss_.r, 50, 8)
    qx, qz = pol(a, ss_.r)
    wf.pond(c, qx, qz, ss_.data["diam"], ss_.data["depth"], name="spring")
    c.feat["spring"].append({"x": qx + 18, "z": qz - 10, "kind": "pond"})
    c.feat["grove_spring"].append({"x": qx, "z": qz, "R": 70})
    # Terrassen
    for key in ("L7", "T2", "T3"):
        s = S[key]
        a = nudge(c, s.az, s.r, s.data["width"] / 2 + 40, 9)
        tx, tz = pol(a, s.r)
        down = (math.degrees(math.atan2(-tx, tz)) % 360)   # hangabwaerts Richtung Basis
        wf.terraces(c, tx, tz, s.data["basins"], s.data["width"], s.data["length"], down, name=key)
        if key == "L7":
            c.feat["landmark"].append({"key": "L7", "x": tx, "z": tz})
    # Salzpfannen
    for key in ["playaC"] + [f"playaD{i}" for i in range(4)]:
        s = S[key]
        a = nudge(c, s.az, s.r, s.data["diam"] / 2 + 30, 8)
        x, z = pol(a, s.r)
        wf.playa(c, x, z, s.data["diam"], name=key)


def hollows(c: Ctx):
    rng = c.rng
    # Krater: 9 (B-E), 2 mit Teich
    plan = [("B", 330, 580, True), ("B", 330, 580, False), ("C", 650, 1060, False), ("C", 650, 1060, False),
            ("D", 1180, 1500, True), ("D", 1180, 1500, False), ("D", 1180, 1500, False), ("E", 1640, 1830, False),
            ("E", 1640, 1830, False)]
    for ring, r0, r1, water in plan:
        for _ in range(300):
            r, a = rng.uniform(r0, r1), rng.uniform(0, 360)
            dmt = rng.uniform(60, 120) if ring in "BC" else rng.uniform(90, 230)
            x, z = pol(a, r)
            if lf.is_free(c, x, z, dmt * 0.8 + 10, wash_margin=10):
                wf.crater(c, x, z, dmt, water=water, name="crater%d" % len(c.feat["crater"]))
                break
    # Geoden (Ring D)
    for k in range(7):
        for _ in range(300):
            r, a = rng.uniform(1170, 1520), rng.uniform(0, 360)
            x, z = pol(a, r)
            d = rng.uniform(42, 90)
            if lf.is_free(c, x, z, d / 2 + 14, wash_margin=10):
                wf.geode(c, x, z, d, name="geode%d" % k)
                break


def fans(c: Ctx):
    rng = c.rng
    n = 0
    # am Fuss der Kaemme (Stirnseite) und an Canyon-Ausgaengen
    for rd in c.feat["ridge"]:
        if n >= 5:
            break
        cv = rd["curve"]
        t = rng.uniform(0.3, 0.7)
        i = int(t * (len(cv.pts) - 1))
        p = cv.pts[i]
        nrm = cv.nrm[i] * rd["front"]
        dist = 110 if rd["name"] == "L6" else 80
        ax, az_ = p[0] - nrm[0] * dist, p[1] - nrm[1] * dist
        dir_ = math.degrees(math.atan2(-nrm[0], nrm[1])) % 360
        wf.fan(c, ax, az_, dir_, rng.uniform(90, 180), rng.uniform(70, 110), name="fan%d" % n)
        n += 1
    for cy in c.feat["canyon"]:
        if n >= 9:
            break
        ex = cy["x"] + math.cos(cy["ang"]) * cy["len"] / 2
        ez = cy["z"] + math.sin(cy["ang"]) * cy["len"] / 2
        dir_ = math.degrees(math.atan2(math.cos(cy["ang"]), -math.sin(cy["ang"]))) % 360
        wf.fan(c, ex, ez, dir_, rng.uniform(80, 140), rng.uniform(70, 100), name="fan%d" % n)
        n += 1
    return n


# ------------------------------------------------------------------ Ring D/E Landmarken
def ring_de_landmarks(c: Ctx):
    S = c.L.slots
    # L8 Kristallkathedrale: felsiger Sockel (Ring-Wall) mit Kristallen (Deko)
    s8 = S["L8"]
    x, z = s8.xz
    g = float(c.h_at(x, z))
    sl, circ = _circle(c, x, z, 60)
    lx, lz = c.local(sl)
    rho = np.hypot(lx - x, lz - z)
    mound = g + 14 * np.exp(-(rho / 34) ** 2) + 4 * np.exp(-((rho - 40) / 10) ** 2)
    c.H[sl] = np.where(rho < 60, np.maximum(c.H[sl], mound), c.H[sl])
    c.mask("outcrop")[sl] |= rho < 40
    c.obstacle[sl] |= rho < 50
    lf.claim(c, sl, rho < 75)
    c.feat["landmark"].append({"key": "L8", "x": x, "z": z, "y": g + 14})
    # L9 Titan-Spiegelturm: Felsnadel Glacier, 70 -> 20
    s9 = S["L9"]
    x, z = s9.xz
    sl = c.win(x, z, 70)
    lx, lz = c.local(sl)
    th = np.arctan2(lz - z, lx - x)
    rho = np.hypot(lx - x, lz - z) * (1 + 0.06 * np.cos(6 * th))
    g = float(np.percentile(c.H[sl][rho < 40], 30))
    top = s9.data["top"]
    hgt = top - g
    # Radius in Abhaengigkeit der Hoehe: 35 unten -> 10 oben, Sockel mit Schutt
    t = np.clip(1 - (rho - 10) / 25.0, 0, 1)
    tower = np.where(rho < 35, g + hgt * t ** 1.6, -1e9)
    tal = np.where(rho < 56, g + 12 * np.clip(1 - (rho - 30) / 26, 0, 1) ** 1.4, -1e9)
    hn = np.maximum(c.H[sl], np.maximum(tower, tal))
    c.H[sl] = hn
    body = tower >= tal
    lf.set_mat(c, sl, body, "Glacier")
    lf.set_mat(c, sl, ~body & (tal > c.H[sl] - 0.1) & (rho < 58), "Rock")
    c.mask("no_strata")[sl] |= rho < 60
    c.obstacle[sl] |= rho < 56
    lf.claim(c, sl, rho < 70)
    c.feat["landmark"].append({"key": "L9", "x": x, "z": z, "y": g, "top": top})


def faults(c: Ctx, n=10):
    """Verwerfungslinien in Ring D (fuer Kristallgaerten, Mineral-Karte)."""
    rng = c.rng
    out = []
    for _ in range(600):
        if len(out) >= n:
            break
        a, r = rng.uniform(0, 360), rng.uniform(1150, 1560)
        x, z = pol(a, r)
        if not lf.is_free(c, x, z, 45, wash_margin=18) or sight_block(a, r):
            continue
        if any(math.hypot(x - f["x"], z - f["z"]) < 280 for f in out):
            continue
        L = rng.uniform(60, 200)
        ang = rng.uniform(0, math.pi)
        out.append({"x": x, "z": z, "ang": ang, "L": L})
        sl, circ = _circle(c, x, z, max(L / 2, 50) + 30)
        lf.claim(c, sl, circ)
    c.feat["fault"] = out


def oases_c(c: Ctx):
    """Oasen in den Lavafeldern (Ring C Nordost), vor den Lavafeldern geplant."""
    rng = c.rng
    for _ in range(400):
        if len(c.feat["oasis_c"]) >= 3:
            break
        a, r = rng.uniform(-60, 120) % 360, rng.uniform(700, 1040)
        x, z = pol(a, r)
        if c.wNE[c.idx(x, z)] < 0.7 or not lf.is_free(c, x, z, 75, wash_margin=10):
            continue
        if any(math.hypot(x - o["x"], z - o["z"]) < 300 for o in c.feat["oasis_c"]):
            continue
        R = rng.uniform(50, 78)
        c.feat["oasis_c"].append({"x": x, "z": z, "R": R})
        wf.pond(c, x + rng.uniform(-10, 10), z + rng.uniform(-10, 10), R * 0.45, 2.0, name="oasis%d" % len(c.feat["oasis_c"]),
                floor_mat="Mud", bank_mat="LeafyGrass", ring_mat="Grass")
        sl, circ = _circle(c, x, z, R * 1.3)
        lx, lz = c.local(sl)
        q = np.hypot(lx - x, lz - z) / R * (1 + 0.45 * c.nz.fbm("oas%d" % len(c.feat["oasis_c"]), lx, lz, 45, 3))
        lf.set_mat(c, sl, (q < 0.85) & (c.slope_now(sl) < 14), "Grass")
        lf.set_mat(c, sl, (q < 0.45) & (c.slope_now(sl) < 14), "LeafyGrass")
        lf.claim(c, sl, q < 1.0)
        c.feat["spring"].append({"x": x, "z": z, "kind": "oasis"})


def small_cones(c: Ctx, n=6):
    rng = c.rng
    done = 0
    for _ in range(500):
        if done >= n:
            break
        a, r = rng.uniform(-60, 120) % 360, rng.uniform(680, 1060)
        x, z = pol(a, r)
        if c.wNE[c.idx(x, z)] < 0.7:
            continue
        d = rng.uniform(60, 110)
        if not lf.is_free(c, x, z, d / 2 + 30, wash_margin=20) or sight_block(a, r):
            continue
        h = rng.uniform(20, 45)
        g = float(c.h_at(x, z))
        fields.volcano(c, x, z, g + h, crater_d=d * 0.28, small=True, name="cone%d" % done)
        done += 1
    return done


def ring_c_mesas(c: Ctx):
    def sector(a, r):
        d1 = min(abs(ang_diff(a, 130)), abs(ang_diff(a, 295)))
        return d1 < 28 or (c.wNE[c.idx(*pol(a, r))] < 0.5 and r < 760)
    return mesa_groups(c, "C", sector)


def ring_e_features(c: Ctx):
    """Ring E: Felsrippen (niedrige Schichtfelsen-Waende), einzelne Felsnadeln."""
    rng = c.rng
    ribs = 0
    for _ in range(500):
        if ribs >= 12:
            break
        a, r = rng.uniform(0, 360), rng.uniform(1620, 1850)
        x, z = pol(a, r)
        if not lf.is_free(c, x, z, 70, wash_margin=25):
            continue
        L = rng.uniform(70, 150)
        ta = a + 90 + rng.uniform(-30, 30)
        p0 = pol(a, r)
        dx, dz = math.sin(math.radians(ta)) * L / 2, -math.cos(math.radians(ta)) * L / 2
        lf.fin(c, (x - dx, z - dz), (x + dx, z + dz), rng.uniform(10, 16), rng.uniform(8, 20), windows=0,
               name="rib%d" % ribs, mask_name="fin")
        ribs += 1
    sp = 0
    for _ in range(500):
        if sp >= 5:
            break
        a, r = rng.uniform(0, 360), rng.uniform(1640, 1840)
        x, z = pol(a, r)
        d = rng.uniform(12, 20)
        if not lf.is_free(c, x, z, d + 30, wash_margin=30) or sight_block(a, r):
            continue
        lf.spire(c, x, z, d, rng.uniform(3, 5), rng.uniform(45, 90))
        sp += 1
    return ribs, sp


def lava_flows(c: Ctx):
    """Klar begrenzte Lavastroeme (Ring C Nordost): von den Kleinvulkanen und aus Spalten."""
    rng = c.rng
    n = 0
    for v in [f for f in c.feat["volcano"] if f["small"]]:
        for k in range(int(rng.integers(1, 3))):
            a = rng.uniform(0, 360)
            sx, sz = v["x"] + v["Rv"] * 0.6 * math.sin(math.radians(a)), v["z"] - v["Rv"] * 0.6 * math.cos(math.radians(a))
            own = np.zeros(c.H.shape, bool)
            vs = c.win(v["x"], v["z"], v["Rv"] * 1.3)
            own[vs] = c.mask("volcano")[vs]
            fields.lava_tongue(c, sx, sz, a, rng.uniform(140, 300), rng.uniform(22, 36), name="ct%d" % n, own=own)
            n += 1
    fis = 0
    for _ in range(300):
        if fis >= 3:
            break
        a, r = rng.uniform(-50, 110) % 360, rng.uniform(700, 1030)
        x, z = pol(a, r)
        if c.wNE[c.idx(x, z)] < 0.7 or not lf.is_free(c, x, z, 50, wash_margin=40):
            continue
        d0 = rng.uniform(0, 360)
        for dd in (0, 180):
            fields.lava_tongue(c, x, z, d0 + dd + rng.uniform(-20, 20), rng.uniform(160, 330), rng.uniform(22, 40), name="ft%d" % n)
            n += 1
        fis += 1
    return n


def build_landforms(c: Ctx):
    """Reihenfolge: Washes -> grosse Landmarken -> Becken -> Felder -> Berge -> Faecher."""
    setup_washes(c)
    carve(c)
    fields.highland(c)
    landmarks(c)
    n_hd, n_fin = hoodoo_garden(c)
    waters(c)
    ridges(c)
    ring_de_landmarks(c)
    fields.wave(c, *pol(212 + c.u(-3, 3), 775), rx=170, rz=80, rot_deg=c.u(0, 180))
    n_cyn = massifs(c)
    oases_c(c)
    faults(c)
    hollows(c)
    small_cones(c)
    n_tun = tunnels(c)
    counts = {"hoodoos": n_hd, "fins": n_fin, "canyons": n_cyn, "tunnels": n_tun}
    for ring in ("A", "B", "D", "E"):
        counts["mesas_" + ring] = mesa_groups(c, ring)
    counts["mesas_C"] = ring_c_mesas(c)
    counts["spires"] = spires(c, 6)
    counts["ribs_E"], counts["spires_E"] = ring_e_features(c)
    lava_flows(c)
    fields.dunes(c)
    counts["fans"] = fans(c)
    return counts
