"""Rendert den Himmel von Insel 1 (Skybox fuer Roblox, Cubemap fuer die three.js-Vorschau, Kontrollbilder).

    python3 render_sky.py              # alles (dauert einige Minuten)
    python3 render_sky.py --only views # nur die Kontroll-Ansichten
    python3 render_sky.py --size 512   # schneller Probelauf

Ausgaben:
    ../../assets/himmel/sky_{Bk,Dn,Ft,Lf,Rt,Up}.png      Roblox-Skybox (Sky.SkyboxBk ... SkyboxUp)
    out/preview/sky/{px,nx,py,ny,pz,nz}.png               three.js CubeTextureLoader (gleiche Reihenfolge)
    out/preview/sky/equirect.png                          Uebersicht (links Norden, Azimut nach rechts)
    out/preview/sky/view_*.png                            Perspektive direkt aus der Himmelsfunktion
    out/preview/sky/check_roblox_*.png                    Perspektive aus den 6 Roblox-Bildern zusammengesetzt
    out/preview/sky/meta.json                             Konventionen + Sonnenrichtung fuer die Vorschau
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from worldgen import sky  # noqa: E402

GAME = HERE.parent.parent  # galactic-miner-tycoon/
ROBLOX_OUT = GAME / "assets" / "himmel"
PREVIEW_OUT = HERE / "out" / "preview" / "sky"

# Kontroll-Ansichten: Name, Azimut, Elevation, horizontales Sichtfeld
VIEWS = [
    ("saturn", 40.0, 20.0, 60.0),
    ("saturn_nah", 40.0, 27.0, 34.0),
    ("sonne_eisriese", 272.0, 16.0, 70.0),
    ("norden_mond_haufen", 0.0, 34.0, 75.0),
    ("mond2_sueden", 150.0, 42.0, 60.0),
    ("zenit_band", 30.0, 75.0, 90.0),
    ("horizont_west", 250.0, 2.0, 90.0),
]


def log(msg):
    print(msg, flush=True)


def face_transform(src_fn, dst_fn, n=8):
    """Sucht die Drehung/Spiegelung, die eine Wuerfelflaeche in eine andere ueberfuehrt (gleiche Pixelmitten)."""
    X, Y = np.meshgrid(np.arange(n) + 0.5, np.arange(n) + 0.5)
    ds = sky.cube_face_dir_fn(src_fn, n)(X.ravel(), Y.ravel()).reshape(n, n, 3)
    dd = sky.cube_face_dir_fn(dst_fn, n)(X.ravel(), Y.ravel()).reshape(n, n, 3)
    for flip in (False, True):
        a = ds[:, ::-1] if flip else ds
        for k in range(4):
            if np.allclose(np.rot90(a, k), dd, atol=1e-9):
                return flip, k
    return None


def apply_transform(img, tr):
    flip, k = tr
    a = img[:, ::-1] if flip else img
    return np.ascontiguousarray(np.rot90(a, k))


def sample_faces(faces, lookup, d):
    """Bilinear aus 6 Bildern (uint8) abtasten, so wie die Engine es tut (Kontrolle der Konvention)."""
    face, u, v = lookup(d)
    out = np.zeros((len(d), 3))
    for name, img in faces.items():
        m = face == name
        if not m.any():
            continue
        n = img.shape[0]
        x = np.clip((u[m] + 1) / 2 * n - 0.5, 0, n - 1)
        y = np.clip((v[m] + 1) / 2 * n - 0.5, 0, n - 1)
        x0, y0 = np.floor(x).astype(int), np.floor(y).astype(int)
        x1, y1 = np.minimum(x0 + 1, n - 1), np.minimum(y0 + 1, n - 1)
        fx, fy = (x - x0)[:, None], (y - y0)[:, None]
        im = img.astype(np.float64)
        top = im[y0, x0] * (1 - fx) + im[y0, x1] * fx
        bot = im[y1, x0] * (1 - fx) + im[y1, x1] * fx
        out[m] = top * (1 - fy) + bot * fy
    return out


def check_conventions():
    """Vorwaerts- und Rueckwaertsabbildung der Flaechen muessen exakt zusammenpassen."""
    n = 16
    X, Y = np.meshgrid(np.arange(n) + 0.5, np.arange(n) + 0.5)
    for table, lookup in ((sky.ROBLOX_FACES, sky.roblox_lookup), (sky.THREE_FACES, sky.threejs_lookup)):
        for name, fn in table.items():
            d = sky.cube_face_dir_fn(fn, n)(X.ravel(), Y.ravel())
            face, u, v = lookup(d)
            assert (face == name).all(), name
            assert np.allclose(u, 2 * X.ravel() / n - 1) and np.allclose(v, 2 * Y.ravel() / n - 1), name
    # Bekannte Richtungen: Roblox Ft = -Z, Lf = +X, Up = +Y; three.js zeigt nx bei Blick nach +X
    assert sky.roblox_lookup(np.array([[0, 0, -1.0]]))[0][0] == "Ft"
    assert sky.roblox_lookup(np.array([[1.0, 0, 0]]))[0][0] == "Lf"
    assert sky.threejs_lookup(np.array([[1.0, 0, 0]]))[0][0] == "nx"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--size", type=int, default=1024, help="Kantenlaenge je Wuerfelflaeche (Roblox nutzt max. 1024)")
    ap.add_argument("--oversample", type=int, default=2, help="intern so viel feiner rendern, dann verkleinern")
    ap.add_argument("--ss", type=int, default=4, help="Unterabtastung je Pixel bei Himmelskoerpern (ss x ss)")
    ap.add_argument("--equirect-width", type=int, default=4096)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--only", default="cube,equirect,views", help="Auswahl: cube, equirect, views")
    args = ap.parse_args()
    parts = set(args.only.split(","))

    check_conventions()
    t0 = time.time()
    model = sky.SkyModel(seed=args.seed)
    sun_az, sun_el = sky.az_el_from_dir(model.sun_dir)
    log(f"Sonne aus Lighting (ClockTime {sky.LIGHTING_CLOCK_TIME}, GeographicLatitude {sky.LIGHTING_LATITUDE}): "
        f"Azimut {sun_az:.2f}, Elevation {sun_el:.2f}")
    ct, lat = sky.solve_roblox_sun(sky.SUN_TARGET_AZ, sky.SUN_TARGET_EL)
    log(f"Exakt Azimut {sky.SUN_TARGET_AZ:g} / Elevation {sky.SUN_TARGET_EL:g} waere ClockTime {ct:.4f}, "
        f"GeographicLatitude {lat:.3f}")
    for name, body, L in (("Saturn", model.saturn, model.saturn_light), ("Mond 1", model.moon1, model.sun_dir),
                          ("Mond 2", model.moon2, model.sun_dir), ("Eisriese", model.ice, model.sun_dir)):
        ph, frac, pa = sky.light_geometry(body.c, L)
        log(f"  {name}: Phasenwinkel {ph:.1f} Grad, {frac * 100:.0f} % beleuchtet, Licht aus {pa:.0f} Grad "
            f"(0 = rechts, 90 = oben)")
    ph, frac, pa = sky.light_geometry(model.saturn.c, model.sun_dir)
    log(f"  (Saturn mit echter Sonne waere: {frac * 100:.0f} % beleuchtet, Licht aus {pa:.0f} Grad, "
        f"Sonne {math.degrees(math.asin(abs(model.saturn.M[2] @ model.sun_dir))):.0f} Grad ueber der Ringebene)")

    PREVIEW_OUT.mkdir(parents=True, exist_ok=True)
    meta = {
        "description": "Himmel Insel 1 (worldgen/sky.py). Weltkoordinaten = Roblox: x Osten, y oben, z Sueden.",
        "threejs": {
            "files": ["px.png", "nx.png", "py.png", "ny.png", "pz.png", "nz.png"],
            "usage": "new THREE.CubeTextureLoader().setPath('out/preview/sky/').load(files); als scene.background "
                     "(colorSpace = SRGBColorSpace). Die Bilder beruecksichtigen schon, dass three.js CubeTextures "
                     "mit gespiegeltem x abtastet: Blick nach +X zeigt nx.png, nach -Z nz.png.",
        },
        "roblox": {
            "files": {f"Skybox{f}": f"assets/himmel/sky_{f}.png" for f in sky.ROBLOX_FACES},
            "faces": {"Ft": "-Z (Norden)", "Bk": "+Z (Sueden)", "Lf": "+X (Osten)", "Rt": "-X (Westen)",
                      "Up": "+Y", "Dn": "-Y"},
        },
        "sun": {"direction": [round(float(v), 6) for v in model.sun_dir], "azimuth": round(sun_az, 3),
                "elevation": round(sun_el, 3), "ClockTime": sky.LIGHTING_CLOCK_TIME,
                "GeographicLatitude": sky.LIGHTING_LATITUDE},
        "seed": args.seed,
    }
    (PREVIEW_OUT / "meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n")

    roblox8 = {}
    if "cube" in parts:
        n_int = args.size * args.oversample
        ROBLOX_OUT.mkdir(parents=True, exist_ok=True)
        lin = {}
        for i, (name, fn) in enumerate(sky.ROBLOX_FACES.items()):
            t = time.time()
            img = sky.render(model, sky.cube_face_dir_fn(fn, n_int), n_int, n_int, ss=args.ss, seed=args.seed + i)
            lin[name] = sky.downsample(img, args.oversample)
            roblox8[name] = sky.to_srgb8(lin[name], seed=args.seed * 10 + i)
            Image.fromarray(roblox8[name]).save(ROBLOX_OUT / f"sky_{name}.png", optimize=True)
            log(f"Roblox sky_{name}.png ({args.size} px) in {time.time() - t:.0f} s")
        # three.js-Flaechen: dieselben Pixel, nur gedreht/gespiegelt
        for i, (name, fn) in enumerate(sky.THREE_FACES.items()):
            for rname, rfn in sky.ROBLOX_FACES.items():
                tr = face_transform(rfn, fn)
                if tr is not None:
                    img8 = apply_transform(roblox8[rname], tr)
                    Image.fromarray(img8).save(PREVIEW_OUT / f"{name}.png", optimize=True)
                    log(f"three.js {name}.png = Roblox {rname} (gespiegelt={tr[0]}, gedreht {tr[1] * 90} Grad)")
                    break
            else:
                raise RuntimeError(f"keine Flaeche passt zu {name}")
        # Kontrolle: three.js-Abtastung der neuen Bilder == Roblox-Abtastung der Roblox-Bilder
        rng = np.random.default_rng(1)
        d = sky.normalize(rng.normal(size=(20000, 3)))
        three8 = {f: np.asarray(Image.open(PREVIEW_OUT / f"{f}.png")) for f in sky.THREE_FACES}
        a = sample_faces(roblox8, sky.roblox_lookup, d)
        b = sample_faces(three8, sky.threejs_lookup, d)
        log(f"Kontrolle Roblox vs. three.js: max. Abweichung {np.abs(a - b).max():.3f} (0 = identisch)")

    if "equirect" in parts:
        t = time.time()
        w = args.equirect_width
        img = sky.render(model, sky.equirect_dir_fn(w, w // 2), w, w // 2, ss=args.ss, seed=args.seed + 50)
        Image.fromarray(sky.to_srgb8(img, seed=5)).save(PREVIEW_OUT / "equirect.png", optimize=True)
        log(f"equirect.png ({w}x{w // 2}) in {time.time() - t:.0f} s")

    if "views" in parts:
        W, H = 1600, 900
        for name, az, el, fov in VIEWS:
            t = time.time()
            fn = sky.perspective_dir_fn(W, H, az, el, fov)
            img = sky.render(model, fn, W, H, ss=args.ss, seed=args.seed + 70)
            Image.fromarray(sky.to_srgb8(img, seed=9)).save(PREVIEW_OUT / f"view_{name}.png", optimize=True)
            log(f"view_{name}.png in {time.time() - t:.0f} s")
        if not roblox8:
            roblox8 = {f: np.asarray(Image.open(ROBLOX_OUT / f"sky_{f}.png")) for f in sky.ROBLOX_FACES
                       if (ROBLOX_OUT / f"sky_{f}.png").exists()}
        if len(roblox8) == 6:
            # So sieht es in Roblox aus: Ansicht aus den 6 Bildern mit der gemessenen Flaechen-Zuordnung
            for name, az, el, fov in VIEWS[:1] + VIEWS[2:4]:
                X, Y = np.meshgrid(np.arange(W) + 0.5, np.arange(H) + 0.5)
                d = sky.perspective_dir_fn(W, H, az, el, fov)(X.ravel(), Y.ravel())
                img = sample_faces(roblox8, sky.roblox_lookup, d).reshape(H, W, 3)
                Image.fromarray(np.clip(img + 0.5, 0, 255).astype(np.uint8)).save(
                    PREVIEW_OUT / f"check_roblox_{name}.png", optimize=True)
            log("check_roblox_*.png geschrieben (aus den Roblox-Bildern zusammengesetzt)")

    log(f"Fertig in {time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()
