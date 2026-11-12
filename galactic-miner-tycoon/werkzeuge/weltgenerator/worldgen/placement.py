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
from .landforms import set_mat
from .layout import LEE_DIR, ang_diff, pol
from .noise import smoothstep as ss
from .world import CELL, MAT, World

LEE = (math.sin(math.radians(LEE_DIR)), -math.cos(math.radians(LEE_DIR)))
# Hindernis-Deko (hoeher als Kniehoehe oder mit Kollision): nur in Deko-Zonen
OBSTACLE_GROUPS = {"BalloonTree", "CrystalM", "CrystalMLit", "CrystalG", "CrystalTitan", "OrganPipe", "PearlCactus",
                   "CopperRock", "Mushroom", "SteamVent", "Lantern", "LanternLit"}


def ring_of(r):
    return "A" if r < 250 else "B" if r < 600 else "C" if r < 1100 else "D" if r < 1600 else "E"


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

    # ---------------- Gelaende-Abfragen
    def ground(self, x, z):
        c = self.c
        fx = (x + 2304.0 - 2.0) / CELL
        fz = (z + 2304.0 - 2.0) / CELL
        ix, iz = int(math.floor(fx)), int(math.floor(fz))
        tx, tz = fx - ix, fz - iz
        H = c.H
        a = H[iz, ix] * (1 - tx) + H[iz, ix + 1] * tx
        b = H[iz + 1, ix] * (1 - tx) + H[iz + 1, ix + 1] * tx
        return float(a * (1 - tz) + b * tz)

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
        if (x - sx) ** 2 + (z - sz) ** 2 < 14 ** 2:
            return False
        return True

    # ---------------- Setzen
    def put(self, group, x, z, s=1.0, variant=0, y=None, yaw=None, lean=True, rx=0.0, rz=0.0, sink=0.15,
            radius=2.0, tmpl=None, mark=True):
        t = tmpl or self.groups[group][int(self.rng.integers(0, len(self.groups[group])))]
        if y is None and group not in ("Tuft", "Pebble") and math.hypot(x, z) < 152.0 + (radius * s + 5 if group in OBSTACLE_GROUPS else 0):
            return None             # Plateau r < 150 bleibt frei (nur Bueschel und Kiesel)
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
        if group in OBSTACLE_GROUPS and y is None or group in ("BalloonTree", "CrystalG"):
            self.obstacles.append((x, z, radius * s))
        return t

    # ---------------- Inseln
    def island(self, x, z, R, theme, **kw):
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


def size_class(p):
    """Groessenklassen 5:4:1 (klein 60-80 %, mittel 100 %, gross 130-160 %)."""
    u = p.rng.uniform()
    if u < 0.5:
        return p.rng.uniform(0.6, 0.8)
    if u < 0.9:
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
        s = size_class(p) * scale
        if young < 2 and p.rng.uniform() < 0.25:
            s = p.rng.uniform(0.45, 0.55) * scale
            young += 1
        if not p.free(x, z, 4.6 * s):
            continue
        p.put("BalloonTree", x, z, s, variant_tree(p, ring), radius=4.4)
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


