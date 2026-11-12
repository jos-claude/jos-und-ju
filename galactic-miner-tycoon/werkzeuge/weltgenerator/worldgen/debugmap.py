"""Schnelle Draufsicht als PNG (Schummerung x Materialfarbe), nur zum Entwickeln."""
from __future__ import annotations

import math

import numpy as np
from PIL import Image

from .materials import BAND_LUT, LAYERS, MATERIAL_COLORS
from .layout import STRATA_BASE, STRATA_PERIOD
from .world import CELL, MAT, STRATA_FLAG, TERRAIN_MATERIALS, VOID, World


def _hex(h):
    h = h.lstrip("#")
    return [int(h[i:i + 2], 16) for i in (0, 2, 4)]


def render(w: World, path, crop=None, scale=1):
    h = w.h.astype(np.float64)
    void = h <= VOID
    hh = np.where(void, np.nan, h)
    gz, gx = np.gradient(np.nan_to_num(hh, nan=-200.0), CELL)
    az, el = math.radians(250), math.radians(30)
    lx, ly, lz = -math.sin(az) * math.cos(el) * -1, math.sin(el), -(-math.cos(az)) * math.cos(el) * -1
    lx, lz = math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el)
    nx, ny, nz_ = -gx, np.ones_like(gx), -gz
    nl = np.sqrt(nx * nx + ny * ny + nz_ * nz_)
    shade = np.clip((nx * lx + ny * ly + nz_ * lz) / nl, 0, 1) * 0.75 + 0.35
    pal = np.zeros((32, 3))
    for i, name in enumerate(TERRAIN_MATERIALS):
        if name in MATERIAL_COLORS:
            pal[i] = _hex(MATERIAL_COLORS[name])
        else:
            pal[i] = (255, 0, 255)
    code = w.mat.astype(np.int64)
    st = code >= STRATA_FLAG
    ti = np.where(st, code - STRATA_FLAG, code)
    yc = np.floor((h - 0.5) / 4) * 4 + 2
    band = BAND_LUT[np.floor(yc + w.strata_off + STRATA_BASE).astype(np.int64) % STRATA_PERIOD]
    idx = np.where(st & (ti == 0), band, ti)
    col = pal[idx]
    img = col * shade[..., None]
    wat = w.water > 0
    if wat.any():
        lv = np.array([0] + list(w.water_levels))[w.water]
        vis = wat & (lv > np.ceil(h / 4) * 4)
        img[vis] = img[vis] * 0.45 + np.array(_hex("#5FE3D6")) * 0.55
    img[void] = (20, 25, 40)
    img = np.clip(img, 0, 255).astype(np.uint8)
    if crop is not None:
        x0, z0, x1, z1 = crop
        i0, i1 = int((x0 + 2304) / 4), int((x1 + 2304) / 4)
        j0, j1 = int((z0 + 2304) / 4), int((z1 + 2304) / 4)
        img = img[j0:j1, i0:i1]
    im = Image.fromarray(img)
    if scale != 1:
        im = im.resize((im.width * scale, im.height * scale), Image.NEAREST)
    im.save(path)


def render_build(w: World, build, path, deco=None):
    """Karte der Bauzonen: Gelaende gedimmt, Bauzone gruen, Deko-Zone violett, Ringe."""
    from PIL import ImageDraw
    render(w, path)
    im = Image.open(path).convert("RGB")
    a = np.asarray(im).astype(np.float64) * 0.55
    g = np.array([90, 220, 120], float)
    a[build] = a[build] * 0.35 + g * 0.65
    if deco is not None:
        a[deco] = a[deco] * 0.4 + np.array([210, 90, 220]) * 0.6
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).resize((1728, 1728), Image.NEAREST)
    d = ImageDraw.Draw(im)
    s = 1728 / 4608
    cx = cy = 864
    for r in (250, 600, 1100, 1600, 1900, 2000):
        rr = r * s
        d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), outline=(255, 255, 255), width=2)
        d.text((cx + rr * 0.71 + 4, cy - rr * 0.71), f"r {r}", fill=(255, 255, 255))
    d.text((20, 20), "Bauzonen (gruen), Deko-Zonen mit Hindernissen (violett)", fill=(255, 255, 255))
    im.save(path)
