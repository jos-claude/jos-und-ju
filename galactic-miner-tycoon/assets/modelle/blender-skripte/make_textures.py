"""Erzeugt kachelbare PBR-Texturen (Farbe, Rauheit, Metall, Normal) fuer alle Materialien.

Braucht nur numpy + Pillow:  python make_textures.py
Ausgabe: ../texturen/  (512 x 512, eine Kachel = 4 x 4 Studs)

Alle Rauschmuster entstehen per FFT und sind deshalb nahtlos kachelbar.
"""

import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gmt_materials import MATERIALS, TEX_SIZE, TEXTURED_TYPES, tex_names  # noqa: E402

N = TEX_SIZE
FY = np.fft.fftfreq(N)[:, None] * N
FX = np.fft.fftfreq(N)[None, :] * N


def band(seed, f_lo, f_hi, ax=1.0, ay=1.0):
    """Band-begrenztes Rauschen (Frequenzen in Zyklen pro Kachel), normiert."""
    r = np.random.default_rng(seed).standard_normal((N, N))
    f = np.sqrt((FX * ax) ** 2 + (FY * ay) ** 2) + 1e-6
    mid = np.sqrt(f_lo * f_hi)
    width = max(np.log(f_hi / f_lo) / 2, 0.3)
    mask = np.exp(-((np.log(f) - np.log(mid)) ** 2) / (2 * width ** 2))
    out = np.real(np.fft.ifft2(np.fft.fft2(r) * mask))
    return (out - out.mean()) / (out.std() + 1e-9)


def blur(img, sigma):
    g = np.exp(-2 * (np.pi ** 2) * (sigma ** 2) * ((FX / N) ** 2 + (FY / N) ** 2))
    return np.real(np.fft.ifft2(np.fft.fft2(img) * g))


def scratches(seed, count, length, horizontal_bias=0.0, width=0.7):
    rng = np.random.default_rng(seed)
    img = np.zeros((N, N))
    for _ in range(count):
        x0, y0 = rng.uniform(0, N, 2)
        a = rng.normal(0, 0.35) if rng.random() < horizontal_bias else rng.uniform(0, np.pi)
        L = rng.uniform(*length)
        t = np.linspace(0, 1, int(L * 3) + 2)
        bend = rng.normal(0, 0.15)
        xs = (x0 + np.cos(a + bend * t) * L * t).astype(int) % N
        ys = (y0 + np.sin(a + bend * t) * L * t).astype(int) % N
        img[ys, xs] = np.maximum(img[ys, xs], rng.uniform(0.5, 1.0))
    img = blur(img, width)
    return np.clip(img / (img.max() + 1e-9) * 2.2, 0, 1)


def smoothstep(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def hex_rgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)])


def normal_from_height(h, max_tilt_deg):
    """Normal-Map; die steilsten 2 % der Flaeche kippen um max_tilt_deg."""
    # periodische Ableitungen; Bild-Zeilen laufen nach unten (= -V)
    dx = (np.roll(h, -1, axis=1) - np.roll(h, 1, axis=1)) * 0.5
    dy = (np.roll(h, -1, axis=0) - np.roll(h, 1, axis=0)) * 0.5
    g98 = np.percentile(np.sqrt(dx ** 2 + dy ** 2), 98) + 1e-9
    strength = np.tan(np.radians(max_tilt_deg)) / g98
    nx = -dx * strength
    ny = dy * strength          # OpenGL-Konvention (+Y = oben in UV)
    nz = np.ones_like(h)
    ln = np.sqrt(nx ** 2 + ny ** 2 + nz ** 2)
    return np.stack([nx / ln, ny / ln, nz / ln], axis=-1) * 0.5 + 0.5


# ---------------------------------------------------------------------------
# Typen: liefern (Helligkeits-Modulation, Overlay-Farbe+Maske, Rauheit, Metall, Hoehe)
# ---------------------------------------------------------------------------
def type_paint():
    low = band(1, 1, 4)
    mid = band(2, 10, 40)
    fine = band(3, 90, 240)
    peel = band(4, 40, 120)
    chips = smoothstep(2.6, 3.1, band(5, 14, 40) + 0.9 * smoothstep(0.5, 1.6, band(6, 2, 6)))
    scr = scratches(7, 28, (12, 60), horizontal_bias=0.6) * 0.8
    metal_mask = np.clip(chips + 0.8 * scr, 0, 1)
    shade = 1.0 + 0.03 * mid + 0.035 * low + 0.015 * fine
    grime = 1.0 - 0.1 * smoothstep(0.5, 1.9, band(8, 1.5, 5))
    shade *= grime
    over_col = hex_rgb("#757B81")
    rough = 0.47 + 0.05 * mid + 0.03 * fine + 0.06 * (1 - grime) * 3
    rough = rough * (1 - metal_mask) + 0.3 * metal_mask
    metal = 0.22 + 0.03 * low
    metal = metal * (1 - metal_mask) + 0.95 * metal_mask
    height = 0.03 * peel - 0.9 * chips - 0.45 * scr
    return shade, (over_col, metal_mask * 0.85), rough, metal, height, 22