# ------------------------------------------------------------------ Themen
def theme_grove(p, isl, big=1.0):
    c = p.c
    ring = isl["ring"]
    F = c.F
    grove_trees(p, isl, int(round(18 * big)))
    scatter(p, isl, "Moss", int(14 * big), 5, cond=lambda iz, ix, x, z: F[iz, ix] > 0.2, var_fn=lambda: int(p.rng.choice([0, 1])),
            lean=False, sink=0.4)
    scatter(p, isl, "Noodle", int(18 * big), 2.2, cond=lambda iz, ix, x, z: 0.08 < F[iz, ix] < 0.6, rmin=0.4, rmax=1.25,
            var_fn=lambda: int(p.rng.choice(4, p=np.array(catalog.NOODLE_W) / 100)))
    scatter(p, isl, "Lantern", int(6 * big), 2.0, cond=lambda iz, ix, x, z: F[iz, ix] > 0.25, var_fn=_rv(p, 3))
    if p.lights["LanternLit"] < 40 and big >= 1.0:
        scatter(p, isl, "LanternLit", 1, 2.0, cond=lambda iz, ix, x, z: F[iz, ix] > 0.3, var_fn=_rv(p, 3))
    scatter(p, isl, "Mushroom", int(5 * big), 2.5, cond=lambda iz, ix, x, z: c.S[iz, ix] > 0.35 or F[iz, ix] > 0.55,
            var_fn=_rv(p, 4))
    tufts(p, isl, int(110 * big))
    scatter(p, isl, "Pebble", int(10 * big), 1.5, s_fn=lambda: p.rng.uniform(0.6, 1.6), var_fn=_rv(p, 6), lean=False, rmin=0.5, rmax=1.2)


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
    """Gras-Bueschel in Klumpen (5-14), keine gleichmaessige Streuung."""
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
    scatter(p, isl, "Moss", 12, 5, cond=lambda iz, ix, x, z: d[iz, ix] < 40, var_fn=lambda: int(p.rng.choice([0, 1])),
            lean=False, sink=0.4, rmax=1.2)
    tufts(p, isl, 60)


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
    scatter(p, isl, "Moss", 8, 5, var_fn=lambda: int(p.rng.choice([0, 1])), lean=False, sink=0.4)
    scatter(p, isl, "Noodle", 14, 2.2, var_fn=lambda: int(p.rng.choice(4, p=np.array(catalog.NOODLE_W) / 100)), rmin=0.3, rmax=1.3)
    tufts(p, isl, 30)


def theme_hoodoo(p, isl):
    c = p.c
    scatter(p, isl, "OrganPipe", 7, 4, cond=lambda iz, ix, x, z: c.F[iz, ix] < 0.35, var_fn=_rv(p, 3), max_slope=18)
    scatter(p, isl, "PearlCactus", 9, 3, cond=lambda iz, ix, x, z: c.F[iz, ix] < 0.25, var_fn=_rv(p, 2), max_slope=20)
    scatter(p, isl, "Noodle", 12, 2.2, var_fn=lambda: int(p.rng.choice([0, 1, 2])))
    scatter(p, isl, "Pebble", 26, 1.5, s_fn=lambda: p.rng.uniform(0.6, 1.8), var_fn=_rv(p, 6), lean=False, max_slope=30)
    scatter(p, isl, "CrystalS", 2, 2, var_fn=lambda: variant_crystal(p, "B"), lean=False)
    scatter(p, isl, "CopperRock", 2, 5, s_fn=lambda: p.rng.uniform(0.7, 1.3), var_fn=lambda: 0, lean=False)


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
    scatter(p, isl, "Moss", 14, 5, var_fn=lambda: int(p.rng.choice([0, 1])), lean=False, sink=0.4)
    scatter(p, isl, "Mushroom", 10, 2.5, var_fn=_rv(p, 4))
    scatter(p, isl, "Lantern", 12, 2.0, var_fn=_rv(p, 3))
    scatter(p, isl, "LanternLit", 2, 2.0, var_fn=_rv(p, 3))
    scatter(p, isl, "Reeds", 10, 1.6, cond=lambda iz, ix, x, z: c.d_water[iz, ix] < 9, var_fn=_rv(p, 2))
    tufts(p, isl, 40)


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
    scatter(p, isl, "Pebble", 10, 1.5, s_fn=lambda: p.rng.uniform(0.6, 1.4), var_fn=_rv(p, 6), lean=False)


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
    scatter(p, isl, "Moss", 8, 5, var_fn=lambda: 2, lean=False, sink=0.4)
    scatter(p, isl, "PearlCactus", 4, 3, var_fn=lambda: 1)
    scatter(p, isl, "Pebble", 14, 1.5, s_fn=lambda: p.rng.uniform(0.6, 1.4), var_fn=lambda: int(p.rng.choice([2, 3, 5])), lean=False)


def theme_terrace(p, isl, terr):
    c = p.c
    for f in c.feat["spring"]:
        if f["kind"] == "terrace" and f.get("group") == terr["name"]:
            for _ in range(40):
                x, z = f["x"] + p.rng.uniform(-14, 14), f["z"] + p.rng.uniform(-14, 14)
                if p.ok_ground(x, z, 14, allow_rock=True) and p.free(x, z, 7):
                    p.put("SteamVent", x, z, 1.0, 0, lean=False, sink=0.6, radius=6)
                    break
    scatter(p, isl, "Moss", 10, 5, var_fn=lambda: int(p.rng.choice([1, 2])), lean=False, sink=0.4, rmin=0.7, rmax=1.3)
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
    scatter(p, isl, "Moss", 10, 5, var_fn=lambda: 2, lean=False, sink=0.4)
    scatter(p, isl, "CrystalTitan", 4, 2.5, var_fn=_rv(p, 2), lean=False, sink=0.4)
    scatter(p, isl, "Pebble", 10, 1.5, s_fn=lambda: p.rng.uniform(0.6, 1.4), var_fn=lambda: int(p.rng.choice([2, 5])), lean=False)


