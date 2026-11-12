"""Foerderband-Set nach referenz/bilder/gebaeude/foerderband-01.jpg.

Modelle (Flussrichtung = Pfeilrichtung):
- ConveyorStraight  12 x 4 Studs, wie im Bild (Fluss +X)
- ConveyorSegment    4 x 4 Studs, gerade Enden, zum Aneinanderreihen (belt_segment)
- ConveyorCurve      Rechtskurve 90 Grad, Grundflaeche 8 x 8 (rein von -Y, raus nach +X)
- ConveyorCurveLeft  gespiegelt (rein von -Y, raus nach -X)
- ConveyorEnd        8 x 4 Studs, Bandstueck + Trichter (Fluss +X in den Trichter)
- OreChunkA/B/C      Erzbrocken, wie sie auf dem Band liegen

Aufruf:  blender -b -P build_conveyor.py   oder   python build_conveyor.py
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import bpy  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

import gmt_lib as g  # noqa: E402

HB = 3.4            # Oberkante Band
BW = 1.5            # halbe Bandbreite
RAIL_IN, RAIL_OUT = 1.5, 1.82
RAIL_Z0, RAIL_Z1 = HB - 0.62, HB + 0.22
SKIRT_Z0 = HB - 1.65
LEG_Y0, LEG_Y1 = 1.6, 2.16
LEG_X = 0.72        # Beinbreite in Laufrichtung


def xz_frame():
    """(u,v,w) -> (x, -w, z): Profil in XZ, Extrusion entlang -Y."""
    return g.frame_at((0, 0, 0), (1, 0, 0), (0, 0, 1))


def prism_xz(poly, y0, y1, bevel=0.0):
    return g.prism(poly, -y1, -y0, xz_frame(), bevel=bevel)


def add_leg(m, x, side, top=None, matrix=None):
    """Bein mit Fuss und zwei Bolzen. side = +1 (hinten) / -1 (vorne)."""
    top = RAIL_Z1 - 0.04 if top is None else top
    y0, y1 = sorted((side * LEG_Y0, side * LEG_Y1))
    mat = matrix or Matrix.Identity(4)
    m.add(g.box_minmax((x - LEG_X / 2, y0, 0.28), (x + LEG_X / 2, y1, top),
                       bevel=0.07, matrix=mat), "Orange")
    yc = (y0 + y1) / 2
    m.add(g.box((1.05, 0.95, 0.3), (x, yc, 0.15), bevel=0.06, matrix=mat),
          "SteelGrey")
    # Kappe oben
    m.add(g.box((LEG_X + 0.08, 0.62, 0.14), (x, yc, top + 0.02), bevel=0.04,
                matrix=mat), "SteelGrey")
    yo = side * (LEG_Y1 + 0.03)
    for z in (top - 0.32, top - 0.78):
        m.add(g.cylinder(0.1, 0.1, (x, yo, z), axis="Y", segs=8, matrix=mat),
              "SteelLight")
    # Bolzen am Fuss
    for dx in (-0.36, 0.36):
        m.add(g.cylinder(0.08, 0.08, (x + dx, yc + side * 0.3, 0.32), segs=8,
                         matrix=mat), "SteelLight")


def straight(name, L, legs_x, arrows_x, hazard=True, plate=True,
             round_ends=True):
    m = g.Model(name)
    x0, x1 = -L / 2, L / 2
    # Band (dunkel), Enden um die Rollen gerundet
    belt = g.stadium(x0 + 0.02, x1 - 0.02, HB - 0.5, HB, segs=6,
                     round_left=round_ends, round_right=round_ends)
    m.add(prism_xz(belt, -BW, BW), "DarkGrey")
    # Unterbau unter dem Band
    m.add(g.box_minmax((x0 + 0.35, -BW - 0.02, HB - 1.55),
                       (x1 - 0.35, BW + 0.02, HB - 0.45)), "DarkGrey")
    # Seitenschienen
    rail = g.stadium(x0, x1, RAIL_Z0, RAIL_Z1, segs=6, round_left=round_ends,
                     round_right=round_ends)
    for s in (-1, 1):
        y0, y1 = sorted((s * RAIL_IN, s * RAIL_OUT))
        m.add(prism_xz(rail, y0, y1, bevel=0.05), "SteelGrey")
        # Bolzen auf der Schiene
        n = max(2, int((L - 1.0) / 1.25) + 1)
        for i in range(n):
            bx = x0 + 0.5 + i * (L - 1.0) / (n - 1)
            if any(abs(bx - lx) < 0.6 for lx in legs_x):
                continue
            m.add(g.cylinder(0.085, 0.1, (bx, s * (RAIL_OUT + 0.03), HB - 0.2),
                             axis="Y", segs=8), "SteelLight")
        # Schuerze unter der Schiene
        sy0, sy1 = sorted((s * (RAIL_OUT - 0.32), s * (RAIL_OUT - 0.1)))
        m.add(g.box_minmax((x0 + 0.5, sy0, SKIRT_Z0), (x1 - 0.5, sy1, RAIL_Z0 + 0.05),
                           bevel=0.03), "Orange")
        face = g.face_frame("-Y" if s < 0 else "+Y", s * (RAIL_OUT - 0.1))
        if hazard:
            u0, u1 = x0 + 0.95, x0 + 0.95 + min(3.2, L * 0.28)
            v0, v1 = SKIRT_Z0 + 0.18, RAIL_Z0 - 0.12
            m.add(g.prism([(u0, v0), (u1, v0), (u1, v1), (u0, v1)], 0, 0.03,
                          face), "Black")
            m.decal(g.hazard_stripes(u0, u1, v0, v1, 0.26, 0.26), face, 0.0,
                    0.05, "Yellow")
        if plate:
            v0, v1 = SKIRT_Z0 + 0.2, RAIL_Z0 - 0.12
            trap = [(-0.85, v0), (0.85, v0), (1.0, v1), (-1.0, v1)]
            m.add(g.prism(trap, 0, 0.06, face, bevel=0.015), "SteelLight")
            for u in (-0.72, 0.72):
                for v in (v0 + 0.12, v1 - 0.12):
                    m.add(g.prism(g.rounded_rect(u - 0.05, u + 0.05, v - 0.05,
                                                 v + 0.05, 0.02, 1), 0.06, 0.1,
                                  face), "SteelGrey")
        for lx in legs_x:
            add_leg(m, lx, s)
    # Pfeile auf dem Band
    top = g.face_frame("+Z", HB)
    for ax in arrows_x:
        poly = [(u + ax, v) for u, v in g.arrow(1.9, 1.15)]
        m.add(g.prism(poly, 0, 0.03, top), "Yellow")
    return m


def curve(name, mirror=False):
    """Rechtskurve: Bogenmittelpunkt (4,-4), Mittellinie r=6."""
    m = g.Model(name)
    cx, cy, rc = 4.0, -4.0, 6.0
    ri, ro = rc - BW, rc + BW
    a0, a1, segs = 90.0, 180.0, 18
    sec = lambda r0, r1, z0, z1, b=False: g.annular_sector(r0, r1, a0, a1, z0, z1, segs, (cx, cy))
    m.add(sec(ri, ro, HB - 0.5, HB), "DarkGrey")
    m.add(sec(ri + 0.02, ro - 0.02, HB - 1.55, HB - 0.45), "DarkGrey")
    for r0, r1 in ((ri - 0.32, ri), (ro, ro + 0.32)):
        m.add(sec(r0, r1, RAIL_Z0, RAIL_Z1), "SteelGrey")
    m.add(sec(ri - 0.22, ri, SKIRT_Z0, RAIL_Z0 + 0.05), "Orange")
    m.add(sec(ro, ro + 0.22, SKIRT_Z0, RAIL_Z0 + 0.05), "Orange")

    def at(theta, r):
        t = math.radians(theta)
        return Vector((cx + r * math.cos(t), cy + r * math.sin(t), 0))

    # Beine: Matrix dreht ein "gerades" Bein (x = tangential, y = radial)
    for theta, side in ((174, 1), (135, 1), (96, 1), (174, -1), (96, -1)):
        r_mid = rc  # Bein-Geometrie wird relativ zur Mittellinie gebaut
        p = at(theta, r_mid)
        mat = (Matrix.Translation(p)
               @ Matrix.Rotation(math.radians(theta - 90), 4, "Z"))
        add_leg(m, 0.0, side, matrix=mat)
    # Bolzen auf der Aussenschiene
    for theta in range(100, 180, 12):
        if any(abs(theta - lt) < 5 for lt in (174, 135, 96)):
            continue
        t = math.radians(theta)
        for r, s in ((ro + 0.35, 1), (ri - 0.35, -1)):
            if s < 0 and theta % 24:
                continue
            p = at(theta, r) + Vector((0, 0, HB - 0.2))
            mat = Matrix.Translation(p) @ Matrix.Rotation(t, 4, "Z")
            m.add(g.cylinder(0.085, 0.1, (0, 0, 0), axis="X", segs=8,
                             matrix=mat), "SteelLight")
    # Pfeil + Winkel entlang der Kurve (Fluss im Uhrzeigersinn)
    for theta, kind in ((168, "arrow"), (146, "chev"), (125, "chev"),
                        (104, "chev")):
        t = math.radians(theta)
        o = at(theta, rc) + Vector((0, 0, HB))
        u = (math.sin(t), -math.cos(t), 0)
        v = (math.cos(t), math.sin(t), 0)
        fr = g.frame_at(o, u, v)
        poly = g.arrow(1.7, 1.1) if kind == "arrow" else g.chevron(0.75, 1.3, 0.34)
        m.add(g.prism(poly, 0, 0.03, fr), "Yellow")
    if mirror:
        flip = Matrix.Scale(-1, 4, (1, 0, 0))
        for bm in m.parts.values():
            bm.transform(flip)
            bm.normal_update()
            import bmesh as _b
            _b.ops.reverse_faces(bm, faces=bm.faces)
    return m


def end_piece(name):
    m = g.Model(name)
    xb0, xb1 = -4.0, 1.0     # Bandteil
    hx0, hx1 = 0.45, 4.0     # Trichter-Koerper
    hy = 1.98
    belt = g.stadium(xb0 + 0.02, xb1, HB - 0.5, HB, segs=6, round_right=False)
    m.add(prism_xz(belt, -BW, BW), "DarkGrey")
    m.add(g.box_minmax((xb0 + 0.35, -BW - 0.02, HB - 1.55), (hx0, BW + 0.02, HB - 0.45)),
          "DarkGrey")
    rail = g.stadium(xb0, hx0 + 0.2, RAIL_Z0, RAIL_Z1, segs=6, round_right=False)
    for s in (-1, 1):
        y0, y1 = sorted((s * RAIL_IN, s * RAIL_OUT))
        m.add(prism_xz(rail, y0, y1, bevel=0.05), "SteelGrey")
        for bx in (xb0 + 0.5, -1.6, -0.4):
            m.add(g.cylinder(0.085, 0.1, (bx, s * (RAIL_OUT + 0.03), HB - 0.2),
                             axis="Y", segs=8), "SteelLight")
        sy0, sy1 = sorted((s * (RAIL_OUT - 0.32), s * (RAIL_OUT - 0.1)))
        m.add(g.box_minmax((xb0 + 0.5, sy0, SKIRT_Z0), (hx0, sy1, RAIL_Z0 + 0.05),
                           bevel=0.03), "Orange")
        face = g.face_frame("-Y" if s < 0 else "+Y", s * (RAIL_OUT - 0.1))
        u0, u1 = (-2.25, hx0 - 0.15) if s < 0 else (-hx0 + 0.15, 2.25)
        v0, v1 = SKIRT_Z0 + 0.15, RAIL_Z0 - 0.1
        m.add(g.prism([(u0, v0), (u1, v0), (u1, v1), (u0, v1)], 0, 0.03, face),
              "Black")
        m.decal(g.hazard_stripes(u0, u1, v0, v1, 0.26, 0.26), face, 0.0, 0.05,
                "Yellow")
        add_leg(m, -2.75, s)
    # Winkel auf dem Band Richtung Trichter
    top = g.face_frame("+Z", HB)
    for ax in (-3.0, -1.95, -0.9):
        m.add(g.prism([(u + ax, v) for u, v in g.chevron(0.62, 1.4, 0.32)], 0,
                      0.03, top), "Yellow")
    # --- Trichter-Koerper ---
    zt = HB + 0.22
    m.add(g.box_minmax((hx0 + 0.15, -hy + 0.15, 0.32), (hx1 - 0.15, hy - 0.15, zt - 0.1)),
          "Orange")
    m.add(g.box_minmax((hx0 - 0.05, -hy - 0.05, 0.0), (hx1 + 0.05, hy + 0.05, 0.34),
                       bevel=0.06), "SteelGrey")
    for x in (hx0 + 0.24, hx1 - 0.24):
        for y in (-hy + 0.24, hy - 0.24):
            m.add(g.box((0.5, 0.5, zt - 0.3), (x, y, 0.3 + (zt - 0.3) / 2), bevel=0.06),
                  "SteelGrey")
    # oberer Rahmen
    m.add(g.box_minmax((hx0, -hy, zt - 0.32), (hx1, hy, zt), bevel=0.05), "SteelGrey")
    # Leuchtfeld an der Stirnseite (+X)
    m.add(g.box_minmax((hx1 - 0.1, -1.45, 0.75), (hx1 + 0.08, 1.45, 2.55), bevel=0.05),
          "SteelGrey")
    for z0, z1 in ((0.95, 1.55), (1.75, 2.35)):
        m.add(g.box_minmax((hx1 + 0.04, -1.2, z0), (hx1 + 0.13, 1.2, z1), bevel=0.03),
              "Cyan")
    # Trichter oben: aussen orange, innen hell, Rand grau, Loch schwarz
    cxh = (hx0 + hx1) / 2

    def sq(s, z, c=(cxh, 0)):
        return [(c[0] - s / 2, c[1] - s / 2, z), (c[0] + s / 2, c[1] - s / 2, z),
                (c[0] + s / 2, c[1] + s / 2, z), (c[0] - s / 2, c[1] + s / 2, z)]

    zf0, zf1 = zt, zt + 1.25
    m.add(g.loft_rings([sq(3.0, zf0), sq(3.9, zf1), sq(3.5, zf1), sq(2.0, zf0 + 0.3)]), "Orange")
    m.add(g.loft_rings([sq(1.98, zf0 + 0.31), sq(3.48, zf1 - 0.01), sq(3.42, zf1 - 0.01),
                sq(1.92, zf0 + 0.33)]), "White")
    m.add(g.box((2.0, 2.0, 0.06), (cxh, 0, zf0 + 0.3)), "Black")
    m.add(g.loft_rings([sq(4.1, zf1 - 0.05), sq(4.1, zf1 + 0.22), sq(3.4, zf1 + 0.22),
                sq(3.4, zf1 - 0.05)]), "SteelGrey")
    # kleine Leuchten an den Ecken des Rands
    for y in (-1.6, 1.6):
        m.add(g.box((0.08, 0.5, 0.12), (cxh + 2.07, y, zf1 + 0.08)), "Cyan")
    for x in (cxh - 1.6, cxh + 1.6):
        m.add(g.box((0.5, 0.08, 0.12), (x, -2.07, zf1 + 0.08)), "Cyan")
    return m


def ore_chunk(name, seed, radius=0.55):
    m = g.Model(name)
    m.add(g.rock(radius, (0, 0, radius * 0.62), seed, squash=(1.1, 0.95, 0.75),
                 subdiv=2, jitter=0.13), "OreRock")
    return m


def main():
    g.reset_scene()
    models_dir, preview_dir = g.out_dirs()
    sc = bpy.context.scene

    built = {}
    defs = [
        ("ConveyorStraight", lambda: straight("ConveyorStraight", 12.0, [-4.6, 4.6],
                                              [-3.4, 0.0, 3.4])),
        ("ConveyorSegment", lambda: straight("ConveyorSegment", 4.0, [0.0], [0.0],
                                             hazard=False, plate=False,
                                             round_ends=False)),
        ("ConveyorCurve", lambda: curve("ConveyorCurve")),
        ("ConveyorCurveLeft", lambda: curve("ConveyorCurveLeft", mirror=True)),
        ("ConveyorEnd", lambda: end_piece("ConveyorEnd")),
        ("OreChunkA", lambda: ore_chunk("OreChunkA", 11, 0.6)),
        ("OreChunkB", lambda: ore_chunk("OreChunkB", 23, 0.48)),
        ("OreChunkC", lambda: ore_chunk("OreChunkC", 37, 0.72)),
    ]
    for name, fn in defs:
        coll = bpy.data.collections.new(name)
        sc.collection.children.link(coll)
        built[name] = fn().build(collection=coll)

    files = {
        "conveyor_straight": ["ConveyorStraight"],
        "conveyor_segment": ["ConveyorSegment"],
        "conveyor_curve": ["ConveyorCurve"],
        "conveyor_curve_left": ["ConveyorCurveLeft"],
        "conveyor_end": ["ConveyorEnd"],
        "ore_chunk": ["OreChunkA", "OreChunkB", "OreChunkC"],
    }
    if "--no-export" not in sys.argv:
        for fname, names in files.items():
            objs = [o for n in names for o in built[n]]
            g.export_fbx(objs, os.path.join(models_dir, fname + ".fbx"))
            print(f"{fname}: {len(objs)} Objekte, {g.tri_count(objs)} Dreiecke")

    # Aufstellung in der .blend-Datei. Vorne wie im Referenzbild:
    # gerade | Kurve | Ende; dahinter die Varianten.
    layout = {"ConveyorStraight": (-9.5, 0, 0), "ConveyorCurve": (3.0, 2.0, 0),
              "ConveyorEnd": (11.5, 4.0, 0), "ConveyorSegment": (-12, 14, 0),
              "ConveyorCurveLeft": (-2, 14, 0), "OreChunkA": (6, 14, 0),
              "OreChunkB": (8, 14, 0), "OreChunkC": (10, 14, 0)}
    for n, off in layout.items():
        for o in built[n]:
            o.location = off
    # ein paar Brocken auf dem geraden Band (nur Deko in der .blend/Vorschau)
    deco = bpy.data.collections.new("Deko_BrockenAufBand")
    sc.collection.children.link(deco)
    for n, p in (("OreChunkA", (-13.2, 0.2, HB)), ("OreChunkC", (-10.3, -0.3, HB)),
                 ("OreChunkB", (-9.3, 0.7, HB)), ("OreChunkA", (-6.0, -0.1, HB))):
        for o in built[n]:
            dup = o.copy()
            dup.name = "Deko_" + o.name
            dup.location = p
            deco.objects.link(dup)
    front_row = {"ConveyorStraight", "ConveyorCurve", "ConveyorEnd"}

    if "--no-blend" not in sys.argv:
        g.save_blend(os.path.join(models_dir, "conveyor.blend"))

    if "--render" in sys.argv:
        g.setup_render()
        for n in built:
            if n not in front_row:
                bpy.data.collections[n].hide_render = True
        vis = [o for n in front_row for o in built[n]] + list(deco.objects)
        g.render_view(vis, os.path.join(preview_dir, "conveyor_iso.png"), "iso",
                      azimuth=-35, elevation=35)
        g.render_view(vis, os.path.join(preview_dir, "conveyor_front.png"), "front")
        g.render_view(vis, os.path.join(preview_dir, "conveyor_top.png"), "top")
        st = built["ConveyorStraight"]
        g.render_view(st, os.path.join(preview_dir, "conveyor_closeup.png"), "iso",
                      azimuth=-30, elevation=28, margin=0.75)
        end = built["ConveyorEnd"]
        g.render_view(end, os.path.join(preview_dir, "conveyor_end_iso.png"), "iso",
                      azimuth=-50, elevation=30, margin=1.0)
        g.render_view(vis, os.path.join(preview_dir, "conveyor_back.png"), "back")


if __name__ == "__main__":
    main()
