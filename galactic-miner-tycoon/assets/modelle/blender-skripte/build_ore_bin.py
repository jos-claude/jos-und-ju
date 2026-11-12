"""Lager-Kasten (bin_*) nach referenz/bilder/gebaeude/lager-kasten-01.jpg.

Modell OreBin (8 x 5 Studs Kasten, 9,2 x 6 mit Sockel, ca. 8,4 hoch):
- OreBin_<Material>        Rahmen, Waende, Sockel, Anzeige, Glas
- OreBin_Lid_<Material>    Deckel mit rundem Einfuelltrichter (ausblenden = offener Kasten)
- OreBin_Fill_<Material>   Erzhaufen hinter dem Glas. Ursprung am Boden des
                           Innenraums; Fuellstand ueber die Hoehe (Z-Groesse) steuern.
- OreBin_GaugeFill_GaugeOrange  oranger Balken der Fuellstandsanzeige (ebenso skalierbar)
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import bpy  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

import gmt_lib as g  # noqa: E402

X0, X1 = -4.0, 4.0      # Kasten aussen
Y0, Y1 = -2.5, 2.5
Z0, Z1 = 1.1, 7.1       # Kasten ueber dem Sockel
T = 0.62                # Rahmenstaerke
FILL = 0.48             # Fuellstand der Vorschau (0..1)


def frame_beams(m):
    c = 0.08
    for x in (X0 + T / 2, X1 - T / 2):
        for y in (Y0 + T / 2, Y1 - T / 2):
            m.add(g.box((T, T, Z1 - Z0), (x, y, (Z0 + Z1) / 2), bevel=c), "SteelGrey")
    for z in (Z0 + T / 2, Z1 - T / 2):
        for y in (Y0 + T / 2, Y1 - T / 2):
            m.add(g.box((X1 - X0 - 2 * T + 0.02, T, T), (0, y, z), bevel=c), "SteelGrey")
        for x in (X0 + T / 2, X1 - T / 2):
            m.add(g.box((T, Y1 - Y0 - 2 * T + 0.02, T), (x, 0, z), bevel=c), "SteelGrey")


def bolt(m, frame, u, v, w=0.0, r=0.11, mat="SteelLight"):
    m.add(g.prism(g.rounded_rect(u - r, u + r, v - r, v + r, r * 0.95, 2), w, w + 0.08,
                  frame), mat)


def braced_panel(m, normal, pos, u0, u1, v0, v1, with_plate):
    """Gelb-orange Seitenwand mit grauem X-Kreuz (und Upgrade-Schild)."""
    fr = g.face_frame(normal, pos)
    m.add(g.prism([(u0, v0), (u1, v0), (u1, v1), (u0, v1)], -0.25, 0.0, fr), "Amber")
    um, vm = (u0 + u1) / 2, (v0 + v1) / 2
    bars = [((u0, v0), (u1, v1)), ((u0, v1), (u1, v0)), ((um, v0), (um, v1)),
            ((u0, vm), (u1, vm))]
    for p, q in bars:
        m.add(g.prism(g.bar2d(p, q, 0.34), 0.0, 0.1, fr), "SteelGrey")
    if with_plate:
        pw, ph = 0.72, 1.05
        m.add(g.prism(g.rounded_rect(um - pw, um + pw, vm - ph, vm + ph, 0.12, 2),
                      0.1, 0.22, fr, bevel=0.02), "SteelLight")
        for k in (-1, 0, 1):
            vv = vm + k * 0.55
            m.add(g.prism(g.rounded_rect(um - 0.42, um + 0.42, vv - 0.16, vv + 0.16,
                                         0.15, 3), 0.22, 0.3, fr), "Cyan")
        for du in (-pw + 0.17, pw - 0.17):
            for dv in (-ph + 0.17, ph - 0.17):
                bolt(m, fr, um + du, vm + dv, 0.22, r=0.07, mat="SteelGrey")


def build_bin():
    m = g.Model("OreBin")
    frame_beams(m)
    zi0, zi1 = Z0 + T, Z1 - T          # Innenraum
    xi0, xi1 = X0 + T, X1 - T
    yi0, yi1 = Y0 + T, Y1 - T
    # Innenraum (dunkel): Boden, Rueckwand, Seiten
    m.add(g.box_minmax((xi0, yi0 - 0.3, Z0), (xi1, Y1 - 0.12, zi0)), "SteelDark")
    m.add(g.box_minmax((xi0, yi1, zi0), (xi1, Y1 - 0.12, zi1)), "SteelDark")
    for x0, x1 in ((X0 + 0.12, xi0), (xi1, X1 - 0.12)):
        m.add(g.box_minmax((x0, yi0 - 0.3, zi0), (x1, yi1, zi1)), "SteelDark")

    # --- Vorderseite: Glas + Anzeige-Saeule ---
    gx1 = X1 - T - 0.8                     # rechte Glaskante
    m.add(g.box_minmax((xi0, Y0 + 0.12, zi0), (gx1, Y0 + 0.2, zi1)), "GlassDark")
    m.add(g.box_minmax((gx1, Y0 + 0.02, zi0), (xi1, Y0 + 0.3, zi1)), "SteelGrey")
    fr = g.face_frame("-Y", Y0 + 0.02)
    gu0, gu1 = gx1 + 0.12, xi1 - 0.1
    gv0, gv1 = zi0 + 0.25, zi1 - 0.3
    m.add(g.prism(g.rounded_rect(gu0, gu1, gv0, gv1, 0.12, 2), 0.0, 0.28, fr), "GaugeOrange")
    m.add(g.prism(g.rounded_rect(gu0 + 0.13, gu1 - 0.13, gv0 + 0.15, gv1 - 0.15, 0.08, 2),
                  0.28, 0.32, fr), "White")
    lvl = gv0 + 0.15 + (gv1 - gv0 - 0.3) * FILL
    m.add(g.prism([(gu0 + 0.13, gv0 + 0.15), (gu1 - 0.13, gv0 + 0.15), (gu1 - 0.13, lvl),
                   (gu0 + 0.13, lvl)], 0.29, 0.34, fr), "GaugeOrange", group="GaugeFill")
    # Bolzen an den Rahmenecken vorne
    frf = g.face_frame("-Y", Y0)
    for u in (X0 + T / 2, X1 - T / 2):
        for v in (Z0 + T / 2, Z1 - T / 2):
            bolt(m, frf, u, v, 0.0)
    for u in (-1.4, 1.4):
        for v in (Z0 + T / 2, Z1 - T / 2):
            bolt(m, frf, u, v, 0.0, r=0.08)

    # --- Seiten und Rueckseite: Paneele mit X-Kreuz ---
    braced_panel(m, "+X", X1 - 0.1, yi0, yi1, zi0, zi1, True)
    braced_panel(m, "-X", X0 + 0.1, -yi1, -yi0, zi0, zi1, True)
    braced_panel(m, "+Y", Y1 - 0.1, -xi1, -xi0, zi0, zi1, False)
    for normal, pos, us in (("+X", X1, (Y0 + T / 2, Y1 - T / 2)),
                            ("-X", X0, (Y0 + T / 2, Y1 - T / 2)),
                            ("+Y", Y1, (X0 + T / 2, X1 - T / 2))):
        frs = g.face_frame(normal, pos)
        for u in us:
            for v in (Z0 + T / 2, Z1 - T / 2):
                bolt(m, frs, u, v, 0.0)

    # --- Sockel mit Warnstreifen und Eckbloecken ---
    m.add(g.box_minmax((-4.55, -3.0, 0.0), (4.55, 3.0, Z0), bevel=0.1), "SteelDark")
    m.add(g.box_minmax((-4.35, -2.8, Z0 - 0.02), (4.35, 2.8, Z0 + 0.12), bevel=0.04),
          "SteelGrey")
    for x in (-4.1, 4.1):
        for y in (-2.55, 2.55):
            m.add(g.box((1.05, 1.05, Z0 + 0.04), (x, y, (Z0 + 0.04) / 2), bevel=0.1),
                  "SteelGrey")
            for normal, pos, u in (("-Y" if y < 0 else "+Y", y + (0.53 if y > 0 else -0.53),
                                    x if y < 0 else -x),
                                   ("+X" if x > 0 else "-X", x + (0.53 if x > 0 else -0.53),
                                    y if x > 0 else -y)):
                bolt(m, g.face_frame(normal, pos), u, Z0 / 2 + 0.02, 0.0, r=0.12)
    frp = g.face_frame("-Y", -3.0)
    u0, u1, v0, v1 = -3.45, 3.45, 0.2, 0.86
    m.add(g.prism([(u0, v0), (u1, v0), (u1, v1), (u0, v1)], 0.0, 0.03, frp), "Black")
    m.decal(g.hazard_stripes(u0, u1, v0, v1, 0.3, 0.3), frp, 0.0, 0.05, "Yellow")
    # Bolzen auf der Sockelseite
    for normal, pos in (("+X", 4.55), ("-X", -4.55)):
        for u in (-1.2, 1.2):
            bolt(m, g.face_frame(normal, pos), u, Z0 / 2, 0.0, r=0.1)

    # --- Deckel mit rundem Trichter ---
    m.add(g.box_minmax((xi0 - 0.02, yi0 - 0.02, Z1 - 0.32), (xi1 + 0.02, yi1 + 0.02, Z1 - 0.12)),
          "Amber", group="Lid")
    fc = (-0.15, 0.0)
    zt = Z1 - 0.12
    m.add(g.cylinder(1.2, 0.22, (fc[0], fc[1], zt + 0.11), segs=24, bevel=0.03),
          "SteelGrey", group="Lid")
    m.add(g.cylinder(0.82, 0.35, (fc[0], fc[1], zt + 0.38), segs=24), "SteelGrey", group="Lid")
    zb, ztop = zt + 0.5, zt + 1.4
    m.add(g.loft_rings([g.circle_ring(0.82, zb, 24, fc), g.circle_ring(1.7, ztop, 24, fc),
                        g.circle_ring(1.55, ztop, 24, fc), g.circle_ring(0.62, zb + 0.12, 24, fc)]),
          "SteelGrey", group="Lid")
    m.add(g.loft_rings([g.circle_ring(0.6, zb + 0.13, 24, fc),
                        g.circle_ring(1.53, ztop - 0.01, 24, fc),
                        g.circle_ring(1.48, ztop - 0.01, 24, fc),
                        g.circle_ring(0.56, zb + 0.15, 24, fc)]), "SteelDark", group="Lid")
    m.add(g.cylinder(0.6, 0.04, (fc[0], fc[1], zb + 0.12), segs=24), "Black", group="Lid")
    # Rand oben am Trichter
    m.add(g.loft_rings([g.circle_ring(1.72, ztop - 0.12, 24, fc), g.circle_ring(1.78, ztop + 0.05, 24, fc),
                        g.circle_ring(1.5, ztop + 0.05, 24, fc), g.circle_ring(1.5, ztop - 0.12, 24, fc)]),
          "SteelGrey", group="Lid")
    return m


def build_fill(level=FILL):
    """Erzhaufen. level 0..1 bezogen auf die Innenhoehe."""
    m = g.Model("OreBin")
    zi0 = Z0 + T
    hi = (Z1 - T) - zi0
    top = zi0 + hi * level
    xi0, xi1 = X0 + T + 0.05, X1 - T - 0.05
    yi0, yi1 = Y0 + 0.22, Y1 - T - 0.05
    base_top = top - 0.45
    m.add(g.box_minmax((xi0, yi0, zi0), (xi1, yi1, base_top)), "OreRockDark", group="Fill")
    seed = 100
    # obere Lage
    nx, ny = 9, 5
    for i in range(nx):
        for j in range(ny):
            seed += 1
            x = xi0 + 0.35 + (xi1 - xi0 - 0.7) * i / (nx - 1) + ((j % 2) * 0.3 - 0.15)
            y = yi0 + 0.4 + (yi1 - yi0 - 0.8) * j / (ny - 1)
            hump = 0.25 * math.sin(i * 1.3 + j * 0.7)
            r = 0.42 + 0.12 * ((seed * 37) % 7) / 6
            m.add(g.rock(r, (x, y, base_top + hump * 0.5), seed, squash=(1.1, 1.0, 0.8),
                         subdiv=1, jitter=0.18), "OreRock", group="Fill")
    # Brocken direkt hinter dem Glas
    rows = max(1, int((base_top - zi0) / 0.7))
    for k in range(rows):
        z = zi0 + 0.35 + k * (base_top - zi0 - 0.2) / max(1, rows)
        for i in range(9):
            seed += 1
            x = xi0 + 0.3 + (xi1 - xi0 - 0.6) * i / 8 + (0.2 if k % 2 else -0.1)
            if x > xi1 - 0.25:
                continue
            r = 0.36 + 0.1 * ((seed * 13) % 5) / 4
            m.add(g.rock(r, (x, yi0 + 0.3, z), seed, squash=(1.0, 0.8, 0.85), subdiv=1,
                         jitter=0.2), "OreRock", group="Fill")
    return m


def main():
    g.reset_scene()
    models_dir, preview_dir = g.out_dirs()
    sc = bpy.context.scene
    coll = bpy.data.collections.new("OreBin")
    sc.collection.children.link(coll)
    objs = build_bin().build(collection=coll) + build_fill().build(collection=coll)
    if "--no-export" not in sys.argv:
        g.export_fbx(objs, os.path.join(models_dir, "ore_bin.fbx"))
        print(f"ore_bin: {len(objs)} Objekte, {g.tri_count(objs)} Dreiecke")
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