def theme_ice(p, isl):
    scatter(p, isl, "CrystalTitan", 6, 2.5, s_fn=lambda: p.rng.uniform(0.7, 1.5), var_fn=_rv(p, 2), lean=False, sink=0.4,
            max_slope=30, allow_rock=True)
    scatter(p, isl, "Moss", 4, 5, var_fn=lambda: 2, lean=False, sink=0.4)


# ------------------------------------------------------------------ Planung (vor dem Finalisieren)
def plan_islands(p: Placer):
    c = p.c
    rng = p.rng
    S = c.L.slots
    lm = {f["key"]: f for f in c.feat["landmark"]}
    sx, _, sz = c.L.spawn
    # Ring A: Haupthain im Lee rechts vom Tor, Teich-Hain, Abendbank, Mesa-Fuesse
    gx, gz = pol(66, 208)
    p.island(gx, gz, 46, "grove", big=1.35, ground="grass")
    for w in c.feat["water"]:
        if w["kind"] in ("pond", "spring") or w["kind"].startswith("oasis"):
            continue
    pond = [w for w in c.feat["water"] if w["kind"] == "pond"]
    if pond:
        w0 = pond[0]
        p.island(w0["x"] + LEE[0] * 12, w0["z"] + LEE[1] * 12, w0["R"] + 40, "pond", water=w0, ground="grass")
    if "L0" in lm:
        l0 = lm["L0"]
        p.island(l0["x"] + LEE[0] * 45, l0["z"] + LEE[1] * 45, 34, "mesa_foot", ground="grass")
    for m in c.feat["mesa"]:
        rr = math.hypot(m["x"], m["z"])
        if rr < 330 and m["stage"] == "mesa" and len([i for i in p.islands if i["ring"] == "A"]) < 6:
            d = m["R"] + 26
            p.island(m["x"] + LEE[0] * d, m["z"] + LEE[1] * d, 36, "mesa_foot", ground="grass")
    # Ring B: Quellwaeldchen, Nadelgarten, Mesa-Fuesse, Zwillingstuerme
    for g in c.feat.get("grove_spring", []):
        p.island(g["x"], g["z"], 62, "spring", ground="grass")
    for k, g in enumerate(c.feat.get("hoodoo_group", [])[:4]):
        p.island(g["x"], g["z"], g["R"] + 10, "hoodoo")
    nb = 0
    for m in sorted(c.feat["mesa"], key=lambda m: -m["R"]):
        rr = math.hypot(m["x"], m["z"])
        if 300 < rr < 600 and m["stage"] == "mesa" and nb < 3:
            d = m["R"] + 30
            p.island(m["x"] + LEE[0] * d, m["z"] + LEE[1] * d, 44, "mesa_foot", ground="grass")
            nb += 1
    if "L2" in lm:
        l2 = lm["L2"]
        p.island(l2["x"] + LEE[0] * 50, l2["z"] + LEE[1] * 50, 40, "grove", big=0.8, ground="grass")
    # Ring D: Haine im Lee grosser Mesas (feuchte Fuesse)
    ndm = 0
    for m in sorted(c.feat["mesa"], key=lambda m: -m["R"]):
        rr = math.hypot(m["x"], m["z"])
        if 1150 < rr < 1550 and m["stage"] == "mesa" and ndm < 4:
            d = m["R"] + 28
            p.island(m["x"] + LEE[0] * d, m["z"] + LEE[1] * d, 42, "mesa_foot", ground="grass")
            ndm += 1
    # Ring C: Oasen, Duenen-Haine, Bogen
    for o in c.feat.get("oasis_c", []):
        p.island(o["x"], o["z"], o["R"] + 15, "oasis", ground="grass")
    if "L4" in lm:
        l4 = lm["L4"]
        p.island(l4["x"], l4["z"], 85, "dunes")
    nd = 0
    for _ in range(400):
        if nd >= 2:
            break
        a, r = rng.uniform(150, 280), rng.uniform(700, 1050)
        x, z = pol(a, r)
        iz, ix = c.idx(x, z)
        if c.mask("dune")[iz, ix] or c.wash_dist[iz, ix] < 30 or any(math.hypot(x - i["x"], z - i["z"]) < 250 for i in p.islands):
            continue
        p.island(x, z, 60, "dunes")
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
                     "cool" if math.hypot(w["x"], w["z"]) > 1600 else "grove", big=0.8, ground="grass")
    # Ring E: kuehle Haine an Nebelbecken, Eisfelder
    for f in c.feat.get("fogbasin", []):
        p.island(f["x"] + LEE[0] * f["R"] * 0.6, f["z"] + LEE[1] * f["R"] * 0.6, 50, "cool")
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
            F = c.F[sl]
            sl_ = c.slope[sl]
            g1 = inner & (q < 0.95 - 0.25 * (1 - F) + 0.2 * c.nz.fbm("grassedge", x, z, 18, 2)) & (sl_ < 16) & ~c.strata[sl]
            set_mat(c, sl, g1 & np.isnan(c.wl[sl]), "Grass")
            set_mat(c, sl, g1 & (F > 0.62) & np.isnan(c.wl[sl]), "LeafyGrass")
    dz &= c.r > 152
    c.deco_zone_plan = dz


