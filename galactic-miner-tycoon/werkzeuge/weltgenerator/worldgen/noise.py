"""Vectorised 2D gradient noise helpers (numpy)."""
from __future__ import annotations

import numpy as np


def _fade(t):
    return t * t * t * (t * (t * 6 - 15) + 10)


class Perlin2D:
    """Classic 2D gradient noise, roughly in [-1, 1]."""

    def __init__(self, seed: int):
        rng = np.random.default_rng(seed)
        p = rng.permutation(256).astype(np.int64)
        self.perm = np.concatenate([p, p])
        ang = rng.uniform(0.0, 2.0 * np.pi, 256)
        self.gx = np.cos(ang)
        self.gy = np.sin(ang)

    def _grad(self, ix, iy, dx, dy):
        h = self.perm[self.perm[ix] + iy]
        return self.gx[h] * dx + self.gy[h] * dy

    def __call__(self, x, y):
        x = np.asarray(x, dtype=np.float64)
        y = np.asarray(y, dtype=np.float64)
        x0 = np.floor(x)
        y0 = np.floor(y)
        xf = x - x0
        yf = y - y0
        xi = x0.astype(np.int64) & 255
        yi = y0.astype(np.int64) & 255
        n00 = self._grad(xi, yi, xf, yf)
        n10 = self._grad(xi + 1, yi, xf - 1, yf)
        n01 = self._grad(xi, yi + 1, xf, yf - 1)
        n11 = self._grad(xi + 1, yi + 1, xf - 1, yf - 1)
        u = _fade(xf)
        v = _fade(yf)
        a = n00 + u * (n10 - n00)
        b = n01 + u * (n11 - n01)
        return (a + v * (b - a)) * 1.41421356


class Noise:
    """Bundle of independent noise layers created from one seed."""

    def __init__(self, seed: int):
        self.seed = seed
        self._layers: dict[str, list[Perlin2D]] = {}

    def _get(self, name: str, octaves: int) -> list[Perlin2D]:
        layers = self._layers.get(name)
        if layers is None or len(layers) < octaves:
            base = abs(hash_str(name)) % (2**31)
            layers = [Perlin2D(self.seed * 7919 + base + k * 104729) for k in range(octaves)]
            self._layers[name] = layers
        return layers

    def perlin(self, name, x, y, scale):
        return self._get(name, 1)[0](x / scale, y / scale)

    def fbm(self, name, x, y, scale, octaves=5, lacunarity=2.0, gain=0.5):
        layers = self._get(name, octaves)
        total = np.zeros(np.broadcast(x, y).shape)
        amp = 1.0
        freq = 1.0 / scale
        norm = 0.0
        for k in range(octaves):
            total += amp * layers[k](x * freq + 17.3 * k, y * freq - 9.1 * k)
            norm += amp
            amp *= gain
            freq *= lacunarity
        return total / norm

    def ridged(self, name, x, y, scale, octaves=5, lacunarity=2.0, gain=0.5, sharpness=2.0):
        """Ridged multifractal in [0, 1] (1 = ridge)."""
        layers = self._get(name, octaves)
        total = np.zeros(np.broadcast(x, y).shape)
        amp = 1.0
        freq = 1.0 / scale
        norm = 0.0
        weight = np.ones_like(total)
        for k in range(octaves):
            n = 1.0 - np.abs(layers[k](x * freq + 31.7 * k, y * freq + 5.3 * k))
            n = n ** sharpness
            n *= weight
            weight = np.clip(n * 1.5, 0.0, 1.0)
            total += amp * n
            norm += amp
            amp *= gain
            freq *= lacunarity
        return total / norm

    def warp(self, name, x, y, scale, strength, octaves=3):
        """Domain warp: returns displaced coordinates."""
        dx = self.fbm(name + ".wx", x, y, scale, octaves)
        dy = self.fbm(name + ".wy", x + 113.0, y - 71.0, scale, octaves)
        return x + dx * strength, y + dy * strength


def hash_str(s: str) -> int:
    """Stable string hash (Python's hash() is salted per process)."""
    h = 2166136261
    for ch in s.encode("utf-8"):
        h ^= ch
        h = (h * 16777619) & 0xFFFFFFFF
    return h


def smoothstep(e0, e1, x):
    t = np.clip((np.asarray(x, dtype=np.float64) - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3 - 2 * t)
