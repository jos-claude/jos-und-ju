"""Spitzhacke in 5 Stufen nach assets/modelle/bauplaene/spitzhacke.md.

Prinzip "ein Geruest, fuenf Haeute": alle Stufen haben denselben Aufbau
(Knauf, Griff, Stiel, Warnringe, Kragen, Kopf-Block, Spitze, Flachende),
jede Stufe hat ein eigenes Erkennungsmerkmal.

Ausrichtung: Hacke steht aufrecht, Stiel entlang +Z, Unterkante Knauf bei
z = 0, Spitze zeigt nach -Y, Flachende nach +Y. 1 Einheit = 1 Stud.

Objekte je Stufe (ein Objekt pro Gruppe und Material):
- Pickaxe<Stufe>_Handle_<Material>  Griff mit Rillen. In Roblox = "Handle",
                                    Mitte bei (0, 0, 0,85) = Griffpunkt.
- Pickaxe<Stufe>_Glow_<Material>    alle Neon-Teile (Lichter, Kristall, Leuchtkante)
- Pickaxe<Stufe>_<Material>         alles andere

Aufruf:  blender -b -P build_pickaxe.py [-- --render] [--no-export] [--no-blend]
Export: pickaxe.glb/.fbx/.blend mit allen 5 Stufen nebeneinander (x = 0, 3, 6, 9, 12).
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import bpy  # noqa: E402  (bpy vor bmesh laden)
import bmesh  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

import gmt_lib as g  # noqa: E402

SEGS = 8          # alle Zylinder 8-eckig (low-poly, wie gedrechselt)
SPACING = 3.0     # Abstand der Stufen im Export

# Stufen-Tabelle (v2 nach den Higgsfield-Bildern referenz/bilder/ausruestung/spitzhacken-*.jpg).
# h = Gesamthoehe, p = Laenge der Spitze, q = Laenge des Hammer-Endes (ab Block-Kante),
# block = Kopf-Block (X, Y, Z). Die Kopf-Mitte lc ergibt sich aus h, Block und Kappe.
TIERS = [
    dict(key="Rust", h=3.4, p=1.00, q=0.50, block=(0.60, 0.66, 0.84),
         head="Rust", block_mat="RustDark", shaft="RustDark", grip="Cream",
         rings=[], lights=0, bolts=None, end_ring=None, pommel="SteelDark"),
    dict(key="Iron", h=3.7, p=1.15, q=0.50, block=(0.62, 0.68, 0.88),
         head="SteelGrey", block_mat="Orange", shaft="SteelMid", grip="Belt",
         rings=["Yellow"], lights=1, bolts=None, end_ring="Orange", pommel="SteelDark"),
    dict(key="Steel", h=3.9, p=1.30, q=0.55, block=(0.62, 0.68, 0.90),
         head="SteelLight", block_mat="Orange", shaft="SteelMid", grip="Belt",
         rings=["Yellow", "Black", "Yellow"], lights=2, bolts="Copper", end_ring="Orange",
         pommel="SteelDark"),
    dict(key="Crystal", h=4.1, p=1.40, q=0.55, block=(0.62, 0.68, 0.90),
         head="SteelLight", block_mat="Orange", shaft="SteelMid", grip="Belt",
         rings=["Yellow", "Black", "Yellow"], lights=3, bolts="SteelLight", end_ring="Orange",
         pommel="SteelDark"),
    dict(key="Titan", h=4.3, p=1.55, q=0.60, block=(0.68, 0.75, 0.98),
         head="Titan", block_mat="Orange", shaft="SteelMid", grip="Belt",
         rings=["Yellow", "Black", "Yellow"], lights=4, bolts=None, end_ring="Cyan",
         pommel="Titan"),
]
CAP_H = 0.15      # achteckige Kappe oben auf dem Block


# ---------------------------------------------------------------------------
# Hilfen
# ---------------------------------------------------------------------------
def chamfer_pts(w, h, ch):
    """Rechteck w x h (u, v) mit Fasen-Ecken -> 8 Punkte (bei ch = 0: 4 Punkte)."""
    x, z = w / 2, h / 2
    if ch <= 0:
        return [(-x, -z), (x, -z), (x, z), (-x, z)]
    c = min(ch, x * 0.45, z * 0.45)
    return [(-x + c, -z), (x - c, -z), (x, -z + c), (x, z - c),
            (x - c, z), (-x + c, z), (-x, z - c), (-x, -z + c)]


def ring_on_curve(y, z, ty, tz, w, h, ch=0.0, shift=0.0):
    """Querschnitt senkrecht zur Kurve (Kurve in der YZ-Ebene, Breite in X).
    shift verschiebt den Querschnitt entlang der Kurven-Normalen (oben)."""
    ln = math.hypot(ty, tz)
    ty, tz = ty / ln, tz / ln
    ny, nz = tz, -ty            # Normale: fuer eine Kurve Richtung -Y zeigt sie nach oben
    if nz < 0:
        ny, nz = -ny, -nz
    return [(u, y + ny * (v + shift), z + nz * (v + shift)) for u, v in chamfer_pts(w, h, ch)]


def bezier(p0, p1, p2, t):
    a = [(1 - t) ** 2 * p0[i] + 2 * (1 - t) * t * p1[i] + t * t * p2[i] for i in (0, 1)]
    d = [2 * (1 - t) * (p1[i] - p0[i]) + 2 * t * (p2[i] - p1[i]) for i in (0, 1)]
    return a, d


def hex_ring_on_curve(y, z, ty, tz, r):
    """Sechseck senkrecht zur Kurve, eine Ecke zeigt nach oben (Kristall)."""
    pts = [(r * math.cos(math.pi / 2 + k * math.pi / 3), r * math.sin(math.pi / 2 + k * math.pi / 3))
           for k in range(6)]
    ln = math.hypot(ty, tz)
    ty, tz = ty / ln, tz / ln
    ny, nz = tz, -ty
    if nz < 0:
        ny, nz = -ny, -nz
    return [(u, y + ny * v, z + nz * v) for u, v in pts]


def loft_solid(rings):
    """Loft durch Ringe gleicher Punktzahl, beide Enden mit Deckel (n-Eck)."""
    bm = bmesh.new()
    vs = [[bm.verts.new(p) for p in r] for r in rings]
    n = len(rings[0])
    for a in range(len(vs) - 1):
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((vs[a][i], vs[a][j], vs[a + 1][j], vs[a + 1][i]))
    bm.faces.new(list(reversed(vs[0])))
    bm.faces.new(vs[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def zcyl(m, r, z0, z1, mat, group=None, bevel=0.0, segs=SEGS):
    m.add(g.cylinder(r, z1 - z0, (0, 0, (z0 + z1) / 2), segs=segs, bevel=bevel), mat, group)


def pick_curve(by, lc, bz, p):
    """Mittellinie der Spitze: Ansatz oben am Block, leichter Buckel, dann nach unten (Sichel)."""
    y0, z0 = -by / 2 + 0.04, lc + 0.08 * bz
    return (y0, z0), (y0 - 0.50 * p, z0 + 0.10), (y0 - p, z0 - 0.46 * p)


# ---------------------------------------------------------------------------
# Eine Stufe
# ---------------------------------------------------------------------------
def build_tier(t):
    m = g.Model("Pickaxe" + t["key"])
    p, q, key = t["p"], t["q"], t["key"]
    bx, by, bz = t["block"]
    lc = t["h"] - CAP_H - bz / 2          # Hoehe der Kopf-Mitte
    dark = "RustDark" if key == "Rust" else "SteelDark"

    # Knauf mit Endring, Griff mit 4 dicken Rillen (Gruppe Handle), Stiel
    z = 0.0
    if t["end_ring"]:
        grp = "Glow" if t["end_ring"] == "Cyan" else None
        zcyl(m, 0.285, 0.0, 0.07, t["end_ring"], group=grp)
        z = 0.07
    zcyl(m, 0.28, z, 0.40, t["pommel"], bevel=0.04)
    zcyl(m, 0.215, 0.40, 1.35, t["grip"], group="Handle")
    for zr in (0.52, 0.76, 1.00, 1.24):
        zcyl(m, 0.26, zr - 0.08, zr + 0.08, t["grip"], group="Handle")
    zcyl(m, 0.19, 1.35, lc, t["shaft"])

    # Kragen direkt unter dem Block, darunter die Warnringe (von oben: Gelb, Schwarz, Gelb)
    zb = lc - bz / 2
    zcyl(m, 0.27, zb - 0.18, zb + 0.02, dark, bevel=0.03)
    zr = zb - 0.18
    for mat in t["rings"]:
        hh = 0.07 if mat == "Black" else 0.10
        zcyl(m, 0.245, zr - hh, zr, mat)
        zr -= hh

    # Kopf-Block und achteckige Kappe (ab Stahl mit Cyan-Licht oben)
    m.add(g.box((bx, by, bz), (0, 0, lc), bevel=0.08), t["block_mat"])
    ztop = lc + bz / 2
    cap_r = 0.18 if key == "Rust" else 0.24
    zcyl(m, cap_r, ztop - 0.02, ztop + CAP_H, dark, bevel=0.03)
    if key in ("Steel", "Crystal", "Titan"):
        zcyl(m, 0.10 if key == "Titan" else 0.08, ztop + CAP_H - 0.01, ztop + CAP_H + 0.03,
             "Cyan", group="Glow")

    # Stufen-Lichter auf beiden X-Seiten (mit hellem Rahmen)
    n = t["lights"]
    spots = {0: [], 1: [(0, 0)], 2: [(-0.14, 0), (0.14, 0)],
             3: [(-0.17, 0), (0, 0), (0.17, 0)],
             4: [(-0.11, -0.11), (0.11, -0.11), (-0.11, 0.11), (0.11, 0.11)]}[n]
    for sx in (-1, 1):
        for yy, dz in spots:
            size = 0.11 if n >= 3 else 0.13
            m.add(g.box((0.03, size + 0.06, size + 0.06), (sx * (bx / 2 + 0.005), yy, lc + dz)),
              "SteelLight")
            m.add(g.box((0.03, size, size), (sx * (bx / 2 + 0.025), yy, lc + dz)), "Cyan", group="Glow")

    # Bolzen in den Block-Ecken (Stahl: Kupfer, Kristall: hell)
    if t["bolts"]:
        for sx in (-1, 1):
            for yy in (-(by / 2 - 0.12), by / 2 - 0.12):
                for dz in (-(bz / 2 - 0.14), bz / 2 - 0.14):
                    m.add(g.cylinder(0.055, 0.05, (sx * (bx / 2 + 0.02), yy, lc + dz), axis="X",
                                     segs=6), t["bolts"])

    # Spitze nach -Y: Sichel-Loft (5 Querschnitte senkrecht zur Kurve)
    P0, P1, P2 = pick_curve(by, lc, bz, p)
    if key == "Crystal":
        # Halte-Ring am Block, darin ein 6-eckiger Kristall (leicht nach unten gebogen)
        m.add(g.cylinder(0.27, 0.16, (0, -by / 2 - 0.06, P0[1]), axis="Y", segs=SEGS, bevel=0.02),
              "SteelLight")
        Q1 = (P0[0] - 0.5 * p, P0[1] + 0.02)
        Q2 = (P0[0] - p, P0[1] - 0.30 * p)
        radii = [0.22, 0.21, 0.17, 0.10, 0.04]
        rings = []
        for i, tt in enumerate((0.0, 0.3, 0.6, 0.85, 1.0)):
            (yy, zz), (dy, dz) = bezier(P0, Q1, Q2, tt)
            rings.append(hex_ring_on_curve(yy, zz, dy, dz, radii[i]))
        m.add(loft_solid(rings), "Crystal", group="Glow")
    else:
        tip = (0.17, 0.16) if key == "Rust" else (0.09, 0.10)
        root = (0.42, 0.56)
        rings = []
        for tt in (0.0, 0.25, 0.5, 0.75, 1.0):
            (yy, zz), (dy, dz) = bezier(P0, P1, P2, tt)
            f = 1 - tt ** 2
            w = tip[0] + (root[0] - tip[0]) * f
            hgt = tip[1] + (root[1] - tip[1]) * f
            rings.append(ring_on_curve(yy, zz, dy, dz, w, hgt, ch=0.06 * (0.4 + 0.6 * f)))
        m.add(loft_solid(rings), t["head"])
        if key == "Titan":
            # Leuchtkante oben auf der Sichel
            strip = []
            for tt in (0.04, 0.25, 0.5, 0.75, 0.96):
                (yy, zz), (dy, dz) = bezier(P0, P1, P2, tt)
                f = 1 - tt ** 2
                hgt = tip[1] + (root[1] - tip[1]) * f
                strip.append(ring_on_curve(yy, zz, dy, dz, 0.07 * (0.5 + 0.5 * f), 0.04,
                                           shift=hgt / 2 + 0.005))
            m.add(loft_solid(strip), "Cyan", group="Glow")

    # Hammer-Ende nach +Y: dunkler Hals und etwas groesseres Schlag-Stueck mit Fasen
    zs = P0[1] - 0.02
    yb = by / 2 - 0.04
    yn = by / 2 + 0.55 * q
    m.add(g.box((0.30, yn - yb, 0.34), (0, (yb + yn) / 2, zs)), dark)
    m.add(g.box((0.38, by / 2 + q - yn, 0.44), (0, (yn + by / 2 + q) / 2, zs), bevel=0.06), t["head"])
    yface = by / 2 + q
    if key == "Crystal":   # kleiner Kristall auf der Schlagflaeche
        m.add(g.box((0.17, 0.05, 0.17), (0, yface + 0.01, zs), rot_z=0,
                    matrix=Matrix.Translation((0, yface + 0.01, zs)) @ Matrix.Rotation(math.radians(45), 4, "Y")
                    @ Matrix.Translation((0, -(yface + 0.01), -zs))), "Crystal", group="Glow")
    if key == "Titan":     # Leuchtstreifen auf der Schlagflaeche
        m.add(g.box((0.06, 0.04, 0.28), (0, yface + 0.01, zs)), "Cyan", group="Glow")

    # Rost: Flicken-Platte auf der +X-Seite, leicht gekippt, mit 2 Bolzen ueber Kreuz
    if key == "Rust":
        pivot = Vector((bx / 2 + 0.03, 0.0, lc + 0.03))
        rot = Matrix.Translation(pivot) @ Matrix.Rotation(math.radians(8), 4, "X")
        m.add(g.box((0.05, 0.36, 0.34), (0, 0, 0), bevel=0.012, matrix=rot), "SteelGrey")
        for yy, dz in ((-0.09, 0.08), (0.09, -0.08)):
            m.add(g.cylinder(0.045, 0.04, (0.035, yy, dz), axis="X", segs=6, matrix=rot), "SteelLight")
    return m


# ---------------------------------------------------------------------------
def main():
    g.reset_scene()
    models_dir, preview_dir = g.out_dirs()
    sc = bpy.context.scene
    coll = bpy.data.collections.new("Pickaxes")
    sc.collection.children.link(coll)
    all_objs, per_tier = [], []
    for i, t in enumerate(TIERS):
        objs = build_tier(t).build(location=(i * SPACING, 0, 0), collection=coll)
        per_tier.append((t["key"], objs))
        all_objs += objs
        mn, mx = g.bounds(objs)
        print(f"Pickaxe{t['key']}: {len(objs)} Objekte, {g.tri_count(objs)} Dreiecke, "
              f"Groesse {tuple(round(v, 2) for v in (mx - mn))}")
    if "--no-export" not in sys.argv:
        g.export_model(all_objs, os.path.join(models_dir, "pickaxe"))
    if "--no-blend" not in sys.argv:
        g.save_blend(os.path.join(models_dir, "pickaxe.blend"))
    if "--render" in sys.argv:
        g.setup_render(res=(1600, 900))
        p = lambda n: os.path.join(preview_dir, n)
        g.render_view(all_objs, p("pickaxe_iso.png"), "iso", azimuth=-35, elevation=22, margin=1.05)
        # Seitenansicht wie im Referenzbild: alle nebeneinander, Spitze nach links.
        # Dafuer jede Stufe kurz um -90 Grad drehen (Spitze -Y -> -X) und weiter auseinander stellen.
        for i, (key, objs) in enumerate(per_tier):
            for o in objs:
                o.rotation_euler = (0, 0, math.radians(-90))
                o.location = (i * 4.2, 0, 0)
        bpy.context.view_layer.update()
        g.render_view(all_objs, p("pickaxe_side.png"), "front", res=(1600, 900), margin=1.06)
        for i, (key, objs) in enumerate(per_tier):
            for o in objs:
                o.rotation_euler = (0, 0, 0)
                o.location = (i * SPACING, 0, 0)
        bpy.context.view_layer.update()
        # Shop-Icons: je Stufe allein im Bild
        for key, objs in per_tier:
            for o in all_objs:
                o.hide_render = o not in objs
            g.render_view(objs, p(f"pickaxe_{key.lower()}_icon.png"), "iso", azimuth=-60,
                          elevation=18, res=(512, 512), margin=1.0)
        for o in all_objs:
            o.hide_render = False


if __name__ == "__main__":
    main()