# ------------------------------------------------------------------ Setzen (nach dem Finalisieren)
def place_all(p: Placer):
    c = p.c
    rng = p.rng
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
    base_ring(p)
    scattered(p)
    edge_extras(p)


def base_ring(p: Placer):
    """Rund um die Basis: Gras-Bueschel in Klumpen (Plateau nur locker), Kiesel, kleine Nudeln, Mini-Kristall."""
    c = p.c
    rng = p.rng
    clumps = 0
    hall = lambda x, z: abs(x) < 42 and 18 < z < 72          # Start-Halle (Jus Place) freihalten
    for _ in range(6000):
        if clumps >= 150:
            break
        a = rng.uniform(0, 360)
        r = rng.uniform(150, 265) if rng.uniform() < 0.75 else rng.uniform(40, 150)
        x, z = pol(a, r)
        if hall(x, z) or (r < 150 and rng.uniform() < 0.6):
            continue
        # Klumpen haeufen sich an Felsfuessen und in Mulden, nicht auf freier Flaeche
        iz, ix = c.idx(x, z)
        if rng.uniform() > 0.25 + 0.75 * min(1.0, float(c.F[iz, ix]) * 2.0 + float(c.masks["talus"][max(0, iz - 6):iz + 7, max(0, ix - 6):ix + 7].any())):
            continue
        if c.mask("wash")[iz, ix] and r < 250:
            continue
        tuft_clump(p, x, z, int(rng.integers(5, 13)) if r > 150 else int(rng.integers(3, 7)), spread=rng.uniform(2.5, 5.0))
        clumps += 1
    # kleine Nudeln (kniehoch) ausserhalb von r 150, in Gruppen
    for k in range(10):
        a, r = rng.uniform(0, 360), rng.uniform(165, 250)
        x0, z0 = pol(a, r)
        for j in range(int(rng.integers(2, 6))):
            x, z = x0 + rng.normal(0, 6), z0 + rng.normal(0, 6)
            if p.ok_ground(x, z, 16) and p.free(x, z, 2) and not c.mask("wash")[c.idx(x, z)]:
                p.put("Noodle", x, z, rng.uniform(0.6, 0.95), int(rng.choice(4, p=np.array(catalog.NOODLE_W) / 100)), radius=2)
    for k in range(60):
        a, r = rng.uniform(0, 360), rng.uniform(60, 250)
        x, z = pol(a, r)
        if not hall(x, z) and p.ok_ground(x, z, 20) and p.free(x, z, 1):
            p.put("Pebble", x, z, rng.uniform(0.5, 1.1), int(rng.integers(0, 6)), lean=False, radius=1)
    # Mini-Kristall links vom Tor (Wegweiser)
    for a, r in ((24, 178), (330, 205)):
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
    iz, ix = np.nonzero(tal & (c.r > 160))
    sel = rng.choice(len(iz), size=min(len(iz), 6000), replace=False)
    n = 0
    from .materials import BAND_LUT, STRATA_PERIOD
    from .layout import STRATA_BASE
    pk = {"Sandstone": 0, "Limestone": 1, "Slate": 2, "Rock": 3, "Mud": 4, "Salt": 5, "Concrete": 5}
    from .world import TERRAIN_MATERIALS
    for k in sel:
        if n >= 1500:
            break
        x = -2304 + 2 + 4 * ix[k] + rng.uniform(-2, 2)
        z = -2304 + 2 + 4 * iz[k] + rng.uniform(-2, 2)
        if not p.ok_ground(x, z, 36, allow_rock=True) or not p.free(x, z, 1.2):
            continue
        y = p.ground(x, z)
        m = TERRAIN_MATERIALS[int(BAND_LUT[int(math.floor(y + 14 + 48)) % STRATA_PERIOD])]
        v = pk.get(m, 4) if rng.uniform() < 0.85 else 4
        p.put("Pebble", x, z, rng.uniform(0.6, 1.9), v, lean=False, radius=1.0)
        n += 1
    for f in c.feat.get("fan", []):
        for k in range(30):
            x = f["x"] + rng.normal(0, 14)
            z = f["z"] + rng.normal(0, 14)
            if p.ok_ground(x, z, 30) and p.free(x, z, 1.5):
                p.put("Pebble", x, z, rng.uniform(1.0, 2.6), int(rng.integers(0, 6)), lean=False, radius=1.2)
    wb = c.masks.get("wash") & (c.wash_dist > -6) & (c.r > 260)
    iz, ix = np.nonzero(wb)
    sel = rng.choice(len(iz), size=min(len(iz), 3000), replace=False)
    n = 0
    for k in sel:
        if n >= 450:
            break
        if rng.uniform() > 0.5 + 0.5 * math.sin(ix[k] * 0.05) * math.cos(iz[k] * 0.04):
            continue
        x = -2304 + 2 + 4 * ix[k]
        z = -2304 + 2 + 4 * iz[k]
        if p.ok_ground(x, z, 30) and p.free(x, z, 1.0):
            p.put("Pebble", x, z, rng.uniform(0.5, 1.3), int(rng.integers(0, 6)), lean=False, radius=0.9)
            n += 1
    # Orgelrohre an Wash-Raendern (Ring B/C, trocken)
    n = 0
    for _ in range(3000):
        if n >= 40:
            break
        a, r = rng.uniform(0, 360), rng.uniform(320, 1050)
        x, z = pol(a, r)
        iz_, ix_ = c.idx(x, z)
        if not (6 < c.wash_dist[iz_, ix_] < 20) or c.F[iz_, ix_] > 0.3:
            continue
        if p.ok_ground(x, z, 16) and p.free(x, z, 9):
            p.put("OrganPipe", x, z, size_class(p), int(rng.integers(0, 3)), radius=4)
            n += 1
            for _ in range(int(rng.integers(2, 5))):
                x2, z2 = x + rng.uniform(-14, 14), z + rng.uniform(-14, 14)
                if p.ok_ground(x2, z2, 16) and p.free(x2, z2, 4):
                    p.put("OrganPipe", x2, z2, size_class(p) * 0.7, int(rng.integers(0, 3)), radius=4)
                    n += 1
    # Kupfer-Patina-Brocken (Ring B): an Schutthalden-Raendern, nicht in Bauzonen
    n = 0
    for _ in range(4000):
        if n >= 60:
            break
        a, r = rng.uniform(0, 360), rng.uniform(270, 600)
        x, z = pol(a, r)
        iz_, ix_ = c.idx(x, z)
        if not c.masks["talus"][iz_, ix_] and not c.deco_zone_plan[iz_, ix_]:
            continue
        if p.ok_ground(x, z, 30, allow_rock=True) and p.free(x, z, 6):
            p.put("CopperRock", x, z, rng.uniform(0.6, 1.4), 0, lean=False, sink=0.6, radius=5)
            n += 1
    # Fossilien in Steilwaenden (Mud/Sandstone-Baender, Ring B-C)
    n = 0
    walls = (c.masks.get("mesa", np.zeros_like(c.void)) & (c.slope > 55) & (c.r > 260) & (c.r < 1100))
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
            x = -2304 + 2 + 4 * j
            z = -2304 + 2 + 4 * i
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
    # Moos-Flecken und Nudel-Felder (kniehoch), feuchte Mulden
    n = 0
    for _ in range(6000):
        if n >= 90:
            break
        a, r = rng.uniform(0, 360), rng.uniform(260, 1600)
        x, z = pol(a, r)
        iz_, ix_ = c.idx(x, z)
        if c.F[iz_, ix_] < 0.35:
            continue
        if p.ok_ground(x, z, 14) and p.free(x, z, 4):
            p.put("Moss", x, z, size_class(p), int(rng.choice([0, 1, 2], p=[0.45, 0.4, 0.15])), lean=False, sink=0.4, radius=4)
            n += 1
    for fi in range(5):
        for _ in range(300):
            a, r = rng.uniform(0, 360), rng.uniform(270, 560)
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