def type_steel():
    brushed = band(11, 60, 220, ax=14.0, ay=1.0)
    streak = band(12, 4, 20, ax=10.0, ay=1.0)
    low = band(13, 1, 4)
    dents = band(14, 6, 18)
    scr = scratches(15, 50, (10, 60), horizontal_bias=0.4, width=0.6) * 0.8
    shade = 1.0 + 0.05 * brushed + 0.04 * streak + 0.03 * low
    shade *= 1.0 - 0.1 * smoothstep(0.5, 1.8, band(16, 1.5, 5))
    over_col = hex_rgb("#C9CED2")
    rough = 0.43 + 0.04 * brushed + 0.04 * streak + 0.04 * low
    rough = rough * (1 - scr) + 0.22 * scr
    metal = 0.88 + 0.02 * low
    height = 0.02 * brushed + 0.02 * dents - 0.35 * scr
    return shade, (over_col, scr * 0.5), rough, metal, height, 14


def type_tread():
    # Riffelblech: 8 x 8 Zellen, Rauten abwechselnd +/-45 Grad
    cells = 8
    s = N // cells
    yy, xx = np.mgrid[0:N, 0:N]
    cx = (xx % s) - s / 2 + 0.5
    cy = (yy % s) - s / 2 + 0.5
    flip = ((xx // s + yy // s) % 2) * 2 - 1
    c, si = np.cos(np.pi / 4), np.sin(np.pi / 4) * flip
    u = cx * c + cy * si
    v = -cx * si + cy * c
    d = np.sqrt((u / (s * 0.42)) ** 2 + (v / (s * 0.1)) ** 2)
    bump = 1 - smoothstep(0.7, 1.0, d)
    low = band(21, 1, 4)
    scr = scratches(22, 50, (10, 50), width=0.6)
    shade = (0.9 + 0.22 * bump + 0.05 * low) * (1 - 0.12 * smoothstep(0.4, 1.6, band(23, 1.5, 5)))
    over_col = hex_rgb("#D3D7DA")
    rough = 0.45 - 0.14 * bump + 0.05 * low
    rough = rough * (1 - scr) + 0.25 * scr
    metal = 0.86 + 0.02 * low
    height = 1.0 * bump - 0.2 * scr
    return shade, (over_col, scr * 0.4), rough, metal, height, 38


def type_rubber():
    yy, xx = np.mgrid[0:N, 0:N]
    period = 32
    rib = smoothstep(0.35, 0.5, np.abs(((xx % period) / period) - 0.5))   # Querrillen
    grain = band(31, 90, 240)
    low = band(32, 1, 5)
    wear = band(33, 2, 10, ax=1.0, ay=6.0)          # Laengs-Abrieb
    shade = 0.92 + 0.07 * grain + 0.06 * low + 0.08 * smoothstep(0.8, 2.0, wear) - 0.12 * rib
    over_col = hex_rgb("#55585C")
    rough = 0.82 + 0.05 * grain - 0.08 * smoothstep(0.8, 2.0, wear)
    metal = np.zeros((N, N))
    height = -0.6 * rib + 0.03 * grain
    return shade, (over_col, np.zeros((N, N))), rough, metal, height, 28


def type_rock():
    low = band(41, 2, 6)
    mid = band(42, 10, 35)
    fine = band(43, 60, 200)
    rust = smoothstep(1.0, 1.8, band(44, 4, 14) + 0.6 * low)
    fleck = smoothstep(2.6, 3.0, band(45, 80, 200))
    shade = 1.0 + 0.1 * mid + 0.08 * low + 0.035 * fine
    over_col = hex_rgb("#9A5530")
    rough = 0.9 - 0.25 * fleck
    metal = 0.05 + 0.7 * fleck
    height = 0.5 * mid + 0.12 * fine + 0.3 * low
    return shade, (over_col, rust * 0.75), rough, metal, height, 30


TYPES = {"paint": type_paint, "steel": type_steel, "tread": type_tread,
         "rubber": type_rubber, "rock": type_rock}


def save(arr, path, mode):
    arr = np.clip(arr, 0, 1)
    img = Image.fromarray((arr * 255 + 0.5).astype(np.uint8), mode)
    if path.endswith(".jpg"):
        img.save(path, quality=90, subsampling=0)
    else:
        img.save(path, optimize=True)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.environ.get("GMT_TEX_DIR", os.path.join(os.path.dirname(here), "texturen"))
    os.makedirs(out, exist_ok=True)
    cache = {}
    for typ in TEXTURED_TYPES:
        shade, (ocol, omask), rough, metal, height, nstr = TYPES[typ]()
        cache[typ] = (shade, ocol, omask)
        names = tex_names(next(m for m, (_, t) in MATERIALS.items() if t == typ))
        save(np.clip(rough, 0.05, 1), os.path.join(out, names["rough"]), "L")
        save(np.broadcast_to(metal, (N, N)).copy(), os.path.join(out, names["metal"]), "L")
        save(normal_from_height(height, nstr), os.path.join(out, names["normal"]), "RGB")
        print("Typ", typ, "fertig")
    for mat, (hexcol, typ) in MATERIALS.items():
        if typ not in cache:
            continue
        shade, ocol, omask = cache[typ]
        base = hex_rgb(hexcol)
        col = base[None, None, :] * shade[..., None]
        if typ == "paint":
            # Abplatzer zeigen Stahl, auf dunklem Lack etwas heller
            col = col * (1 - omask[..., None]) + ocol[None, None, :] * omask[..., None]
        else:
            col = col * (1 - omask[..., None]) + (ocol[None, None, :] * 0.5 + base * 0.5) * omask[..., None]
        save(col, os.path.join(out, tex_names(mat)["color"]), "RGB")
    print("Texturen in", out)


if __name__ == "__main__":
    main()
