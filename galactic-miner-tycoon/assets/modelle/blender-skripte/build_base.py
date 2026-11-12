"""Basis aus Raum-Modulen nach referenz/bilder/gebaeude/basis-01.jpg.

Modelle:
- BaseHall  Start-Halle (Raum 1): 16 x 12 Studs, ca. 14 hoch mit Antenne.
            Tuer als eigene Gruppe (BaseHall_Door_*), Verbindungsstutzen links/rechts.
- BaseRoom  Gesperrter Raum (8,8 x 11 Studs) mit Rolltor (BaseRoom_Shutter_*).
            Steht links und rechts neben der Halle (x = -13 / +13, y = -0,5).
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import bpy  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

import gmt_lib as g  # noqa: E402

ROOM_POS = 13.0
ROOM_Y = -0.5


def foot_leg(m, x, y, z_top, size=1.15, foot=2.1):
    m.add(g.box((size, size, z_top - 0.3), (x, y, 0.3 + (z_top - 0.3) / 2), bevel=0.12),
          "SteelGrey")
    m.add(g.box((foot, foot, 0.3), (x, y, 0.15), bevel=0.08), "SteelGrey")
    for dx in (-1, 1):
        for dy in (-1, 1):
            m.add(g.cylinder(0.13, 0.1, (x + dx * (foot / 2 - 0.3), y + dy * (foot / 2 - 0.3),
                                         0.33), segs=8), "SteelLight")


def hazard(m, normal, pos, u0, u1, v0, v1, stripe=0.38):
    fr = g.face_frame(normal, pos)
    m.add(g.prism([(u0, v0), (u1, v0), (u1, v1), (u0, v1)], 0.0, 0.03, fr), "Black")
    m.decal(g.hazard_stripes(u0, u1, v0, v1, stripe, stripe), fr, 0.0, 0.05, "Yellow")


def cyan_panel(m, normal, pos, u, v, w=0.5, h=0.95):
    fr = g.face_frame(normal, pos)
    m.add(g.prism(g.rounded_rect(u - w / 2 - 0.15, u + w / 2 + 0.15, v - h / 2 - 0.15,
                                 v + h / 2 + 0.15, 0.08, 1), 0.0, 0.12, fr), "SteelGrey")
    m.add(g.prism(g.rounded_rect(u - w / 2, u + w / 2, v - h / 2, v + h / 2, 0.06, 1),
                  0.12, 0.2, fr), "Cyan")


def ring_in_face(m, normal, pos, outer, inner, w0, w1, mat, group=None):
    fr = g.face_frame(normal, pos)
    m.add(g.loft_rings([g.poly_ring(outer, w0, fr), g.poly_ring(outer, w1, fr),
                        g.poly_ring(inner, w1, fr), g.poly_ring(inner, w0, fr)]), mat, group)


def circle2d(r, n=24, c=(0, 0)):
    return [(c[0] + r * math.cos(2 * math.pi * k / n), c[1] + r * math.sin(2 * math.pi * k / n))
            for k in range(n)]


def build_hall():
    m = g.Model("BaseHall")
    X0, X1, Y0, Y1 = -8.0, 8.0, -6.0, 6.0
    ZB, ZT = 1.8, 12.6          # Unterkante / Oberkante Koerper
    P = 1.15                     # Eckpfeiler
    # Waende
    m.add(g.box_minmax((X0 + 0.25, Y0 + 0.25, ZB + 0.3), (X1 - 0.25, Y1 - 0.25, ZT - 0.9)), "Orange")
    # Eckpfeiler
    for x in (X0 + P / 2 - 0.07, X1 - P / 2 + 0.07):
        for y in (Y0 + P / 2 - 0.07, Y1 - P / 2 + 0.07):
            m.add(g.box((P, P, ZT - ZB - 0.25), (x, y, ZB + 0.02 + (ZT - ZB - 0.25) / 2),
                        bevel=0.2), "SteelGrey")
    # unteres Rahmenband
    m.add(g.loft_rings([g.rect_ring(X0, X1, Y0, Y1, ZB), g.rect_ring(X0, X1, Y0, Y1, ZB + 0.45),
                        g.rect_ring(X0 + 0.5, X1 - 0.5, Y0 + 0.5, Y1 - 0.5, ZB + 0.45),
                        g.rect_ring(X0 + 0.5, X1 - 0.5, Y0 + 0.5, Y1 - 0.5, ZB)]), "SteelGrey")
    # oberer Rahmen: grauer Balken + heller Fasen-Rand
    zr0, zr1, zr2 = ZT - 1.05, ZT - 0.35, ZT
    m.add(g.loft_rings([g.rect_ring(X0, X1, Y0, Y1, zr0), g.rect_ring(X0, X1, Y0, Y1, zr1),
                        g.rect_ring(X0 + 1.1, X1 - 1.1, Y0 + 1.1, Y1 - 1.1, zr1),
                        g.rect_ring(X0 + 1.1, X1 - 1.1, Y0 + 1.1, Y1 - 1.1, zr0)]), "SteelGrey")
    m.add(g.loft_rings([g.rect_ring(X0, X1, Y0, Y1, zr1),
                        g.rect_ring(X0 + 0.4, X1 - 0.4, Y0 + 0.4, Y1 - 0.4, zr2),
                        g.rect_ring(X0 + 1.1, X1 - 1.1, Y0 + 1.1, Y1 - 1.1, zr2),
                        g.rect_ring(X0 + 1.1, X1 - 1.1, Y0 + 1.1, Y1 - 1.1, zr1)]), "SteelLight")
    # Dach (vertieft im Rahmen)
    m.add(g.box_minmax((X0 + 1.05, Y0 + 1.05, ZT - 1.0), (X1 - 1.05, Y1 - 1.05, ZT - 0.45)),
          "Orange")

    # --- Vorderseite ---
    fy = Y0 + 0.25                          # Wandflaeche vorne
    door_out = g.chamfer_rect(-3.3, 3.3, ZB + 0.45, 9.6, 1.0, top_only=True)
    door_in = g.chamfer_rect(-2.55, 2.55, ZB + 0.7, 8.85, 0.7, top_only=True)
    ring_in_face(m, "-Y", fy, door_out, door_in, -0.05, 0.7, "SteelGrey")
    # Tuerfluegel (zwei Haelften, Fuge in der Mitte)
    frd = g.face_frame("-Y", fy)
    for u0, u1 in ((-2.6, -0.04), (0.04, 2.6)):
        half = g.clip_rect(door_in, u0, u1, -100, 100)
        m.add(g.prism(half, -0.1, 0.25, frd), "DarkGrey", group="Door")
    # Rampe vom Tuerschweller zum Boden
    fr_yz = g.frame_at((0, 0, 0), (0, 1, 0), (0, 0, 1))      # w = +X
    ramp = [(fy - 0.7, ZB + 0.72), (fy - 0.7, ZB + 0.42), (fy - 4.4, 0.0), (fy - 4.4, 0.28)]
    m.add(g.prism(ramp, -2.7, 2.7, fr_yz, bevel=0.05), "SteelLight")
    slope = math.atan2(ZB + 0.72 - 0.28, 3.7)
    for t in (0.12, 0.88):
        yy = fy - 0.7 - 3.7 * t
        zz = ZB + 0.72 - (ZB + 0.72 - 0.28) * t
        for x in (-2.3, 2.3):
            mat = (Matrix.Translation((x, yy, zz + 0.02))
                   @ Matrix.Rotation(slope, 4, "X"))
            m.add(g.cylinder(0.14, 0.1, (0, 0, 0), segs=8, matrix=mat), "SteelGrey")
    # Bullaugen
    for u in (-5.3, 5.3):
        ring_in_face(m, "-Y", fy, circle2d(1.15, 24, (u, 7.6)), circle2d(0.78, 24, (u, 7.6)),
                     -0.05, 0.38, "SteelGrey")
        m.add(g.prism(circle2d(0.8, 24, (u, 7.6)), -0.05, 0.12, frd), "Glass")
    # Leuchtfeld rechts neben der Tuer
    cyan_panel(m, "-Y", fy, 4.35, 4.5, 0.55, 1.05)
    # Warnstreifen links und rechts der Tuer
    hazard(m, "-Y", fy, X0 + P, -3.35, ZB + 0.5, ZB + 1.2)
    hazard(m, "-Y", fy, 3.35, X1 - P, ZB + 0.5, ZB + 1.2)
    # Bolzen an den Pfeilern
    for x in (X0 + P / 2, X1 - P / 2):
        for z in (ZB + 0.8, ZT - 1.4):
            m.add(g.cylinder(0.13, 0.1, (x, Y0 - 0.02, z), axis="Y", segs=8), "SteelLight")

    # --- Dach-Aufbauten ---
    zroof = ZT - 0.45
    for x in (-5.0, -3.8):
        m.add(g.cylinder(0.45, 0.9, (x, 3.3, zroof + 0.45), segs=12, bevel=0.05), "SteelGrey")
        m.add(g.cylinder(0.3, 0.04, (x, 3.3, zroof + 0.91), segs=12), "Black")
    for x in (-4.2, 4.0):
        m.add(g.box((1.7, 1.7, 0.35), (x, -2.0, zroof + 0.17), bevel=0.08), "SteelGrey")
        m.add(g.box((1.2, 1.2, 0.06), (x, -2.0, zroof + 0.36)), "SteelLight")
    # Satellitenschuessel
    dx, dy = 4.4, 2.4
    m.add(g.cylinder(0.55, 0.25, (dx, dy, zroof + 0.12), segs=16, bevel=0.03), "SteelGrey")
    m.add(g.cylinder(0.2, 1.7, (dx, dy, zroof + 1.0), segs=10), "SteelGrey")
    dish = (Matrix.Translation((dx, dy, zroof + 1.8)) @ Matrix.Rotation(math.radians(25), 4, "Z")
            @ Matrix.Rotation(math.radians(-42), 4, "Y"))
    bowl = g.loft_rings([g.circle_ring(0.3, 0.0, 20), g.circle_ring(1.35, 0.42, 20),
                         g.circle_ring(1.22, 0.42, 20), g.circle_ring(0.22, 0.1, 20)])
    m.add(g.transform_bm(bowl, dish), "SteelGrey")
    m.add(g.cylinder(0.32, 0.25, (0, 0, -0.05), segs=10, matrix=dish), "SteelGrey")
    m.add(g.cylinder(0.06, 1.1, (0, 0, 0.6), segs=6, matrix=dish), "SteelLight")
    m.add(g.cylinder(0.14, 0.18, (0, 0, 1.15), segs=8, matrix=dish), "SteelGrey")

    # --- Beine ---
    for x in (X0 + 0.9, X1 - 0.9):
        for y in (Y0 + 0.9, Y1 - 0.9):
            foot_leg(m, x, y, ZB, size=1.2, foot=2.2)
    # --- Verbindungsstutzen zu den Nachbarraeumen ---
    for s in (-1, 1):
        xa, xb = sorted((s * (X1 - 0.1), s * (ROOM_POS - 4.4 + 0.1)))
        m.add(g.box_minmax((xa, ROOM_Y - 3.0, ZB + 1.6), (xb, ROOM_Y + 3.0, ZB + 6.4), bevel=0.08),
              "DarkGrey")
    return m


def build_room():
    m = g.Model("BaseRoom")
    X0, X1, Y0, Y1 = -4.4, 4.4, -5.5, 5.5
    ZB, ZT = 1.6, 9.4
    P = 1.05
    # Waende + Dachblock mit Fase
    m.add(g.box_minmax((X0 + 0.2, Y0 + 0.2, ZB + 0.4), (X1 - 0.2, Y1 - 0.2, ZT - 0.8)), "Orange")
    m.add(g.box_minmax((X0 + 0.1, Y0 + 0.1, ZT - 0.95), (X1 - 0.1, Y1 - 0.1, ZT), bevel=0.38),
          "Orange")
    for x in (X0 + P / 2, X1 - P / 2):
        for y in (Y0 + P / 2, Y1 - P / 2):
            m.add(g.box((P, P, ZT - ZB - 0.05), (x, y, ZB + (ZT - ZB - 0.05) / 2), bevel=0.22),
                  "SteelGrey")
    m.add(g.loft_rings([g.rect_ring(X0 + 0.05, X1 - 0.05, Y0 + 0.05, Y1 - 0.05, ZB),
                        g.rect_ring(X0 + 0.05, X1 - 0.05, Y0 + 0.05, Y1 - 0.05, ZB + 0.42),
                        g.rect_ring(X0 + 0.5, X1 - 0.5, Y0 + 0.5, Y1 - 0.5, ZB + 0.42),
                        g.rect_ring(X0 + 0.5, X1 - 0.5, Y0 + 0.5, Y1 - 0.5, ZB)]), "SteelGrey")
    fy = Y0 + 0.2
    # Rahmen ums Rolltor
    outer = [(-3.45, ZB + 1.15), (3.45, ZB + 1.15), (3.45, 8.0), (-3.45, 8.0)]
    inner = [(-2.95, ZB + 1.45), (2.95, ZB + 1.45), (2.95, 7.55), (-2.95, 7.55)]
    ring_in_face(m, "-Y", fy, outer, inner, -0.05, 0.3, "SteelGrey")
    # Rolltor: Lamellen + Kasten oben
    fr = g.face_frame("-Y", fy)
    n = 9
    z0, z1 = ZB + 1.45, 7.2
    hgt = (z1 - z0) / n
    for k in range(n):
        v0 = z0 + k * hgt
        m.add(g.prism([(-2.95, v0), (2.95, v0), (2.95, v0 + hgt - 0.07), (-2.95, v0 + hgt - 0.07)],
                      0.0, 0.14, fr, bevel=0.03), "DarkGrey", group="Shutter")
    m.add(g.prism([(-2.95, z1), (2.95, z1), (2.95, 7.55), (-2.95, 7.55)], 0.0, 0.22, fr,
                  bevel=0.04), "DarkGrey", group="Shutter")
    # Warnstreifen unter dem Tor
    hazard(m, "-Y", fy, X0 + P, X1 - P, ZB + 0.45, ZB + 1.1, stripe=0.34)
    # Leuchtfeld am rechten Pfeiler
    cyan_panel(m, "-Y", Y0, X1 - P / 2, 4.6, 0.42, 0.95)
    # Bolzen an den Pfeilern
    for x in (X0 + P / 2, X1 - P / 2):
        m.add(g.cylinder(0.12, 0.1, (x, Y0 - 0.02, ZB + 0.75), axis="Y", segs=8), "SteelLight")
    # Beine
    for x in (X0 + 0.8, X1 - 0.8):
        for y in (Y0 + 0.8, Y1 - 0.8):
            foot_leg(m, x, y, ZB, size=1.0, foot=1.9)
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
        g.export_fbx(hall, os.path.join(models_dir, "base_hall.fbx"))
        g.export_fbx(room, os.path.join(models_dir, "base_room.fbx"))
        print(f"base_hall: {len(hall)} Objekte, {g.tri_count(hall)} Dreiecke")
        print(f"base_room: {len(room)} Objekte, {g.tri_count(room)} Dreiecke")
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


if __name__ == "__main__":
    main()
