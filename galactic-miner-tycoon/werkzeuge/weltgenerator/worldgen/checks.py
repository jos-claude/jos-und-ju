"""Pruefungen nach Vorgabe 2.6: Bauzonen je Ring, Flood-Fill, Wasser, Mulden, Plateau."""
from __future__ import annotations

import math

import numpy as np
from numba import njit
from scipy import ndimage as ndi

from .layout import RING_EDGES, RING_NAMES
from .world import CELL, N, VOID, World


def slope_deg(h):
    gz, gx = np.gradient(h, CELL)
    return np.degrees(np.arctan(np.hypot(gx, gz)))


def analyse(w: World, c, deco_zone=None):
    h = np.where(w.h <= VOID, np.nan, w.h.astype(np.float64))
    void = np.isnan(h)
    hf = np.nan_to_num(h, nan=-500.0)
    sl = slope_deg(hf)
    sl[void] = 90
    lv = np.array([np.nan] + list(w.water_levels))[w.water]
    wdepth = np.where(w.water > 0, lv - np.ceil(hf / 4.0) * 4.0, 0.0)
    wdepth = np.where(wdepth > 0, lv - hf, 0.0)
    obstacle = c.obstacle.copy()
    if deco_zone is not None:
        obstacle |= deco_zone
    walk = (~void) & (sl <= 25.0) & (wdepth <= 4.0)
    lab, _ = ndi.label(walk)
    cz, cx = N // 2, N // 2
    reach = lab == lab[cz, cx]
    cand = (~void) & (sl <= 6.0) & (~obstacle) & (wdepth <= 0.5)
    patch = ndi.binary_opening(cand, structure=np.ones((10, 10), bool))
    build = patch & reach
    r = c.r
    out = {"rings": {}, "build": build}
    for i, name in enumerate(RING_NAMES):
        m = (r >= RING_EDGES[i]) & (r < RING_EDGES[i + 1]) & ~(void & (r < 1900))
        m2 = (r >= RING_EDGES[i]) & (r < min(RING_EDGES[i + 1], 1880))
        out["rings"][name] = (float(build[m].mean()), float(build[m2].mean()) if name == "E" else None)
    # Wasser
    vis = wdepth > 0
    out["water_max"] = float(wdepth[vis].max()) if vis.any() else 0.0
    # Ufer: Nachbarn von Wasser ohne Wasser muessen hoeher als der Spiegel sein (Eindaemmung)
    leaks = 0
    if vis.any():
        for dz, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nb_h = np.roll(np.roll(hf, dz, 0), dx, 1)
            nb_w = np.roll(np.roll(w.water, dz, 0), dx, 1)
            leaks += int((vis & (nb_w == 0) & (nb_h < lv - 0.01)).sum())
    out["water_leaks"] = leaks
    # Mulden (Priority-Flood): Tiefe und Innenneigung
    filled = _fill_depressions(np.where(void, -500.0, hf))
    dep = filled - hf
    dep[void] = 0
    # nur kleine, lokale Senken zaehlen (das D-Becken ist absichtlich abflusslos = Salzpfannen)
    lab2, n2 = ndi.label(dep > 0.75)
    sizes = ndi.sum(np.ones_like(dep), lab2, index=np.arange(1, n2 + 1)) if n2 else np.zeros(0)
    small = np.concatenate([[False], sizes < 4000])[lab2] & (w.water == 0)
    out["depr_count"] = int(len(np.unique(lab2[small])) - (1 if 0 in lab2[small] else 0)) if small.any() else 0
    out["depr_max"] = float(dep[small].max()) if small.any() else 0.0
    out["depr_steep"] = int((small & (sl > 30)).sum())
    # Plateau
    pl = r < 150
    out["plateau_dev"] = float(np.nanmax(np.abs(h[pl] - np.nanmedian(h[pl]))))
    out["plateau_obst"] = int(obstacle[pl].sum())
    out["reach_frac"] = float(reach[(~void) & (r < 1880)].mean())
    return out


def _fill_depressions(h):
    """Priority-Flood: fuellt alle abflusslosen Senken bis zum Ueberlauf."""
    return _pflood(np.ascontiguousarray(h, dtype=np.float64))


@njit(cache=True)
def _pflood(h):
    n0, n1 = h.shape
    out = h.copy()
    done = np.zeros((n0, n1), np.bool_)
    cap = n0 * n1 + 16
    hv = np.empty(cap)
    hi = np.empty(cap, np.int64)
    size = 0
    # Rand in den Heap
    for i in range(n0):
        for j in range(n1):
            if i == 0 or j == 0 or i == n0 - 1 or j == n1 - 1 or h[i, j] <= -499.0:
                done[i, j] = True
                # push
                k = size
                size += 1
                hv[k] = out[i, j]
                hi[k] = i * n1 + j
                while k > 0:
                    p = (k - 1) // 2
                    if hv[p] <= hv[k]:
                        break
                    hv[p], hv[k] = hv[k], hv[p]
                    hi[p], hi[k] = hi[k], hi[p]
                    k = p
    while size > 0:
        v = hv[0]
        idx = hi[0]
        size -= 1
        hv[0] = hv[size]
        hi[0] = hi[size]
        k = 0
        while True:
            l = 2 * k + 1
            r = l + 1
            m = k
            if l < size and hv[l] < hv[m]:
                m = l
            if r < size and hv[r] < hv[m]:
                m = r
            if m == k:
                break
            hv[m], hv[k] = hv[k], hv[m]
            hi[m], hi[k] = hi[k], hi[m]
            k = m
        i = idx // n1
        j = idx % n1
        for di in range(-1, 2):
            for dj in range(-1, 2):
                a = i + di
                b = j + dj
                if a < 0 or b < 0 or a >= n0 or b >= n1 or done[a, b]:
                    continue
                done[a, b] = True
                if out[a, b] < v:
                    out[a, b] = v
                k = size
                size += 1
                hv[k] = out[a, b]
                hi[k] = a * n1 + b
                while k > 0:
                    p = (k - 1) // 2
                    if hv[p] <= hv[k]:
                        break
                    hv[p], hv[k] = hv[k], hv[p]
                    hi[p], hi[k] = hi[k], hi[p]
                    k = p
    return out


def report_lines(res):
    lines = ["Pruefwerte:"]
    for k, (v, v2) in res["rings"].items():
        extra = f" (bis r 1880 ohne Randgebirge: {v2 * 100:.0f} %)" if v2 is not None else ""
        lines.append(f"  Bauzone Ring {k}: {v * 100:.0f} %{extra}  {'OK' if v >= 0.6 else 'UNTER 60 %'}")
    lines.append(f"  Flood-Fill: {res['reach_frac'] * 100:.0f} % der Flaeche bis r 1880 von der Basis erreichbar (Neigung <= 25)")
    lines.append(f"  Wasser: max. Tiefe {res['water_max']:.2f} (<= 4), offene Ufer-Kanten {res['water_leaks']}")
    lines.append(f"  Lokale Mulden ohne Wasser: {res['depr_count']}, max. Tiefe {res['depr_max']:.1f}, Zellen > 30 Grad darin: {res['depr_steep']}")
    lines.append(f"  Plateau r<150: Abweichung {res['plateau_dev']:.2f}, Hindernis-Zellen {res['plateau_obst']}")
    return lines
