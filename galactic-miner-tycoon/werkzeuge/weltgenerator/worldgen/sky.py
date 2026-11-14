"""Prozeduraler Himmel (Skybox) fuer Insel 1 (Vorgabe: referenz/welt-design-insel-1.md, Abschnitt 6).

Der Himmel ist eine reine Funktion der Blickrichtung. Daraus entstehen alle Ausgaben
(Roblox-Skybox, three.js-Cubemap, Equirect-Uebersicht, Perspektiv-Ansichten), damit sie
garantiert zusammenpassen.

Koordinaten wie in Roblox: x = Osten, y = oben, z = Sueden (Norden = -Z).
Azimut 0 = Norden, 90 = Osten (im Uhrzeigersinn von oben), Elevation ueber dem Horizont.

Aufbau:
- "weiche" Schicht (pro Pixel einmal): Verlauf, Horizont-Gluehen, Nebelband, Sterne, Sonnen-Glow.
  Sterne werden mit der Pixelgroesse (footprint) gefaltet -> kein Flimmern, keine Treppen.
- "harte" Schicht (Himmelskoerper): Sonne, Saturn mit Ringen, Monde, Eisriese. Nur Pixel in der
  Naehe eines Koerpers werden mit vielen Unterabtastungen (Supersampling) berechnet.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from numba import njit, prange

# ---------------------------------------------------------------------------
# Farben und Richtungen
# ---------------------------------------------------------------------------


def hex_rgb(h: str) -> np.ndarray:
    """'#RRGGBB' -> sRGB 0..1."""
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)])


def srgb_to_linear(c):
    c = np.asarray(c, dtype=np.float64)
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def linear_to_srgb(c):
    c = np.clip(np.asarray(c, dtype=np.float64), 0.0, None)
    return np.where(c <= 0.0031308, 12.92 * c, 1.055 * np.power(c, 1.0 / 2.4) - 0.055)


def hex_lin(h: str) -> np.ndarray:
    return srgb_to_linear(hex_rgb(h))


def dir_from_az_el(az_deg: float, el_deg: float) -> np.ndarray:
    a, e = math.radians(az_deg), math.radians(el_deg)
    return np.array([math.sin(a) * math.cos(e), math.sin(e), -math.cos(a) * math.cos(e)])


def az_el_from_dir(d) -> tuple[float, float]:
    d = np.asarray(d, dtype=np.float64)
    d = d / np.linalg.norm(d)
    return math.degrees(math.atan2(d[0], -d[2])) % 360.0, math.degrees(math.asin(np.clip(d[1], -1, 1)))


def normalize(v):
    v = np.asarray(v, dtype=np.float64)
    return v / np.linalg.norm(v, axis=-1, keepdims=True)


def smoothstep(e0, e1, x):
    t = np.clip((np.asarray(x, dtype=np.float64) - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def _screen_frame(c):
    """Rechts/Oben-Achsen fuer einen Betrachter, der in Richtung c schaut (Horizont waagerecht)."""
    c = normalize(c)
    r = normalize(np.cross(c, [0.0, 1.0, 0.0]))
    u = np.cross(r, c)
    return r, u


# ---------------------------------------------------------------------------
# Sonne in Roblox (Lighting:GetSunDirection)
# ---------------------------------------------------------------------------
# Formel aus zwei unabhaengigen Nachbauten des Roblox-Renderers, beide an Studio gemessen
# (Anime-Vanguards/roblox-object-renderer: "fitted to Studio samples within 1e-4";
# TabooHarmony/roblox-headless-renderer: "sampled in Studio at 6/9/12/14/18h"):
# Die Sonne laeuft auf einem Kreis um die Z-Achse, geneigt um (Breitengrad - 23,5 Grad).


def roblox_sun_direction(clock_time: float, latitude_deg: float) -> np.ndarray:
    h = (clock_time - 12.0) / 24.0 * 2.0 * math.pi
    tilt = math.radians(latitude_deg - 23.5)
    return np.array([-math.sin(h) * math.cos(tilt), math.cos(h) * math.cos(tilt), math.sin(tilt)])


def solve_roblox_sun(az_deg: float, el_deg: float) -> tuple[float, float]:
    """ClockTime und GeographicLatitude, die genau diese Sonnenrichtung ergeben."""
    d = dir_from_az_el(az_deg, el_deg)
    tilt = math.asin(d[2])
    h = math.atan2(-d[0], d[1])
    return (12.0 + h / (2.0 * math.pi) * 24.0) % 24.0, math.degrees(tilt) + 23.5


# Ziel-Sonnenrichtung (Review: Sonne hoeher fuer helleren Boden; vorher Elevation 22 Grad)
SUN_TARGET_AZ = 250.0
SUN_TARGET_EL = 30.0
# Empfohlene Lighting-Werte -> Azimut 250,00 Grad, Elevation 30,00 Grad (TimeOfDay 15:53:44)
LIGHTING_CLOCK_TIME = 15.8956
LIGHTING_LATITUDE = 40.73


# ---------------------------------------------------------------------------
# 3D-Gradientenrauschen (numba)
# ---------------------------------------------------------------------------


@njit(fastmath=True, inline="always")
def _fade(t):
    return t * t * t * (t * (t * 6.0 - 15.0) + 10.0)


@njit(fastmath=True, inline="always")
def _grad(h, x, y, z):
    h = h & 15
    u = x if h < 8 else y
    if h < 4:
        v = y
    elif h == 12 or h == 14:
        v = x
    else:
        v = z
    return (u if (h & 1) == 0 else -u) + (v if (h & 2) == 0 else -v)


@njit(fastmath=True)
def _perlin(x, y, z, perm):
    fx = math.floor(x)
    fy = math.floor(y)
    fz = math.floor(z)
    X = int(fx) & 255
    Y = int(fy) & 255
    Z = int(fz) & 255
    x -= fx
    y -= fy
    z -= fz
    u = _fade(x)
    v = _fade(y)
    w = _fade(z)
    A = perm[X] + Y
    AA = perm[A] + Z
    AB = perm[A + 1] + Z
    B = perm[X + 1] + Y
    BA = perm[B] + Z
    BB = perm[B + 1] + Z
    g000 = _grad(perm[AA], x, y, z)
    g100 = _grad(perm[BA], x - 1.0, y, z)
    g010 = _grad(perm[AB], x, y - 1.0, z)
    g110 = _grad(perm[BB], x - 1.0, y - 1.0, z)
    g001 = _grad(perm[AA + 1], x, y, z - 1.0)
    g101 = _grad(perm[BA + 1], x - 1.0, y, z - 1.0)
    g011 = _grad(perm[AB + 1], x, y - 1.0, z - 1.0)
    g111 = _grad(perm[BB + 1], x - 1.0, y - 1.0, z - 1.0)
    a = g000 + u * (g100 - g000)
    b = g010 + u * (g110 - g010)
    c = g001 + u * (g101 - g001)
    d = g011 + u * (g111 - g011)
    e = a + v * (b - a)
    f = c + v * (d - c)
    return e + w * (f - e)


@njit(parallel=True, fastmath=True)
def _fbm_kernel(p, perm, octaves, lacunarity, gain, ridged):
    n = p.shape[0]
    out = np.empty(n)
    for i in prange(n):
        x = p[i, 0]
        y = p[i, 1]
        z = p[i, 2]
        amp = 1.0
        freq = 1.0
        s = 0.0
        norm = 0.0
        for o in range(octaves):
            v = _perlin(x * freq + o * 17.13, y * freq + o * 31.71, z * freq + o * 7.77, perm)
            if ridged:
                v = 1.0 - abs(v)
                v = v * v
            s += amp * v
            norm += amp
            amp *= gain
            freq *= lacunarity
        out[i] = s / norm
    return out


class Noise3:
    """3D-fbm; Werte bei ridged=False etwa in [-0.6, 0.6] (Standardabweichung ~0.2)."""

    def __init__(self, seed: int):
        p = np.random.default_rng(seed).permutation(256).astype(np.int64)
        self.perm = np.concatenate([p, p])

    def fbm(self, pts, octaves=5, lacunarity=2.0, gain=0.5, ridged=False):
        pts = np.ascontiguousarray(pts, dtype=np.float64).reshape(-1, 3)
        return _fbm_kernel(pts, self.perm, int(octaves), float(lacunarity), float(gain), bool(ridged))


# ---------------------------------------------------------------------------
# Sterne (numba, mit Pixel-Footprint gefaltet)
# ---------------------------------------------------------------------------


@njit(parallel=True, fastmath=True)
def _stars_kernel(dirs, fp, pos, sig2, peak, rgb, starts, counts, order, G, cs, filt, out):
    n = dirs.shape[0]
    for i in prange(n):
        dx = dirs[i, 0]
        dy = dirs[i, 1]
        dz = dirs[i, 2]
        f2 = (filt * fp[i]) ** 2
        cx = min(max(int((dx + 1.0) / cs), 0), G - 1)
        cy = min(max(int((dy + 1.0) / cs), 0), G - 1)
        cz = min(max(int((dz + 1.0) / cs), 0), G - 1)
        r = 0.0
        g = 0.0
        b = 0.0
        for ix in range(max(cx - 1, 0), min(cx + 2, G)):
            for iy in range(max(cy - 1, 0), min(cy + 2, G)):
                for iz in range(max(cz - 1, 0), min(cz + 2, G)):
                    key = (ix * G + iy) * G + iz
                    st = starts[key]
                    for kk in range(st, st + counts[key]):
                        k = order[kk]
                        ex = dx - pos[k, 0]
                        ey = dy - pos[k, 1]
                        ez = dz - pos[k, 2]
                        d2 = ex * ex + ey * ey + ez * ez
                        s2 = sig2[k] + f2
                        if d2 < 12.0 * s2:
                            w = peak[k] * sig2[k] / s2 * math.exp(-0.5 * d2 / s2)
                            r += w * rgb[k, 0]
                            g += w * rgb[k, 1]
                            b += w * rgb[k, 2]
        out[i, 0] += r
        out[i, 1] += g
        out[i, 2] += b


@njit(parallel=True, fastmath=True)
def _glow_stars_kernel(dirs, fp, pos, sig2, peak, rgb, glow_amp, glow_s2, filt, out):
    """Wenige helle Sterne mit Halo: brute force ueber alle."""
    n = dirs.shape[0]
    m = pos.shape[0]
    for i in prange(n):
        f2 = (filt * fp[i]) ** 2
        r = 0.0
        g = 0.0
        b = 0.0
        for k in range(m):
            ex = dirs[i, 0] - pos[k, 0]
            ey = dirs[i, 1] - pos[k, 1]
            ez = dirs[i, 2] - pos[k, 2]
            d2 = ex * ex + ey * ey + ez * ez
            if d2 > 60.0 * glow_s2[k]:
                continue
            s2 = sig2[k] + f2
            w = peak[k] * sig2[k] / s2 * math.exp(-0.5 * d2 / s2)
            gs2 = glow_s2[k] + f2
            w += glow_amp[k] * glow_s2[k] / gs2 * math.exp(-math.sqrt(d2 / gs2) * 2.2)
            r += w * rgb[k, 0]
            g += w * rgb[k, 1]
            b += w * rgb[k, 2]
        out[i, 0] += r
        out[i, 1] += g
        out[i, 2] += b


class StarField:
    """Sterne als Liste; Abfrage ueber ein 3D-Gitter auf der Einheitskugel."""

    CELL = 0.02  # Gitterzelle (Sehne ~1,15 Grad), groesser als jeder Stern-Radius

    def __init__(self, pos, fwhm_deg, peak, rgb, glow=None):
        self.pos = np.ascontiguousarray(normalize(pos))
        sig = np.radians(np.asarray(fwhm_deg, dtype=np.float64)) / 2.3548
        self.sig2 = np.ascontiguousarray(sig ** 2)
        self.peak = np.ascontiguousarray(peak, dtype=np.float64)
        self.rgb = np.ascontiguousarray(rgb, dtype=np.float64)
        self.glow = glow
        G = int(math.ceil(2.0 / self.CELL)) + 1
        self.G = G
        c = np.clip(((self.pos + 1.0) / self.CELL).astype(np.int64), 0, G - 1)
        key = (c[:, 0] * G + c[:, 1]) * G + c[:, 2]
        self.order = np.ascontiguousarray(np.argsort(key, kind="stable"))
        counts = np.bincount(key, minlength=G ** 3)
        self.counts = counts.astype(np.int64)
        self.starts = (np.cumsum(counts) - counts).astype(np.int64)

    def eval(self, dirs, fp, filt=0.45):
        out = np.zeros((len(dirs), 3))
        dirs = np.ascontiguousarray(dirs, dtype=np.float64)
        fp = np.ascontiguousarray(fp, dtype=np.float64)
        if self.glow is None:
            _stars_kernel(dirs, fp, self.pos, self.sig2, self.peak, self.rgb, self.starts, self.counts,
                          self.order, self.G, self.CELL, filt, out)
        else:
            amp, gs = self.glow
            gs2 = np.radians(np.asarray(gs, dtype=np.float64)) ** 2
            _glow_stars_kernel(dirs, fp, self.pos, self.sig2, self.peak, self.rgb,
                               np.ascontiguousarray(amp, dtype=np.float64), gs2, filt, out)
        return out


# ---------------------------------------------------------------------------
# Himmelskoerper (harte Schicht): liefern vormultiplizierte Farbe + Deckkraft
# ---------------------------------------------------------------------------


def _ray_spheroid(o, dl, R, q):
    """Strahl (Ursprung o, Richtungen dl, lokal) gegen Rotationsellipsoid (Pol = z, z gestaucht um 1/q).
    Gibt Abstand t (inf = kein Treffer) und kleinsten Abstand b des Strahls zum Mittelpunkt (skaliert)."""
    s = np.array([1.0, 1.0, q])
    ds = dl * s
    os_ = o * s
    a = np.einsum("ij,ij->i", ds, ds)
    bb = 2.0 * (ds @ os_)
    c = os_ @ os_ - R * R
    disc = bb * bb - 4.0 * a * c
    t = np.full(len(dl), np.inf)
    hit = disc > 0.0
    t[hit] = (-bb[hit] - np.sqrt(disc[hit])) / (2.0 * a[hit])
    t[t <= 0.0] = np.inf
    tca = -(ds @ os_) / a
    closest = os_[None, :] + tca[:, None] * ds
    b = np.linalg.norm(closest, axis=1)
    b[tca <= 0.0] = np.inf
    return t, b, closest


class SunDisc:
    def __init__(self, direction, diameter_deg=2.0):
        self.c = normalize(direction)
        self.r = math.radians(diameter_deg / 2.0)
        self.core = hex_lin("#FFF1D0")
        self.rim = hex_lin("#FFE2B0")

    def cone(self):
        return self.c, self.r

    def shade(self, d):
        cosang = np.clip(d @ self.c, -1.0, 1.0)
        ang = np.arccos(cosang)
        inside = ang < self.r
        x = np.clip(ang / self.r, 0.0, 1.0)
        mu = np.sqrt(np.clip(1.0 - x * x, 0.0, 1.0))
        # Randverdunkelung: Kern weiss-golden, Rand pfirsich
        t = mu ** 0.55
        col = self.rim[None, :] * (1 - t[:, None]) + self.core[None, :] * t[:, None]
        col *= (1.35 * (0.72 + 0.28 * mu))[:, None]
        a = inside.astype(np.float64)
        return col * a[:, None], a


class Saturn:
    """Saturn als echte 3D-Kugel (leicht abgeplattet) mit Ringebene, Schatten in beide Richtungen."""

    def __init__(self, center_dir, diameter_deg, ring_opening_deg, roll_deg, light_dir, light_rgb, seed,
                 flattening=0.055):
        c = normalize(center_dir)
        self.c = c
        self.R = math.sin(math.radians(diameter_deg / 2.0))  # Abstand 1 -> Winkelradius exakt
        self.q = 1.0 / (1.0 - flattening)
        r0, u0 = _screen_frame(c)
        rho = math.radians(roll_deg)  # positiv = rechte Seite hoeher
        A = math.cos(rho) * r0 + math.sin(rho) * u0
        P = -math.sin(rho) * r0 + math.cos(rho) * u0
        B = math.radians(ring_opening_deg)
        N = normalize(math.cos(B) * P - math.sin(B) * c)  # Nordpol: Betrachter sieht von Norden
        self.M = np.stack([A, np.cross(N, A), N])  # Zeilen = lokale Achsen
        self.o = self.M @ (-c)  # Betrachter lokal (Saturn im Ursprung)
        self.L = normalize(self.M @ normalize(light_dir))
        self.light = np.asarray(light_rgb, dtype=np.float64)
        self.noise = Noise3(seed)
        self.ring_in, self.ring_out = 1.22, 2.29
        self._build_ring_profile()
        self._build_band_lut()

    # -- Ringe --------------------------------------------------------------
    def _build_ring_profile(self):
        rho = np.linspace(1.10, 2.40, 26001)
        a = np.zeros_like(rho)
        col = np.zeros((len(rho), 3))
        nz = self.noise

        def fbm1(f, octaves=4, off=0.0):
            pts = np.stack([rho * f + off, np.full_like(rho, 0.37 + off), np.full_like(rho, 0.71)], axis=1)
            return nz.fbm(pts, octaves=octaves, gain=0.55)

        n_lo = fbm1(18.0, 4, 3.1) / 0.3
        n_mid = fbm1(70.0, 4, 9.7) / 0.3
        n_hi = fbm1(230.0, 3, 21.3) / 0.3

        C_col, B_col, A_col, Cas_col = (hex_rgb(h) for h in ("#6E6A5E", "#D8C9A3", "#B9AD93", "#1A2530"))

        # C-Ring 1,24-1,53: dunkel, 40 % transparent, mit hellen Plateaus und Maxwell-Luecke
        m = (rho >= 1.24) & (rho < 1.53)
        aC = 0.6 * smoothstep(1.24, 1.275, rho)
        aC = aC * (1.0 + 0.18 * n_mid + 0.10 * n_hi)
        plateau = smoothstep(1.43, 1.435, rho) * (1 - smoothstep(1.495, 1.50, rho))
        aC = aC + 0.12 * plateau
        aC = aC * (1 - 0.85 * (np.abs(rho - 1.452) < 0.0035))
        aC = aC * (0.85 + 0.15 * smoothstep(1.30, 1.52, rho))
        a[m] = aC[m]
        cC = C_col[None, :] * (1.0 + 0.10 * n_mid[:, None] + 0.12 * plateau[:, None])
        col[m] = cC[m]

        # B-Ring 1,53-1,95: hell, fast deckend, starke Feinstruktur
        m = (rho >= 1.53) & (rho < 1.95)
        tB = (rho - 1.53) / 0.42
        aB = 0.78 + 0.18 * smoothstep(0.0, 0.35, tB)
        aB = aB * (1.0 + 0.05 * n_mid + 0.03 * n_hi)
        bB = 0.80 + 0.26 * smoothstep(0.02, 0.45, tB) - 0.05 * smoothstep(0.8, 1.0, tB)
        bB = bB * (1.0 + 0.10 * n_lo + 0.09 * n_mid + 0.06 * n_hi)
        a[m] = aB[m]
        col[m] = (B_col[None, :] * bB[:, None])[m]

        # Cassini-Teilung 1,95-2,03: fast durchsichtig, dunkel, mit Huygens-Ringlein
        m = (rho >= 1.95) & (rho < 2.03)
        aCas = 0.10 + 0.05 * n_hi
        huy = np.exp(-(((rho - 1.962) / 0.0028) ** 2))
        aCas = aCas + 0.45 * huy
        a[m] = aCas[m]
        col[m] = (Cas_col[None, :] * (1 - huy[:, None]) + C_col[None, :] * 1.25 * huy[:, None])[m]

        # A-Ring 2,03-2,27: grau-beige, nach aussen etwas dunkler, Encke-Spalt bei 2,21
        m = (rho >= 2.03) & (rho <= 2.27)
        tA = (rho - 2.03) / 0.24
        aA = 0.80 - 0.10 * tA
        aA = aA * (1.0 + 0.05 * n_mid + 0.03 * n_hi)
        aA = aA * smoothstep(2.03, 2.034, rho) * (1 - smoothstep(2.266, 2.270, rho))
        encke = np.abs(rho - 2.21) < 0.0065
        keeler = np.abs(rho - 2.258) < 0.0022
        aA = np.where(encke, 0.05, aA)
        aA = np.where(keeler, 0.25 * aA, aA)
        bA = (1.04 - 0.14 * tA) * (1.0 + 0.06 * n_lo + 0.06 * n_mid + 0.04 * n_hi)
        bA = bA * (1.0 + 0.10 * np.exp(-(((rho - 2.195) / 0.008) ** 2)))  # helle Kante innen am Encke-Spalt
        a[m] = aA[m]
        col[m] = (A_col[None, :] * bA[:, None])[m]

        a = np.clip(a, 0.0, 0.97)
        self.prof_rho = rho
        self.prof_a = a
        self.prof_col = srgb_to_linear(np.clip(col, 0, 1))
        # Optische Tiefe senkrecht (Spezifikation = Deckkraft so wie man die Ringe sieht, Oeffnung 20 Grad)
        mu_view = abs(self.o[2]) / np.linalg.norm(self.o)
        tau = -mu_view * np.log(1.0 - a)
        # Halbschatten der Sonne (2 Grad) ~ 0,015 R -> radial weichzeichnen
        k = 61
        w = np.hanning(k)
        w /= w.sum()
        self.prof_tau_blur = np.convolve(tau, w, mode="same")

    def ring_sample(self, rho):
        a = np.interp(rho, self.prof_rho, self.prof_a, left=0.0, right=0.0)
        col = np.stack([np.interp(rho, self.prof_rho, self.prof_col[:, i]) for i in range(3)], axis=1)
        return a, col

    def ring_transmission(self, rho, mu0):
        tau = np.interp(rho, self.prof_rho, self.prof_tau_blur, left=0.0, right=0.0)
        return np.exp(-tau / np.maximum(mu0, 0.05))

    # -- Wolkenbaender -----------------------------------------------------
    def _build_band_lut(self):
        Z1, Z2, B1, B2, EQ, POLE = (hex_rgb(h) for h in ("#D9C79B", "#D9C79B", "#C9AE7A", "#B89A6A", "#E6D9B5",
                                                          "#A8B5A0"))
        # (bis |Breite|, Farbe) von Aequator Richtung Pol; Norden und Sueden leicht verschieden
        north = [(6.5, EQ), (9.5, Z1), (17.0, B1), (21.0, Z2), (27.5, B2), (33.0, EQ * 0.5 + Z1 * 0.5), (40.0, B1),
                 (46.0, Z1), (52.5, B2), (59.0, B1 * 0.6 + Z1 * 0.4), (67.0, B2 * 0.5 + B1 * 0.5),
                 (72.0, B2 * 0.5 + POLE * 0.5), (90.1, POLE)]
        south = [(6.0, EQ), (9.0, Z1), (16.0, B1), (20.5, Z2), (28.0, B2), (34.0, Z1), (41.0, B1), (48.0, Z1),
                 (55.0, B2), (62.0, B1 * 0.5 + POLE * 0.5), (90.1, POLE)]
        lat = np.arange(-90.0, 90.0001, 0.05)
        col = np.zeros((len(lat), 3))
        for sign, table in ((1, north), (-1, south)):
            sel = lat * sign >= 0
            al = np.abs(lat[sel])
            out = np.zeros((sel.sum(), 3))
            lo = 0.0
            for hi, cc in table:
                m = (al >= lo) & (al < hi)
                out[m] = cc
                lo = hi
            col[sel] = out
        # weiche Uebergaenge (1,1 Grad)
        k = int(round(1.1 / 0.05 * 3))
        x = np.arange(-k, k + 1) * 0.05
        w = np.exp(-0.5 * (x / 1.1) ** 2)
        w /= w.sum()
        pad = np.concatenate([np.repeat(col[:1], k, 0), col, np.repeat(col[-1:], k, 0)])
        col = np.stack([np.convolve(pad[:, i], w, mode="valid") for i in range(3)], axis=1)
        # Kontrast etwas zuruecknehmen (Referenzbild: weiche, cremige Baender)
        mean = col[np.abs(lat) < 60].mean(axis=0)
        col = mean + (col - mean) * 0.82
        self.band_lat = lat
        self.band_col = col  # sRGB

    def _albedo(self, n_loc, p_loc):
        lat = np.degrees(np.arcsin(np.clip(n_loc[:, 2], -1, 1)))
        lon = np.arctan2(p_loc[:, 1], p_loc[:, 0])
        cl, sl = np.cos(lon), np.sin(lon)
        latr = np.radians(lat)
        nz = self.noise
        # Breiten-Verwirbelung: Bandkanten wellig
        warp = nz.fbm(np.stack([cl * 1.6 + 5.0, sl * 1.6, latr * 7.0], 1), octaves=4) * 3.2
        warp += nz.fbm(np.stack([cl * 4.0, sl * 4.0 + 2.0, latr * 22.0], 1), octaves=3) * 1.2
        latw = np.clip(lat + warp, -90, 90)
        col = np.stack([np.interp(latw, self.band_lat, self.band_col[:, i]) for i in range(3)], axis=1)
        # feine Streifen entlang der Laengengrade
        streak = nz.fbm(np.stack([cl * 3.0 + 11.0, sl * 3.0, latr * 60.0], 1), octaves=4, gain=0.6)
        col *= (1.0 + 0.10 * streak)[:, None]
        # Polar-Sechseck (Nordpol, ~78 Grad) als feine dunkle Linie
        colat = 90.0 - lat
        hex_r = 11.5 / np.cos(np.radians((np.degrees(lon) % 60.0) - 30.0))
        hexline = np.exp(-(((colat - hex_r) / 1.8) ** 2)) * (lat > 0)
        col *= (1.0 - 0.06 * hexline)[:, None]
        # ein heller Sturmfleck im noerdlichen Band
        storm_c = np.array([math.cos(0.5) * math.cos(math.radians(41.5)), math.sin(0.5) * math.cos(math.radians(41.5)),
                            math.sin(math.radians(41.5))])
        sd = np.einsum("ij,j->i", n_loc, storm_c)
        storm = np.exp(-((1.0 - sd) / 0.0009))
        col = col * (1 - 0.6 * storm[:, None]) + hex_rgb("#F2EBD5")[None, :] * 0.6 * storm[:, None]
        return srgb_to_linear(np.clip(col, 0, 1))

    # -- Zeichnen ----------------------------------------------------------
    def cone(self):
        # groesster Winkelabstand des Ringaussenrands von der Mitte (nahe Seite erscheint perspektivisch groesser)
        phi = np.linspace(0.0, 2.0 * np.pi, 1441)
        q = np.stack([np.cos(phi), np.sin(phi), np.zeros_like(phi)], 1) * (self.ring_out * self.R)
        w = normalize(q @ self.M + self.c)
        return self.c, float(np.arccos(np.clip(w @ self.c, -1, 1)).max()) + math.radians(0.3)

    def shade(self, d):
        n = len(d)
        R, q, L = self.R, self.q, self.L
        dl = d @ self.M.T
        o = self.o
        V = -dl
        rgb = np.zeros((n, 3))
        alpha = np.zeros(n)

        t_g, b, closest = _ray_spheroid(o, dl, R, q)
        hit = np.isfinite(t_g)

        # Atmosphaerischer Saum ausserhalb des Randes (nur auf der Tagseite)
        halo = (~hit) & (b < R * 1.06)
        if halo.any():
            m_dir = normalize(closest[halo] * np.array([1.0, 1.0, 1.0 / q]))
            lf = smoothstep(-0.25, 0.6, m_dir @ L)
            g = np.exp(-(b[halo] - R) / (0.010 * R)) * lf
            rgb[halo] += hex_lin("#FFE8C4")[None, :] * (0.22 * g)[:, None] * self.light

        if hit.any():
            dh = dl[hit]
            p = o[None, :] + t_g[hit][:, None] * dh
            nrm = normalize(p * np.array([1.0, 1.0, q * q]))
            mu = np.clip(np.einsum("ij,ij->i", nrm, -dh), 0.0, 1.0)
            mu0 = nrm @ L
            alb = self._albedo(nrm, p)
            # weicher Terminator (leichtes "Wrap") + maessige Randverdunkelung
            diff = np.clip((mu0 + 0.06) / 1.06, 0.0, 1.0) ** 1.12
            limb = 0.52 + 0.48 * mu ** 0.55
            # Ringschatten auf der Kugel
            T = np.ones(len(p))
            if abs(L[2]) > 1e-6:
                ts = -p[:, 2] / L[2]
                ok = ts > 0
                Qs = p[ok] + ts[ok][:, None] * L[None, :]
                rho_s = np.hypot(Qs[:, 0], Qs[:, 1]) / R
                T[ok] = self.ring_transmission(rho_s, abs(L[2]))
            # Licht wird am Terminator waermer (laengerer Weg durch die Atmosphaere)
            warm = smoothstep(-0.05, 0.35, mu0)
            tint = np.stack([np.ones_like(warm), 0.86 + 0.14 * warm, 0.70 + 0.30 * warm], 1)
            direct = alb * self.light * (1.12 * diff * limb * T)[:, None] * tint
            # Randlicht (Rim-Glow) auf der beleuchteten Seite
            rim = (1.0 - mu) ** 3.2 * smoothstep(-0.15, 0.55, mu0)
            direct += hex_lin("#FFE8C4")[None, :] * self.light * (0.30 * rim)[:, None]
            # Nachtseite: Restlicht + Ringschein (beleuchtete Nordseite der Ringe hellt Norden auf)
            ringshine = 0.030 * np.clip(nrm[:, 2], 0, 1) * (1 - diff)
            night = alb * (0.010 + ringshine)[:, None]
            rgb[hit] = direct + night
            alpha[hit] = 1.0

        # Ringe: Schnitt mit der Ebene z = 0
        dz = dl[:, 2]
        with np.errstate(divide="ignore", invalid="ignore"):
            t_r = np.where(np.abs(dz) > 1e-12, -o[2] / dz, np.inf)
        Q = o[None, :] + t_r[:, None] * dl
        rho = np.hypot(Q[:, 0], Q[:, 1]) / R
        ring = (t_r > 0) & (rho >= self.ring_in) & (rho <= self.ring_out) & (t_r < t_g)
        if ring.any():
            a, col = self.ring_sample(rho[ring])
            Qr = Q[ring]
            mu0 = abs(L[2])
            mu = np.abs(V[ring][:, 2])
            lit_face = np.sign(L[2]) == np.sign(V[ring][:, 2])
            F = np.where(lit_face, 1.38 * mu0 / (mu0 + mu), 0.6 * (1.0 - a))
            # Planetenschatten auf den Ringen (weiche Kante = Sonnenscheibe)
            sc = np.array([1.0, 1.0, q])
            Ls = L * sc
            Qs = Qr * sc
            tca = -(Qs @ Ls) / (Ls @ Ls)
            cl = Qs + tca[:, None] * Ls[None, :]
            bb = np.linalg.norm(cl, axis=1)
            sh = np.where(tca > 0, smoothstep(R * 0.985, R * 1.015, bb), 1.0)
            light = F * (sh + (1 - sh) * 0.025)
            ring_rgb = col * self.light * light[:, None]
            rgb[ring] = ring_rgb * a[:, None] + (1 - a[:, None]) * rgb[ring]
            alpha[ring] = a + (1 - a) * alpha[ring]
        return rgb, alpha


class RockyMoon:
    """Mond mit Kratern (Normalen-Stoerung) und Phase passend zur Sonne."""

    def __init__(self, center_dir, diameter_deg, light_dir, base_hex, seed, craters=55, maria=0.22, crater_depth=1.0):
        self.c = normalize(center_dir)
        self.R = math.sin(math.radians(diameter_deg / 2.0))
        r0, u0 = _screen_frame(self.c)
        rng = np.random.default_rng(seed)
        ang = rng.uniform(0, 2 * math.pi)
        ax = normalize(math.cos(ang) * r0 + math.sin(ang) * u0 + 0.3 * self.c)
        bx = normalize(np.cross(ax, self.c))
        self.M = np.stack([bx, np.cross(ax, bx), ax])
        self.o = self.M @ (-self.c)
        self.L = normalize(self.M @ normalize(light_dir))
        self.base = hex_rgb(base_hex)
        self.noise = Noise3(seed + 1)
        self.maria = maria
        self.crater_depth = crater_depth
        cc = normalize(rng.normal(size=(craters, 3)))
        rad = np.radians(2.5 + 9.0 * rng.random(craters) ** 2.2)  # viele kleine, wenige grosse
        self.cr_c, self.cr_r = cc, rad
        self.cr_alb = rng.uniform(-0.06, 0.10, craters)

    def cone(self):
        return self.c, math.asin(self.R) + math.radians(0.15)

    def shade(self, d):
        n = len(d)
        dl = d @ self.M.T
        t, b, closest = _ray_spheroid(self.o, dl, self.R, 1.0)
        hit = np.isfinite(t)
        rgb = np.zeros((n, 3))
        alpha = np.zeros(n)
        if not hit.any():
            return rgb, alpha
        p = self.o[None, :] + t[hit][:, None] * dl[hit]
        nrm = normalize(p)
        mu = np.clip(np.einsum("ij,ij->i", nrm, -dl[hit]), 1e-3, 1.0)
        nz = self.noise
        mar = nz.fbm(nrm * 1.8, octaves=4)
        alb = 1.0 - self.maria * smoothstep(-0.02, 0.18, mar)
        alb *= 1.0 + 0.08 * nz.fbm(nrm * 9.0 + 3.0, octaves=3)
        # Krater: Schuessel + Wall als Neigung der Normale
        pert = np.zeros_like(nrm)
        for c, r, al in zip(self.cr_c, self.cr_r, self.cr_alb):
            cosd = nrm @ c
            near = cosd > math.cos(r * 1.6)
            if not near.any():
                continue
            nn = nrm[near]
            ang = np.arccos(np.clip(cosd[near], -1, 1))
            x = ang / r
            tvec = c[None, :] - cosd[near][:, None] * nn
            tvec = tvec / np.maximum(np.linalg.norm(tvec, axis=1, keepdims=True), 1e-9)
            # Hoehenprofil h(x) = -exp(-(x/0.75)^4) + 0.3 exp(-((x-1)/0.25)^2): flacher Boden, weicher Wall
            g1 = np.exp(-((x / 0.75) ** 4))
            g2 = np.exp(-(((x - 1.0) / 0.25) ** 2))
            dh = g1 * 4.0 * x ** 3 / 0.75 ** 4 - 0.3 * g2 * 2.0 * (x - 1.0) / 0.25 ** 2
            pert[near] += (0.16 * self.crater_depth * dh)[:, None] * tvec
            alb[near] *= 1.0 + al * g1 + 0.05 * g2
        ns = normalize(nrm + pert)
        mu0 = ns @ self.L
        mu0_geo = nrm @ self.L
        # Mond: Mischung Lommel-Seeliger (flache Scheibe) + Lambert
        mu0c = np.clip(mu0, 0, 1)
        ls = 2.0 * mu0c / (mu0c + mu)
        bright = (0.55 * ls + 0.45 * mu0c) * smoothstep(-0.04, 0.06, mu0_geo)
        col = srgb_to_linear(np.clip(self.base[None, :] * alb[:, None], 0, 1))
        rgb[hit] = col * (1.05 * bright + 0.008)[:, None]
        alpha[hit] = 1.0
        return rgb, alpha


class IceGiant:
    """Tuerkiser Eisriese als duenne Sichel mit Vorwaertsstreu-Saum."""

    def __init__(self, center_dir, diameter_deg, light_dir, seed):
        self.c = normalize(center_dir)
        self.R = math.sin(math.radians(diameter_deg / 2.0))
        r0, u0 = _screen_frame(self.c)
        ax = normalize(math.cos(math.radians(65)) * r0 + math.sin(math.radians(65)) * u0 - 0.35 * self.c)
        bx = normalize(np.cross(ax, self.c))
        self.M = np.stack([bx, np.cross(ax, bx), ax])
        self.o = self.M @ (-self.c)
        self.L = normalize(self.M @ normalize(light_dir))
        self.noise = Noise3(seed)
        self.base = hex_rgb("#6FD0D6")
        self.rim = hex_lin("#BFF5F0")

    def cone(self):
        return self.c, math.asin(self.R * 1.12) + math.radians(0.15)

    def shade(self, d):
        n = len(d)
        R = self.R
        dl = d @ self.M.T
        t, b, closest = _ray_spheroid(self.o, dl, R, 1.0)
        hit = np.isfinite(t)
        rgb = np.zeros((n, 3))
        alpha = np.zeros(n)
        # Saum: Licht wird in der Hochatmosphaere nach vorn gestreut (Ring um die Scheibe, sonnenseitig hell)
        near = (b < R * 1.12)
        if near.any():
            m_dir = normalize(closest[near])
            lf = np.clip(m_dir @ self.L, -1, 1)
            side = 0.12 + 0.88 * smoothstep(-0.55, 0.85, lf) ** 1.5
            dist = np.abs(b[near] - R) / R
            ring = np.exp(-dist / 0.018) * side
            outside = b[near] > R
            ring = np.where(outside, ring, ring * 0.0)
            rgb[near] += self.rim[None, :] * (0.55 * ring)[:, None]
        if hit.any():
            p = self.o[None, :] + t[hit][:, None] * dl[hit]
            nrm = normalize(p)
            mu = np.clip(np.einsum("ij,ij->i", nrm, -dl[hit]), 0.0, 1.0)
            mu0 = nrm @ self.L
            lat = nrm[:, 2]
            band = 1.0 + 0.05 * np.sin(lat * 9.0 + 0.6 * self.noise.fbm(nrm * 3.0, octaves=3) * 6) \
                + 0.04 * self.noise.fbm(np.stack([nrm[:, 0] * 2, nrm[:, 1] * 2, lat * 14], 1), octaves=3)
            col = srgb_to_linear(np.clip(self.base[None, :] * band[:, None], 0, 1))
            diff = np.clip(mu0, 0, 1) ** 0.9
            limb = 0.62 + 0.38 * mu ** 0.5
            lit = col * (1.65 * diff * limb)[:, None]
            # Randlicht an der beleuchteten Kante
            rim = (1.0 - mu) ** 2.2 * smoothstep(-0.25, 0.45, mu0)
            lit += self.rim[None, :] * (0.95 * rim)[:, None]
            night = hex_lin("#07161B")[None, :] * (0.6 + 0.4 * mu)[:, None]
            rgb[hit] += lit + night * (1 - diff)[:, None]
            alpha[hit] = 1.0
        return rgb, alpha


# ---------------------------------------------------------------------------
# Der ganze Himmel
# ---------------------------------------------------------------------------


@dataclass
class SkySpec:
    """Werte aus welt-design-insel-1.md, Abschnitt 6.2 (Winkel in Grad)."""

    zenith: str = "#0A1B2C"
    horizon: str = "#1F4F5C"
    below: str = "#2A2440"
    horizon_glow: str = "#F2A07C"
    horizon_glow_alpha: float = 0.25
    horizon_glow_height: float = 6.0
    # Runde 3 (Horizont): Schimmer auf dem ganzen Kreis (vorher Az 180-320) und bis ~-8 Grad unter den Horizont, in
    # der Farbe der Atmosphaere (Lighting.Atmosphere.Color) -> kein dunkles Void-Band hinter dem Randgebirge
    horizon_glow_az: tuple = (0.0, 360.0)
    horizon_glow_below: str = "#CDB8DA"
    sun_disc_deg: float = 2.0
    sun_glow_deg: float = 12.0
    sun_glow: str = "#FFB070"
    sun_glow_alpha: float = 0.35
    saturn: tuple = (40.0, 28.0, 14.0)  # Azimut, Elevation, Kugel-Durchmesser
    saturn_ring_opening: float = 20.0
    saturn_roll: float = 14.0  # rechte Seite hoeher (Vorgabe "Roll -14 Grad, rechte Seite hoeher")
    # Saturn-Licht (Stil): Phasenwinkel 30,5 Grad = 93 % beleuchtet, Licht von links (Positionswinkel
    # auf dem Bild: 0 = rechts, 90 = oben). Die echte Sonne steht von Saturn aus gesehen 76 Grad ueber
    # der Ringebene -> es gaebe weder Ring- noch Planetenschatten. None = physikalisch.
    saturn_phase: float | None = 30.5
    saturn_light_pa: float | None = 185.0
    moon1: tuple = (14.0, 40.0, 2.0)
    moon2: tuple = (150.0, 50.0, 1.1)
    ice_giant: tuple = (300.0, 14.0, 3.0)
    cluster: tuple = (335.0, 42.0, 6.0)
    band_from_az: float = 300.0  # Nebelband: Grosskreis Az 300 El 0 -> Zenit -> Az 120 El 0
    band_width: float = 20.0
    n_small: int = 1500
    n_medium: int = 150
    n_bright: int = 25
    n_cluster: int = 150
    n_filaments: int = 40


def light_geometry(center_dir, light_dir):
    """Phasenwinkel (Grad), beleuchteter Anteil und Positionswinkel des Lichts auf dem Bild (0 = rechts, 90 = oben)."""
    c = normalize(center_dir)
    L = normalize(light_dir)
    r, u = _screen_frame(c)
    phase = math.degrees(math.acos(np.clip(L @ -c, -1, 1)))
    pa = math.degrees(math.atan2(L @ u, L @ r)) % 360.0
    return phase, (1.0 + math.cos(math.radians(phase))) / 2.0, pa


def saturn_light_dir(center_dir, sun_dir, phase_deg=None, pa_deg=None):
    """Lichtrichtung fuer das Saturnsystem: echte Sonne, oder Phase/Positionswinkel vorgegeben (Stil)."""
    c = normalize(center_dir)
    phase0, _, pa0 = light_geometry(c, sun_dir)
    phase = phase0 if phase_deg is None else phase_deg
    pa = pa0 if pa_deg is None else pa_deg
    r, u = _screen_frame(c)
    ph, ps = math.radians(phase), math.radians(pa)
    return normalize(math.cos(ph) * (-c) + math.sin(ph) * (math.cos(ps) * r + math.sin(ps) * u))


class SkyModel:
    def __init__(self, seed: int = 7, spec: SkySpec | None = None, sun_dir=None):
        self.spec = spec = spec or SkySpec()
        self.seed = seed
        rng = np.random.default_rng(seed)
        if sun_dir is None:
            sun_dir = roblox_sun_direction(LIGHTING_CLOCK_TIME, LIGHTING_LATITUDE)
        self.sun_dir = normalize(sun_dir)
        self.noise = Noise3(seed * 31 + 5)
        self.noise2 = Noise3(seed * 31 + 6)
        self.noise3 = Noise3(seed * 31 + 7)

        # Nebelband-Rahmen: e1 = Az 300 am Horizont, e2 = Zenit, nb = Normale der Ebene
        self.b_e1 = dir_from_az_el(spec.band_from_az, 0.0)
        self.b_e2 = np.array([0.0, 1.0, 0.0])
        self.b_n = normalize(np.cross(self.b_e1, self.b_e2))

        # Himmelskoerper
        sun_rgb = np.array([1.0, 0.95, 0.86])
        self.sun = SunDisc(self.sun_dir, spec.sun_disc_deg)
        sc = dir_from_az_el(spec.saturn[0], spec.saturn[1])
        self.saturn_light = L_sat = saturn_light_dir(sc, self.sun_dir, spec.saturn_phase, spec.saturn_light_pa)
        self.saturn = Saturn(sc, spec.saturn[2], spec.saturn_ring_opening, spec.saturn_roll, L_sat, sun_rgb,
                             seed + 100)
        self.moon1 = RockyMoon(dir_from_az_el(*spec.moon1[:2]), spec.moon1[2], self.sun_dir, "#A9B2C0", seed + 200,
                               craters=38, maria=0.20, crater_depth=0.55)
        self.moon2 = RockyMoon(dir_from_az_el(*spec.moon2[:2]), spec.moon2[2], self.sun_dir, "#E8D9A8", seed + 300,
                               craters=12, maria=0.10, crater_depth=0.6)
        self.ice = IceGiant(dir_from_az_el(*spec.ice_giant[:2]), spec.ice_giant[2], self.sun_dir, seed + 400)
        self.bodies = [self.sun, self.saturn, self.moon1, self.moon2, self.ice]
        self.cones = [b.cone() for b in self.bodies]

        self._make_filaments(rng)
        self._make_stars(rng)

    # -- Nebelband ---------------------------------------------------------
    def band_coords(self, d):
        a = d @ self.b_e1
        b = d @ self.b_e2
        c = d @ self.b_n
        u = np.degrees(np.arctan2(b, a))  # 0 = Az 300 am Horizont, 90 = Zenit, 180 = Az 120
        v = np.degrees(np.arcsin(np.clip(c, -1, 1)))
        return u, v

    def _band_static(self, d):
        _, v = self.band_coords(d)
        return np.exp(-0.5 * (v / (self.spec.band_width / 2.3548)) ** 2)

    def _make_filaments(self, rng):
        n = self.spec.n_filaments
        f = {}
        # Staubfaeden: ueberwiegend im sichtbaren Teil des Bandes (u -15..195), meist entlang des Bandes
        f["u"] = rng.uniform(-15.0, 195.0, n)
        f["v"] = rng.normal(0.0, 4.5, n)
        f["ang"] = np.radians(rng.normal(0.0, 12.0, n))
        f["len"] = rng.uniform(7.0, 30.0, n)
        f["w"] = rng.uniform(0.35, 1.3, n)
        f["amp"] = rng.uniform(0.30, 0.75, n)
        f["A1"] = rng.uniform(0.3, 1.4, n)
        f["k1"] = rng.uniform(0.12, 0.35, n)
        f["p1"] = rng.uniform(0, 2 * np.pi, n)
        f["seed"] = rng.uniform(0, 100, n)
        self.fil = f

    def _filament_dust(self, u, v):
        f = self.fil
        keep = np.ones_like(u)
        for i in range(len(f["u"])):
            du = (u - f["u"][i] + 180.0) % 360.0 - 180.0
            dv = v - f["v"][i]
            ca, sa = math.cos(f["ang"][i]), math.sin(f["ang"][i])
            s = du * ca + dv * sa
            half = f["len"][i] / 2.0
            near = (np.abs(s) < half) & (np.abs(-du * sa + dv * ca) < 6.0)
            if not near.any():
                continue
            s_n = s[near]
            t = -du[near] * sa + dv[near] * ca
            # sanft geschwungene Mittellinie, Breite und Dichte schwanken mit Rauschen entlang des Fadens
            off = f["A1"][i] * np.sin(f["k1"][i] * s_n + f["p1"][i])
            nn = self.noise3.fbm(np.stack([s_n * 0.18 + f["seed"][i], np.full_like(s_n, f["seed"][i]),
                                           t * 0.35], 1), octaves=3)
            w = f["w"][i] * (0.7 + 0.9 * np.clip(nn + 0.3, 0, 1))
            across = np.exp(-(((t - off - 0.6 * nn) / w) ** 2))
            taper = smoothstep(half, half * 0.35, np.abs(s_n))
            breakup = smoothstep(-0.25, 0.25, nn + 0.1)
            keep[near] *= 1.0 - f["amp"][i] * across * taper * breakup
        return 1.0 - keep

    def band_fields(self, d, el=None):
        """Felder des Nebelbands je Richtung: Profil, Wolkendichte, Magenta, Staub (alle 0..1)."""
        n = len(d)
        if el is None:
            el = np.degrees(np.arcsin(np.clip(d[:, 1], -1, 1)))
        out = {k: np.zeros(n) for k in ("prof", "dens", "mag", "dust")}
        u, v = self.band_coords(d)
        # unter dem Horizont auslaufen lassen (Dn-Flaeche nur Verlauf + Sterne)
        fade = smoothstep(-34.0, -14.0, el)
        sel = (np.abs(v) < 58.0) & (fade > 0)
        out["sel"] = sel
        if not sel.any():
            return out
        us, vs = u[sel], v[sel]
        ur = np.radians(us)
        vr = np.radians(vs)
        nz, nz2, nz3 = self.noise, self.noise2, self.noise3
        cu, su = np.cos(ur), np.sin(ur)
        # Mittellinie und Breite schwanken entlang des Bandes
        off = nz.fbm(np.stack([cu * 1.2, su * 1.2, np.full_like(cu, 3.3)], 1), octaves=3) * 8.0
        sig = (self.spec.band_width / 2.3548) * (1.0 + 0.6 * nz.fbm(np.stack([cu * 1.5, su * 1.5,
                                                                                 np.full_like(cu, 7.1)], 1), octaves=3))
        x = (vs - off) / sig
        prof = np.exp(-0.5 * x ** 2)
        wide = np.exp(-0.5 * (x / 1.9) ** 2) * smoothstep(56.0, 38.0, np.abs(vs))
        # Wolken: leicht entlang des Bandes gestreckt, Domain-Warp fuer organische Formen
        P = np.stack([cu * 3.0, su * 3.0, vr * 4.6], 1)
        wx = nz2.fbm(P * 0.9 + 1.7, octaves=3)
        wy = nz2.fbm(P * 0.9 + 9.2, octaves=3)
        Pw = P + 0.8 * np.stack([wx, wy, wx * 0.7], 1)
        c1 = nz.fbm(Pw * 1.4, octaves=6, gain=0.55)
        clouds = smoothstep(-0.30, 0.42, c1)
        knots = smoothstep(0.05, 0.45, nz3.fbm(Pw * 3.2 + 5.0, octaves=4))  # helle Sternwolken
        dens = prof ** 1.15 * (0.28 + 0.62 * clouds + 0.35 * knots * clouds)
        # Magenta-Zuege: eher an den Raendern, langgezogen
        Pm = np.stack([cu * 2.2 + 4.0, su * 2.2, vr * 6.0], 1)
        mag = smoothstep(0.05, 0.38, nz3.fbm(Pm + 0.5 * np.stack([wy, wx, wy], 1), octaves=5, gain=0.55))
        mag *= wide * (0.35 + 0.65 * (1 - prof))
        # Staub: grosse weiche Dunkelwolken in der Bandmitte + 40 einzelne Faeden
        lane_n = nz2.fbm(np.stack([cu * 4.0 + 2.0, su * 4.0, vr * 9.0], 1) + 0.6 * np.stack([wx, wy, wx], 1),
                         octaves=5, gain=0.5)
        lanes = smoothstep(0.10, 0.34, lane_n) * np.exp(-0.5 * (x / 0.85) ** 2) * 0.75
        dust_f = self._filament_dust(us, vs) * (0.4 + 0.6 * wide)
        dust = 1.0 - (1.0 - lanes) * (1.0 - dust_f)
        f = fade[sel]
        out["prof"][sel] = prof * f
        out["dens"][sel] = dens * f
        out["mag"][sel] = mag * f
        out["dust"][sel] = dust * f
        return out

    def _nebula(self, d, el):
        """Farbe (linear) und Deckkraft des Bandes sowie die Staubdichte."""
        n = len(d)
        bf = self.band_fields(d, el)
        sel = bf["sel"]
        col = np.zeros((n, 3))
        a = np.zeros(n)
        if not sel.any():
            return col, a, bf["dust"]
        dens, mag, dust = bf["dens"][sel], bf["mag"][sel], bf["dust"][sel]
        grain = 1.0 + 0.25 * self.noise3.fbm(d[sel] * 260.0, octaves=2)  # unaufgeloeste Sterne
        core = hex_lin("#5A8FA8")
        magc = hex_lin("#9B6BB8")
        a_core = np.clip(0.12 * 1.25 * dens * grain * (1.0 - 0.92 * dust), 0, 0.2)
        a_mag = np.clip(0.08 * mag * (1.0 - 0.7 * dust), 0, 0.1)
        # zwei Schichten "over" zusammenfassen
        a_tot = 1 - (1 - a_core) * (1 - a_mag)
        c_tot = core[None, :] * a_core[:, None] * (1 - a_mag[:, None]) + magc[None, :] * a_mag[:, None]
        col[sel] = c_tot / np.maximum(a_tot, 1e-9)[:, None]
        a[sel] = a_tot
        return col, a, bf["dust"]

    # -- Sterne ------------------------------------------------------------
    def _random_dirs(self, rng, n, band_boost=0.6):
        out = []
        total = 0
        while total < n:
            v = normalize(rng.normal(size=(n * 2, 3)))
            w = (1.0 + band_boost * self._band_static(v)) / (1.0 + band_boost)
            v = v[rng.random(len(v)) < w]
            out.append(v)
            total += len(v)
        return np.concatenate(out)[:n]

    def _star_colors(self, rng, n):
        pal = np.stack([hex_lin("#FFF2DC"), hex_lin("#CFE6FF"), hex_lin("#FFD6B8")])
        idx = rng.choice(3, n, p=[0.5, 0.35, 0.15])
        return pal[idx]

    def _make_stars(self, rng):
        sp = self.spec
        pos_s = self._random_dirs(rng, sp.n_small)
        fw_s = rng.uniform(0.04, 0.08, sp.n_small)
        pk_s = 0.18 + 1.1 * rng.random(sp.n_small) ** 2.6
        pos_m = self._random_dirs(rng, sp.n_medium)
        fw_m = np.full(sp.n_medium, 0.10)
        pk_m = 0.55 + 0.5 * rng.random(sp.n_medium)
        # Sternhaufen (Plummer-Verteilung, Radius ~3 Grad)
        cc = dir_from_az_el(sp.cluster[0], sp.cluster[1])
        r0, u0 = _screen_frame(cc)
        uu = rng.random(sp.n_cluster) * 0.93
        rr = 1.35 / np.sqrt(uu ** (-2.0 / 3.0) - 1.0)
        rr = np.minimum(rr, sp.cluster[2] / 2.0 * 1.15)
        th = rng.uniform(0, 2 * np.pi, sp.n_cluster)
        ox = np.radians(rr) * np.cos(th) * 1.25
        oy = np.radians(rr) * np.sin(th) * 0.85
        pos_c = normalize(cc[None, :] + ox[:, None] * r0[None, :] + oy[:, None] * u0[None, :])
        fw_c = rng.uniform(0.045, 0.10, sp.n_cluster)
        pk_c = 0.25 + 0.9 * rng.random(sp.n_cluster) ** 2.0
        pal_c = np.stack([hex_lin("#BFE6FF"), hex_lin("#FFE9C8")])
        rgb_c = pal_c[rng.choice(2, sp.n_cluster, p=[0.6, 0.4])]
        self.cluster_dir = cc
        pos = np.concatenate([pos_s, pos_m, pos_c])
        fw = np.concatenate([fw_s, fw_m, fw_c])
        pk = np.concatenate([pk_s, pk_m, pk_c])
        rgb = np.concatenate([self._star_colors(rng, sp.n_small), self._star_colors(rng, sp.n_medium), rgb_c])
        # Sternstaub: viele sehr schwache Sterne (Referenzbild wirkt dicht), im Band nach Wolkendichte
        n_dust = 4500
        pos_d = self._random_dirs(rng, n_dust, band_boost=0.6)
        fw_d = rng.uniform(0.035, 0.06, n_dust)
        pk_d = 0.06 + 0.22 * rng.random(n_dust) ** 2.0
        cand = normalize(rng.normal(size=(60000, 3)))
        bf = self.band_fields(cand)
        w = bf["dens"] * (1.0 - 0.85 * bf["dust"])
        pos_b = cand[rng.random(len(cand)) < w / max(w.max(), 1e-9)][:9000]
        nb = len(pos_b)
        fw_b = rng.uniform(0.035, 0.065, nb)
        pk_b = 0.05 + 0.25 * rng.random(nb) ** 2.2
        pos = np.concatenate([pos, pos_d, pos_b])
        fw = np.concatenate([fw, fw_d, fw_b])
        pk = np.concatenate([pk, pk_d, pk_b])
        rgb = np.concatenate([rgb, self._star_colors(rng, n_dust), self._star_colors(rng, nb)])
        self.n_band_stars = nb
        self.stars = StarField(pos, fw, pk, rgb)
        # helle Sterne mit Glow
        pos_b = self._random_dirs(rng, sp.n_bright, band_boost=0.3)
        fw_b = np.full(sp.n_bright, 0.20)
        pk_b = 1.2 + 0.8 * rng.random(sp.n_bright)
        glow_amp = 0.10 + 0.12 * rng.random(sp.n_bright)
        glow_s = np.full(sp.n_bright, 0.30)
        self.bright = StarField(pos_b, fw_b, pk_b, self._star_colors(rng, sp.n_bright), glow=(glow_amp, glow_s))

    # -- Grund-Verlauf -----------------------------------------------------
    def gradient(self, d):
        el = np.degrees(np.arcsin(np.clip(d[:, 1], -1, 1)))
        sp = self.spec
        zen, hor, bel = hex_rgb(sp.zenith), hex_rgb(sp.horizon), hex_rgb(sp.below)
        s = np.clip(np.sin(np.radians(np.maximum(el, 0.0))), 0, 1)
        t = (1.0 - s) ** 1.9
        up = zen[None, :] * (1 - t[:, None]) + hor[None, :] * t[:, None]
        # unter dem Horizont: Tuerkis -> Daemmerblau -> Violett (direkt gemischt wuerde es grau)
        mid = hex_rgb("#22364E")
        t1 = smoothstep(0.0, -5.0, el)
        t2 = smoothstep(-3.0, -13.0, el)
        low = hor[None, :] * (1 - t1[:, None]) + mid[None, :] * t1[:, None]
        low = low * (1 - t2[:, None]) + bel[None, :] * t2[:, None]
        low *= (1.0 - 0.28 * smoothstep(-12.0, -70.0, el))[:, None]
        col = np.where((el >= 0)[:, None], up, low)
        return srgb_to_linear(col), el

    def smooth(self, d, fp):
        n = len(d)
        sp = self.spec
        col, el = self.gradient(d)
        az = np.degrees(np.arctan2(d[:, 0], -d[:, 2])) % 360.0
        # sanfte grossflaechige Farbschwankung (nur ueber dem Horizont, Dn bleibt rotationssymmetrisch)
        var = self.noise3.fbm(d * 1.3 + 40.0, octaves=3)
        m = smoothstep(-20.0, -5.0, el)
        col *= (1.0 + 0.10 * var * m)[:, None]
        col[:, 2] *= 1.0 + 0.06 * self.noise2.fbm(d * 1.1 + 13.0, octaves=2) * m
        # Nebelband
        ncol, na, dust = self._nebula(d, el)
        col *= (1.0 - 0.22 * dust)[:, None]
        col = col * (1 - na[:, None]) + ncol * na[:, None]
        # Sternhaufen: schwacher Schimmer unaufgeloester Sterne
        ang_c = np.degrees(np.arccos(np.clip(d @ self.cluster_dir, -1, 1)))
        col += hex_lin("#BFE6FF")[None, :] * (0.012 * np.exp(-0.5 * (ang_c / 1.6) ** 2))[:, None]
        # Sterne (Extinktion nahe am Horizont, im Staub gedimmt)
        ext = 0.45 + 0.55 * smoothstep(-2.0, 12.0, np.abs(el))
        st = self.stars.eval(d, fp) + self.bright.eval(d, fp)
        col += st * (ext * (1.0 - 0.65 * dust))[:, None]
        # Horizont-Gluehen (Pfirsich) zwischen Az 180 und 320
        a0, a1 = sp.horizon_glow_az
        if a1 - a0 >= 360.0:
            w_az = np.ones_like(az)
        else:
            w_az = smoothstep(a0, a0 + 30.0, az) * (1 - smoothstep(a1 - 30.0, a1, az))
        sun_az = az_el_from_dir(self.sun_dir)[0]
        daz = np.abs((az - sun_az + 180.0) % 360.0 - 180.0)
        w_az = w_az * (0.75 + 0.25 * np.exp(-(daz / 35.0) ** 2))
        h = sp.horizon_glow_height
        e = el - 0.6
        # unter dem Horizont: kraeftiger (bis 2,2-fach), haelt bis -4 Grad und laeuft bis -14 Grad aus (-8: ~0,36)
        w_el = np.where(e >= 0, np.exp(-e / (h * 0.40)) * (0.82 + 0.18 * np.exp(-e / 0.8)),
                        (1.0 + 1.2 * smoothstep(0.0, -3.0, e)) * (1.0 - smoothstep(-4.0, -14.0, e)))
        ga = np.clip(sp.horizon_glow_alpha * w_az * w_el, 0.0, 0.9)
        tb = smoothstep(0.0, -4.0, e)[:, None]
        glow = hex_lin(sp.horizon_glow)[None, :] * (1 - tb) + hex_lin(sp.horizon_glow_below)[None, :] * tb
        col = col * (1 - ga[:, None]) + glow * ga[:, None]
        # Sonnen-Glow bis 12 Grad (+ breiter, sehr schwacher Hof)
        ang_s = np.degrees(np.arccos(np.clip(d @ self.sun_dir, -1, 1)))
        r = sp.sun_disc_deg / 2.0
        x = np.clip(np.maximum(ang_s - r, 0.0) / (sp.sun_glow_deg - r), 0, 1)
        p = (0.65 * np.exp(-4.2 * x) + 0.35 * np.exp(-1.6 * x)) * (1 - x * x) ** 2
        ga = sp.sun_glow_alpha * p
        col = col * (1 - ga[:, None]) + hex_lin(sp.sun_glow)[None, :] * ga[:, None]
        col += hex_lin("#FFB070")[None, :] * (0.05 * np.exp(-ang_s / 9.0))[:, None]
        col += hex_lin("#FFE2B0")[None, :] * (0.55 * np.exp(-np.maximum(ang_s - r, 0.0) / 0.45))[:, None]
        return col

    # -- Himmelskoerper ----------------------------------------------------
    def bodies_mask(self, d, fp):
        m = np.zeros(len(d), dtype=bool)
        for c, r in self.cones:
            m |= d @ c > np.cos(r + 2.0 * fp)
        return m

    def bodies_shade(self, d):
        rgb = np.zeros((len(d), 3))
        a = np.zeros(len(d))
        for b, (c, r) in zip(self.bodies, self.cones):
            sel = d @ c > math.cos(r)
            if sel.any():
                cr, ca = b.shade(d[sel])
                rgb[sel] = cr + (1 - ca[:, None]) * rgb[sel]
                a[sel] = ca + (1 - ca) * a[sel]
        return rgb, a

    def airlight(self, d):
        """Ein Hauch Himmelsfarbe ueber den Koerpern (sie stehen 'im' Himmel, nicht davor geklebt)."""
        g, el = self.gradient(d)
        trans = 0.90 + 0.08 * smoothstep(5.0, 60.0, el)
        return g * 0.30, trans

    # -- Pixel -------------------------------------------------------------
    def shade_pixels(self, d, fp, sub_dirs, ss=4, rng=None):
        """d: Pixelmitten, fp: Pixelgroesse (rad), sub_dirs(idx, ox, oy) -> Richtungen fuer Unterabtastung."""
        col = self.smooth(d, fp)
        mask = self.bodies_mask(d, fp)
        idx = np.nonzero(mask)[0]
        if len(idx):
            rng = rng or np.random.default_rng(0)
            acc = np.zeros((len(idx), 3))
            acc_a = np.zeros(len(idx))
            for i in range(ss):
                for j in range(ss):
                    jx = rng.random(len(idx))
                    jy = rng.random(len(idx))
                    ox = (i + jx) / ss - 0.5
                    oy = (j + jy) / ss - 0.5
                    ds = sub_dirs(idx, ox, oy)
                    r, a = self.bodies_shade(ds)
                    acc += r
                    acc_a += a
            acc /= ss * ss
            acc_a /= ss * ss
            air, trans = self.airlight(d[idx])
            col[idx] = acc * trans[:, None] + acc_a[:, None] * air + (1 - acc_a[:, None]) * col[idx]
        return col

    def radiance(self, d, fp=None):
        """Einzelne Richtungen ohne Supersampling (z. B. fuer Tests)."""
        d = normalize(d)
        if fp is None:
            fp = np.full(len(d), math.radians(0.05))
        col = self.smooth(d, fp)
        r, a = self.bodies_shade(d)
        air, trans = self.airlight(d)
        return r * trans[:, None] + a[:, None] * air + (1 - a[:, None]) * col


# ---------------------------------------------------------------------------
# Projektionen: Pixel (x nach rechts, y nach unten, Mitte bei i + 0,5) -> Richtung
# ---------------------------------------------------------------------------

# Roblox-Skybox (gemessen in Studio, siehe assets/himmel/README.md):
# Ft = -Z, Bk = +Z, Lf = +X, Rt = -X, jeweils aufrecht von innen gesehen;
# Up/Dn um eine Vierteldrehung: auf Up zeigt "rechts" nach -Z und "unten" nach -X,
# auf Dn zeigt "rechts" nach -Z und "unten" nach +X.
ROBLOX_FACES = {
    "Bk": lambda u, v: (-u, -v, np.ones_like(u)),
    "Dn": lambda u, v: (v, -np.ones_like(u), -u),
    "Ft": lambda u, v: (u, -v, -np.ones_like(u)),
    "Lf": lambda u, v: (np.ones_like(u), -v, u),
    "Rt": lambda u, v: (-np.ones_like(u), -v, -u),
    "Up": lambda u, v: (-v, np.ones_like(u), -u),
}


def roblox_lookup(d):
    """Umkehrung: Richtung -> (Flaeche, u, v) wie Roblox die Skybox abtastet."""
    d = np.asarray(d, dtype=np.float64)
    ax, ay, az = (np.maximum(np.abs(d[:, i]), 1e-300) for i in range(3))
    face = np.empty(len(d), dtype=object)
    u = np.zeros(len(d))
    v = np.zeros(len(d))
    mx = (ax >= ay) & (ax >= az)
    my = ~mx & (ay >= az)
    mz = ~mx & ~my
    for m, name, uu, vv in (
        (mx & (d[:, 0] > 0), "Lf", d[:, 2] / ax, -d[:, 1] / ax),
        (mx & (d[:, 0] <= 0), "Rt", -d[:, 2] / ax, -d[:, 1] / ax),
        (my & (d[:, 1] > 0), "Up", -d[:, 2] / ay, -d[:, 0] / ay),
        (my & (d[:, 1] <= 0), "Dn", -d[:, 2] / ay, d[:, 0] / ay),
        (mz & (d[:, 2] > 0), "Bk", -d[:, 0] / az, -d[:, 1] / az),
        (mz & (d[:, 2] <= 0), "Ft", d[:, 0] / az, -d[:, 1] / az),
    ):
        face[m] = name
        u[m] = uu[m]
        v[m] = vv[m]
    return face, u, v


# three.js (CubeTextureLoader-Reihenfolge px, nx, py, ny, pz, nz). three.js tastet CubeTextures
# fuer scene.background/envMap mit gespiegeltem x ab (WebGLBackground: Matrix diag(-1, 1, 1)).
# Die Bilder sind so erzeugt, dass die Weltrichtungen (Roblox-Koordinaten = three.js-Welt) stimmen.
def _gl_face(face, sc, tc):
    one = np.ones_like(sc)
    return {
        "px": (one, -tc, -sc),
        "nx": (-one, -tc, sc),
        "py": (sc, one, tc),
        "ny": (sc, -one, -tc),
        "pz": (sc, -tc, one),
        "nz": (-sc, -tc, -one),
    }[face]


THREE_FACES = {
    f: (lambda u, v, f=f: (lambda r: (-r[0], r[1], r[2]))(_gl_face(f, u, v)))
    for f in ("px", "nx", "py", "ny", "pz", "nz")
}


def threejs_lookup(d):
    """So wie three.js die CubeTexture abtastet (zum Pruefen): Richtung -> (Flaeche, s, t in [-1,1])."""
    r = np.asarray(d, dtype=np.float64).copy()
    r[:, 0] *= -1.0
    ax, ay, az = (np.maximum(np.abs(r[:, i]), 1e-300) for i in range(3))
    face = np.empty(len(r), dtype=object)
    s = np.zeros(len(r))
    t = np.zeros(len(r))
    mx = (ax >= ay) & (ax >= az)
    my = ~mx & (ay >= az)
    mz = ~mx & ~my
    for m, name, ss, tt in (
        (mx & (r[:, 0] > 0), "px", -r[:, 2] / ax, -r[:, 1] / ax),
        (mx & (r[:, 0] <= 0), "nx", r[:, 2] / ax, -r[:, 1] / ax),
        (my & (r[:, 1] > 0), "py", r[:, 0] / ay, r[:, 2] / ay),
        (my & (r[:, 1] <= 0), "ny", r[:, 0] / ay, -r[:, 2] / ay),
        (mz & (r[:, 2] > 0), "pz", r[:, 0] / az, -r[:, 1] / az),
        (mz & (r[:, 2] <= 0), "nz", -r[:, 0] / az, -r[:, 1] / az),
    ):
        face[m] = name
        s[m] = ss[m]
        t[m] = tt[m]
    return face, s, t


def cube_face_dir_fn(face_fn, n):
    def fn(px, py):
        u = 2.0 * px / n - 1.0
        v = 2.0 * py / n - 1.0
        x, y, z = face_fn(u, v)
        return normalize(np.stack([x, y, z], axis=-1))
    return fn


def equirect_dir_fn(width, height):
    """x: Azimut 0..360 (links Norden, nach rechts im Uhrzeigersinn), y: Elevation +90..-90."""
    def fn(px, py):
        az = np.radians(px / width * 360.0)
        el = np.radians(90.0 - py / height * 180.0)
        return np.stack([np.sin(az) * np.cos(el), np.sin(el), -np.cos(az) * np.cos(el)], axis=-1)
    return fn


def perspective_dir_fn(width, height, az_deg, el_deg, hfov_deg):
    f = dir_from_az_el(az_deg, el_deg)
    r, u = _screen_frame(f)
    tx = math.tan(math.radians(hfov_deg) / 2.0)
    ty = tx * height / width

    def fn(px, py):
        x = (2.0 * px / width - 1.0) * tx
        y = (1.0 - 2.0 * py / height) * ty
        return normalize(f[None, :] + x[:, None] * r[None, :] + y[:, None] * u[None, :])
    return fn


# ---------------------------------------------------------------------------
# Rendern
# ---------------------------------------------------------------------------


def render(model: SkyModel, dir_fn, width, height, ss=4, chunk=262144, seed=0, progress=None):
    """Rendert ein Bild (lineares RGB, float32). Himmelskoerper mit ss x ss Unterabtastung je Pixel."""
    out = np.zeros((height * width, 3), dtype=np.float32)
    total = height * width
    rows = max(1, chunk // width)
    rng = np.random.default_rng(seed)
    for y0 in range(0, height, rows):
        y1 = min(height, y0 + rows)
        X, Y = np.meshgrid(np.arange(width) + 0.5, np.arange(y0, y1) + 0.5)
        px, py = X.ravel(), Y.ravel()
        d = dir_fn(px, py)
        ex = dir_fn(px + 0.5, py) - dir_fn(px - 0.5, py)
        ey = dir_fn(px, py + 0.5) - dir_fn(px, py - 0.5)
        fp = np.sqrt(np.linalg.norm(ex, axis=1) * np.linalg.norm(ey, axis=1))

        def sub(idx, ox, oy, px=px, py=py):
            return dir_fn(px[idx] + ox, py[idx] + oy)

        out[y0 * width:y1 * width] = model.shade_pixels(d, fp, sub, ss=ss, rng=rng)
        if progress:
            progress(y1 * width / total)
    return out.reshape(height, width, 3)


def downsample(img, k):
    if k == 1:
        return img
    h, w, c = img.shape
    return img.reshape(h // k, k, w // k, k, c).mean(axis=(1, 3))


def to_srgb8(img, seed=0):
    """Weiche Schulter gegen hartes Clipping, sRGB, 8 Bit mit leichtem Dithering gegen Banding."""
    x = np.asarray(img, dtype=np.float64)
    knee = 0.80
    over = x > knee
    x = np.where(over, knee + (1 - knee) * (1 - np.exp(-(x - knee) / (1 - knee))), x)
    s = linear_to_srgb(x)
    rng = np.random.default_rng(seed)
    noise = rng.random(s.shape) - rng.random(s.shape)
    return np.clip(np.round(s * 255.0 + noise * 0.75), 0, 255).astype(np.uint8)
