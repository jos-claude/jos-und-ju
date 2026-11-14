"""Deko-Platzierung (Vorgabe 5.1-5.3): Dichte-Inseln mit Leitform, Oekologie-Regeln, Ruhe dazwischen.

Ablauf: plan_islands() vor dem Finalisieren (malt Gras/Moos-Boden unter die Haine, markiert Deko-Zonen),
place_all() danach (setzt die Vorlagen). Hindernis-Deko nur in Deko-Zonen, in Bauzonen nur Kniehohes.
"""
from __future__ import annotations

import math
from collections import Counter, defaultdict

import numpy as np

from . import catalog
from .ctx import Ctx
from .landforms import set_mat, set_strata_top
from .layout import LEE_DIR, PLATEAU_FREE_R, PLATEAU_R, RING_EDGES, ang_diff, pol, sr
from .noise import smoothstep as ss
from .world import CELL, HALF, MAT, World

LEE = (math.sin(math.radians(LEE_DIR)), -math.cos(math.radians(LEE_DIR)))
PLATEAU_OK = ("Tuft", "Pebble", "Noodle")
# Hindernis-Deko (hoeher als Kniehoehe oder mit Kollision): nur in Deko-Zonen
OBSTACLE_GROUPS = {"BalloonTree", "CrystalM", "CrystalMLit", "CrystalG", "CrystalTitan", "OrganPipe", "PearlCactus",
                   "CopperRock", "Mushroom", "SteamVent", "Lantern", "LanternLit", "Boulder", "BandBlock", "RockNeedle"}


def ring_of(r):
    e = RING_EDGES
    return "A" if r < e[1] else "B" if r < e[2] else "C" if r < e[3] else "D" if r < e[4] else "E"


def cell_xz(ix, iz):
    """Mitte der Raster-Spalte [iz, ix] in Weltkoordinaten."""
    return -HALF + CELL / 2 + CELL * ix, -HALF + CELL / 2 + CELL * iz


