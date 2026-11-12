"""Foerderband-Set nach referenz/bilder/gebaeude/foerderband-01.jpg.

Modelle (Flussrichtung = Pfeilrichtung, Grundraster 4 Studs):
- ConveyorStraight  8 x 3,6 Studs, wie im Bild (Fluss +X)
- ConveyorSegment   4 x 3,6 Studs, gerade Enden, zum Aneinanderreihen (belt_segment)
- ConveyorCurve     Rechtskurve 90 Grad, Grundflaeche 8 x 8 (rein bei x=-2 von -Y,
                    raus bei y=+2 nach +X)
- ConveyorCurveLeft gespiegelt (rein bei x=+2 von -Y, raus bei y=+2 nach -X)
- ConveyorEnd       6 x 3,6 Studs, Bandstueck + Trichter (Fluss +X in den Trichter)
- OreChunkA/B/C     Erzbrocken, wie sie auf dem Band liegen

Aufruf:  blender -b -P build_conveyor.py [-- --render]   oder   python build_conveyor.py
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import bpy  # noqa: E402  (bpy vor bmesh laden)
import bmesh  # noqa: E402
from mathutils import Matrix  # noqa: E402

import gmt_lib as g  # noqa: E402

HB = 2.75                    # Oberkante Band
BW = 1.5                     # halbe Bandbreite
RAIL_IN, RAIL_OUT = 1.5, 1.82
RAIL_Z0, RAIL_Z1 = HB - 0.4, HB + 0.2        # graues Schienenband
BEAM_Y0, BEAM_Y1 = 1.58, 1.78                # oranger Traeger (etwas eingerueckt)
BEAM_Z0 = HB - 1.45
LIP_Z0 = HB - 1.55                           # graue Lippe unter dem Traeger
LEG = 0.9                                    # Bein-Querschnitt
LEG_Y0, LEG_Y1 = 1.42, 2.32
BOLT_R = 0.15


def xz_frame():
    """(u,v,w) -> (x, -w, z): Profil in XZ, Extrusion entlang -Y."""
    return g.frame_at((0, 0, 0), (1, 0, 0), (0, 0, 1))


def prism_xz(poly, y0, y1, bevel=0.0):
    return g.prism(poly, -y1, -y0, xz_frame(), bevel=bevel)


def bolt_y(m, x, y, z, side, r=BOLT_R, matrix=None):
    """Sechskant-Bolzen auf einer Flaeche mit Normale side*Y."""
    m.add(g.cylinder(r, 0.12, (x, y + side * 0.04, z), axis="Y", segs=6, matrix=matrix),
          "SteelLight")


def add_leg(m, x, side, matrix=None):
    """Dickes Bein mit Fussplatte und einem Bolzen oben (side=+1 links/hinten)."""
    mat = matrix or Matrix.Identity(4)
    y0, y1 = sorted((side * LEG_Y0, side * LEG_Y1))
    top = RAIL_Z0 + 0.02
    m.add(g.box_minmax((x - LEG / 2, y0, 0.26), (x + LEG / 2, y1, top), bevel=0.12,
                       matrix=mat), "Orange")
    yc = (y0 + y1) / 2
    m.add(g.box((LEG + 0.42, LEG + 0.34, 0.26), (x, yc, 0.13), bevel=0.07, matrix=mat),
          "SteelGrey")
    bolt_y(m, x, side * LEG_Y1, top - 0.35, side, r=0.17, matrix=mat)
    for dx in (-1, 1):
        m.add(g.cylinder(0.09, 0.08, (x + dx * (LEG / 2 + 0.08), yc, 0.28), segs=6,
                         matrix=mat), "SteelLight")


def side_frame_straight(m, x0, x1, end_plates=True):
    """Schienenband, oranger Traeger, Lippe und End-Platten auf beiden Seiten."""
    for s in (-1, 1):
        ry0, ry1 = sorted((s * RAIL_IN, s * RAIL_OUT))
        by0, by1 = sorted((s * BEAM_Y0, s * BEAM_Y1))
        ly0, ly1 = sorted((s * BEAM_Y0, s * (BEAM_Y1 + 0.03)))
        m.add(g.box_minmax((x0, ry0, RAIL_Z0), (x1, ry1, RAIL_Z1), bevel=0.05), "SteelGrey")
        bx0 = x0 + (0.7 if end_plates else 0.0)
        bx1 = x1 - (0.7 if end_plates else 0.0)
        m.add(g.box_minmax((bx0, by0, BEAM_Z0), (bx1, by1, RAIL_Z0 + 0.02)), "Orange")
        m.add(g.box_minmax((bx0, ly0, LIP_Z0), (bx1, ly1, BEAM_Z0 + 0.01), bevel=0.02),
              "SteelGrey")
        if end_plates:
            for ex0, ex1 in ((x0, x0 + 0.75), (x1 - 0.75, x1)):
                plate = g.rounded_rect(ex0, ex1, LIP_Z0, RAIL_Z1, 0.36, 4)
                m.add(prism_xz(plate, ry0 - (0.02 if s > 0 else 0),
                               ry1 + (0.02 if s < 0 else 0), bevel=0.03), "SteelGrey")
                for z in (RAIL_Z1 - 0.3, LIP_Z0 + 0.45):
                    bolt_y(m, (ex0 + ex1) / 2, s * (RAIL_OUT + 0.02), z, s)


def belt_body(m, x0, x1, round_left=True, round_right=True):
    belt = g.stadium(x0 + 0.05, x1 - 0.05, HB - 0.45, HB, segs=6,
                     round_left=round_left, round_right=round_right)
    m.add(prism_xz(belt, -BW, BW), "Belt")
    m.add(g.box_minmax((x0 + 0.4, -BW + 0.02, BEAM_Z0 + 0.05), (x1 - 0.4, BW - 0.02, HB - 0.4)),
          "DarkGrey")


def beam_face(s):
    return g.face_frame("-Y" if s < 0 else "+Y", s * BEAM_Y1)


def hazard_on_beam(m, s, xa, xb):
    """Warnstreifen auf dem Traeger zwischen xa und xb (Welt-x)."""
    fr = beam_face(s)
    u0, u1 = (xa, xb) if s < 0 else (-xb, -xa)
    v0, v1 = BEAM_Z0 + 0.14, RAIL_Z0 - 0.12
    m.sticker([(u0, v0), (u1, v0), (u1, v1), (u0, v1)], fr, "Black", 0.008, 0.035)
    for p in g.hazard_stripes(u0, u1, v0, v1, 0.24, 0.24):
        m.sticker(p, fr, "Yellow", 0.02, 0.05)


def plate_on_beam(m, s, xc, width):
    fr = beam_face(s)
    u = xc if s < 0 else -xc
    v0, v1 = BEAM_Z0 + 0.16, RAIL_Z0 - 0.12
    trap = [(u - width / 2, v0), (u + width / 2, v0), (u + width / 2 - 0.22, v1),
            (u - width / 2 + 0.22, v1)]                                # unten breiter
    m.sticker(trap, fr, "SteelLight", 0.01, 0.07, bevel=0.015)
    for du in (-width / 2 + 0.3, width / 2 - 0.3):
        for v in (v0 + 0.13, v1 - 0.13):
            m.add(g.prism(g.rounded_rect(u + du - 0.06, u + du + 0.06, v - 0.06, v + 0.06,
                                         0.03, 1), 0.07, 0.11, fr), "SteelGrey")


def straight(name, L, legs_x, arrows_x, hazard=None, plate=None, end_plates=True):
    m = g.Model(name)
    x0, x1 = -L / 2, L / 2
    belt_body(m, x0, x1, end_plates, end_plates)
    side_frame_straight(m, x0, x1, end_plates)
    for s in (-1, 1):
        for lx in legs_x:
            add_leg(m, lx, s)
        if hazard:
            hazard_on_beam(m, s, *hazard)
        if plate:
            plate_on_beam(m, s, *plate)
        for bx in (x0 + L * 0.25, x0 + L * 0.75):
            if all(abs(bx - lx) > 0.8 for lx in legs_x):
                bolt_y(m, bx, s * RAIL_OUT, (RAIL_Z0 + RAIL_Z1) / 2, s)
    top = g.face_frame("+Z", HB)
    for ax in arrows_x:
        m.sticker([(u + ax, v) for u, v in g.arrow(1.9, 1.2, shaft=0.32)], top, "Yellow",
                  0.01, 0.04)
    return m


# ---------------------------------------------------------------------------
# Kurve: Pfad = Einlauf (gerade) + Viertelkreis + Auslauf (gerade)
# ---------------------------------------------------------------------------
CURVE_C = (2.0, -2.0)
CURVE_R = 4.0


def curve_path(segs=18):
    pts = []
    for y in (-4.0, -3.0):
        pts.append(((-2.0, y), (-1.0, 0.0)))
    for k in range(segs + 1):
        th = math.radians(180 - 90 * k / segs)
        pts.append(((CURVE_C[0] + CURVE_R * math.cos(th), CURVE_C[1] + CURVE_R * math.sin(th)),
                    (math.cos(th), math.sin(th))))
    for x in (3.0, 4.0):
        pts.append(((x, 2.0), (0.0, 1.0)))
    return pts


def frame_on_curve(where, lateral=0.0, z=0.0):
    """where: ('in', y) | ('arc', theta) | ('out', x). u = Laufrichtung, v = links (aussen)."""
    kind, val = where
    if kind == "in":
        p, n = (-2.0, val), (-1.0, 0.0)
    elif kind == "out":
        p, n = (val, 2.0), (0.0, 1.0)
    else:
        th = math.radians(val)
        p = (CURVE_C[0] + CURVE_R * math.cos(th), CURVE_C[1] + CURVE_R * math.sin(th))
        n = (math.cos(th), math.sin(th))
    t = (n[1], -n[0])
    o = (p[0] + n[0] * lateral, p[1] + n[1] * lateral, z)
    return g.frame_at(o, (t[0], t[1], 0), (n[0], n[1], 0))


def curve(name, mirror=False):
    m = g.Model(name)
    path = curve_path()
    m.add(g.sweep(path, -BW, BW, HB - 0.45, HB), "Belt")
    m.add(g.sweep(path, -BW + 0.02, BW - 0.02, BEAM_Z0 + 0.05, HB - 0.4), "DarkGrey")
    for s in (-1, 1):
        r0, r1 = sorted((s * RAIL_IN, s * RAIL_OUT))
        b0, b1 = sorted((s * BEAM_Y0, s * BEAM_Y1))
        l0, l1 = sorted((s * BEAM_Y0, s * (BEAM_Y1 + 0.03)))
        m.add(g.sweep(path, r0, r1, RAIL_Z0, RAIL_Z1), "SteelGrey")
        m.add(g.sweep(path, b0, b1, BEAM_Z0, RAIL_Z0 + 0.02), "Orange")
        m.add(g.sweep(path, l0, l1, LIP_Z0, BEAM_Z0 + 0.01), "SteelGrey")
    # 6 Beine: aussen Einlauf/Mitte/Auslauf, innen Einlauf/Ecke/Auslauf
    for where, side in ((("in", -3.25), 1), (("arc", 135), 1), (("out", 3.25), 1),
                        (("in", -3.25), -1), (("arc", 135), -1), (("out", 3.25), -1)):
        add_leg(m, 0.0, side, matrix=frame_on_curve(where))
    # grosse Bolzen auf den Schienen
    for where in (("arc", 160), ("arc", 110)):
        for s in (-1, 1):
            fr = frame_on_curve(where)
            m.add(g.cylinder(BOLT_R, 0.12, (0, s * (RAIL_OUT + 0.04), (RAIL_Z0 + RAIL_Z1) / 2),
                             axis="Y", segs=6, matrix=fr), "SteelLight")
    # Pfeil im Einlauf, 5 kraeftige Winkel im Bogen/Auslauf
    fr = frame_on_curve(("in", -3.05), 0.0, HB)
    m.sticker(g.arrow(1.8, 1.15, shaft=0.31), fr, "Yellow", 0.01, 0.04)
    for where in (("arc", 164), ("arc", 146), ("arc", 128), ("arc", 110), ("out", 2.95)):
        fr = frame_on_curve(where, 0.0, HB)
        m.sticker(g.chevron(0.85, 1.35, 0.42), fr, "Yellow", 0.01, 0.04)
    if mirror:
        flip = Matrix.Scale(-1, 4, (1, 0, 0))
        for bm in m.parts.values():
            bm.transform(flip)
            bmesh.ops.reverse_faces(bm, faces=bm.faces)
            bm.normal_update()
    return m


# ---------------------------------------------------------------------------
# Endstueck mit Trichter
# ---------------------------------------------------------------------------
def end_piece(name):
    m = g.Model(name)
    x0, x1 = -3.0, 3.0
    hx0 = 0.5                      # Beginn Gehaeuse
    post_x0 = 2.35                 # Endpfosten
    belt_body(m, x0, hx0 + 0.3, True, False)
    zt = RAIL_Z1
    for s in (-1, 1):
        ry0, ry1 = sorted((s * RAIL_IN, s * RAIL_OUT))
        by0, by1 = sorted((s * BEAM_Y0, s * BEAM_Y1))
        ly0, ly1 = sorted((s * BEAM_Y0, s * (BEAM_Y1 + 0.03)))
        # Schienenband ueber die ganze Laenge, am Ende rund nach unten in den Pfosten
        R = 0.65
        m.add(g.box_minmax((x0 + 0.7, ry0, RAIL_Z0), (post_x0 + 0.02, ry1, zt), bevel=0.04),
              "SteelGrey")
        post = [(post_x0, 0.28), (x1, 0.28)]
        for k in range(9):
            a = math.radians(90 * k / 8)
            post.append((x1 - R + R * math.cos(a), zt - R + R * math.sin(a)))
        post.append((post_x0, zt))
        m.add(prism_xz(post, ry0, ry1, bevel=0.04), "SteelGrey")
        # End-Platte am Bandanfang
        plate = g.rounded_rect(x0, x0 + 0.75, LIP_Z0, zt, 0.36, 4)
        m.add(prism_xz(plate, ry0 - (0.02 if s > 0 else 0), ry1 + (0.02 if s < 0 else 0),
                       bevel=0.03), "SteelGrey")
        for z in (zt - 0.3, LIP_Z0 + 0.45):
            bolt_y(m, x0 + 0.375, s * (RAIL_OUT + 0.02), z, s)
        for z in (zt - 0.5, 0.75):
            bolt_y(m, (post_x0 + x1) / 2 - 0.05, s * (RAIL_OUT + 0.02), z, s)
        # Traeger + Lippe zwischen End-Platte und Pfosten
        m.add(g.box_minmax((x0 + 0.7, by0, BEAM_Z0), (post_x0 + 0.02, by1, RAIL_Z0 + 0.02)),
              "Orange")
        m.add(g.box_minmax((x0 + 0.7, ly0, LIP_Z0), (post_x0 + 0.02, ly1, BEAM_Z0 + 0.01),
                           bevel=0.02), "SteelGrey")
        hazard_on_beam(m, s, -1.55, post_x0 - 0.1)
        add_leg(m, -1.95, s)
    # Gehaeuse zwischen den Schienen
    m.add(g.box_minmax((hx0, -RAIL_IN, 0.28), (post_x0 + 0.1, RAIL_IN, zt)), "Orange")
    m.add(g.box_minmax((hx0 - 0.1, -RAIL_OUT - 0.1, 0.0), (x1 + 0.08, RAIL_OUT + 0.1, 0.3),
                       bevel=0.06), "SteelGrey")
    # Stirnseite: grauer Rahmen mit zwei Leuchtbalken
    m.add(g.box_minmax((post_x0 + 0.05, -RAIL_IN, 0.28), (x1 - 0.05, RAIL_IN, zt - 0.1)),
          "SteelGrey")
    fr = g.face_frame("+X", x1 - 0.05)
    for v0, v1 in ((0.8, 1.25), (1.45, 1.9)):
        m.sticker(g.rounded_rect(-1.05, 1.05, v0 - 0.08, v1 + 0.08, 0.08, 2), fr, "DarkGrey",
                  0.0, 0.04)
        m.sticker(g.rounded_rect(-0.97, 0.97, v0, v1, 0.06, 2), fr, "Cyan", 0.04, 0.08)
    # Trichter: oranger Kragen, Trichter, dicker Rand, graue Innenwand, Loch
    cx = (hx0 + x1) / 2 - 0.05

    def sq(sz, z):
        return g.rect_ring(cx - sz / 2, cx + sz / 2, -sz / 2, sz / 2, z)

    zc0, zc1 = zt - 0.02, zt + 0.32
    zf1 = zt + 1.05
    zr0, zr1 = zf1 - 0.05, zf1 + 0.36
    m.add(g.loft_rings([sq(2.3, zc0), sq(2.3, zc1), sq(1.5, zc1), sq(1.5, zc0)]), "Orange")
    m.add(g.loft_rings([sq(2.3, zc1 - 0.01), sq(3.0, zf1), sq(2.55, zf1), sq(1.45, zc1 + 0.12)]),
          "Orange")
    m.add(g.loft_rings([sq(1.43, zc1 + 0.13), sq(2.53, zf1 + 0.02), sq(2.47, zf1 + 0.02),
                        sq(1.38, zc1 + 0.16)]), "SteelLight")
    m.add(g.box((1.48, 1.48, 0.05), (cx, 0, zc1 + 0.12)), "Black")
    m.add(g.loft_rings([sq(3.15, zr0), sq(3.15, zr1), sq(2.45, zr1), sq(2.45, zr0)]),
          "SteelGrey")
    # je eine Leuchtleiste mittig auf jeder Randseite
    zl = (zr0 + zr1) / 2
    for nrm, pos in (("+X", cx + 1.575), ("-X", cx - 1.575)):
        m.sticker(g.rounded_rect(-0.48, 0.48, zl - 0.07, zl + 0.07, 0.05, 2),
                  g.face_frame(nrm, pos), "Cyan", 0.0, 0.05)
    for nrm, pos in (("+Y", 1.575), ("-Y", -1.575)):
        m.sticker(g.rounded_rect(-0.48, 0.48, zl - 0.07, zl + 0.07, 0.05, 2),
                  g.face_frame(nrm, pos, (cx, 0)), "Cyan", 0.0, 0.05)
    # Winkel auf dem Band Richtung Trichter
    top = g.face_frame("+Z", HB)
    for ax in (-2.15, -1.3, -0.45):
        m.sticker([(u + ax, v) for u, v in g.chevron(0.62, 1.4, 0.38)], top, "Yellow", 0.01, 0.04)
    return m


def ore_chunk(name, seed, radius):
    m = g.Model(name)
    bm = g.rock(radius, (0, 0, 0), seed, squash=(1.15, 0.95, 0.8), subdiv=1, jitter=0.26)
    zmin = -radius * 0.42
    for v in bm.verts:
        if v.co.z < zmin:
            v.co.z = zmin
    bmesh.ops.translate(bm, vec=(0, 0, -zmin), verts=bm.verts)
    m.add(bm, "OreRock")
    return m


MODELS = {
    "ConveyorStraight": lambda: straight("ConveyorStraight", 8.0, [-2.75, 2.75], [-1.7, 1.7],
                                         hazard=(-2.2, -0.55), plate=(0.65, 2.1)),
    "ConveyorSegment": lambda: straight("ConveyorSegment", 4.0, [0.0], [0.0], end_plates=False),
    "ConveyorCurve": lambda: curve("ConveyorCurve"),
    "ConveyorCurveLeft": lambda: curve("ConveyorCurveLeft", mirror=True),
    "ConveyorEnd": lambda: end_piece("ConveyorEnd"),
    "OreChunkA": lambda: ore_chunk("OreChunkA", 11, 0.55),
    "OreChunkB": lambda: ore_chunk("OreChunkB", 23, 0.36),
    "OreChunkC": lambda: ore_chunk("OreChunkC", 37, 0.47),
}

FILES = {
    "conveyor_straight": ["ConveyorStraight"],
    "conveyor_segment": ["ConveyorSegment"],
    "conveyor_curve": ["ConveyorCurve"],
    "conveyor_curve_left": ["ConveyorCurveLeft"],
    "conveyor_end": ["ConveyorEnd"],
    "ore_chunk": ["OreChunkA", "OreChunkB", "OreChunkC"],
}


def main():
    g.reset_scene()
    models_dir, preview_dir = g.out_dirs()
    sc = bpy.context.scene
    built = {}
    for name, fn in MODELS.items():
        coll = bpy.data.collections.new(name)
        sc.collection.children.link(coll)
        built[name] = fn().build(collection=coll)
    if "--no-export" not in sys.argv:
        for fname, names in FILES.items():
            objs = [o for n in names for o in built[n]]
            g.export_model(objs, os.path.join(models_dir, fname))
            mn, mx = g.bounds(objs)
            print(f"{fname}: {len(objs)} Objekte, {g.tri_count(objs)} Dreiecke, "
                  f"Groesse {tuple(round(v, 2) for v in (mx - mn))}")

    # Aufstellung in der .blend-Datei wie im Referenzbild: gerade | Kurve | Ende
    layout = {"ConveyorStraight": (-9.0, 0, 0), "ConveyorCurve": (2.0, 2.0, 0),
              "ConveyorEnd": (9.5, 4.0, 0), "ConveyorSegment": (-12, 14, 0),
              "ConveyorCurveLeft": (-2, 14, 0), "OreChunkA": (6, 14, 0),
              "OreChunkB": (8, 14, 0), "OreChunkC": (10, 14, 0)}
    for n, off in layout.items():
        for o in built[n]:
            o.location = off
    deco = bpy.data.collections.new("Deko_BrockenAufBand")
    sc.collection.children.link(deco)
    for n, p in (("OreChunkA", (-11.6, 0.3, HB)), ("OreChunkC", (-9.6, -0.4, HB)),
                 ("OreChunkB", (-8.8, 0.6, HB)), ("OreChunkA", (-6.6, -0.1, HB))):
        for o in built[n]:
            dup = o.copy()
            dup.name = "Deko_" + o.name
            dup.location = p
            deco.objects.link(dup)
    front_row = ["ConveyorStraight", "ConveyorCurve", "ConveyorEnd"]
    if "--no-blend" not in sys.argv:
        g.save_blend(os.path.join(models_dir, "conveyor.blend"))

    if "--render" in sys.argv:
        g.setup_render()
        for n in built:
            if n not in front_row:
                bpy.data.collections[n].hide_render = True
        vis = [o for n in front_row for o in built[n]] + list(deco.objects)
        p = lambda f: os.path.join(preview_dir, f)
        g.render_view(vis, p("conveyor_iso.png"), "iso", azimuth=-35, elevation=35)
        g.render_view(vis, p("conveyor_front.png"), "front")
        g.render_view(vis, p("conveyor_back.png"), "back")
        g.render_view(vis, p("conveyor_top.png"), "top")
        g.render_view(built["ConveyorStraight"] + list(deco.objects), p("conveyor_closeup.png"),
                      "iso", azimuth=-30, elevation=28, margin=0.8, focus=(-9.0, 0, 1.5))
        g.render_view(built["ConveyorEnd"], p("conveyor_end_iso.png"), "iso", azimuth=-60,
                      elevation=28, margin=1.0)
        g.render_view(built["ConveyorEnd"], p("conveyor_end_face.png"), "iso", azimuth=70,
                      elevation=20, margin=1.0)


if __name__ == "__main__":
    main()