def edge_extras(p: Placer):
    """Rand: Balkone, Schwebinseln (Haine), Kristalle auf Schwebfelsen, haengende Kristalle, Wolken, unsichtbare Wand."""
    c = p.c
    rng = p.rng
    for b in c.feat["balcony"]:
        isl = {"x": b["x"] * 0.995, "z": b["z"] * 0.995, "R": 22, "ring": "E"}
        scatter(p, isl, "Moss", 2, 4, s_fn=lambda: p.rng.uniform(0.4, 0.6), var_fn=lambda: 2, lean=False, sink=0.4, allow_rock=True)
        tufts(p, isl, 14)
        scatter(p, isl, "CrystalS", 2, 1.5, var_fn=lambda: 1, lean=False, allow_rock=True)
    for f in c.feat["float"]:
        if f["big"]:
            isl = {"x": f["x"], "z": f["z"], "R": f["R"] * 0.7, "ring": "D"}
            grove_trees(p, isl, 6)
            scatter(p, isl, "Moss", 6, 5, var_fn=_rv(p, 3), lean=False, sink=0.4, allow_rock=True)
            scatter(p, isl, "CrystalS", 4, 1.6, var_fn=lambda: variant_crystal(p, "D"), lean=False, allow_rock=True)
            tufts(p, isl, 16)
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
        p.put("Moss", f["x"], f["z"], f["R"] / 13.0, 2, y=f["y"] - 0.3, lean=False, mark=False)
    # haengende Kristalle unter der Plattform (Kopf nach unten)
    n = 0
    for _ in range(4000):
        if n >= 40:
            break
        a = rng.uniform(0, 360)
        r = rng.uniform(1990, 2070)
        x, z = pol(a, r)
        iz, ix = c.idx(x, z)
        if c.void[iz, ix] or np.isnan(c.bottom[iz, ix]) or c.mask("float")[iz, ix]:
            continue
        y = float(c.bottom[iz, ix]) + 1.0
        p.put("CrystalM", x, z, rng.uniform(0.8, 1.8), variant_crystal(p, "D"), y=y, rx=math.pi + rng.uniform(-0.2, 0.2),
              lean=False, mark=False)
        n += 1
    # Wolken unter der Plattform
    for k in range(12):
        a = k * 30 + rng.uniform(-10, 10)
        r = rng.uniform(1700, 2600)
        x, z = pol(a, r)
        p.put("Cloud", x, z, rng.uniform(3.0, 7.0), 0, y=rng.uniform(-548, -348), lean=False, mark=False)
    # Nebel in den Nebelbecken
    for f in c.feat.get("fogbasin", []):
        for k in range(3):
            x, z = f["x"] + rng.uniform(-0.4, 0.4) * f["R"], f["z"] + rng.uniform(-0.4, 0.4) * f["R"]
            p.put("FogBall", x, z, rng.uniform(1.4, 2.4), 0, y=p.ground(x, z) + 5, lean=False, mark=False)
    # Unsichtbare Wand am Rand (r 2008), 64 Stuecke
    for k in range(64):
        a = k * 360 / 64
        x, z = pol(a, 2008)
        p.put("EdgeBarrier", x, z, 1.0, 0, y=-60.0, yaw=-math.radians(a), lean=False, mark=False)