class Placer:
    def __init__(self, c: Ctx, w: World):
        self.c, self.w = c, w
        self.rng = np.random.default_rng(c.seed * 977 + 5)
        self.cat, self.groups = catalog.build_catalog(np.random.default_rng(c.seed * 31 + 2))
        for t in self.cat.values():
            w.add_template(t)
        self.grid = defaultdict(list)
        self.count = Counter()
        self.parts = Counter()
        self.lights = Counter()
        self.islands = []
        self.obstacles = []
        self.rock_key = None        # je Spalte: Gestein des naechsten Felsens (fuer Kiesel), siehe rock_map()
        self.obst_grid = defaultdict(list)

    # ---------------- Belegung (keine Ueberschneidungen)
    def free(self, x, z, r):
        gx, gz = int(x // 16), int(z // 16)
        rr = int(r // 16) + 2
        for i in range(gx - rr, gx + rr + 1):
            for j in range(gz - rr, gz + rr + 1):
                for (px, pz, pr) in self.grid.get((i, j), ()):
                    if (px - x) ** 2 + (pz - z) ** 2 < (pr + r) ** 2:
                        return False
        return True

    def mark(self, x, z, r):
        self.grid[(int(x // 16), int(z // 16))].append((x, z, r))

    def obstacle_mask(self, pad=5.0):
        """Deko-Zone = Flaeche der Hindernis-Deko (+ Rand), fuer die Bauzonen-Pruefung."""
        from scipy import ndimage as ndi
        m = np.zeros(self.c.H.shape, bool)
        for (x, z, r) in self.obstacles:
            iz, ix = self.c.idx(x, z)
            rr = int(math.ceil((r + pad) / CELL))
            yy, xx = np.ogrid[-rr:rr + 1, -rr:rr + 1]
            disk = xx * xx + yy * yy <= rr * rr
            z0, z1, x0, x1 = max(0, iz - rr), min(m.shape[0], iz + rr + 1), max(0, ix - rr), min(m.shape[1], ix + rr + 1)
            m[z0:z1, x0:x1] |= disk[z0 - iz + rr:z1 - iz + rr, x0 - ix + rr:x1 - ix + rr]
        return m

    def near_obstacle(self, x, z, d):
        gx, gz = int(x // 32), int(z // 32)
        for i in (gx - 1, gx, gx + 1):
            for j in (gz - 1, gz, gz + 1):
                for (px, pz, pr) in self.obst_grid.get((i, j), ()):
                    if (px - x) ** 2 + (pz - z) ** 2 < (pr + d) ** 2:
                        return True
        return False

    # ---------------- Gelaende-Abfragen
    def ground(self, x, z):
        c = self.c
        fx = (x + HALF - CELL / 2) / CELL
        fz = (z + HALF - CELL / 2) / CELL
        ix, iz = int(math.floor(fx)), int(math.floor(fz))
        tx, tz = fx - ix, fz - iz
        H = c.H
        a = H[iz, ix] * (1 - tx) + H[iz, ix + 1] * tx
        b = H[iz + 1, ix] * (1 - tx) + H[iz + 1, ix + 1] * tx
        return float(a * (1 - tz) + b * tz)

    def low_ground(self, x, z, rad):
        """Tiefster Bodenpunkt unter einem breiten Objekt (Mitte + 6 Randpunkte): am Hang schwebt nichts."""
        hs = [self.ground(x, z)] + [self.ground(x + rad * math.cos(a), z + rad * math.sin(a))
                                    for a in np.linspace(0, 2 * math.pi, 6, endpoint=False)]
        return min(hs)

    def cell(self, x, z):
        return self.c.idx(x, z)

    def ok_ground(self, x, z, max_slope=22.0, allow_rock=False, allow_water=False):
        c = self.c
        iz, ix = self.cell(x, z)
        if c.void[iz, ix]:
            return False
        if not allow_water and not np.isnan(c.wl[iz, ix]):
            return False
        if c.slope[iz, ix] > max_slope:
            return False
        if not allow_rock and (c.strata[iz, ix] and c.slope[iz, ix] > 8):
            return False
        sx, _, sz = c.L.spawn
        if (x - sx) ** 2 + (z - sz) ** 2 < 15 ** 2:
            return False
        if -40 <= x <= 40 and 20 <= z <= 70:          # Start-Halle (Jus Place)
            return False
        return True

    # ---------------- Setzen
    def put(self, group, x, z, s=1.0, variant=0, y=None, yaw=None, lean=True, rx=0.0, rz=0.0, sink=0.15,
            radius=2.0, tmpl=None, mark=True, obstacle=None):
        if group == "Pebble":
            # Kiesel = Bruchstuecke des naechsten Felsens: Material und Farbe des Bands darueber, keine Zufallsfarbe
            key = "Rock"
            if self.rock_key is not None:
                iz, ix = self.cell(x, z)
                key = self.rock_key[iz, ix]
            grp = self.groups["Pebble_" + key]
            tmpl = grp[int(self.rng.integers(0, len(grp)))]
            variant = 0
        grounded = y is None
        t = tmpl or self.groups[group][int(self.rng.integers(0, len(self.groups[group])))]
        if y is None and group not in PLATEAU_OK and math.hypot(x, z) < PLATEAU_FREE_R + (radius * s + 5 if group in OBSTACLE_GROUPS else 0):
            return None             # Plateau bleibt frei (nur Kniehohes ohne Kollision); Runde 2: r 120 statt 152
        if y is None:
            y = self.ground(x, z) - sink * s
        if yaw is None:
            yaw = float(self.rng.uniform(0, 2 * math.pi))
        if lean:
            a = math.radians(self.rng.uniform(3, 6) + self.rng.uniform(-2, 2))
            cy, sy = math.cos(yaw), math.sin(yaw)
            dlx = cy * LEE[0] - sy * LEE[1]
            dlz = sy * LEE[0] + cy * LEE[1]
            rz += -a * dlx
            rx += a * dlz
        self.w.place(t.name, x, y, z, yaw, rx, rz, s, variant)
        self.count[group] += 1
        self.parts[group] += len(t.parts)
        self.lights[group] += sum(1 for p in t.parts if p.light)
        if mark:
            self.mark(x, z, radius * s)
        if obstacle is None:
            obstacle = (group in OBSTACLE_GROUPS and grounded) or group in ("BalloonTree", "CrystalG")
        if obstacle:
            self.obstacles.append((x, z, radius * s))
            self.obst_grid[(int(x // 32), int(z // 32))].append((x, z, radius * s))
        return t

    # ---------------- Inseln
    def island(self, x, z, R, theme, **kw):
        if theme in ("grove", "mesa_foot"):
            R = R * 0.7          # Runde 1: Haine kompakter (gleiche Baumzahl auf 0,7 x Radius)
        isl = {"x": x, "z": z, "R": R, "theme": theme, "ring": ring_of(math.hypot(x, z))}
        isl.update(kw)
        self.islands.append(isl)
        return isl

    def candidates(self, isl, n, bias=1.0, rmin=0.0, rmax=1.0):
        rng = self.rng
        u = rng.uniform(0, 1, n)
        rr = isl["R"] * (rmin + (rmax - rmin) * u ** (0.5 * bias))
        a = rng.uniform(0, 2 * math.pi, n)
        # Insel-Umriss unregelmaessig
        wob = 1.0 + 0.25 * np.sin(3 * a + isl["x"] * 0.01) + 0.15 * np.sin(5 * a + isl["z"] * 0.02)
        return isl["x"] + rr * wob * np.cos(a), isl["z"] + rr * wob * np.sin(a)


def variant_tree(p, ring):
    if ring == "E":
        return int(p.rng.choice([6, 7, 8]))
    return int(p.rng.choice(6, p=np.array(catalog.CROWN_W) / sum(catalog.CROWN_W)))


def variant_crystal(p, ring):
    if ring == "E":
        return int(p.rng.choice([1, 4]))
    if ring in "BC":
        return int(p.rng.choice([0, 2, 1]))
    return int(p.rng.choice(5, p=np.array(catalog.CRYSTAL_W) / sum(catalog.CRYSTAL_W)))


def size_class(p, big=0.1):
    """Groessenklassen 5:4:1 (klein 60-80 %, mittel 100 %, gross 130-160 %); big = Anteil der grossen."""
    u = p.rng.uniform()
    if u < 0.5 * (1.0 - big) / 0.9:
        return p.rng.uniform(0.6, 0.8)
    if u < 1.0 - big:
        return p.rng.uniform(0.9, 1.1)
    return p.rng.uniform(1.3, 1.6)


# ------------------------------------------------------------------ Bausteine je Art
def grove_trees(p: Placer, isl, n, scale=1.0, lead=True, cool=False):
    """Hain: eine grosse Leitpflanze, 1-2 Junge, Rest in Groessenklassen; dichter im Lee."""
    c = p.c
    ring = isl["ring"]
    placed = 0
    cx, cz = isl["x"] + LEE[0] * isl["R"] * 0.15, isl["z"] + LEE[1] * isl["R"] * 0.15
    if lead:
        for _ in range(40):
            x, z = cx + p.rng.uniform(-8, 8), cz + p.rng.uniform(-8, 8)
            s = p.rng.uniform(1.9, 2.4) * scale
            if p.ok_ground(x, z, 18) and p.free(x, z, 6 * s):
                p.put("BalloonTree", x, z, s, variant_tree(p, ring), radius=5.0)
                placed += 1
                break
    xs, zs = p.candidates(isl, n * 20, bias=1.3)
    young = 0
    for x, z in zip(xs, zs):
        if placed >= n:
            break
        if not p.ok_ground(x, z, 18):
            continue
        iz, ix = p.cell(x, z)
        lee_bonus = (x - isl["x"]) * LEE[0] + (z - isl["z"]) * LEE[1]
        if p.rng.uniform() > 0.7 + 0.3 * np.tanh(lee_bonus / max(isl["R"], 1)) + 0.4 * float(c.F[iz, ix]):
            continue
        s = size_class(p, big=0.2) * scale          # Runde 1: 20 % grosse Baeume (vorher 10 %)
        if young < 2 and p.rng.uniform() < 0.25:
            s = p.rng.uniform(0.45, 0.55) * scale
            young += 1
        if not p.free(x, z, 4.0 * s):          # Runde 1: etwas dichter (kompaktere Haine, gleiche Baumzahl)
            continue
        p.put("BalloonTree", x, z, s, variant_tree(p, ring), radius=4.0)
        placed += 1
    return placed


def scatter(p: Placer, isl, group, n, rad, cond=None, s_fn=None, var_fn=None, bias=1.0, rmin=0.0, rmax=1.0,
            max_slope=24.0, lean=True, sink=0.15, allow_water=False, allow_rock=False, y_fn=None):
    placed = 0
    xs, zs = p.candidates(isl, n * 14, bias=bias, rmin=rmin, rmax=rmax)
    for x, z in zip(xs, zs):
        if placed >= n:
            break
        if not p.ok_ground(x, z, max_slope, allow_rock=allow_rock, allow_water=allow_water):
            continue
        iz, ix = p.cell(x, z)
        if cond is not None and not cond(iz, ix, x, z):
            continue
        # Hindernis-Deko sammelt sich an Fels und anderen Hindernissen (Schatten, Feuchte) -> Bauflaechen bleiben ganz
        if group in OBSTACLE_GROUPS and not (at_rock(p, x, z, 12.0) or p.near_obstacle(x, z, 8.0)) and p.rng.uniform() > 0.25:
            continue
        s = s_fn() if s_fn else size_class(p)
        if not p.free(x, z, rad * s):
            continue
        v = var_fn() if var_fn else int(p.rng.integers(0, 3))
        y = y_fn(x, z) if y_fn else None
        p.put(group, x, z, s, v, y=y, lean=lean, sink=sink, radius=rad)
        placed += 1
    return placed


def _rv(p, n):
    return lambda: int(p.rng.integers(0, n))


def rock_map(p: Placer):
    """Je Spalte das Gestein des naechsten Felsens (Band in halber Wandhoehe) -> Kiesel-Material."""
    from scipy import ndimage as ndi
    from .layout import STRATA_BASE
    from .materials import BAND_LUT, STRATA_PERIOD
    from .world import STRATA_FLAG, TERRAIN_MATERIALS
    c, w = p.c, p.w
    st = ((w.mat & STRATA_FLAG) > 0) & ~c.void
    h = np.where(c.void, -1e9, c.H)
    hmax = ndi.maximum_filter(np.where(st, h, -1e9), size=15)
    ymid = np.where(st, 0.5 * (h + np.maximum(hmax, h)), 0.0)
    band = BAND_LUT[np.mod(np.floor(ymid + w.strata_off + STRATA_BASE).astype(np.int64), STRATA_PERIOD)]
    _, (iz, ix) = ndi.distance_transform_edt(~st, return_indices=True)
    near = band[iz, ix]
    keys = np.array([m if m in catalog.ROCKS else "Rock" for m in TERRAIN_MATERIALS], dtype=object)
    p.rock_key = keys[near]
    p.rock_dist = ndi.distance_transform_edt(~st) * CELL


def at_rock(p: Placer, x, z, reach=10.0):
    """Punkt liegt am Fels oder an einer Steilstelle (dort ist ohnehin keine Bauflaeche)."""
    c = p.c
    iz, ix = p.cell(x, z)
    if c.slope[iz, ix] > 6 or c.obstacle[iz, ix]:
        return True
    rr = int(math.ceil(reach / CELL))
    return bool(c.obstacle[max(0, iz - rr):iz + rr + 1, max(0, ix - rr):ix + rr + 1].any())


def boulder_groups(p: Placer, isl, n):
    """Mittlere Groesse (2-8 Studs): Brocken-Gruppen aus Schutt, bevorzugt zum Fels hin, nicht auf freier Bauflaeche."""
    c = p.c
    done = 0
    n = int(round(n * 0.7))          # Runde 1: 30 % weniger, dafuer groesser (2,0-3,8; Ring D/E wie bisher 1,2-2,4)
    mid = isl.get("ring", "A") in "ABC"
    xs, zs = p.candidates(isl, max(n, 1) * 25, rmin=0.2, rmax=1.25)
    for x, z in zip(xs, zs):
        if done >= n:
            break
        if not p.ok_ground(x, z, 30, allow_rock=True):
            continue
        rock_here = at_rock(p, x, z, 12.0)
        if not rock_here and p.rng.uniform() < 0.9:
            continue
        s = p.rng.uniform(2.0, 3.8) if mid else p.rng.uniform(1.2, 2.4)
        if s > 2.6 and not rock_here:
            s = p.rng.uniform(2.0, 2.6)          # grosse Brocken nur am Fels (Bauflaechen bleiben ganz)
        if not p.free(x, z, 2.2 * s):
            continue
        y = None
        if s > 2.0:                                   # grosse Brocken: auf den tiefsten Punkt setzen (Hang)
            if math.hypot(x, z) < PLATEAU_FREE_R + 1.9 * s + 5:
                continue                              # Plateau bleibt frei (put prueft das nur ohne y)
            y = p.low_ground(x, z, 1.2 * s) - 0.25 * s
        p.put("Boulder", x, z, s, int(p.rng.integers(0, 3)), y=y, lean=False, sink=0.25, radius=1.9, obstacle=True)
        for _ in range(int(p.rng.integers(1, 4))):
            a, d = p.rng.uniform(0, 2 * math.pi), p.rng.uniform(2.5, 5.0) * s
            x2, z2 = x + math.cos(a) * d, z + math.sin(a) * d
            s2 = p.rng.uniform(0.6, 1.1)
            if p.ok_ground(x2, z2, 30, allow_rock=True) and p.free(x2, z2, 1.6 * s2):
                p.put("Boulder", x2, z2, s2, int(p.rng.integers(0, 3)), lean=False, sink=0.25, radius=1.6,
                      obstacle=s2 > 0.9)      # kleine Brocken sind kniehoch
        done += 1
    return done


def moss_patch(c, x0, z0, R, h=0.0, core="LeafyGrass", rim="Grass", rng_seed=0):
    """Moos als Terrain (ersetzt die Moos-Teile): LeafyGrass-Kern, Grass-Saum, zerfaserter Rand, leicht erhaben."""
    sl = c.win(x0, z0, R * 1.35)
    x, z = c.local(sl)
    th = np.arctan2(z - z0, x - x0)
    q = np.hypot(x - x0, z - z0) / R
    q = q * (1 + 0.18 * np.sin(3 * th + rng_seed) + 0.12 * np.sin(5 * th + 2 * rng_seed)) \
        + 0.18 * c.nz.fbm("mossq", x, z, 6, 2)
    m = (q < 1.0) & ~c.void[sl] & np.isnan(c.wl[sl])
    if not m.any():
        return
    st = c.strata[sl]
    ns = m & ~st & (c.slope[sl] < 24)
    set_mat(c, sl, ns & (q < 0.62), core)
    set_mat(c, sl, ns & (q >= 0.62), rim)
    set_strata_top(c, sl, m & st & (c.slope[sl] < 30), core)
    if h > 0:
        c.H[sl] += np.where(ns, h * ss(1.0, 0.25, q), 0.0)


# ------------------------------------------------------------------ Themen
def theme_grove(p, isl, big=1.0):
    c = p.c
    ring = isl["ring"]
    F = c.F
    grove_trees(p, isl, int(round(18 * big)))
    scatter(p, isl, "Noodle", int(18 * big), 2.2, cond=lambda iz, ix, x, z: 0.08 < F[iz, ix] < 0.6, rmin=0.4, rmax=1.25,
            var_fn=lambda: int(p.rng.choice(4, p=np.array(catalog.NOODLE_W) / 100)))
    scatter(p, isl, "Lantern", int(6 * big), 2.0, cond=lambda iz, ix, x, z: F[iz, ix] > 0.25, var_fn=_rv(p, 3))
    if p.lights["LanternLit"] < 40 and big >= 1.0:
        scatter(p, isl, "LanternLit", 1, 2.0, cond=lambda iz, ix, x, z: F[iz, ix] > 0.3, var_fn=_rv(p, 3))
    scatter(p, isl, "Mushroom", int(5 * big), 2.5, cond=lambda iz, ix, x, z: c.S[iz, ix] > 0.35 or F[iz, ix] > 0.55,
            var_fn=_rv(p, 4))
    scatter(p, isl, "Mushroom", 3, 2.5, var_fn=_rv(p, 4), rmin=0.7, rmax=1.15)     # Runde 1: Pilz-Saum
    # Gras-Bueschel: im Hain uebernimmt das animierte Terrain-Gras (Terrain.Decoration auf Grass)
    scatter(p, isl, "Pebble", int(6 * big), 1.5, s_fn=lambda: p.rng.uniform(0.6, 1.6), lean=False, rmin=0.5, rmax=1.2)
    boulder_groups(p, isl, int(p.rng.integers(3, 6)))


def tuft_clump(p, x0, z0, n, spread=4.0):
    k = 0
    for _ in range(n * 3):
        if k >= n:
            break
        x, z = x0 + p.rng.normal(0, spread), z0 + p.rng.normal(0, spread)
        if not p.ok_ground(x, z, 24) or not p.free(x, z, 0.45):
            continue
        flower = p.rng.uniform() < 0.22
        grp = p.groups["Tuft"][3 + int(p.rng.integers(0, 2))] if flower else p.groups["Tuft"][int(p.rng.integers(0, 3))]
        p.put("Tuft", x, z, p.rng.uniform(0.75, 1.35), int(p.rng.integers(0, 3)), tmpl=grp, sink=0.08, radius=0.4)
        k += 1
    return k


def tufts(p, isl, n, rmax=1.25):
    """Gras-Bueschel in Klumpen (5-14), keine gleichmaessige Streuung. Weit draussen (Ring C-E) nur die Haelfte."""
    if isl.get("ring", "A") in "CDE":
        n = n // 2
    k = 0
    xs, zs = p.candidates(isl, max(4, n // 6), bias=0.9, rmax=rmax)
    for x, z in zip(xs, zs):
        if k >= n:
            break
        k += tuft_clump(p, x, z, int(p.rng.integers(5, 15)), spread=p.rng.uniform(2.5, 5.5))


def theme_pond(p, isl, water):
    c = p.c
    d = c.d_water
    # Schilf-Saum am Ufer
    scatter(p, isl, "Reeds", 18, 1.6, cond=lambda iz, ix, x, z: d[iz, ix] < 9, s_fn=lambda: p.rng.uniform(0.8, 1.4),
            var_fn=_rv(p, 2), rmax=1.1)
    # Baeume im Lee des Teichs
    lee_isl = dict(isl)
    lee_isl["x"] = water["x"] + LEE[0] * (water["R"] + 28)
    lee_isl["z"] = water["z"] + LEE[1] * (water["R"] + 28)
    lee_isl["R"] = 34
    grove_trees(p, lee_isl, 9)
    scatter(p, isl, "Lantern", 10, 2.0, cond=lambda iz, ix, x, z: d[iz, ix] < 30, var_fn=_rv(p, 3), rmax=1.2)
    scatter(p, isl, "LanternLit", 1, 2.0, cond=lambda iz, ix, x, z: d[iz, ix] < 25, var_fn=_rv(p, 3))
    boulder_groups(p, isl, 3)


def theme_spring(p, isl):
    for f in p.c.feat["spring"]:
        if f["kind"] == "pond" and math.hypot(f["x"] - isl["x"], f["z"] - isl["z"]) < isl["R"] + 20:
            p.put("SteamVent", f["x"], f["z"], 1.0, 0, lean=False, sink=0.6, radius=6)
    theme_grove(p, isl, 1.1)
    scatter(p, isl, "Reeds", 10, 1.6, cond=lambda iz, ix, x, z: p.c.d_water[iz, ix] < 9, var_fn=_rv(p, 2))


def theme_mesa_foot(p, isl):
    c = p.c
    grove_trees(p, isl, 12)
    scatter(p, isl, "Mushroom", 6, 2.5, cond=lambda iz, ix, x, z: c.S[iz, ix] > 0.3, var_fn=_rv(p, 4))
    scatter(p, isl, "Mushroom", 3, 2.5, var_fn=_rv(p, 4), rmin=0.7, rmax=1.15)     # Runde 1: Pilz-Saum
    scatter(p, isl, "Noodle", 14, 2.2, var_fn=lambda: int(p.rng.choice(4, p=np.array(catalog.NOODLE_W) / 100)), rmin=0.3, rmax=1.3)
    boulder_groups(p, isl, int(p.rng.integers(4, 8)))


def theme_hoodoo(p, isl):
    c = p.c
    scatter(p, isl, "OrganPipe", 7, 4, cond=lambda iz, ix, x, z: c.F[iz, ix] < 0.35, var_fn=_rv(p, 3), max_slope=18)
    scatter(p, isl, "PearlCactus", 9, 3, cond=lambda iz, ix, x, z: c.F[iz, ix] < 0.25, var_fn=_rv(p, 2), max_slope=20)
    scatter(p, isl, "Noodle", 12, 2.2, var_fn=lambda: int(p.rng.choice([0, 1, 2])))
    scatter(p, isl, "Pebble", 16, 1.5, s_fn=lambda: p.rng.uniform(0.6, 1.8), lean=False, max_slope=30)
    boulder_groups(p, isl, int(p.rng.integers(3, 7)))
    scatter(p, isl, "CrystalS", 2, 2, var_fn=lambda: variant_crystal(p, "B"), lean=False)
    scatter(p, isl, "CopperRock", 2, 5, s_fn=lambda: p.rng.uniform(0.7, 1.3), var_fn=lambda: 0, lean=False)
    # Runde 1: schlanke Felsnadeln zwischen den Hoodoos (~10 je Gruppe, in kleinen Trupps)
    scatter(p, isl, "RockNeedle", 10, 2.2, s_fn=lambda: p.rng.uniform(0.8, 1.35), var_fn=_rv(p, 4), lean=False,
            sink=0.4, max_slope=26, allow_rock=True, rmax=1.15)


def theme_oasis(p, isl):
    c = p.c
    for f in c.feat["spring"]:
        if f["kind"] == "oasis" and math.hypot(f["x"] - isl["x"], f["z"] - isl["z"]) < 12:
            q = (f["x"] + p.rng.uniform(-30, 30), f["z"] + p.rng.uniform(-30, 30))
            for _ in range(30):
                if p.ok_ground(*q, 12) and p.free(q[0], q[1], 7):
                    p.put("SteamVent", q[0], q[1], 1.0, 0, lean=False, sink=0.6, radius=6)
                    break
                q = (f["x"] + p.rng.uniform(-45, 45), f["z"] + p.rng.uniform(-45, 45))
    grove_trees(p, isl, 7)
    scatter(p, isl, "Mushroom", 10, 2.5, var_fn=_rv(p, 4))
    scatter(p, isl, "Lantern", 12, 2.0, var_fn=_rv(p, 3))
    scatter(p, isl, "LanternLit", 2, 2.0, var_fn=_rv(p, 3))
    scatter(p, isl, "Reeds", 10, 1.6, cond=lambda iz, ix, x, z: c.d_water[iz, ix] < 9, var_fn=_rv(p, 2))
    boulder_groups(p, isl, 3)


def theme_dunes(p, isl):
    c = p.c
    scatter(p, isl, "OrganPipe", 8, 4, var_fn=_rv(p, 3), max_slope=14)
    scatter(p, isl, "PearlCactus", 10, 3, var_fn=_rv(p, 2), max_slope=14)
    p_one = p.groups["PearlCactus"][-1]
    for _ in range(2):
        xs, zs = p.candidates(isl, 30)
        for x, z in zip(xs, zs):
            if p.ok_ground(x, z, 14) and p.free(x, z, 3):
                p.put("PearlCactus", x, z, size_class(p), int(p.rng.integers(0, 2)), tmpl=p_one, radius=3)
                break
    grove_trees(p, isl, 3, lead=True)
    scatter(p, isl, "Noodle", 10, 2.2, var_fn=lambda: int(p.rng.choice([0, 1])))
    scatter(p, isl, "Pebble", 6, 1.5, s_fn=lambda: p.rng.uniform(0.6, 1.4), lean=False)
    boulder_groups(p, isl, 3)


def theme_crystal_garden(p, isl, fault):
    """Kristalle entlang einer Verwerfungslinie (dicht auf der Linie, lockerer daneben)."""
    c = p.c
    ring = isl["ring"]
    fam = variant_crystal(p, ring)
    fam2 = variant_crystal(p, ring)
    L = fault["L"]
    lit = 0
    for k in range(70):
        t = p.rng.uniform(-0.55, 0.55)
        off = p.rng.normal(0, 7 + 10 * abs(t))
        x = fault["x"] + math.cos(fault["ang"]) * L * t - math.sin(fault["ang"]) * off
        z = fault["z"] + math.sin(fault["ang"]) * L * t + math.cos(fault["ang"]) * off
        if not p.ok_ground(x, z, 26):
            continue
        near = abs(off) < 9
        if near and p.count.get("_gm%d" % id(fault), 0) < 12:
            use_lit = lit < 2 and p.lights["CrystalMLit"] < 30 and p.rng.uniform() < 0.3
            grp = "CrystalMLit" if use_lit else "CrystalM"
            s = p.rng.uniform(0.7, 1.4)
            if p.free(x, z, 3.0 * s):
                p.put(grp, x, z, s, fam if p.rng.uniform() < 0.75 else fam2, lean=False, sink=0.6, radius=2.6)
                p.count["_gm%d" % id(fault)] += 1
                lit += use_lit
        else:
            s = p.rng.uniform(0.8, 1.6)
            if p.free(x, z, 1.8 * s):
                p.put("CrystalS", x, z, s, fam if p.rng.uniform() < 0.7 else fam2, lean=False, sink=0.3, radius=1.4)
    scatter(p, isl, "PearlCactus", 4, 3, var_fn=lambda: 1)
    scatter(p, isl, "Pebble", 8, 1.5, s_fn=lambda: p.rng.uniform(0.6, 1.4), lean=False)
    boulder_groups(p, isl, int(p.rng.integers(3, 6)))


def theme_terrace(p, isl, terr):
    c = p.c
    for f in c.feat["spring"]:
        if f["kind"] == "terrace" and f.get("group") == terr["name"]:
            for _ in range(40):
                x, z = f["x"] + p.rng.uniform(-14, 14), f["z"] + p.rng.uniform(-14, 14)
                if p.ok_ground(x, z, 14, allow_rock=True) and p.free(x, z, 7):
                    p.put("SteamVent", x, z, 1.0, 0, lean=False, sink=0.6, radius=6)
                    break
    scatter(p, isl, "Lantern", 8, 2.0, var_fn=_rv(p, 3), rmin=0.75, rmax=1.3)
    scatter(p, isl, "LanternLit", 1, 2.0, var_fn=_rv(p, 3), rmin=0.75, rmax=1.3)
    scatter(p, isl, "CrystalS", 6, 1.6, var_fn=lambda: variant_crystal(p, "D"), lean=False, rmin=0.8, rmax=1.3)
    scatter(p, isl, "Reeds", 8, 1.6, cond=lambda iz, ix, x, z: c.d_water[iz, ix] < 8, var_fn=_rv(p, 2), rmax=1.0)


def theme_geode(p, isl, g):
    lit = p.lights["CrystalMLit"] < 34
    for k in range(9):
        a = p.rng.uniform(0, 2 * math.pi)
        rr = g["R"] * p.rng.uniform(0.75, 1.05)
        x, z = g["x"] + math.cos(a) * rr, g["z"] + math.sin(a) * rr
        if not p.ok_ground(x, z, 30, allow_rock=True):
            continue
        # Kristalle neigen sich zur Mulden-Mitte
        yaw = math.atan2(g["x"] - x, g["z"] - z)
        if k < 3:
            grp = "CrystalMLit" if (k == 0 and lit) else "CrystalM"
            s = p.rng.uniform(0.7, 1.2)
        else:
            grp, s = "CrystalS", p.rng.uniform(1.0, 1.8)
        if p.free(x, z, 2.0 * s):
            p.put(grp, x, z, s, variant_crystal(p, "D"), yaw=yaw, lean=False, rx=math.radians(18), sink=0.5, radius=2)


def theme_cool(p, isl):
    c = p.c
    grove_trees(p, isl, 10, scale=0.75)
    scatter(p, isl, "CrystalTitan", 4, 2.5, var_fn=_rv(p, 2), lean=False, sink=0.05)
    scatter(p, isl, "Pebble", 6, 1.5, s_fn=lambda: p.rng.uniform(0.6, 1.4), lean=False)
    boulder_groups(p, isl, 3)


def theme_ice(p, isl):
    scatter(p, isl, "CrystalTitan", 6, 2.5, s_fn=lambda: p.rng.uniform(0.7, 1.5), var_fn=_rv(p, 2), lean=False, sink=0.05,
            max_slope=30, allow_rock=True)


# ------------------------------------------------------------------ Planung (vor dem Finalisieren)
def plan_islands(p: Placer):
    c = p.c
    rng = p.rng
    S = c.L.slots
    lm = {f["key"]: f for f in c.feat["landmark"]}
    sx, _, sz = c.L.spawn
    # Ring A: Haupthain im Lee rechts vom Tor, Teich-Hain, Abendbank, Mesa-Fuesse
    # Runde 2: Ring A ist Plateau -> Haupthain direkt am Plateau-Rand (r 165), rechts vom Saturn-Tor
    gx, gz = pol(84, 166)
    p.island(gx, gz, 46, "grove", big=1.35, ground="grass")
    for w in c.feat["water"]:
        if w["kind"] in ("pond", "spring") or w["kind"].startswith("oasis"):
            continue
    pond = [w for w in c.feat["water"] if w["kind"] == "pond"]
    if pond:
        w0 = pond[0]
        p.island(w0["x"] + LEE[0] * 10, w0["z"] + LEE[1] * 10, w0["R"] + 24, "pond", water=w0, ground="grass")
    if "L0" in lm:
        l0 = lm["L0"]
        p.island(l0["x"] + LEE[0] * 45, l0["z"] + LEE[1] * 45, 34, "mesa_foot", ground="grass")
    # Runde 2: Mesa-Fuss-Haine am Kranz um das Plateau (vorher Ring A bis r 330)
    n_in = 0
    for m in c.feat["mesa"]:
        rr = math.hypot(m["x"], m["z"])
        if rr < 240 and m["stage"] == "mesa" and n_in < 3:
            d = m["R"] + 26
            x, z = m["x"] + LEE[0] * d, m["z"] + LEE[1] * d
            if math.hypot(x, z) < PLATEAU_FREE_R + 30 or any(math.hypot(x - i["x"], z - i["z"]) < 60 for i in p.islands):
                continue
            p.island(x, z, 36, "mesa_foot", ground="grass")
            n_in += 1
    # Ring B: Quellwaeldchen, Nadelgarten, Mesa-Fuesse, Zwillingstuerme
    for g in c.feat.get("grove_spring", []):
        p.island(g["x"], g["z"], 42, "spring", ground="grass")
    for k, g in enumerate(c.feat.get("hoodoo_group", [])[:4]):
        p.island(g["x"], g["z"], g["R"] + 10, "hoodoo")
    nb = 0
    for m in sorted(c.feat["mesa"], key=lambda m: -m["R"]):
        rr = math.hypot(m["x"], m["z"])
        if sr(300) + 20 < rr < sr(600) and m["stage"] == "mesa" and nb < 2:
            d = m["R"] + 30
            x, z = m["x"] + LEE[0] * d, m["z"] + LEE[1] * d
            if any(math.hypot(x - i["x"], z - i["z"]) < 70 for i in p.islands):
                continue
            p.island(x, z, 42, "mesa_foot", ground="grass")
            nb += 1
    if "L2" in lm:
        l2 = lm["L2"]
        p.island(l2["x"] + LEE[0] * 50, l2["z"] + LEE[1] * 50, 40, "grove", big=0.8, ground="grass")
    # Ring D: Haine im Lee grosser Mesas (feuchte Fuesse)
    ndm = 0
    for m in sorted(c.feat["mesa"], key=lambda m: -m["R"]):
        rr = math.hypot(m["x"], m["z"])
        if sr(1150) < rr < sr(1550) and m["stage"] == "mesa" and ndm < 4:
            d = m["R"] + 28
            p.island(m["x"] + LEE[0] * d, m["z"] + LEE[1] * d, 42, "mesa_foot", ground="grass")
            ndm += 1
    # Runde 1: Ring C bekommt 3 kleine Mesa-Fuss-Haine (Mittelfeld im Zielbild-Blick Az 300-110 bevorzugt)
    ncm = 0
    cm = [m for m in c.feat["mesa"] if sr(640) < math.hypot(m["x"], m["z"]) < sr(1100) and m["stage"] == "mesa"]
    cm.sort(key=lambda m: (abs(ang_diff(math.degrees(math.atan2(m["x"], -m["z"])), 25.0)) > 85, -m["R"]))
    for m in cm:
        if ncm >= 3:
            break
        d = m["R"] + 28
        x, z = m["x"] + LEE[0] * d, m["z"] + LEE[1] * d
        iz, ix = c.idx(x, z)
        if c.wash_dist[iz, ix] < 25 or c.void[iz, ix] or any(math.hypot(x - i["x"], z - i["z"]) < 90 for i in p.islands):
            continue
        p.island(x, z, 42, "mesa_foot", ground="grass")
        ncm += 1
    # Ring C: Oasen, Duenen-Haine, Bogen
    for o in c.feat.get("oasis_c", []):
        p.island(o["x"], o["z"], o["R"] + 15, "oasis", ground="grass")
    if "L4" in lm:
        l4 = lm["L4"]
        p.island(l4["x"], l4["z"], 70, "dunes")
    nd = 0
    for _ in range(400):
        if nd >= 2:
            break
        a, r = rng.uniform(150, 280), rng.uniform(sr(700), sr(1050))
        x, z = pol(a, r)
        iz, ix = c.idx(x, z)
        if c.mask("dune")[iz, ix] or c.wash_dist[iz, ix] < 22 or any(math.hypot(x - i["x"], z - i["z"]) < 140 for i in p.islands):
            continue
        p.island(x, z, 50, "dunes")
        nd += 1
    for cy in c.feat.get("oasis_canyon", []):
        p.island(cy["x"], cy["z"], 32, "oasis", ground="grass")
    # Ring D: Kristallgaerten, Terrassen, Geoden, Krater-Teich
    for f in c.feat.get("fault", [])[:7]:
        p.island(f["x"], f["z"], max(55, f["L"] * 0.55), "crystal", fault=f)
    for t in c.feat.get("terrace", []):
        p.island(t["x"], t["z"], max(t["w"], t["l"]) * 0.55, "terrace", terr=t)
    for g in c.feat.get("geode", []):
        p.island(g["x"], g["z"], g["R"] + 8, "geode", geode=g)
    for w in c.feat["water"]:
        if w["kind"] == "crater":
            p.island(w["x"] + LEE[0] * (w["R"] + 20), w["z"] + LEE[1] * (w["R"] + 20), 40,
                     "cool" if math.hypot(w["x"], w["z"]) > RING_EDGES[4] else "grove", big=0.8, ground="grass")
    # Ring E: kuehle Haine an Nebelbecken, Eisfelder
    for f in c.feat.get("fogbasin", []):
        p.island(f["x"] + LEE[0] * f["R"] * 0.6, f["z"] + LEE[1] * f["R"] * 0.6, 42, "cool")
    for f in c.feat.get("ice", [])[:4]:
        p.island(f["x"], f["z"], f["R"], "ice")
    # Deko-Zone + Bodenbewuchs malen
    dz = np.zeros(c.H.shape, bool)
    for isl in p.islands:
        sl = c.win(isl["x"], isl["z"], isl["R"] * 1.4)
        x, z = c.local(sl)
        th = np.arctan2(z - isl["z"], x - isl["x"])
        q = np.hypot(x - isl["x"], z - isl["z"]) / isl["R"] / (1.0 + 0.25 * np.sin(3 * th + isl["x"] * 0.01)
                                                               + 0.15 * np.sin(5 * th + isl["z"] * 0.02))
        q = q * (1 + 0.15 * c.nz.fbm("islq", x, z, 25, 2))
        inner = q < 1.0
        dz[sl] |= inner
        if isl.get("ground") == "grass":
            # Wiese: LeafyGrass-Kern (innere Haelfte), Grass-Ring, Rand ueber 8-16 Studs mit Ground verzahnt
            F = c.F[sl]
            sl_ = c.slope[sl]
            dry = np.isnan(c.wl[sl]) & ~c.strata[sl] & (sl_ < 16)
            # Runde 1: ruhiger, kompakter Rand (0,08 x fbm(18) statt 0,22 x fbm(7))
            fray = 0.08 * c.nz.fbm("grassedge", x, z, 18, 2) + 0.12 * c.nz.fbm("grassedge2", x, z, 22, 2)
            g1 = inner & (q < 0.92 - 0.15 * (1 - F) + fray) & dry
            set_mat(c, sl, g1, "Grass")
            set_mat(c, sl, g1 & (q < 0.5 + 0.25 * F + fray), "LeafyGrass")
            # Haine stehen auf leichten Huegeln (+1-1,6 Studs, sehr flach auslaufend)
            if isl["theme"] in ("grove", "mesa_foot", "spring", "cool"):
                dw = c.d_water[sl] if hasattr(c, "d_water") else np.full(q.shape, 99.0)
                A = float(rng.uniform(1.0, 1.6))
                c.H[sl] += np.where(dry & (dw > 14), A * ss(1.1, 0.05, q) * ss(14, 30, dw), 0.0)
    spring_pots(p)
    moss_terrain(p)
    dz &= c.r > PLATEAU_FREE_R
    c.deco_zone_plan = dz


def spring_pots(p: Placer, n=8):
    """Runde 1: kleine tuerkise Quelltoepfe (Oe 18-32, Tiefe 2, Boden Concrete, Salzrand, Sandring) in Hain-Inseln
    Ring A-C (wie die Pfuetzen im Zielbild). Nur auf ebenem, trockenem Boden ohne Fels; nicht im Plateau."""
    from . import waterforms as wf
    c = p.c
    rng = np.random.default_rng(c.seed * 7717 + 11)     # eigener Zufall
    # Ring B/C (Ring A hat die knappsten Bauflaechen); mittig im Hain, wo die Baeume ohnehin Deko-Zone sind
    isl = [i for i in p.islands if i["theme"] in ("grove", "mesa_foot", "oasis", "spring", "pond")
           and RING_EDGES[2] < math.hypot(i["x"], i["z"]) < sr(1100)]          # Runde 2: erst ab Ring C
    if not isl:
        return 0
    done = 0
    per = {}
    pots = []
    for _ in range(600):
        if done >= n:
            break
        i = isl[int(rng.integers(0, len(isl)))]
        if per.get(id(i), 0) >= 1 + (i["R"] > 45):
            continue
        a, rr = rng.uniform(0, 2 * math.pi), i["R"] * rng.uniform(0.15, 0.6)
        x, z = i["x"] + math.cos(a) * rr, i["z"] + math.sin(a) * rr
        d = float(rng.uniform(18, 32))
        R = d / 2 + 8
        if math.hypot(x, z) < PLATEAU_FREE_R + 10 + R or any(math.hypot(x - q[0], z - q[1]) < 55 for q in pots):
            continue
        sl = c.win(x, z, R)
        lx, lz = c.local(sl)
        circ = (lx - x) ** 2 + (lz - z) ** 2 < R * R
        if (c.void[sl][circ].any() or (~np.isnan(c.wl[sl][circ])).any() or (c.slope[sl][circ] > 6).any()
                or c.strata[sl][circ].any() or (c.wash_dist[sl][circ] < 8).any() or c.obstacle[sl][circ].any()):
            continue
        wf.pond(c, x, z, d, 2.0, floor_mat="Concrete", bank_mat="Salt", ring_mat="Sand", ring_w=8.0, name="pot%d" % done)
        per[id(i)] = per.get(id(i), 0) + 1
        pots.append((x, z))
        done += 1
    c.feat["spring_pot"] = [{"x": x, "z": z} for x, z in pots]
    return done


def moss_terrain(p: Placer):
    """Moospolster als Terrain-Flecken (Oe 6-30, +0,5-1,5) statt Teile: in Inseln, feuchten Mulden, auf dem Plateau
    (dort flach), auf Balkonen und grossen Schwebinseln."""
    c = p.c
    rng = p.rng
    per = {"grove": 7, "pond": 6, "spring": 6, "mesa_foot": 4, "oasis": 6, "crystal": 3, "terrace": 4, "cool": 5,
           "ice": 2, "hoodoo": 0, "dunes": 0, "geode": 0}
    for isl in p.islands:
        n = per.get(isl["theme"], 0)
        k = 0
        for _ in range(n * 12):
            if k >= n:
                break
            a, rr = rng.uniform(0, 2 * math.pi), isl["R"] * math.sqrt(rng.uniform(0.05, 1.1))
            x, z = isl["x"] + math.cos(a) * rr, isl["z"] + math.sin(a) * rr
            iz, ix = c.idx(x, z)
            if c.void[iz, ix] or not np.isnan(c.wl[iz, ix]) or c.slope[iz, ix] > 14 or math.hypot(x, z) < PLATEAU_FREE_R:
                continue
            if isl["theme"] not in ("crystal", "terrace", "ice", "cool") and c.F[iz, ix] < 0.15:
                continue
            R = rng.uniform(4, 15)
            cool = isl["theme"] in ("crystal", "ice", "cool")
            moss_patch(c, x, z, R, h=float(np.clip(0.09 * R, 0.5, 1.5)), rim="LeafyGrass" if cool else "Grass",
                       rng_seed=float(rng.uniform(0, 6)))
            k += 1
    # feuchte Mulden draussen (frueher 90 Moos-Teile): flacher, damit Bauflaechen eben bleiben
    k = 0
    for _ in range(6000):
        if k >= 60:
            break
        a, r = rng.uniform(0, 360), rng.uniform(PLATEAU_FREE_R + 10, sr(1600))
        x, z = pol(a, r)
        iz, ix = c.idx(x, z)
        if c.F[iz, ix] < 0.35 or c.void[iz, ix] or not np.isnan(c.wl[iz, ix]) or c.slope[iz, ix] > 12:
            continue
        R = rng.uniform(5, 14)
        moss_patch(c, x, z, R, h=float(np.clip(0.05 * R, 0.3, 0.7)), rng_seed=float(rng.uniform(0, 6)))
        k += 1
    # Plateau r 40-115: ein paar flache Moosflecken (nur Material, keine Hoehe -> Bauflaeche bleibt eben)
    k = 0
    for _ in range(400):
        if k >= 6:
            break
        a, r = rng.uniform(0, 360), rng.uniform(40, PLATEAU_R)
        x, z = pol(a, r)
        if abs(x) < 46 and 14 < z < 76:
            continue
        iz, ix = c.idx(x, z)
        if c.slope[iz, ix] > 8 or c.mask("wash")[iz, ix]:
            continue
        moss_patch(c, x, z, rng.uniform(3.5, 7), h=0.0, rng_seed=float(rng.uniform(0, 6)))
        k += 1
    # Balkone und grosse Schwebinseln: Moos-/Wiesendecke auf dem Fels
    for b in c.feat.get("balcony", []):
        moss_patch(c, b["x"] * 0.995, b["z"] * 0.995, 10, h=0.0, rng_seed=float(rng.uniform(0, 6)))
    for f in c.feat.get("float", []):
        if f["big"]:
            moss_patch(c, f["x"], f["z"], f["R"] * 0.55, h=0.0, rim="Grass", rng_seed=float(rng.uniform(0, 6)))


# ------------------------------------------------------------------ Setzen (nach dem Finalisieren)
def place_all(p: Placer):
    c = p.c
    rng = p.rng
    rock_map(p)
    # Runde 2: Hoodoo-Saeulen sind Zusatzformen (nicht in der Hoehenkarte) -> als belegt markieren, sonst stehen
    # Kiesel, Brocken oder Nadeln in den Saeulen
    for h in c.feat.get("hoodoo", []):
        p.mark(h["x"], h["z"], h["hat_r"] + 1.0)
    for isl in p.islands:
        th = isl["theme"]
        if th == "grove":
            theme_grove(p, isl, isl.get("big", 1.0))
        elif th == "pond":
            theme_pond(p, isl, isl["water"])
        elif th == "spring":
            theme_spring(p, isl)
        elif th == "mesa_foot":
            theme_mesa_foot(p, isl)
        elif th == "hoodoo":
            theme_hoodoo(p, isl)
        elif th == "oasis":
            theme_oasis(p, isl)
        elif th == "dunes":
            theme_dunes(p, isl)
        elif th == "crystal":
            theme_crystal_garden(p, isl, isl["fault"])
        elif th == "terrace":
            theme_terrace(p, isl, isl["terr"])
        elif th == "geode":
            theme_geode(p, isl, isl["geode"])
        elif th == "cool":
            theme_cool(p, isl)
        elif th == "ice":
            theme_ice(p, isl)
    landmarks(p)
    volcano_plume(p)
    base_ring(p)
    band_blocks(p, 170)
    scattered(p)
    field_clusters(p)
    edge_extras(p)
    ground_mist(p)


def base_ring(p: Placer):
    """Rund um die Basis: Gras-Bueschel in Klumpen (Plateau nur locker), Kiesel, kleine Nudeln, Mini-Kristall."""
    c = p.c
    rng = p.rng
    clumps = 0
    hall = lambda x, z: abs(x) < 42 and 18 < z < 72          # Start-Halle (Jus Place) freihalten
    for _ in range(6000):
        if clumps >= 48:
            break
        a = rng.uniform(0, 360)
        r = rng.uniform(PLATEAU_R, 200) if rng.uniform() < 0.75 else rng.uniform(40, PLATEAU_R)
        x, z = pol(a, r)
        if hall(x, z) or (r < PLATEAU_R and rng.uniform() < 0.6):
            continue
        # Klumpen haeufen sich an Felsfuessen und in Mulden, nicht auf freier Flaeche
        iz, ix = c.idx(x, z)
        if rng.uniform() > 0.25 + 0.75 * min(1.0, float(c.F[iz, ix]) * 2.0 + float(c.masks["talus"][max(0, iz - 6):iz + 7, max(0, ix - 6):ix + 7].any())):
            continue
        if c.mask("wash")[iz, ix] and r < 200:
            continue
        tuft_clump(p, x, z, int(rng.integers(4, 9)) if r > PLATEAU_R else int(rng.integers(3, 6)), spread=rng.uniform(2.5, 5.0))
        clumps += 1
    # kleine Nudeln (kniehoch) ausserhalb von r 150, in Gruppen
    for k in range(10):
        a, r = rng.uniform(0, 360), rng.uniform(PLATEAU_FREE_R + 5, 200)
        x0, z0 = pol(a, r)
        for j in range(int(rng.integers(2, 6))):
            x, z = x0 + rng.normal(0, 6), z0 + rng.normal(0, 6)
            if p.ok_ground(x, z, 16) and p.free(x, z, 2) and not c.mask("wash")[c.idx(x, z)]:
                p.put("Noodle", x, z, rng.uniform(0.6, 0.95), int(rng.choice(4, p=np.array(catalog.NOODLE_W) / 100)), radius=2)
    k = 0
    for _ in range(600):                                  # Kiesel nur, wo Fels in der Naehe ist (nicht auf freie Bauflaeche)
        if k >= 30:
            break
        a, r = rng.uniform(0, 360), rng.uniform(60, 200)
        x, z = pol(a, r)
        iz, ix = c.idx(x, z)
        if p.rock_dist[iz, ix] > 50:
            continue
        if not hall(x, z) and p.ok_ground(x, z, 20) and p.free(x, z, 1):
            p.put("Pebble", x, z, rng.uniform(0.5, 1.1), lean=False, radius=1)
            k += 1
    # Plateau r 25-150: sparsam, in Gruepchen, viel freier Boden (alles kniehoch, ohne Kollision)
    def plateau_spot(rmin=25, rmax=PLATEAU_R - 2):
        for _ in range(200):
            a, r = rng.uniform(0, 360), rng.uniform(rmin, rmax)
            x, z = pol(a, r)
            if p.ok_ground(x, z, 10) and not c.mask("wash")[c.idx(x, z)]:
                return x, z
        return None
    for k in range(7):                                    # Kiesel-Gruppen (3-5)
        q = plateau_spot()
        if q:
            for j in range(int(rng.integers(3, 6))):
                x, z = q[0] + rng.normal(0, 1.8), q[1] + rng.normal(0, 1.8)
                if p.ok_ground(x, z, 12) and p.free(x, z, 0.8):
                    p.put("Pebble", x, z, rng.uniform(0.4, 1.0), lean=False, radius=0.7)
    for k in range(14):                                   # Bueschel-Gruppen
        q = plateau_spot()
        if q:
            tuft_clump(p, q[0], q[1], int(rng.integers(3, 7)), spread=2.5)
    for k in range(10):                                   # einzelne Bluemchen
        q = plateau_spot()
        if q:
            p.put("Tuft", q[0], q[1], rng.uniform(0.9, 1.2), int(rng.integers(0, 3)), tmpl=p.groups["Tuft"][3 + k % 2], sink=0.08, radius=0.5)
    for k in range(3):                                    # kleine Nudelpflanzen <= 6 Studs
        q = plateau_spot(40, PLATEAU_R - 2)
        if q and p.free(q[0], q[1], 2):
            p.put("Noodle", q[0], q[1], rng.uniform(0.7, 0.82), int(rng.choice(4, p=np.array(catalog.NOODLE_W) / 100)), radius=2)
    # Mini-Kristall links vom Tor (Wegweiser)
    for a, r in ((24, 138), (330, 150)):
        x, z = pol(a + rng.uniform(-3, 3), r)
        for _ in range(20):
            if p.ok_ground(x, z, 16) and p.free(x, z, 2):
                p.put("CrystalS", x, z, rng.uniform(1.0, 1.3), 0, lean=False, sink=0.3, radius=1.5)
                break
            x, z = x + rng.uniform(-6, 6), z + rng.uniform(-6, 6)


def scattered(p: Placer):
    """Ausserhalb der Inseln: Kiesel an Schutthalden/Faechern/Wash-Raendern, Kupfer-Brocken (Ring B), Fossilien,
    Moos-Flecken, Nudel-Felder (kniehoch, auch in Bauzonen erlaubt)."""
    c = p.c
    rng = p.rng
    # Kiesel: Schutthalden (Farbe des Bandes darueber), Faecher-Spitzen, Wash-Raender
    tal = c.masks.get("talus")
    tq = np.nan_to_num(getattr(c, "talus_q", np.full(c.H.shape, 0.5)), nan=0.5)
    iz, ix = np.nonzero(tal & (c.r > PLATEAU_FREE_R + 5))
    sel = rng.choice(len(iz), size=min(len(iz), 3000), replace=False)
    n = 0
    for k in sel:                                       # Cluster aus 3-7 Kieseln: gross nah am Fels, klein weiter weg
        if n >= 1300:
            break
        x0, z0 = cell_xz(ix[k], iz[k])
        if math.hypot(x0, z0) > sr(600) + 50 and rng.uniform() > 0.45:    # weit draussen sparen (Teile-Budget, Handys)
            continue
        q = float(tq[iz[k], ix[k]])
        for j in range(int(rng.integers(3, 8))):
            x, z = x0 + rng.normal(0, 3.5), z0 + rng.normal(0, 3.5)
            s = float(np.clip((1.9 - 1.3 * q) * rng.uniform(0.6, 1.2), 0.4, 2.4))
            if not p.ok_ground(x, z, 36, allow_rock=True) or not p.free(x, z, 0.6 * s):
                continue
            p.put("Pebble", x, z, s, lean=False, radius=0.8, sink=0.35)
            n += 1
    for f in c.feat.get("fan", []):
        for k in range(16):
            x = f["x"] + rng.normal(0, 14)
            z = f["z"] + rng.normal(0, 14)
            if p.ok_ground(x, z, 30) and p.free(x, z, 1.5):
                p.put("Pebble", x, z, rng.uniform(0.8, 2.2), lean=False, radius=1.2, sink=0.35)
    # Runde 1: Kiesel-Saum direkt am Wash-Rand (0 < wash_dist < 6), r 160-900, in Gruepchen zu 2-4 (bis 400 Stueck)
    wb = (c.wash_dist > 0) & (c.wash_dist < 6) & (c.r > PLATEAU_FREE_R + 10) & (c.r < sr(900)) & ~c.void
    iz, ix = np.nonzero(wb)
    sel = rng.choice(len(iz), size=min(len(iz), 4000), replace=False)
    n = 0
    for k in sel:
        if n >= 400:
            break
        if rng.uniform() > 0.5 + 0.5 * math.sin(ix[k] * 0.05) * math.cos(iz[k] * 0.04):
            continue
        x0, z0 = cell_xz(ix[k], iz[k])
        for j in range(int(rng.integers(2, 5))):
            x, z = x0 + rng.normal(0, 2.2), z0 + rng.normal(0, 2.2)
            if p.ok_ground(x, z, 30) and p.free(x, z, 0.8):
                p.put("Pebble", x, z, rng.uniform(0.5, 1.3), lean=False, radius=0.8, sink=0.35)
                n += 1
    # Orgelrohre an Wash-Raendern (Ring B/C, trocken)
    n = 0
    for _ in range(3000):
        if n >= 40:
            break
        a, r = rng.uniform(0, 360), rng.uniform(sr(320), sr(1050))
        x, z = pol(a, r)
        iz_, ix_ = c.idx(x, z)
        if not (6 < c.wash_dist[iz_, ix_] < 20) or c.F[iz_, ix_] > 0.3:
            continue
        if not c.deco_zone_plan[iz_, ix_] and not at_rock(p, x, z, 8.0):     # Hindernis-Deko nicht auf Bauflaeche
            continue
        if p.ok_ground(x, z, 16) and p.free(x, z, 9):
            p.put("OrganPipe", x, z, size_class(p), int(rng.integers(0, 3)), radius=4)
            n += 1
            for _ in range(int(rng.integers(2, 5))):
                x2, z2 = x + rng.uniform(-14, 14), z + rng.uniform(-14, 14)
                if p.ok_ground(x2, z2, 16) and p.free(x2, z2, 4) and (c.deco_zone_plan[c.idx(x2, z2)] or at_rock(p, x2, z2, 8.0)):
                    p.put("OrganPipe", x2, z2, size_class(p) * 0.7, int(rng.integers(0, 3)), radius=4)
                    n += 1
    # Kupfer-Patina-Brocken (Ring B): an Schutthalden-Raendern, nicht in Bauzonen.
    # Runde 2: 36 statt 60 und nur noch auf Hindernis-Flaeche (Halde/Fels) - Ring B hat die knappsten Bauflaechen
    n = 0
    for _ in range(4000):
        if n >= 36:
            break
        a, r = rng.uniform(0, 360), rng.uniform(PLATEAU_FREE_R + 15, sr(600) + 40)
        x, z = pol(a, r)
        iz_, ix_ = c.idx(x, z)
        if not (c.masks["talus"][iz_, ix_] and at_rock(p, x, z, 4.0)):
            continue
        if c.obstacle[max(0, iz_ - 3):iz_ + 4, max(0, ix_ - 3):ix_ + 4].mean() < 0.45:
            continue
        if p.ok_ground(x, z, 30, allow_rock=True) and p.free(x, z, 6):
            p.put("CopperRock", x, z, rng.uniform(0.6, 1.4), 0, lean=False, sink=0.6, radius=5)
            n += 1
    # Fossilien in Steilwaenden (Mud/Sandstone-Baender, Ring B-C)
    n = 0
    walls = (c.masks.get("mesa", np.zeros_like(c.void)) & (c.slope > 55) & (c.r > PLATEAU_FREE_R + 10) & (c.r < sr(1100)))
    iz, ix = np.nonzero(walls)
    if len(iz):
        sel = rng.choice(len(iz), size=min(len(iz), 4000), replace=False)
        gz, gx = np.gradient(c.H, CELL)
        for k in sel:
            if n >= 40:
                break
            i, j = iz[k], ix[k]
            nxv, nzv = -gx[i, j], -gz[i, j]
            ln = math.hypot(nxv, nzv)
            if ln < 1e-3:
                continue
            nxv, nzv = nxv / ln, nzv / ln
            x, z = cell_xz(j, i)
            hi = c.H[i, j]
            lo = p.ground(x + nxv * 6, z + nzv * 6)
            if hi - lo < 12:
                continue
            y = lo + rng.uniform(4, min(16, hi - lo - 4))
            if not p.free(x, z, 6):
                continue
            yaw = math.atan2(nxv, nzv)
            p.put("Fossil", x + nxv * 2.2, z + nzv * 2.2, rng.uniform(0.6, 1.0), 0, y=y, yaw=yaw, lean=False,
                  rz=rng.uniform(0, 6.28), radius=4)
            n += 1
    # Nudel-Felder (kniehoch); die Moosflecken sind jetzt Terrain (moss_terrain). Runde 1: 5 -> 2 (Teile sparen)
    for fi in range(2):
        for _ in range(300):
            a, r = rng.uniform(0, 360), rng.uniform(PLATEAU_FREE_R + 20, sr(560))
            x0, z0 = pol(a, r)
            if any(math.hypot(x0 - i["x"], z0 - i["z"]) < i["R"] + 60 for i in p.islands):
                continue
            if p.ok_ground(x0, z0, 10):
                break
        var = int(rng.choice(4, p=np.array(catalog.NOODLE_W) / 100))
        k = 0
        for _ in range(200):
            if k >= int(rng.integers(20, 40)):
                break
            x, z = x0 + rng.normal(0, 22), z0 + rng.normal(0, 22)
            if p.ok_ground(x, z, 12) and p.free(x, z, 2.0):
                p.put("Noodle", x, z, rng.uniform(0.6, 1.0), var if rng.uniform() < 0.7 else int(rng.integers(0, 3)), radius=1.8)
                k += 1


def field_clusters(p: Placer):
    """Runde 2 (Dichte statt Leere): kleine, kniehohe Gruppen in den freien Ebenen von Ring B-E, Abstand ~40-60 Studs -
    Kristall-Kluepchen, Kiesel/kleine Brocken, Bueschel, Nudeln. Nichts davon ist Hindernis (keine Kollision, <= ~8
    Studs hoch), die Bauzonen bleiben also ganz. Nicht in Washes, Wasser, Deko-Inseln, auf dem Plateau."""
    c = p.c
    rng = np.random.default_rng(c.seed * 9203 + 41)      # eigener Zufall: aendert die uebrige Deko nicht
    want = {"B": 70, "C": 110, "D": 100, "E": 55}
    done = Counter()
    centers = []
    cg = defaultdict(list)

    def far(x, z, d):
        gx, gz = int(x // 64), int(z // 64)
        for i in (gx - 1, gx, gx + 1):
            for j in (gz - 1, gz, gz + 1):
                for (qx, qz) in cg.get((i, j), ()):
                    if (qx - x) ** 2 + (qz - z) ** 2 < d * d:
                        return False
        return True

    for _ in range(30000):
        if all(done[k] >= v for k, v in want.items()):
            break
        a = rng.uniform(0, 360)
        r = math.sqrt(rng.uniform((PLATEAU_FREE_R + 12) ** 2, (RING_EDGES[-1] - 40) ** 2))
        ring = ring_of(r)
        if ring not in want or done[ring] >= want[ring]:
            continue
        x, z = pol(a, r)
        iz, ix = c.idx(x, z)
        if (c.void[iz, ix] or not np.isnan(c.wl[iz, ix]) or c.slope[iz, ix] > 12 or c.wash_dist[iz, ix] < 3
                or c.deco_zone_plan[iz, ix] or c.obstacle[iz, ix]):
            continue
        if not far(x, z, rng.uniform(36, 52)):
            continue
        cg[(int(x // 64), int(z // 64))].append((x, z))
        centers.append((x, z))
        done[ring] += 1
        u = rng.uniform()
        ne = c.wNE[iz, ix] > 0.5
        if (ring == "D" and u < 0.6) or (ring == "E" and u < 0.35) or (ring in "BC" and u < 0.14):
            kind = "crystal"
        elif u < 0.55:
            kind = "rocks"
        elif u < 0.8 and ring != "E":
            kind = "noodle" if (ring == "C" and not ne) or rng.uniform() < 0.4 else "tuft"
        else:
            kind = "tuft"
        n = int(rng.integers(3, 7))
        fam = variant_crystal(p, ring)
        for k in range(n * 3):
            if n <= 0:
                break
            x2, z2 = x + rng.normal(0, 4.5), z + rng.normal(0, 4.5)
            if not p.ok_ground(x2, z2, 16) or c.deco_zone_plan[c.idx(x2, z2)]:
                continue
            if kind == "crystal":
                s = rng.uniform(0.8, 1.45)
                if not p.free(x2, z2, 1.3 * s):
                    continue
                p.put("CrystalS", x2, z2, s, fam if rng.uniform() < 0.75 else variant_crystal(p, ring), lean=False,
                      sink=0.3, radius=1.3)
            elif kind == "rocks":
                if rng.uniform() < 0.35:
                    s = rng.uniform(0.55, 0.9)
                    if not p.free(x2, z2, 1.7 * s):
                        continue
                    p.put("Boulder", x2, z2, s, int(rng.integers(0, 3)), lean=False, sink=0.25, radius=1.6, obstacle=False)
                else:
                    s = rng.uniform(0.6, 1.5)
                    if not p.free(x2, z2, 0.7 * s):
                        continue
                    p.put("Pebble", x2, z2, s, lean=False, radius=0.8, sink=0.35)
            elif kind == "noodle":
                if not p.free(x2, z2, 1.8):
                    continue
                p.put("Noodle", x2, z2, rng.uniform(0.6, 0.9), int(rng.choice(4, p=np.array(catalog.NOODLE_W) / 100)),
                      radius=1.8)
            else:
                tuft_clump(p, x2, z2, int(rng.integers(3, 6)), spread=2.5)
                n -= 2
            n -= 1
    c.feat["field_cluster"] = [{"x": x, "z": z} for x, z in centers]
    return len(centers)


def band_blocks(p: Placer, target=120):
    """Runde 1: Schicht-Brocken (6-14 Studs) an Tafelberg-Fuessen und auf dem steilen Teil der Halden, Ring A-D.
    Material/Farbe = Band des naechsten Felsens. Nur auf Hindernis-Flaeche (kostet keine Bauzone)."""
    c = p.c
    rng = p.rng
    tal = c.masks.get("talus")
    tq = np.nan_to_num(getattr(c, "talus_q", np.full(c.H.shape, 0.5)), nan=1.0)
    cand = tal & c.obstacle & (tq < 0.45) & (c.r > PLATEAU_FREE_R + 10) & (c.r < sr(1150)) & ~c.void
    iz, ix = np.nonzero(cand)
    if not len(iz):
        return 0
    sel = rng.choice(len(iz), size=min(len(iz), 6000), replace=False)
    n = 0
    for k in sel:
        if n >= target:
            break
        x, z = cell_xz(ix[k], iz[k])
        x, z = x + rng.uniform(-1.5, 1.5), z + rng.uniform(-1.5, 1.5)
        s = float(rng.uniform(0.7, 1.5))
        if p.near_obstacle(x, z, 10.0 * s) and rng.uniform() < 0.5:
            continue
        rr = int(math.ceil((4.6 * s + 5.0) / CELL))         # Deko-Zone (Radius + 5) muss auf Hindernis-Flaeche liegen
        if c.obstacle[max(0, iz[k] - rr):iz[k] + rr + 1, max(0, ix[k] - rr):ix[k] + rr + 1].mean() < 0.62:
            continue
        if not p.ok_ground(x, z, 38, allow_rock=True) or not p.free(x, z, 5.0 * s):
            continue
        key = p.rock_key[iz[k], ix[k]] if p.rock_key is not None else "Sandstone"
        key = key if key in catalog.BAND_BLOCK_MATS else "Sandstone"
        grp = p.groups["BandBlock_" + key]
        t = grp[int(rng.integers(0, len(grp)))]
        y = p.low_ground(x, z, 4.0 * s) - 0.5 * s            # am Hang auf den tiefsten Punkt setzen (nichts schwebt)
        p.put("BandBlock", x, z, s, int(rng.integers(0, 2)), tmpl=t, y=y, lean=False, radius=4.6, obstacle=True,
              rx=float(rng.uniform(-0.12, 0.12)), rz=float(rng.uniform(-0.12, 0.12)))
        n += 1
    return n


def volcano_plume(p: Placer):
    """Runde 1: Rauchfahne, Glutrand und Licht im Krater des grossen Vulkans (L5)."""
    for k, v in enumerate(f for f in p.c.feat["volcano"] if not f["small"]):
        dep = v["top"] - v["floor"]
        rc = v["Rc"]
        rf = max(rc - dep / math.tan(math.radians(24.0)), rc * 0.25)
        t = catalog.volcano_plume(k, rc, dep, rf)
        p.w.add_template(t)
        p.put("VolcanoPlume", v["x"], v["z"], 1.0, 0, y=v["floor"], yaw=0.0, lean=False, mark=False, tmpl=t, obstacle=False)


def landmarks(p: Placer):
    c = p.c
    rng = p.rng
    lm = {f["key"]: f for f in c.feat["landmark"]}
    # L8 Kristallkathedrale: Grosskristalle + Lichtstrahl
    if "L8" in lm:
        f = lm["L8"]
        y0 = p.ground(f["x"], f["z"])
        p.put("LightBeam", f["x"], f["z"], 1.0, 1, y=y0 + 10, lean=False, radius=4, yaw=0.0)
        for k in range(6):
            a = k * 1.05 + rng.uniform(-0.25, 0.25)
            rr = 6 + 14 * (k > 0)
            x, z = f["x"] + math.cos(a) * rr, f["z"] + math.sin(a) * rr
            s = 1.15 if k == 0 else rng.uniform(0.7, 1.0)
            yaw = math.atan2(x - f["x"], z - f["z"])
            p.put("CrystalG", x, z, s, [2, 4, 1][k % 3], lean=False, yaw=yaw, rx=math.radians(-12 if k else 0), sink=4.0,
                  radius=6)
        for k in range(10):
            a, rr = rng.uniform(0, 6.28), rng.uniform(24, 46)
            x, z = f["x"] + math.cos(a) * rr, f["z"] + math.sin(a) * rr
            grp = "CrystalMLit" if k < 3 else "CrystalM"
            if p.ok_ground(x, z, 34, allow_rock=True) and p.free(x, z, 3):
                p.put(grp, x, z, rng.uniform(0.8, 1.4), [2, 4, 3][k % 3], lean=False, sink=0.6, radius=3)
        isl = {"x": f["x"], "z": f["z"], "R": 60, "ring": "D"}
        scatter(p, isl, "CrystalS", 14, 1.5, var_fn=lambda: int(rng.choice([2, 4])), lean=False, rmin=0.4, max_slope=34,
                allow_rock=True)
    # L9 Titan-Spiegelturm: eisblaue Neon-Adern + Lichtstrahl
    if "L9" in lm:
        f = lm["L9"]
        g, top = f["y"], f["top"]
        hgt = top - g
        for v in range(6):
            th = v * math.pi / 3 + 0.3
            for k in range(14):
                y = g + 14 + k * (hgt - 26) / 14
                t = (y - g) / hgt
                rad = 10 + 25 * (1 - t ** (1 / 1.6))
                rad_next = 10 + 25 * (1 - min(1, t + 0.02) ** (1 / 1.6))
                slope = (rad - rad_next) / (0.02 * hgt)
                x = f["x"] + math.sin(th) * (rad + 0.4)
                z = f["z"] + math.cos(th) * (rad + 0.4)
                p.put("TitanVein", x, z, 1.0, 0, y=y, yaw=th, rx=-math.atan(slope), rz=0.08 * math.sin(k * 0.9 + v),
                      lean=False, mark=False, tmpl=_vein(p, hgt / 14))
        p.put("LightBeam", f["x"], f["z"], 1.0, 0, y=top - 2, lean=False, yaw=0.0, mark=False)
        isl = {"x": f["x"], "z": f["z"], "R": 75, "ring": "E"}
        scatter(p, isl, "CrystalTitan", 7, 2.5, var_fn=_rv(p, 2), lean=False, rmin=0.6, max_slope=34, allow_rock=True)
    # Vulkanrand: 3 Dampfquellen
    for f in c.feat["spring"]:
        if f["kind"] in ("volcano", "cone"):
            if f["kind"] == "cone" and p.count["SteamVent"] > 18:
                continue
            for _ in range(20):
                x, z = f["x"] + rng.uniform(-6, 6), f["z"] + rng.uniform(-6, 6)
                if p.free(x, z, 6):
                    p.put("SteamVent", x, z, 0.8, 0, lean=False, sink=0.8, radius=5)
                    break


_VEIN_CACHE = {}


def _vein(p, seg_len):
    key = round(seg_len, 1)
    if key not in _VEIN_CACHE:
        from .world import PartDef, Template
        t = Template(f"TitanVein_{len(_VEIN_CACHE)}", "Landmark",
                     [PartDef("Block", (1.3, seg_len * 1.04, 1.6), (0.0, 0.0, 0.0), np.eye(3), "main", "Neon",
                              transparency=0.05, cast_shadow=False)],
                     [{"main": catalog.C("#9BE8FF")}])
        _VEIN_CACHE[key] = t
        p.w.add_template(t)
    return _VEIN_CACHE[key]


def ground_mist(p: Placer, target=95):
    """Bodennebel als Akzent: Mulden, Teiche, Salzpfannen, Terrassen, Oasen, Nebelbecken, Fuss des Randgebirges.
    Nicht auf dem Plateau (r < 150) und nicht in den Washes."""
    c = p.c
    rng = p.rng
    spots = []
    for w in c.feat["water"]:
        if w["kind"].startswith("pot"):
            continue                  # Runde 1: kleine Quelltoepfe bleiben klar (Nebel wuerde sie verdecken)
        if math.hypot(w["x"], w["z"]) < RING_EDGES[2] + 20:
            continue                  # Runde 2: Teich/Quelle nahe der Basis klar (Nebel wirkte im Zielblick wie Blasen)
        spots += [(w["x"], w["z"], max(w["R"], 25), 2)]
    for f in c.feat.get("playa", []):
        spots += [(f["x"], f["z"], f["R"] * 0.8, 4)]
    for t in c.feat.get("terrace", []):
        spots += [(t["x"], t["z"], max(t["w"], t["l"]) * 0.45, 4)]
    for o in c.feat.get("oasis_c", []):
        spots += [(o["x"], o["z"], o["R"], 2)]
    for f in c.feat.get("fogbasin", []):
        spots += [(f["x"], f["z"], f["R"] * 0.7, 6)]
    for g in c.feat.get("geode", []):
        spots += [(g["x"], g["z"], g["R"], 1)]
    n = 0
    for (sx, sz, R, k) in spots:
        for _ in range(k):
            for _try in range(12):
                a, rr = rng.uniform(0, 6.28), R * math.sqrt(rng.uniform(0, 1))
                x, z = sx + math.cos(a) * rr, sz + math.sin(a) * rr
                iz, ix = c.idx(x, z)
                if math.hypot(x, z) < PLATEAU_FREE_R + 10 or c.void[iz, ix] or c.wash_dist[iz, ix] < 0 or c.slope[iz, ix] > 18:
                    continue
                y = p.ground(x, z) + rng.uniform(2, 6)
                if not np.isnan(c.wl[iz, ix]):
                    y = max(y, float(c.wl[iz, ix]) + 2.0)
                p.put("Mist", x, z, rng.uniform(0.5, 1.8), int(rng.integers(0, 2)), y=y, lean=False, mark=False)
                n += 1
                break
    # Fuss des Randgebirges (Mulden am Hang)
    for _ in range(3000):
        if n >= target:
            break
        a = rng.uniform(0, 360)
        x, z = pol(a, rng.uniform(sr(1820), sr(1900)))
        iz, ix = c.idx(x, z)
        if c.void[iz, ix] or c.slope[iz, ix] > 14 or c.wash_dist[iz, ix] < 0 or c.F[iz, ix] < 0.12:
            continue
        p.put("Mist", x, z, rng.uniform(0.9, 2.0), int(rng.integers(0, 2)), y=p.ground(x, z) + rng.uniform(3, 8), lean=False,
              mark=False)
        n += 1
    # ruhige Nebel-Partikel in den Nebelbecken
    for f in c.feat.get("fogbasin", []):
        for k in range(2):
            x, z = f["x"] + rng.uniform(-0.3, 0.3) * f["R"], f["z"] + rng.uniform(-0.3, 0.3) * f["R"]
            p.put("MistEmitter", x, z, 1.0, 0, y=p.ground(x, z) + 4, lean=False, mark=False)
    return n


def edge_extras(p: Placer):
    """Rand: Balkone, Schwebinseln (Haine), Kristalle auf Schwebfelsen, haengende Kristalle, Wolken, unsichtbare Wand."""
    c = p.c
    rng = p.rng
    for b in c.feat["balcony"]:
        isl = {"x": b["x"] * 0.995, "z": b["z"] * 0.995, "R": 22, "ring": "E"}
        tufts(p, isl, 10)
        scatter(p, isl, "CrystalS", 2, 1.5, var_fn=lambda: 1, lean=False, allow_rock=True)
    for f in c.feat["float"]:
        if f["big"]:
            isl = {"x": f["x"], "z": f["z"], "R": f["R"] * 0.7, "ring": "D"}
            grove_trees(p, isl, 6)
            scatter(p, isl, "CrystalS", 4, 1.6, var_fn=lambda: variant_crystal(p, "D"), lean=False, allow_rock=True)
        else:
            for k in range(int(rng.integers(0, 3))):
                x, z = f["x"] + rng.uniform(-0.4, 0.4) * f["R"], f["z"] + rng.uniform(-0.4, 0.4) * f["R"]
                if p.ok_ground(x, z, 30, allow_rock=True):
                    p.put("CrystalS", x, z, rng.uniform(1.0, 2.2), variant_crystal(p, "D"), lean=False, sink=0.3, radius=1.5)
    for f in c.feat["lowfloat"]:
        for k in range(int(rng.integers(0, 2)) + (1 if rng.uniform() < 0.5 else 0)):
            a = rng.uniform(0, 6.28)
            rr = f["R"] * rng.uniform(0, 0.5)
            p.put("CrystalS", f["x"] + math.cos(a) * rr, f["z"] + math.sin(a) * rr, rng.uniform(0.8, 1.5),
                  variant_crystal(p, "E"), y=f["y"], lean=False, mark=False)
    # haengende Kristalle unter der Plattform (Kopf nach unten); Runde 1: 40 -> 12 (Teile sparen)
    n = 0
    for _ in range(4000):
        if n >= 12:
            break
        a = rng.uniform(0, 360)
        r = rng.uniform(sr(1990), sr(2070))
        x, z = pol(a, r)
        iz, ix = c.idx(x, z)
        if c.void[iz, ix] or np.isnan(c.bottom[iz, ix]) or c.mask("float")[iz, ix]:
            continue
        y = float(c.bottom[iz, ix]) + 1.0
        p.put("CrystalM", x, z, rng.uniform(0.8, 1.8), variant_crystal(p, "D"), y=y, rx=math.pi + rng.uniform(-0.2, 0.2),
              lean=False, mark=False)
        n += 1
    # Wolken unter der Plattform (Runde 2: halber Radius, ~0,6 x so gross, naeher an der Unterseite)
    for k in range(12):
        a = k * 30 + rng.uniform(-10, 10)
        r = rng.uniform(sr(1700), sr(2600))
        x, z = pol(a, r)
        p.put("Cloud", x, z, rng.uniform(2.0, 4.2), 0, y=rng.uniform(-360, -230), lean=False, mark=False)
    # Nebel in den Nebelbecken
    for f in c.feat.get("fogbasin", []):
        for k in range(3):
            x, z = f["x"] + rng.uniform(-0.4, 0.4) * f["R"], f["z"] + rng.uniform(-0.4, 0.4) * f["R"]
            p.put("FogBall", x, z, rng.uniform(1.4, 2.4), 0, y=p.ground(x, z) + 5, lean=False, mark=False)
    # Unsichtbare Wand am Rand: Runde 2 32 Stuecke (je 200 breit, Abstand 197) auf r 1006 statt 64 auf r 2008
    from .terrain import RIM_R
    rb = RIM_R + 16.0
    for k in range(32):
        a = k * 360 / 32
        x, z = pol(a, rb)
        p.put("EdgeBarrier", x, z, 1.0, 0, y=-60.0, yaw=-math.radians(a), lean=False, mark=False)
