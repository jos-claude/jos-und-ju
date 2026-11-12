"""Schnelles Rauschen mit numba (parallel). Deterministisch ueber Namen + Seed.

Funktionen arbeiten auf beliebig geformten numpy-Arrays (werden intern flach gemacht).
- fbm      : fraktales Gradientenrauschen, etwa in [-1, 1]
- ridged   : Grat-Rauschen in [0, 1] (1 = Grat)
- billow   : |Rauschen|-Summe in [0, 1]
- voronoi  : F1, F2 und Zellen-ID eines verwackelten Gitters (Basaltsaeulen, Risse)
"""
from __future__ import annotations

import numpy as np
from numba import njit, prange

from .noise import hash_str


def _tables(seed: int, name: str):
    rng = np.random.default_rng((seed * 1_000_003 + hash_str(name)) % (2**63))
    p = rng.permutation(256).astype(np.int64)
    perm = np.concatenate([p, p])
    ang = rng.uniform(0.0, 2.0 * np.pi, 256)
    return perm, np.cos(ang), np.sin(ang)


@njit(fastmath=True, cache=True, inline="always")
def _fade(t):
    return t * t * t * (t * (t * 6.0 - 15.0) + 10.0)


@njit(fastmath=True, cache=True)
def _perlin(x, y, perm, gx, gy):
    x0 = np.floor(x)
    y0 = np.floor(y)
    xf = x - x0
    yf = y - y0
    xi = int(x0) & 255
    yi = int(y0) & 255
    h00 = perm[perm[xi] + yi]
    h10 = perm[perm[xi + 1] + yi]
    h01 = perm[perm[xi] + yi + 1]
    h11 = perm[perm[xi + 1] + yi + 1]
    n00 = gx[h00] * xf + gy[h00] * yf
    n10 = gx[h10] * (xf - 1.0) + gy[h10] * yf
    n01 = gx[h01] * xf + gy[h01] * (yf - 1.0)
    n11 = gx[h11] * (xf - 1.0) + gy[h11] * (yf - 1.0)
    u = _fade(xf)
    v = _fade(yf)
    a = n00 + u * (n10 - n00)
    b = n01 + u * (n11 - n01)
    return (a + v * (b - a)) * 1.41421356


@njit(parallel=True, fastmath=True, cache=True)
def _fbm_kernel(x, y, perm, gx, gy, inv_scale, octaves, lac, gain, mode, sharp, out):
    n = x.size
    for i in prange(n):
        fx = x[i] * inv_scale
        fy = y[i] * inv_scale
        amp = 1.0
        norm = 0.0
        total = 0.0
        weight = 1.0
        for k in range(octaves):
            v = _perlin(fx + 17.31 * k, fy - 9.17 * k, perm, gx, gy)
            if mode == 0:
                total += amp * v
            elif mode == 1:
                r = 1.0 - abs(v)
                r = r ** sharp
                r *= weight
                weight = min(max(r * 1.5, 0.0), 1.0)
                total += amp * r
            else:
                total += amp * abs(v)
            norm += amp
            amp *= gain
            fx *= lac
            fy *= lac
        out[i] = total / norm


class FastNoise:
    """Wie noise.Noise, aber schnell. Ebenen werden ueber Namen unterschieden."""

    def __init__(self, seed: int):
        self.seed = seed
        self._cache: dict[str, tuple] = {}

    def _t(self, name):
        t = self._cache.get(name)
        if t is None:
            t = _tables(self.seed, name)
            self._cache[name] = t
        return t

    def _run(self, name, x, y, scale, octaves, lac, gain, mode, sharp=2.0):
        x = np.asarray(x, dtype=np.float64)
        y = np.asarray(y, dtype=np.float64)
        x, y = np.broadcast_arrays(x, y)
        shape = x.shape
        xf = np.ascontiguousarray(x).ravel()
        yf = np.ascontiguousarray(y).ravel()
        out = np.empty(xf.size)
        perm, gx, gy = self._t(name)
        _fbm_kernel(xf, yf, perm, gx, gy, 1.0 / scale, int(octaves), float(lac), float(gain), mode, float(sharp), out)
        return out.reshape(shape)

    def fbm(self, name, x, y, scale, octaves=5, lac=2.0, gain=0.5):
        return self._run(name, x, y, scale, octaves, lac, gain, 0)

    def ridged(self, name, x, y, scale, octaves=5, lac=2.0, gain=0.5, sharp=2.0):
        return self._run(name, x, y, scale, octaves, lac, gain, 1, sharp)

    def billow(self, name, x, y, scale, octaves=4, lac=2.0, gain=0.5):
        return self._run(name, x, y, scale, octaves, lac, gain, 2)

    def warp(self, name, x, y, scale, strength, octaves=3):
        dx = self.fbm(name + ".wx", x, y, scale, octaves)
        dy = self.fbm(name + ".wy", np.asarray(x) + 113.0, np.asarray(y) - 71.0, scale, octaves)
        return x + dx * strength, y + dy * strength

    def voronoi(self, name, x, y, cell, jitter=0.85):
        x = np.asarray(x, dtype=np.float64)
        y = np.asarray(y, dtype=np.float64)
        x, y = np.broadcast_arrays(x, y)
        shape = x.shape
        xf = np.ascontiguousarray(x).ravel()
        yf = np.ascontiguousarray(y).ravel()
        f1 = np.empty(xf.size)
        f2 = np.empty(xf.size)
        cid = np.empty(xf.size, np.int64)
        salt = (self.seed * 2654435761 + hash_str(name)) & 0x7FFFFFFF
        _voronoi_kernel(xf, yf, 1.0 / cell, jitter, salt, f1, f2, cid)
        return f1.reshape(shape) * cell, f2.reshape(shape) * cell, cid.reshape(shape)


@njit(fastmath=True, cache=True, inline="always")
def _hash2(ix, iy, salt):
    h = (ix * 374761393 + iy * 668265263 + salt * 2246822519) & 0xFFFFFFFF
    h = ((h ^ (h >> 13)) * 1274126177) & 0xFFFFFFFF
    h = h ^ (h >> 16)
    return h


@njit(parallel=True, fastmath=True, cache=True)
def _voronoi_kernel(x, y, inv_cell, jitter, salt, f1, f2, cid):
    n = x.size
    for i in prange(n):
        px = x[i] * inv_cell
        py = y[i] * inv_cell
        cx = int(np.floor(px))
        cy = int(np.floor(py))
        d1 = 1e9
        d2 = 1e9
        best = 0
        for oy in range(-1, 2):
            for ox in range(-1, 2):
                gx = cx + ox
                gy = cy + oy
                h = _hash2(gx, gy, salt)
                jx = ((h & 0xFFFF) / 65535.0 - 0.5) * jitter + 0.5
                jy = (((h >> 16) & 0xFFFF) / 65535.0 - 0.5) * jitter + 0.5
                dx = gx + jx - px
                dy = gy + jy - py
                d = np.sqrt(dx * dx + dy * dy)
                if d < d1:
                    d2 = d1
                    d1 = d
                    best = h
                elif d < d2:
                    d2 = d
        f1[i] = d1
        f2[i] = d2
        cid[i] = best
