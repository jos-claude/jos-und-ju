"""Oekologie-Karten (Vorgabe 5.1): Feuchte F, Mineral M, Schatten S, je 0..1, aus Gelaende und Wasser berechnet."""
from __future__ import annotations

import math

import numpy as np
from numba import njit, prange
from scipy import ndimage as ndi

from .ctx import Ctx
from .layout import LEE_DIR, SUN_AZ, SUN_EL
from .world import CELL, N


@njit(parallel=True, cache=True)
def _shadow(h, dx, dz, tan_el, steps, cell):
    n0, n1 = h.shape
    out = np.zeros((n0, n1), np.float32)
    for i in prange(n0):
        for j in range(n1):
            h0 = h[i, j]
            if h0 < -400:
                continue
            for k in range(1, steps):
                ii = int(i + dz * k + 0.5)
                jj = int(j + dx * k + 0.5)
                if ii < 0 or jj < 0 or ii >= n0 or jj >= n1:
                    break
                if h[ii, jj] > h0 + 1.5 + tan_el * k * cell:
                    out[i, j] = 1.0
                    break
    return out


def compute(c: Ctx):
    H = np.where(c.void, -500.0, c.H)
    # Wassernaehe: Wasserflaechen, Quellen, Becken
    water = ~np.isnan(c.wl) & ~c.void
    for f in c.feat.get("spring", []):
        iz, ix = c.idx(f["x"], f["z"])
        water[max(0, iz - 2):iz + 3, max(0, ix - 2):ix + 3] = True
    d_w = ndi.distance_transform_edt(~water) * CELL
    wnear = np.clip(1.0 - d_w / 150.0, 0, 1)
    # Muldigkeit (konkav) aus geglaetteter Hoehe
    hs = ndi.gaussian_filter(np.where(c.void, np.nanmedian(c.H), c.H), 5)
    lap = ndi.laplace(hs) / (CELL * CELL)
    conc = np.clip(lap * 60.0, 0, 1)
    # Lee: Hang schaut nach Azimut 70
    gz, gx = np.gradient(hs, CELL)
    a = math.radians(LEE_DIR)
    lee_dir = -(gx * math.sin(a) - gz * math.cos(a))
    lee = np.clip(lee_dir * 6.0, 0, 1)
    F = np.clip(0.5 * wnear + 0.3 * conc + 0.2 * lee, 0, 1)
    # Schatten: Gelaende verdeckt die Sonne (Az 250, El 22) -> Nordostseite hoher Waende
    sa = math.radians(SUN_AZ)
    sh = _shadow(H.astype(np.float64), math.sin(sa), -math.cos(sa), math.tan(math.radians(SUN_EL)), 60, CELL)
    S = np.clip(ndi.gaussian_filter(sh, 2) * 1.2 + conc * 0.3, 0, 1)
    # Mineral: Verwerfungen, Beckenraender Ring D, Mesa-Fuesse, Quellen
    fault = np.zeros((N, N), bool)
    for f in c.feat.get("fault", []):
        for t in np.linspace(-0.5, 0.5, 40):
            x = f["x"] + math.cos(f["ang"]) * f["L"] * t
            z = f["z"] + math.sin(f["ang"]) * f["L"] * t
            iz, ix = c.idx(x, z)
            fault[iz, ix] = True
    d_f = ndi.distance_transform_edt(~fault) * CELL
    tal = c.masks.get("talus", np.zeros((N, N), bool))
    d_t = ndi.distance_transform_edt(~tal) * CELL
    sp = np.zeros((N, N), bool)
    for f in c.feat.get("spring", []):
        iz, ix = c.idx(f["x"], f["z"])
        sp[iz, ix] = True
    d_s = ndi.distance_transform_edt(~sp) * CELL
    M = np.maximum.reduce([np.exp(-d_f / 45.0), 0.55 * np.exp(-d_t / 25.0) * (c.r > 300), 0.8 * np.exp(-d_s / 60.0)])
    c.F, c.M, c.S = F.astype(np.float32), M.astype(np.float32), S.astype(np.float32)
    c.wnear = wnear.astype(np.float32)
    c.d_water = d_w.astype(np.float32)
