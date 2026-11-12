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


def map_data(c):
    """Daten fuer die Karten-Ueberlagerung: Ringe, Washes, Landmarken."""
    names = {"L0": "L0 Abendbank", "L1a": "L1 Saturn-Tor", "L1b": "", "L2": "L2 Zwillingstuerme", "L3": "L3 Nadelgarten",
             "L4": "L4 Bogen", "L5": "L5 Rauchfang", "L6": "L6 Regenbogen-Kamm", "L7": "L7 Silberstufen",
             "L8": "L8 Kristallkathedrale", "L9": "L9 Titan-Spiegelturm"}
    lms = []
    for f in c.feat["landmark"]:
        lab = names.get(f["key"], f["key"])
        if lab:
            lms.append({"key": f["key"], "label": lab, "x": round(f["x"], 1), "z": round(f["z"], 1)})
    for i, b in enumerate(c.feat["balcony"]):
        lms.append({"key": "L10", "label": "L10 Balkon %d" % (i + 1), "x": round(b["x"], 1), "z": round(b["z"], 1)})
    for key in ("T2", "T3"):
        for t in c.feat["terrace"]:
            if t["name"] == key:
                lms.append({"key": key, "label": key + " Terrassen", "x": round(t["x"], 1), "z": round(t["z"], 1)})
    washes = []
    for rs, az in c.wash_lines:
        pts = []
        for r, a in zip(rs[40::10], az[40::10]):
            if r > 1880:
                break
            x, z = pol(float(a), float(r))
            pts += [round(x, 1), round(z, 1)]
        washes.append(pts)
    sx, _, sz = c.L.spawn
    return {"rings": [250, 600, 1100, 1600, 2000], "washes": washes, "landmarks": lms, "spawn": [round(sx, 1), round(sz, 1)]}


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
    # Nahansicht eines Tafelbergs (ca. 80 Studs, Augenhoehe, Sonnenseite)
    best = None
    for m in c.feat["mesa"]:
        rr = math.hypot(m["x"], m["z"])
        if m["stage"] != "mesa" or m.get("R0", 0) < 38 or not (280 < rr < 1500):
            continue
        for da in (-30, -15, 0, 15, 30):
            a = 250 + da
            dist = m["R"] * 0.9 + 80
            px, pz = _ahead(m["x"], m["z"], a, dist)
            g = H(px, pz)
            if abs(g - m["base"]) > 6:
                continue
            ok = True
            for k in range(1, 12):
                qx, qz = _ahead(px, pz, a + 180, (dist - m["R"]) * k / 12 * 0.8)
                if H(qx, qz) > g + 6:
                    ok = False
                    break
            score = m.get("R0", 0) + len(m["levels"]) * 6 - abs(da) * 0.2
            if ok and (best is None or score > best[0]):
                best = (score, px, pz, g, m)
    if best:
        _, px, pz, g, m = best
        cams["mesa_close"] = _cam((px, g + 5.0, pz), (m["x"], g + (m["top"] - m["base"]) * 0.45, m["z"]), fov=70,
                                  shadow=(m["x"], m["z"], 300))
    # Deko-Nahansichten (aus den Inseln)
    isl = getattr(c, "deco_islands", [])
    ga = next((i for i in isl if i["theme"] == "grove" and i["ring"] == "A"), None)
    if ga:
        cpos = _ahead(ga["x"], ga["z"], 215, 62)
        cams["grove_a"] = _cam((cpos[0], H(*cpos) + 7, cpos[1]), (ga["x"], H(ga["x"], ga["z"]) + 12, ga["z"]), fov=70,
                               shadow=(ga["x"], ga["z"], 180))
    cg = [i for i in isl if i["theme"] == "crystal"]
    if cg:
        g = max(cg, key=lambda i: i["fault"]["L"])
        cpos = _ahead(g["x"], g["z"], 200, 75)
        cams["ring_d_garden"] = _cam((cpos[0], H(*cpos) + 9, cpos[1]), (g["x"], H(g["x"], g["z"]) + 5, g["z"]), fov=70,
                                     shadow=(g["x"], g["z"], 200))
    oa = next((i for i in isl if i["theme"] == "oasis" and i["ring"] == "C"), None)
    if oa:
        cpos = _ahead(oa["x"], oa["z"], 230, 150)
        cams["ring_c_oasis"] = _cam((cpos[0], H(*cpos) + 34, cpos[1]), (oa["x"], H(oa["x"], oa["z"]) + 4, oa["z"]), fov=70,
                                    shadow=(oa["x"], oa["z"], 320))
    l9 = lm.get("L9")
    if l9:
        cpos = _ahead(l9["x"], l9["z"], 200, 420)
        cams["ring_e_tower"] = _cam((cpos[0], H(*cpos) + 14, cpos[1]), (l9["x"], 150, l9["z"]), fov=70, shadow=(l9["x"], l9["z"], 600))
    return cams
