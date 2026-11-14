"""Kamera-Presets fuer die Vorschau (Positionen aus dem fertigen Gelaende und den Landmarken)."""
from __future__ import annotations

import math

from .layout import RING_EDGES, RING_NAMES, pol, sr


def _cam(pos, target, fov=70, shadow=None, near=0.5):
    d = {"pos": [round(float(v), 2) for v in pos], "target": [round(float(v), 2) for v in target], "fov": fov, "near": near}
    if shadow:
        d["shadow"] = {"center": [round(float(shadow[0]), 1), round(float(shadow[1]), 1)], "radius": float(shadow[2])}
    return d


def _ahead(x, z, az, dist):
    a = math.radians(az)
    return x + math.sin(a) * dist, z - math.cos(a) * dist


def _free_view(H, tx, tz, ty, az0, dists, lift, offs=(0, 20, -20, 40, -40, 60, -60, 90, -90)):
    """Runde 2: Kameraposition um ein Ziel suchen, von der aus der Blick nicht im Gelaende haengt (Strahl abtasten)."""
    for da in offs:
        for dist in dists:
            px, pz = _ahead(tx, tz, az0 + da, dist)
            py = H(px, pz) + lift
            ok = True
            for k in range(1, 24):
                t = k / 24.0
                qx, qz = px + (tx - px) * t, pz + (tz - pz) * t
                if H(qx, qz) > py + (ty - py) * t - 2.0 and t < 0.85:
                    ok = False
                    break
            if ok:
                return (px, py, pz)
    px, pz = _ahead(tx, tz, az0, dists[0])
    return (px, H(px, pz) + lift, pz)


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
        step = max(1, int(round(20.0 / (rs[1] - rs[0]))))
        i0 = int(round(sr(160) / (rs[1] - rs[0])))
        for r, a in zip(rs[i0::step], az[i0::step]):
            if r > sr(1880):
                break
            x, z = pol(float(a), float(r))
            pts += [round(x, 1), round(z, 1)]
        washes.append(pts)
    sx, _, sz = c.L.spawn
    mids = [round((a + b) / 2) for a, b in zip(RING_EDGES[:-1], RING_EDGES[1:])]
    return {"rings": RING_EDGES[1:], "ringNames": RING_NAMES, "ringMids": mids, "washes": washes, "landmarks": lms,
            "spawn": [round(sx, 1), round(sz, 1)], "extent": round(c.x.max() + 2.0)}


