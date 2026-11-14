"""Arbeits-Kontext des Generators: Raster, Rauschen, Masken, Merkmal-Listen."""
from __future__ import annotations

from collections import defaultdict

import numpy as np

from .fastnoise import FastNoise
from .layout import az_of, make_layout
from .world import CELL, HALF, MAT, N, World


class Ctx:
    def __init__(self, seed: int):
        self.seed = seed
        self.rng = np.random.default_rng(seed * 7_919 + 13)
        self.nz = FastNoise(seed)
        self.x, self.z = World.coords()
        self.r = np.hypot(self.x, self.z)
        self.az = az_of(self.x, self.z)
        self.L = make_layout(seed)
        self.H = np.zeros((N, N))
        self.void = np.zeros((N, N), bool)
        self.top = np.full((N, N), MAT["Ground"], np.uint8)
        self.strata = np.zeros((N, N), bool)
        self.S_local = np.zeros((N, N))           # lokale Schicht-Verschiebung (Kaemme, Wave)
        self.S_local_w = np.zeros((N, N))         # Gewicht der lokalen Verschiebung
        self.wl = np.full((N, N), np.nan)         # Wasserspiegel je Spalte
        self.bottom = np.full((N, N), np.nan)     # explizite Unterkante (Rand, Schwebfelsen)
        self.masks: dict[str, np.ndarray] = {}
        self.obstacle = np.zeros((N, N), bool)    # keine Bauzone (Landform)
        self.feat = defaultdict(list)             # Merkmale fuer Oekologie und Deko
        self.ops: list[dict] = []                 # Terrain-Zusatzformen
        self.water_levels: list[float] = []

    # ---------- Masken ----------
    def mask(self, name: str) -> np.ndarray:
        m = self.masks.get(name)
        if m is None:
            m = np.zeros((N, N), bool)
            self.masks[name] = m
        return m

    # ---------- Fenster ----------
    @staticmethod
    def win(cx: float, cz: float, rad: float):
        ix0 = max(0, int((cx - rad + HALF) // CELL))
        ix1 = min(N, int((cx + rad + HALF) // CELL) + 2)
        iz0 = max(0, int((cz - rad + HALF) // CELL))
        iz1 = min(N, int((cz + rad + HALF) // CELL) + 2)
        return (slice(iz0, iz1), slice(ix0, ix1))

    def local(self, sl):
        return self.x[sl], self.z[sl]

    def idx(self, x, z):
        ix = np.clip(((np.asarray(x) + HALF) // CELL).astype(int), 0, N - 1)
        iz = np.clip(((np.asarray(z) + HALF) // CELL).astype(int), 0, N - 1)
        return iz, ix

    def h_at(self, x, z):
        iz, ix = self.idx(x, z)
        return self.H[iz, ix]

    def slope_now(self, sl):
        h = self.H[sl]
        gz, gx = np.gradient(h, CELL)
        return np.degrees(np.arctan(np.hypot(gx, gz)))

    def stage(self, name: str):
        """Eigener Zufallsstrom je Bau-Stufe (Runde 1): Aenderungen an einer Stufe wuerfeln die spaeteren Stufen nicht
        mehr neu durch (vorher teilten sich alle Stufen c.rng). Gleicher Seed + Name -> gleiche Folge."""
        import zlib
        self.rng = np.random.default_rng([self.seed, zlib.crc32(name.encode())])
        return self.rng

    def u(self, a=0.0, b=1.0, size=None):
        return self.rng.uniform(a, b, size)

    def add_water(self, level: float) -> float:
        self.water_levels.append(float(level))
        return level
