"""Lager-Kasten (bin_*) nach referenz/bilder/gebaeude/lager-kasten-01.jpg.

Modell OreBin (Kasten 8 x 5,3 Studs, mit Sockel 9,1 x 6,3, ca. 8,7 hoch):
- OreBin_<Material>          Rahmen, Waende, Sockel, Anzeige, Glas
- OreBin_Lid_<Material>      Deckel mit rundem Einfuelltrichter (ausblenden = offener Kasten)
- OreBin_Fill_<Material>     Erzhaufen hinter dem Glas (Boden am Kastenboden);
                             Fuellstand im Spiel ueber die Hoehe steuern
- OreBin_GaugeFill_GaugeOrange  oranger Balken der Fuellstandsanzeige (ebenso)
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import bpy  # noqa: E402  (bpy vor bmesh laden)

import gmt_lib as g  # noqa: E402

X0, X1 = -4.0, 4.0      # Kasten aussen
Y0, Y1 = -2.65, 2.65
Z0, Z1 = 1.1, 7.1       # Kasten ueber dem Sockel
T = 0.62                # Rahmenstaerke
FILL = 0.5              # Fuellstand der Vorschau (0..1)
BOLT = 0.15
XI0, XI1 = X0 + T, X1 - T
YI0, YI1 = Y0 + T, Y1 - T
ZI0, ZI1 = Z0 + T, Z1 - T
GX1 = XI1 - 0.95        # rechte Glaskante (rechts davon die Anzeige-Saeule)


def bolt(m, frame, u, v, w=0.0, r=BOLT, mat="SteelLight"):
    m.add(g.prism(g.circle2d(r, 6, (u, v)), w, w + 0.1, frame, bevel=0.02), mat)


def frame(m):
    """Rahmen: oberer und unterer Ring + vier Eckpfosten (buendig, ohne Kappen)."""
    for za, zb in ((Z0, Z0 + T), (Z1 - T, Z1)):
        m.add(g.loft_rings([g.rect_ring(X0, X1, Y0, Y1, za), g.rect_ring(X0, X1, Y0, Y1, zb),
                            g.rect_ring(XI0, XI1, YI0, YI1, zb),
                            g.rect_ring(XI0, XI1, YI0, YI1, za)]), "SteelGrey")
    for x in (X0 + T / 2, X1 - T / 2):
        for y in (Y0 + T / 2, Y1 - T / 2):
            m.add(g.box((T, T, Z1 - Z0 - 2 * T + 0.02), (x, y, (Z0 + Z1) / 2)), "SteelGrey")
    # Bolzen: nur an den vier Ecken jeder Rahmenseite
    for normal, pos, us in (("-Y", Y0, (X0 + T / 2, X1 - T / 2)),
                            ("+Y", Y1, (X0 + T / 2, X1 - T / 2)),
                            ("+X", X1, (Y0 + T / 2, Y1 - T / 2)),
                            ("-X", X0, (Y0 + T / 2, Y1 - T / 2))):
        fr = g.face_frame(normal, pos)
        for u in us:
            for v in (Z0 + T / 2, Z1 - T / 2):
                bolt(m, fr, u if normal in ("-Y", "+X") else -u, v)


def braced_panel(m, normal, pos, u0, u1, v0, v1, with_plate):
    """Gelb-orange Seitenwand mit Streben (breite Mittelstrebe) und ggf. Upgrade-Schild."""
    fr = g.face_frame(normal, pos)
    m.add(g.prism([(u0, v0), (u1, v0), (u1, v1), (u0, v1)], -0.3, -0.12, fr), "Amber")
    um, vm = (u0 + u1) / 2, (v0 + v1) / 2
    for p, q, wdt in (((u0, v0), (u1, v1), 0.45), ((u0, v1), (u1, v0), 0.45),
                      ((u0, vm), (u1, vm), 0.45)):
        m.add(g.prism(g.clip_rect(g.bar2d(p, q, wdt), u0, u1, v0, v1), -0.12, -0.02, fr),
              "SteelGrey")
    m.add(g.prism([(um - 0.35, v0), (um + 0.35, v0), (um + 0.35, v1), (um - 0.35, v1)],
                  -0.12, 0.0, fr), "SteelGrey")
    if with_plate:
        pw, ph = 0.93, 1.2
        m.add(g.prism(g.rounded_rect(um - pw, um + pw, vm - ph, vm + ph, 0.14, 2),
                      0.0, 0.22, fr, bevel=0.04), "White")
        iw, ih = 0.72, 1.0
        m.add(g.prism(g.rounded_rect(um - iw, um + iw, vm - ih, vm + ih, 0.08, 2),
                      0.22, 0.28, fr), "Orange")
        for k in (-1, 0, 1):
            vv = vm + k * 0.56
            m.add(g.prism(g.rounded_rect(um - 0.5, um + 0.5, vv - 0.2, vv + 0.2, 0.19, 3),
                          0.28, 0.32, fr), "SteelDark")
            m.add(g.prism(g.rounded_rect(um - 0.43, um + 0.43, vv - 0.14, vv + 0.14, 0.13, 3),
                          0.32, 0.37, fr), "Cyan")
        for du in (-iw + 0.14, iw - 0.14):
            for dv in (-ih + 0.14, ih - 0.14):
                bolt(m, fr, um + du, vm + dv, 0.28, r=0.07, mat="SteelGrey")


def build_bin():
    m = g.Model("OreBin")
    frame(m)
    # Innenraum (dunkel): Boden, Rueckwand, Seiten
    m.add(g.box_minmax((XI0, YI0 - 0.4, Z0 + 0.1), (XI1, Y1 - 0.15, ZI0)), "DarkGrey")
    m.add(g.box_minmax((XI0, YI1 - 0.02, ZI0), (XI1, Y1 - 0.15, ZI1)), "DarkGrey")
    for x0, x1 in ((X0 + 0.15, XI0 + 0.02), (XI1 - 0.02, X1 - 0.15)):
        m.add(g.box_minmax((x0, YI0 - 0.4, ZI0), (x1, YI1, ZI1)), "DarkGrey")

    # --- Vorderseite: Glas mit dunkler Fase + Anzeige-Saeule ---
    lip_out = [(XI0, ZI0), (GX1, ZI0), (GX1, ZI1), (XI0, ZI1)]
    lip_in = [(XI0 + 0.16, ZI0 + 0.16), (GX1 - 0.16, ZI0 + 0.16), (GX1 - 0.16, ZI1 - 0.16),
              (XI0 + 0.16, ZI1 - 0.16)]
    fr0 = g.face_frame("-Y", Y0)
    m.add(g.loft_rings([g.poly_ring(lip_out, -0.02, fr0), g.poly_ring(lip_in, -0.2, fr0),
                        g.poly_ring(lip_in, -0.26, fr0), g.poly_ring(lip_out, -0.26, fr0)]),
          "DarkGrey")
    m.add(g.box_minmax((XI0 + 0.1, Y0 + 0.2, ZI0 + 0.1), (GX1 - 0.1, Y0 + 0.26, ZI1 - 0.1)),
          "GlassDark")
    m.add(g.box_minmax((GX1, Y0 + 0.02, ZI0 - 0.02), (XI1 + 0.02, Y0 + 0.4, ZI1 + 0.02)),
          "SteelGrey")
    fr = g.face_frame("-Y", Y0 + 0.02)
    gc = (GX1 + XI1) / 2
    gu0, gu1 = gc - 0.38, gc + 0.38
    gv0, gv1 = ZI0 + 0.08, ZI1 - 0.04
    m.add(g.prism(g.rounded_rect(gu0, gu1, gv0, gv1, 0.14, 2), 0.0, 0.14, fr, bevel=0.03),
          "GaugeOrange")
    m.add(g.prism(g.rounded_rect(gu0 + 0.15, gu1 - 0.15, gv0 + 0.14, gv1 - 0.14, 0.08, 2),
                  0.14, 0.17, fr), "Cream")
    lvl = gv0 + 0.14 + (gv1 - gv0 - 0.28) * FILL
    m.add(g.prism([(gu0 + 0.15, gv0 + 0.14), (gu1 - 0.15, gv0 + 0.14), (gu1 - 0.15, lvl),
                   (gu0 + 0.15, lvl)], 0.15, 0.19, fr), "GaugeOrange", group="GaugeFill")

    # --- Seiten und Rueckseite ---
    braced_panel(m, "+X", X1, YI0, YI1, ZI0, ZI1, True)       # Upgrade-Schild nur rechts
    braced_panel(m, "-X", X0, -YI1, -YI0, ZI0, ZI1, False)
    braced_panel(m, "+Y", Y1, -XI1, -XI0, ZI0, ZI1, False)

    # --- Sockel mit Warnstreifen und Eckbloecken ---
    m.add(g.box_minmax((-4.55, -3.15, 0.0), (4.55, 3.15, Z0), bevel=0.1), "SteelDark")
    for x in (-4.0, 4.0):
        for y in (-2.6, 2.6):
            m.add(g.box((1.15, 1.15, Z0 + 0.06), (x, y, (Z0 + 0.06) / 2), bevel=0.13),
                  "SteelGrey")
            sx, sy = (1 if x > 0 else -1), (1 if y > 0 else -1)
            fy = g.face_frame("-Y" if sy < 0 else "+Y", y + sy * 0.575)
            bolt(m, fy, x if sy < 0 else -x, Z0 / 2, 0.0, r=0.17)
            fx = g.face_frame("+X" if sx > 0 else "-X", x + sx * 0.575)
            bolt(m, fx, y if sx > 0 else -y, Z0 / 2, 0.0, r=0.17)
    frp = g.face_frame("-Y", -3.15)
    u0, u1, v0, v1 = -3.4, 3.4, 0.22, 0.88
    m.sticker([(u0, v0), (u1, v0), (u1, v1), (u0, v1)], frp, "Black", 0.008, 0.035)
    for p in g.hazard_stripes(u0, u1, v0, v1, 0.3, 0.3):
        m.sticker(p, frp, "Yellow", 0.02, 0.05)

    # --- Deckel: graue Platte, oranges Feld, runder Trichter (Gunmetal) ---
    m.add(g.box_minmax((X0 + 0.24, Y0 + 0.24, Z1 - 0.02), (X1 - 0.24, Y1 - 0.24, Z1 + 0.21),
                       bevel=0.05), "SteelGrey", group="Lid")
    m.add(g.box_minmax((X0 + 0.75, Y0 + 0.7, Z1 + 0.2), (X1 - 0.75, Y1 - 0.7, Z1 + 0.27)),
          "Amber", group="Lid")
    fc = (-0.15, 0.0)
    zb = Z1 + 0.27
    ztop = zb + 1.3
    m.add(g.cylinder(1.26, 0.3, (fc[0], fc[1], zb + 0.15), segs=28, bevel=0.06),
          "Gunmetal", group="Lid")
    m.add(g.loft_rings([g.circle_ring(0.95, zb + 0.25, 28, fc), g.circle_ring(1.42, ztop - 0.2, 28, fc),
                        g.circle_ring(1.28, ztop - 0.2, 28, fc), g.circle_ring(0.72, zb + 0.38, 28, fc)]),
          "Gunmetal", group="Lid")
    m.add(g.loft_rings([g.circle_ring(0.7, zb + 0.39, 28, fc), g.circle_ring(1.27, ztop - 0.19, 28, fc),
                        g.circle_ring(1.23, ztop - 0.19, 28, fc), g.circle_ring(0.66, zb + 0.41, 28, fc)]),
          "SteelDark", group="Lid")
    m.add(g.cylinder(0.7, 0.04, (fc[0], fc[1], zb + 0.39), segs=28), "Black", group="Lid")
    # dicker, gerollter Rand
    m.add(g.loft_rings([g.circle_ring(1.42, ztop - 0.24, 28, fc), g.circle_ring(1.52, ztop - 0.12, 28, fc),
                        g.circle_ring(1.48, ztop, 28, fc), g.circle_ring(1.28, ztop, 28, fc),
                        g.circle_ring(1.26, ztop - 0.24, 28, fc)]), "Gunmetal", group="Lid")
    return m


def build_fill(level=FILL):
    """Erzhaufen aus groben Brocken, vom Boden bis zum Fuellstand dicht gepackt."""
    m = g.Model("OreBin")
    hi = ZI1 - ZI0
    top = ZI0 + hi * level
    xa, xb = XI0 + 0.05, XI1 - 0.05
    ya, yb = Y0 + 0.3, YI1 - 0.05
    m.add(g.box_minmax((xa + 0.3, ya + 0.6, ZI0), (xb - 0.3, yb, top - 0.35)), "OreRockDark",
          group="Fill")
    seed = 100
    # vordere Lagen direkt hinter dem Glas
    rows = max(1, int((top - ZI0 - 0.2) / 0.72))
    for k in range(rows + 1):
        z = ZI0 + 0.42 + k * (top - ZI0 - 0.6) / max(1, rows)
        n = 7
        for i in range(n):
            seed += 1
            x = xa + 0.45 + (xb - xa - 0.9) * i / (n - 1) + (0.28 if k % 2 else -0.12)
            if x > xb - 0.35:
                continue
            r = 0.5 + 0.08 * ((seed * 13) % 5) / 4
            m.add(g.rock(r, (x, ya + 0.48, z), seed, squash=(1.05, 0.85, 0.85), subdiv=2,
                         jitter=0.14), "OreRock", group="Fill")
    # obere Lage als Haufen
    nx, ny = 7, 4
    for i in range(nx):
        for j in range(ny):
            seed += 1
            x = xa + 0.5 + (xb - xa - 1.0) * i / (nx - 1) + ((j % 2) * 0.35 - 0.17)
            y = ya + 0.9 + (yb - ya - 1.3) * j / (ny - 1)
            hump = 0.22 * math.sin(i * 1.1 + j * 0.9) + 0.15 * (j / (ny - 1))
            r = 0.5 + 0.1 * ((seed * 37) % 7) / 6
            m.add(g.rock(r, (x, y, top - 0.25 + hump), seed, squash=(1.05, 1.0, 0.8),
                         subdiv=2, jitter=0.14), "OreRock", group="Fill")
    return m


def main():
    g.reset_scene()
    models_dir, preview_dir = g.out_dirs()
    sc = bpy.context.scene
    coll = bpy.data.collections.new("OreBin")
    sc.collection.children.link(coll)
    objs = build_bin().build(collection=coll) + build_fill().build(collection=coll)
    if "--no-export" not in sys.argv:
        g.export_model(objs, os.path.join(models_dir, "ore_bin"))
        mn, mx = g.bounds(objs)
        print(f"ore_bin: {len(objs)} Objekte, {g.tri_count(objs)} Dreiecke, "
              f"Groesse {tuple(round(v, 2) for v in (mx - mn))}")
    if "--no-blend" not in sys.argv:
        g.save_blend(os.path.join(models_dir, "ore_bin.blend"))
    if "--render" in sys.argv:
        g.setup_render()
        p = lambda n: os.path.join(preview_dir, n)
        g.render_view(objs, p("ore_bin_iso.png"), "iso", azimuth=35, elevation=30)
        g.render_view(objs, p("ore_bin_front.png"), "front")
        g.render_view(objs, p("ore_bin_side.png"), "side")
        g.render_view(objs, p("ore_bin_top.png"), "top")
        lid = [o for o in objs if o.get("gmt_group") == "Lid"]
        fill = [o for o in objs if o.get("gmt_group") in ("Fill", "GaugeFill")]
        for o in lid + fill:
            o.hide_render = True
        g.render_view(objs, p("ore_bin_empty_open.png"), "iso", azimuth=35, elevation=38)
        for o in fill:
            o.hide_render = False
        g.render_view(objs, p("ore_bin_open.png"), "iso", azimuth=35, elevation=38)


if __name__ == "__main__":
    main()
