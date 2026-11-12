"""Basis aus Raum-Modulen nach referenz/bilder/gebaeude/basis-01.jpg.

Modelle:
- BaseHall  Start-Halle (Raum 1): 16 x 12 Studs, 12,6 hoch (+ Antenne).
            Tuer als eigene Gruppe (BaseHall_Door_*), Verbindungsgaenge links/rechts.
- BaseRoom  Gesperrter Raum (8,8 x 9,6 Studs) mit Rolltor (BaseRoom_Shutter_*).
            Steht links und rechts neben der Halle (x = -13 / +13, y = -0,2).
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import bpy  # noqa: E402  (bpy vor bmesh laden)
from mathutils import Matrix  # noqa: E402

import gmt_lib as g  # noqa: E402

ROOM_POS = 13.0
ROOM_Y = -0.2
ROOM_W, ROOM_D = 8.8, 9.6
ROOM_ZB, ROOM_ZT = 1.4, 9.4


def hex_bolt(m, normal, pos, u, v, r=0.21, center=(0.0, 0.0)):
    fr = g.face_frame(normal, pos, center)
    m.add(g.prism(g.circle2d(r, 6, (u, v)), 0.0, 0.12, fr, bevel=0.02), "SteelLight")


def foot(m, x, y, size):
    m.add(g.box((size, size, 0.3), (x, y, 0.15), bevel=0.08), "TreadPlate")
    for dx in (-1, 1):
        for dy in (-1, 1):
            m.add(g.cylinder(0.13, 0.1, (x + dx * (size / 2 - 0.3), y + dy * (size / 2 - 0.3),
                                         0.33), segs=6), "SteelLight")


def hazard(m, normal, pos, u0, u1, v0, v1, stripe=0.38, center=(0.0, 0.0)):
    fr = g.face_frame(normal, pos, center)
    m.sticker([(u0, v0), (u1, v0), (u1, v1), (u0, v1)], fr, "Black", 0.008, 0.035)
    for p in g.hazard_stripes(u0, u1, v0, v1, stripe, stripe):
        m.sticker(p, fr, "Yellow", 0.02, 0.05)


def cyan_panel(m, normal, pos, u, v, w=0.5, h=0.95, center=(0.0, 0.0)):
    fr = g.face_frame(normal, pos, center)
    m.add(g.prism(g.rounded_rect(u - w / 2 - 0.16, u + w / 2 + 0.16, v - h / 2 - 0.16,
                                 v + h / 2 + 0.16, 0.08, 1), 0.0, 0.14, fr, bevel=0.03),
          "SteelGrey")
    m.add(g.prism(g.rounded_rect(u - w / 2, u + w / 2, v - h / 2, v + h / 2, 0.06, 1),
                  0.14, 0.22, fr), "Cyan")


def ring_in_face(m, normal, pos, outer, inner, w0, w1, mat, group=None):
    fr = g.face_frame(normal, pos)
    m.add(g.loft_rings([g.poly_ring(outer, w0, fr), g.poly_ring(outer, w1, fr),
                        g.poly_ring(inner, w1, fr), g.poly_ring(inner, w0, fr)]), mat, group)


def build_hall():
    m = g.Model("BaseHall")
    X0, X1, Y0, Y1 = -8.0, 8.0, -6.0, 6.0
    ZB, ZT = 1.0, 12.6
    ZF = ZT - 1.65               # Unterkante Dachrahmen (13 % der Hoehe)
    P = 1.2
    # Waende (orange), dunkler Sockelstreifen, graues Rahmenband
    m.add(g.box_minmax((X0 + 0.25, Y0 + 0.25, ZB + 1.0), (X1 - 0.25, Y1 - 0.25, ZF + 0.05)),
          "Orange")
    m.add(g.box_minmax((X0 + 0.3, Y0 + 0.3, ZB), (X1 - 0.3, Y1 - 0.3, ZB + 0.62)), "SteelDark")
    m.add(g.loft_rings([g.rect_ring(X0 + 0.1, X1 - 0.1, Y0 + 0.1, Y1 - 0.1, ZB + 0.6),
                        g.rect_ring(X0 + 0.1, X1 - 0.1, Y0 + 0.1, Y1 - 0.1, ZB + 1.05),
                        g.rect_ring(X0 + 0.6, X1 - 0.6, Y0 + 0.6, Y1 - 0.6, ZB + 1.05),
                        g.rect_ring(X0 + 0.6, X1 - 0.6, Y0 + 0.6, Y1 - 0.6, ZB + 0.6)]),
          "SteelGrey")
    # Eckpfeiler als durchgehende Saeulen bis zum Boden (Beine buendig)
    for x in (X0 + P / 2 - 0.07, X1 - P / 2 + 0.07):
        for y in (Y0 + P / 2 - 0.07, Y1 - P / 2 + 0.07):
            m.add(g.box_minmax((x - P / 2, y - P / 2, 0.28), (x + P / 2, y + P / 2, ZF + 0.02),
                               bevel=0.2), "SteelGrey")
            foot(m, x, y, 2.2)
            sx = 1 if x > 0 else -1
            hex_bolt(m, "-Y" if y < 0 else "+Y", y + (P / 2 if y > 0 else -P / 2), x if y < 0 else -x,
                     ZB + 0.82)
            hex_bolt(m, "+X" if sx > 0 else "-X", x + sx * P / 2, y if sx > 0 else -y, ZB + 0.82)
    # dicker Dachrahmen mit breiter, heller 45-Grad-Fase
    C, RW = 0.8, 1.6
    m.add(g.loft_rings([g.rect_ring(X0, X1, Y0, Y1, ZF), g.rect_ring(X0, X1, Y0, Y1, ZT - C),
                        g.rect_ring(X0 + RW, X1 - RW, Y0 + RW, Y1 - RW, ZT - C),
                        g.rect_ring(X0 + RW, X1 - RW, Y0 + RW, Y1 - RW, ZF)]), "SteelGrey")
    m.add(g.loft_rings([g.rect_ring(X0, X1, Y0, Y1, ZT - C - 0.001),
                        g.rect_ring(X0 + C, X1 - C, Y0 + C, Y1 - C, ZT),
                        g.rect_ring(X0 + RW, X1 - RW, Y0 + RW, Y1 - RW, ZT),
                        g.rect_ring(X0 + RW, X1 - RW, Y0 + RW, Y1 - RW, ZT - C - 0.001)]),
          "SteelLight")
    zroof = ZT - 0.5
    m.add(g.box_minmax((X0 + RW - 0.02, Y0 + RW - 0.02, ZF), (X1 - RW + 0.02, Y1 - RW + 0.02, zroof)),
          "Orange")

    # --- Vorderseite ---
    fy = Y0 + 0.25
    frd = g.face_frame("-Y", fy)
    door_out = g.chamfer_rect(-3.1, 3.1, ZB, 8.8, 0.5, top_only=True)
    door_in = g.chamfer_rect(-2.55, 2.55, ZB + 0.3, 8.25, 0.35, top_only=True)
    ring_in_face(m, "-Y", fy, door_out, door_in, -0.05, 0.45, "SteelGrey")
    for u0, u1 in ((-2.6, -0.04), (0.04, 2.6)):
        half = g.clip_rect(door_in, u0, u1, -100, 100)
        m.add(g.prism(half, -0.15, 0.15, frd), "DarkGrey", group="Door")
    # flache Rampe (ca. 17 Grad) aus Riffelblech
    fr_yz = g.frame_at((0, 0, 0), (0, 1, 0), (0, 0, 1))      # u = y, v = z, w = x
    sill = ZB + 0.3
    y_top, y_bot = fy - 0.45, fy - 0.45 - sill / math.tan(math.radians(17))
    ramp = [(y_top, sill), (y_top, sill - 0.28), (y_bot + 0.6, 0.0), (y_bot, 0.0), (y_bot, 0.12)]
    m.add(g.prism(ramp, -2.7, 2.7, fr_yz, bevel=0.04), "TreadPlate")
    slope = math.atan2(sill, y_top - y_bot)
    for t in (0.1, 0.85):
        yy = y_top - (y_top - y_bot) * t
        zz = sill - sill * t
        for x in (-2.35, 2.35):
            mat = Matrix.Translation((x, yy, zz + 0.02)) @ Matrix.Rotation(slope, 4, "X")
            m.add(g.cylinder(0.14, 0.1, (0, 0, 0), segs=6, matrix=mat), "SteelLight")
    # Bullaugen (20 % kleiner), Glas blassblau
    for u in (-5.3, 5.3):
        ring_in_face(m, "-Y", fy, g.circle2d(0.92, 24, (u, 7.3)), g.circle2d(0.62, 24, (u, 7.3)),
                     -0.05, 0.32, "SteelGrey")
        m.add(g.prism(g.circle2d(0.64, 24, (u, 7.3)), -0.05, 0.1, frd), "Glass")
    cyan_panel(m, "-Y", fy, 4.3, 4.3, 0.55, 1.05)
    # Warnstreifen vorne und um die Ecken auf die Seiten
    hz0, hz1 = ZB + 1.1, ZB + 1.95
    hazard(m, "-Y", fy, X0 + P - 0.05, -3.15, hz0, hz1)
    hazard(m, "-Y", fy, 3.15, X1 - P + 0.05, hz0, hz1)
    hazard(m, "+X", X1 - 0.25, Y0 + P - 0.05, Y1 - P + 0.05, hz0, hz1)
    hazard(m, "-X", X0 + 0.25, -(Y1 - P + 0.05), -(Y0 + P - 0.05), hz0, hz1)

    # --- Dach-Aufbauten ---
    for x in (-5.0, -3.7):            # spitz zulaufende, hohle Schornsteine
        c = (x, 3.2)
        m.add(g.loft_rings([g.circle_ring(0.58, zroof, 14, c), g.circle_ring(0.42, zroof + 1.45, 14, c),
                            g.circle_ring(0.28, zroof + 1.45, 14, c), g.circle_ring(0.3, zroof + 1.1, 14, c)]),
              "SteelGrey")
        m.add(g.cylinder(0.31, 0.04, (x, 3.2, zroof + 1.1), segs=14), "Black")
    for x in (-4.2, 4.0):             # flache Dachplatten
        m.add(g.box((2.05, 2.05, 0.35), (x, -2.0, zroof + 0.17), bevel=0.12), "SteelGrey")
    # Satellitenschuessel: dicker Mast auf breiter Platte, schaut nach +X und etwas nach hinten
    dx, dy = 4.4, 2.4
    m.add(g.cylinder(1.2, 0.25, (dx, dy, zroof + 0.12), segs=20, bevel=0.05), "SteelGrey")
    m.add(g.cylinder(0.36, 2.3, (dx, dy, zroof + 1.4), segs=12), "SteelGrey")
    m.add(g.box((0.9, 0.9, 0.5), (dx, dy, zroof + 2.6), bevel=0.1), "SteelDark")
    dish = (Matrix.Translation((dx + 0.25, dy, zroof + 2.85)) @ Matrix.Rotation(math.radians(20), 4, "Z")
            @ Matrix.Rotation(math.radians(45), 4, "Y"))
    bowl = g.loft_rings([g.circle_ring(0.35, 0.0, 24), g.circle_ring(1.6, 0.55, 24),
                         g.circle_ring(1.48, 0.55, 24), g.circle_ring(0.26, 0.12, 24)])
    m.add(g.transform_bm(bowl, dish), "SteelGrey")
    m.add(g.cylinder(0.08, 2.4, (0, 0, 1.25), segs=6, matrix=dish), "SteelLight")
    m.add(g.cylinder(0.2, 0.3, (0, 0, 2.45), segs=8, matrix=dish), "SteelDark")

    # --- Verbindungsgaenge zu den Nachbarraeumen (schiefergrau) ---
    rz_top = ROOM_ZT - 0.18 * (ROOM_ZT - ROOM_ZB)
    rz_bot = rz_top - 0.71 * (ROOM_ZT - ROOM_ZB)
    for s in (-1, 1):
        xa, xb = sorted((s * (X1 - 0.3), s * (ROOM_POS - ROOM_W / 2 + 0.25)))
        m.add(g.box_minmax((xa, ROOM_Y - 2.8, rz_bot), (xb, ROOM_Y + 2.8, rz_top), bevel=0.1), "Slate")
        m.add(g.box_minmax((xa + 0.15, ROOM_Y - 3.0, rz_top - 0.35), (xb - 0.15, ROOM_Y + 3.0, rz_top + 0.05),
                           bevel=0.06), "SteelGrey")
    return m


def build_room():
    m = g.Model("BaseRoom")
    X0, X1 = -ROOM_W / 2, ROOM_W / 2
    Y0, Y1 = -ROOM_D / 2, ROOM_D / 2
    ZB, ZT = ROOM_ZB, ROOM_ZT
    P = 1.25
    m.add(g.box_minmax((X0 + 0.2, Y0 + 0.2, ZB + 0.4), (X1 - 0.2, Y1 - 0.2, ZT - 0.9)), "Orange")
    m.add(g.box_minmax((X0 + 0.12, Y0 + 0.12, ZT - 1.05), (X1 - 0.12, Y1 - 0.12, ZT), bevel=0.42),
          "OrangeLight")
    m.add(g.loft_rings([g.rect_ring(X0 + 0.08, X1 - 0.08, Y0 + 0.08, Y1 - 0.08, ZB),
                        g.rect_ring(X0 + 0.08, X1 - 0.08, Y0 + 0.08, Y1 - 0.08, ZB + 0.45),
                        g.rect_ring(X0 + 0.5, X1 - 0.5, Y0 + 0.5, Y1 - 0.5, ZB + 0.45),
                        g.rect_ring(X0 + 0.5, X1 - 0.5, Y0 + 0.5, Y1 - 0.5, ZB)]), "SteelGrey")
    # dicke Eckpfeiler mit Fasen, durchgehend bis zum Fuss
    for x in (X0 + P / 2 - 0.05, X1 - P / 2 + 0.05):
        for y in (Y0 + P / 2 - 0.05, Y1 - P / 2 + 0.05):
            m.add(g.box_minmax((x - P / 2, y - P / 2, 0.28), (x + P / 2, y + P / 2, ZT - 0.1),
                               bevel=0.3), "SteelGrey")
            foot(m, x, y, 2.0)
            sx = 1 if x > 0 else -1
            hex_bolt(m, "-Y" if y < 0 else "+Y", y + (P / 2 if y > 0 else -P / 2), x if y < 0 else -x,
                     ZB + 0.22, r=0.2)
            hex_bolt(m, "+X" if sx > 0 else "-X", x + sx * P / 2, y if sx > 0 else -y, ZB + 0.22, r=0.2)
    fy = Y0 + 0.2
    fr = g.face_frame("-Y", fy)
    # Rolltor direkt in der orangen Wand: dunkle Nische + 6 breite Lamellen mit tiefen Fugen
    su0, su1 = X0 + P + 0.1, X1 - P - 0.1
    sz0, sz1 = ZB + 1.3, ZT - 1.65
    m.add(g.prism([(su0, sz0), (su1, sz0), (su1, sz1), (su0, sz1)], -0.3, 0.01, fr), "Black",
          group="Shutter")
    n = 6
    h = (sz1 - sz0) / n
    for k in range(n):
        v0 = sz0 + k * h + 0.06
        v1 = v0 + h - 0.16
        m.add(g.prism([(su0 + 0.05, v0), (su1 - 0.05, v0), (su1 - 0.05, v1), (su0 + 0.05, v1)],
                      -0.05, 0.16, fr, bevel=0.05), "DarkGrey", group="Shutter")
    # eckiger Rolltor-Kasten (hellorange, gefast)
    m.add(g.prism([(su0 - 0.15, sz1), (su1 + 0.15, sz1), (su1 + 0.15, sz1 + 0.7), (su0 - 0.15, sz1 + 0.7)],
                  0.0, 0.45, fr, bevel=0.12), "OrangeLight", group="Shutter")
    # Warnstreifen unter dem Tor, um die Ecken herum auf die Seiten
    hz0, hz1 = ZB + 0.5, ZB + 1.15
    hazard(m, "-Y", fy, X0 + P - 0.05, X1 - P + 0.05, hz0, hz1, stripe=0.34)
    for nrm, pos, sgn in (("+X", X1 - 0.2, 1), ("-X", X0 + 0.2, -1)):
        u0, u1 = sorted((sgn * (Y0 + P - 0.05), sgn * (Y1 - P + 0.05)))
        hazard(m, nrm, pos, u0, u1, hz0, hz1, stripe=0.34)
    # Leuchtfeld am rechten Pfeiler
    cyan_panel(m, "-Y", Y0 - 0.05, X1 - P / 2 + 0.05, 4.5, 0.45, 1.0)
    return m


def main():
    g.reset_scene()
    models_dir, preview_dir = g.out_dirs()
    sc = bpy.context.scene
    ch = bpy.data.collections.new("BaseHall")
    sc.collection.children.link(ch)
    hall = build_hall().build(collection=ch)
    cr = bpy.data.collections.new("BaseRoom")
    sc.collection.children.link(cr)
    room = build_room().build(collection=cr)
    if "--no-export" not in sys.argv:
        g.export_model(hall, os.path.join(models_dir, "base_hall"))
        g.export_model(room, os.path.join(models_dir, "base_room"))
        for n, objs in (("base_hall", hall), ("base_room", room)):
            mn, mx = g.bounds(objs)
            print(f"{n}: {len(objs)} Objekte, {g.tri_count(objs)} Dreiecke, "
                  f"Groesse {tuple(round(v, 2) for v in (mx - mn))}")
    # Aufstellung wie im Bild: Raum links, Halle, Raum rechts
    for o in room:
        o.location = (-ROOM_POS, ROOM_Y, 0)
    cr2 = bpy.data.collections.new("BaseRoom_Rechts")
    sc.collection.children.link(cr2)
    room2 = []
    for o in room:
        d = o.copy()
        d.name = o.name + "_Rechts"
        d.location = (ROOM_POS, ROOM_Y, 0)
        cr2.objects.link(d)
        room2.append(d)
    if "--no-blend" not in sys.argv:
        g.save_blend(os.path.join(models_dir, "base.blend"))
    if "--render" in sys.argv:
        g.setup_render()
        allo = hall + room + room2
        p = lambda n: os.path.join(preview_dir, n)
        g.render_view(allo, p("base_iso.png"), "iso", azimuth=-38, elevation=30)
        g.render_view(allo, p("base_front.png"), "front")
        g.render_view(allo, p("base_side.png"), "side")
        g.render_view(allo, p("base_top.png"), "top")
        g.render_view(hall + room, p("base_closeup.png"), "iso", azimuth=-30, elevation=25,
                      margin=0.7, focus=(-6, -6, 6))
        g.render_view(hall, p("base_roof.png"), "iso", azimuth=-20, elevation=40, margin=0.75,
                      focus=(1.5, 0, 11.5))


if __name__ == "__main__":
    main()