def make(c):
    """c: Ctx nach dem Bau. Gibt {name: camera} zurueck."""
    H = lambda x, z: float(c.h_at(x, z))  # noqa: E731
    lm = {f["key"]: f for f in c.feat["landmark"]}
    cams = {}
    sx, _, sz = c.L.spawn
    eye = H(sx, sz) + 5.0
    # Runde 2 (Entscheidung 022): Entfernungen x 0,5; Augenhoehe und Nahansichten (Objekt-Massstab) bleiben
    # (a) Held: hinter der Basis, schraeg von oben, Richtung Az 40 (Saturn im Bild)
    hx, hz = pol(220, sr(270))
    tx, tz = pol(40, sr(900))
    cams["hero"] = _cam((hx, 90, hz), (tx, 55, tz), fov=80, shadow=(*pol(40, sr(420)), 520))
    ax, az_ = pol(222, sr(330))
    t2 = pol(40, sr(220))
    cams["aerial"] = _cam((ax, 170, az_), (t2[0], -10, t2[1]), fov=70, shadow=(*pol(40, sr(200)), 420))
    # (b) Augenhoehe am Spawn
    for a in (40, 105, 195, 250, 295):
        t = _ahead(sx, sz, a, sr(1000))
        cams[f"spawn_{a:03d}"] = _cam((sx, eye, sz), (t[0], eye + 14, t[1]), fov=70, shadow=(*_ahead(sx, sz, a, sr(650)), 560))
    # (c) Postkarten
    p = pol(222, 110)
    cams["ring_a"] = _cam((p[0], H(*p) + 16, p[1]), (*pol(40, 200)[:1], 30, pol(40, 200)[1]), fov=70, shadow=(*pol(40, 110), 400))
    l3 = lm.get("L3")
    if l3:
        cpos = _ahead(l3["x"], l3["z"], 75, 170)
        tgt = _ahead(l3["x"], l3["z"], 285, 70)
        cams["ring_b_hoodoos"] = _cam((cpos[0], H(*cpos) + 22, cpos[1]), (tgt[0], H(*tgt) + 32, tgt[1]), fov=65,
                                      shadow=(l3["x"], l3["z"], 300))
    l5 = lm.get("L5")
    if l5:
        a5 = math.degrees(math.atan2(l5["x"], -l5["z"])) % 360
        cp = _free_view(H, l5["x"], l5["z"], 70, a5 + 180, (300, 360, 250), 30)
        cams["ring_c_volcano"] = _cam(cp, (l5["x"], 75, l5["z"]), fov=70, shadow=(l5["x"], l5["z"], 420))
    l4 = lm.get("L4")
    if l4:
        a4 = math.degrees(math.atan2(l4["x"], -l4["z"])) % 360
        ty = H(l4["x"], l4["z"]) + 22
        cp = _free_view(H, l4["x"], l4["z"], ty, a4 + 160, (110, 140, 170, 90), 20)
        cams["ring_c_arch"] = _cam(cp, (l4["x"], ty, l4["z"]), fov=70, shadow=(l4["x"], l4["z"], 400))
    l7 = lm.get("L7")
    if l7:
        # leicht von oben, vom Hangfuss Richtung Quelle (Gegenlicht)
        t7 = next((t for t in c.feat["terrace"] if t["name"] == "L7"), {"x": l7["x"], "z": l7["z"], "down": 75})
        cpos = _ahead(t7["x"], t7["z"], t7["down"], 150)
        tgt = _ahead(t7["x"], t7["z"], t7["down"] + 180, 30)
        cams["ring_d_terraces"] = _cam((cpos[0], H(*cpos) + 55, cpos[1]), (tgt[0], H(*tgt) - 4, tgt[1]), fov=65,
                                       shadow=(t7["x"], t7["z"], 400))
    l6 = lm.get("L6")
    if l6:
        a6 = math.degrees(math.atan2(l6["x"], -l6["z"])) % 360
        cp = _free_view(H, l6["x"], l6["z"], 60, a6 + 180, (260, 320, 220), 22, offs=(-4, 10, -18, 24, -30))
        cams["ring_d_ridge"] = _cam(cp, (l6["x"], 55, l6["z"]), fov=70, shadow=(l6["x"], l6["z"], 400))
    b = c.feat["balcony"][0]
    bx, bz = _ahead(b["x"], b["z"], b["az"] + 180, 18)
    t = _ahead(b["x"], b["z"], b["az"] - 5, sr(1200))
    cams["ring_e_balcony"] = _cam((bx, b["y"] + 6, bz), (t[0], b["y"] + 40, t[1]), fov=75, shadow=(b["x"], b["z"], 350))
    b = c.feat["balcony"][2]
    bx, bz = _ahead(b["x"], b["z"], b["az"] + 180, 14)
    t = _ahead(b["x"], b["z"], b["az"] + 12, sr(1200))       # Runde 2: 12 statt 30 Grad (sonst Blick in den Kamm)
    cams["balcony_245"] = _cam((bx, b["y"] + 6, bz), (t[0], b["y"] - 30, t[1]), fov=75, shadow=(b["x"], b["z"], 350))
    # Nahansicht eines Tafelbergs (ca. 80 Studs, Augenhoehe, Sonnenseite)
    # Runde 2: nicht direkt neben einem Deko-Objekt (sonst steht ein Kristall vor der Linse)
    from scipy.spatial import cKDTree
    dxz = getattr(c, "deco_xz", None)
    deco_tree = cKDTree(dxz) if dxz is not None and len(dxz) else None
    best = None
    for m in c.feat["mesa"]:
        rr = math.hypot(m["x"], m["z"])
        if m["stage"] != "mesa" or m.get("R0", 0) < 34 or not (sr(280) < rr < sr(1500)):
            continue
        for da in (-30, -15, 0, 15, 30):
            a = 250 + da
            dist = m["R"] * 0.9 + 80
            px, pz = _ahead(m["x"], m["z"], a, dist)
            g = H(px, pz)
            if abs(g - m["base"]) > 6:
                continue
            if deco_tree is not None and deco_tree.query((px, pz))[0] < 9.0:
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
    # Runde 2: Ring A ist Plateau -> der Haupthain (erste Hain-Insel, r ~165) ist die Nahansicht
    ga = next((i for i in isl if i["theme"] == "grove" and i["ring"] in "AB"), None)
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
    fb = c.feat.get("fogbasin", [])
    if fb:
        # Nebelbecken im Gegenlicht: Kamera auf der sonnenabgewandten Seite, auf Beckenhoehe, nicht im Randgebirge
        best = None
        for f in fb:
            hb = H(f["x"], f["z"])
            for da in (0, -25, 25, -50, 50, -80, 80):
                for dist in (f["R"] * 0.9 + 60, f["R"] * 0.9 + 100):
                    cx_, cz_ = _ahead(f["x"], f["z"], 70 + da, dist)
                    if math.hypot(cx_, cz_) > sr(1860):
                        continue
                    score = abs(H(cx_, cz_) - hb) + abs(da) * 0.15
                    if best is None or score < best[0]:
                        best = (score, cx_, cz_, f, hb)
        if best:
            _, cx_, cz_, f, hb = best
            cams["ring_e_fog"] = _cam((cx_, H(cx_, cz_) + 9, cz_), (f["x"], hb + 5, f["z"]), fov=70, shadow=(f["x"], f["z"], 350))
    l9 = lm.get("L9")
    if l9:
        cp = _free_view(H, l9["x"], l9["z"], 110, 200, (240, 300, 200), 16, offs=(0, 20, -20, 35, -35, 50))
        cams["ring_e_tower"] = _cam(cp, (l9["x"], 115, l9["z"]), fov=70, shadow=(l9["x"], l9["z"], 400))
    # (z) Zielbild-Kamera: der Studio-Screenshot, aus dem das KI-Zielbild entstand
    #     (referenz/bilder/welt/ki-ziel/insel1-ziel-v1.png), Runde 2 auf den halben Massstab gesetzt
    #     (vorher (-420, 320, 520) -> (150, 0, -200)). Roblox-Standard-FOV 70 (vertikal).
    cams["ziel"] = _cam((-210, 160, 260), (75, 0, -100), fov=70, shadow=(0, -50, 640))
    return cams
