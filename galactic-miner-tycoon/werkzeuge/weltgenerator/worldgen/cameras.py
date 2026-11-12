"""Kamera-Presets fuer die Vorschau (Positionen aus dem fertigen Gelaende und den Landmarken)."""
from __future__ import annotations

import math

from .layout import pol


def _cam(pos, target, fov=70, shadow=None, near=0.5):
    d = {"pos": [round(float(v), 2) for v in pos], "target": [round(float(v), 2) for v in target], "fov": fov, "near": near}
    if shadow:
        d["shadow"] = {"center": [round(float(shadow[0]), 1), round(float(shadow[1]), 1)], "radius": float(shadow[2])}
    return d


def _ahead(x, z, az, dist):
    a = math.radians(az)
    return x + math.sin(a) * dist, z - math.cos(a) * dist


def make(c):
    """c: Ctx nach dem Bau. Gibt {name: camera} zurueck."""
    H = lambda x, z: float(c.h_at(x, z))  # noqa: E731
    lm = {f["key"]: f for f in c.feat["landmark"]}
    cams = {}
    sx, _, sz = c.L.spawn
    eye = H(sx, sz) + 5.0
    # (a) Held: hinter der Basis, schraeg von oben, Richtung Az 40 (Saturn im Bild)
    hx, hz = pol(220, 270)
    tx, tz = pol(40, 900)
    cams["hero"] = _cam((hx, 135, hz), (tx, 95, tz), fov=80, shadow=(*pol(40, 420), 900))
    ax, az_ = pol(222, 330)
    t2 = pol(40, 220)
    cams["aerial"] = _cam((ax, 300, az_), (t2[0], -10, t2[1]), fov=70, shadow=(*pol(40, 200), 700))
    # (b) Augenhoehe am Spawn
    for a in (40, 105, 195, 250, 295):
        t = _ahead(sx, sz, a, 1000)
        cams[f"spawn_{a:03d}"] = _cam((sx, eye, sz), (t[0], eye + 25, t[1]), fov=70, shadow=(*_ahead(sx, sz, a, 650), 900))
    # (c) Postkarten
    p = pol(222, 150)
    cams["ring_a"] = _cam((p[0], H(*p) + 16, p[1]), (*pol(40, 320)[:1], 40, pol(40, 320)[1]), fov=70, shadow=(*pol(40, 150), 600))
    l3 = lm.get("L3")
    if l3:
        cpos = _ahead(l3["x"], l3["z"], 75, 260)
        tgt = _ahead(l3["x"], l3["z"], 285, 120)
        cams["ring_b_hoodoos"] = _cam((cpos[0], H(*cpos) + 22, cpos[1]), (tgt[0], H(*tgt) + 35, tgt[1]), fov=65,
                                      shadow=(l3["x"], l3["z"], 450))
    l5 = lm.get("L5")
    if l5:
        cpos = pol(31, 470)
        cams["ring_c_volcano"] = _cam((cpos[0], H(*cpos) + 30, cpos[1]), (l5["x"], 150, l5["z"]), fov=70,
                                      shadow=(*_ahead(cpos[0], cpos[1], 34, 500), 750))
    l4 = lm.get("L4")
    if l4:
        a4 = math.degrees(math.atan2(l4["x"], -l4["z"])) % 360
        cpos = _ahead(l4["x"], l4["z"], a4 + 160, 170)
        cams["ring_c_arch"] = _cam((cpos[0], H(*cpos) + 9, cpos[1]), (l4["x"], H(l4["x"], l4["z"]) + 22, l4["z"]), fov=70,
                                   shadow=(l4["x"], l4["z"], 400))
    l7 = lm.get("L7")
    if l7:
        cpos = _ahead(l7["x"], l7["z"], 70, 210)
        tgt = _ahead(l7["x"], l7["z"], 275, 300)
        cams["ring_d_terraces"] = _cam((cpos[0], H(*cpos) + 26, cpos[1]), (tgt[0], H(*tgt) + 10, tgt[1]), fov=70,
                                       shadow=(l7["x"], l7["z"], 500))
    l6 = lm.get("L6")
    if l6:
        a6 = math.degrees(math.atan2(l6["x"], -l6["z"])) % 360
        cpos = pol(a6 - 4, 1020)
        cams["ring_d_ridge"] = _cam((cpos[0], H(*cpos) + 20, cpos[1]), (l6["x"], 70, l6["z"]), fov=70,
                                    shadow=(*_ahead(cpos[0], cpos[1], a6, 330), 600))
    b = c.feat["balcony"][0]
    bx, bz = _ahead(b["x"], b["z"], b["az"] + 180, 18)
    t = _ahead(b["x"], b["z"], b["az"] - 5, 1200)
    cams["ring_e_balcony"] = _cam((bx, b["y"] + 6, bz), (t[0], b["y"] + 60, t[1]), fov=75, shadow=(b["x"], b["z"], 500))
    b = c.feat["balcony"][2]
    bx, bz = _ahead(b["x"], b["z"], b["az"] + 180, 14)
    t = _ahead(b["x"], b["z"], b["az"] + 30, 1200)
    cams["balcony_245"] = _cam((bx, b["y"] + 6, bz), (t[0], b["y"] - 40, t[1]), fov=75, shadow=(b["x"], b["z"], 500))
    # (d) Draufsicht
    cams["top"] = _cam((0, 5200, 1), (0, 0, 0), fov=48, shadow=(0, 0, 2350), near=50)
    l9 = lm.get("L9")
    if l9:
        cpos = _ahead(l9["x"], l9["z"], 200, 420)
        cams["ring_e_tower"] = _cam((cpos[0], H(*cpos) + 14, cpos[1]), (l9["x"], 150, l9["z"]), fov=70, shadow=(l9["x"], l9["z"], 600))
    return cams
