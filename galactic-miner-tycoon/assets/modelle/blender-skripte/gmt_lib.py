"""Gemeinsame Bausteine fuer die Blender-Modelle von Galactic Miner Tycoon.

Laeuft mit Blender 4.x/5.x (``blender -b -P build_xyz.py``) oder mit dem
Python-Modul ``bpy`` (``python build_xyz.py``).

Konventionen (passend zu ``drill_iron.blend``):
- 1 Blender-Einheit = 1 Stud. Boden bei z = 0, Vorderseite zeigt nach -Y.
- Materialnamen ``Mat_<Farbe>``; Farben wie beim Bohrer.
- Pro Modell entsteht **ein Objekt pro (Gruppe, Material)**, z. B.
  ``OreBin_Orange`` oder ``OreBin_Fill_OreRock``. So wird in Roblox jedes
  Objekt eine MeshPart mit genau einer Farbe/einem Material.
"""

import math
import os
import random

import bmesh
import bpy
from mathutils import Matrix, Vector

# ---------------------------------------------------------------------------
# Farben (sRGB-Hex). Die ersten Werte entsprechen den Materialien des Bohrers.
# ---------------------------------------------------------------------------
PALETTE = {
    "Orange": "#F2A12E",      # Hauptfarbe Beine/Waende (wie Bohrer)
    "Amber": "#EDBA4E",       # gelbliches Orange (Lager-Kasten-Seiten)
    "Yellow": "#F6D117",      # Pfeile, Warnstreifen
    "Black": "#1C1C1D",       # Warnstreifen, Loecher
    "SteelGrey": "#8C939B",   # Rahmen, Schienen
    "SteelDark": "#5E656D",   # dunklere Stahlteile, Sockel
    "SteelLight": "#BABEC4",  # Bolzen, Schilder, Rampe
    "DarkGrey": "#3A3F46",    # Bandoberflaeche, Tueren, Rolltore
    "White": "#E6E3DD",       # helle Schilder, Trichter innen
    "Cyan": "#7FF6EF",        # Leuchten (in Roblox: Neon)
    "Glass": "#CFE8F1",       # Bullaugen (in Roblox: Glass)
    "GlassDark": "#6E7F89",   # getoentes Glas am Lager-Kasten
    "GaugeOrange": "#F07A12", # Fuellstandsanzeige
    "OreRock": "#7B6C61",     # Erzbrocken
    "OreRockDark": "#5F544D", # Erzhaufen-Grundkoerper
}

EMISSIVE = {"Cyan"}
TRANSPARENT = {"Glass": 0.6, "GlassDark": 0.28}


def srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def hex_to_linear(h):
    h = h.lstrip("#")
    return tuple(srgb_to_linear(int(h[i:i + 2], 16) / 255.0) for i in (0, 2, 4))


def get_mat(name):
    full = "Mat_" + name
    mat = bpy.data.materials.get(full)
    if mat:
        return mat
    mat = bpy.data.materials.new(full)
    try:
        mat.use_nodes = True
    except Exception:
        pass
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    col = hex_to_linear(PALETTE[name]) + (1.0,)
    bsdf.inputs["Base Color"].default_value = col
    bsdf.inputs["Roughness"].default_value = 0.55
    mat.diffuse_color = col
    if name in EMISSIVE:
        bsdf.inputs["Emission Color"].default_value = col
        bsdf.inputs["Emission Strength"].default_value = 2.5
    if name in TRANSPARENT:
        bsdf.inputs["Alpha"].default_value = TRANSPARENT[name]
        try:
            mat.surface_render_method = "BLENDED"
        except Exception:
            pass
    return mat


# ---------------------------------------------------------------------------
# Szene
# ---------------------------------------------------------------------------
def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.unit_settings.system = "METRIC"
    sc.unit_settings.scale_length = 1.0
    return sc


# ---------------------------------------------------------------------------
# bmesh-Helfer. Jede Funktion liefert ein fertig transformiertes bmesh.
# ---------------------------------------------------------------------------
def _bevel(bm, amount, segments=1):
    if amount <= 0:
        return
    bmesh.ops.bevel(bm, geom=list(bm.edges) + list(bm.verts), offset=amount,
                    segments=segments, profile=0.5, affect="EDGES",
                    clamp_overlap=True)


def _finish(bm, matrix=None):
    if matrix is not None:
        bmesh.ops.transform(bm, matrix=matrix, verts=bm.verts)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def box(size, center, bevel=0.0, rot_z=0.0, matrix=None):
    """Quader. size=(sx,sy,sz), center=(x,y,z)."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    _bevel(bm, bevel)
    m = Matrix.Translation(Vector(center)) @ Matrix.Rotation(rot_z, 4, "Z")
    if matrix is not None:
        m = matrix @ m
    return _finish(bm, m)


def box_minmax(mn, mx, bevel=0.0, matrix=None):
    size = [b - a for a, b in zip(mn, mx)]
    center = [(a + b) / 2 for a, b in zip(mn, mx)]
    return box(size, center, bevel=bevel, matrix=matrix)


def cylinder(r, depth, center, axis="Z", segs=16, r2=None, bevel=0.0,
             matrix=None):
    """Zylinder (oder Kegelstumpf mit r2) entlang axis."""
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segs,
                          radius1=r, radius2=r if r2 is None else r2,
                          depth=depth)
    _bevel(bm, bevel)
    rot = Matrix.Identity(4)
    if axis == "X":
        rot = Matrix.Rotation(math.radians(90), 4, "Y")
    elif axis == "Y":
        rot = Matrix.Rotation(math.radians(-90), 4, "X")
    elif axis == "-Y":
        rot = Matrix.Rotation(math.radians(90), 4, "X")
    m = Matrix.Translation(Vector(center)) @ rot
    if matrix is not None:
        m = matrix @ m
    return _finish(bm, m)


def prism(poly, w0, w1, frame, bevel=0.0):
    """Extrudiert ein 2D-Polygon [(u,v),...] von w0 bis w1.

    frame ist eine 4x4-Matrix, die (u, v, w) in Weltkoordinaten abbildet.
    """
    bm = bmesh.new()
    bot = [bm.verts.new((u, v, w0)) for u, v in poly]
    top = [bm.verts.new((u, v, w1)) for u, v in poly]
    n = len(poly)
    bm.faces.new(list(reversed(bot)))
    bm.faces.new(top)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((bot[i], bot[j], top[j], top[i]))
    _bevel(bm, bevel)
    big = [f for f in bm.faces if len(f.verts) > 4]
    if big:
        bmesh.ops.triangulate(bm, faces=big, quad_method="BEAUTY",
                              ngon_method="BEAUTY")
    return _finish(bm, frame)


def frustum_box(bottom, top, z0, z1, center=(0, 0)):
    """Rechteckiger Kegelstumpf: bottom=(sx,sy) bei z0, top=(sx,sy) bei z1."""
    bm = bmesh.new()
    cx, cy = center
    def ring(sx, sy, z):
        return [bm.verts.new((cx + x * sx / 2, cy + y * sy / 2, z))
                for x, y in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    b = ring(*bottom, z0)
    t = ring(*top, z1)
    bm.faces.new(list(reversed(b)))
    bm.faces.new(t)
    for i in range(4):
        j = (i + 1) % 4
        bm.faces.new((b[i], b[j], t[j], t[i]))
    return _finish(bm)


def quads(faces):
    """Einzelne Flaechen (Liste von Punktlisten) als ein bmesh."""
    bm = bmesh.new()
    for pts in faces:
        bm.faces.new([bm.verts.new(p) for p in pts])
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    return bm


def annular_sector(ri, ro, a0, a1, z0, z1, segs=16, center=(0, 0)):
    """Ringsegment (fuer Kurven). Winkel in Grad, gegen den Uhrzeigersinn."""
    bm = bmesh.new()
    cx, cy = center
    rows = []
    for k in range(segs + 1):
        a = math.radians(a0 + (a1 - a0) * k / segs)
        c, s = math.cos(a), math.sin(a)
        rows.append([bm.verts.new((cx + r * c, cy + r * s, z))
                     for r, z in ((ri, z0), (ro, z0), (ro, z1), (ri, z1))])
    for k in range(segs):
        a, b = rows[k], rows[k + 1]
        for i in range(4):
            j = (i + 1) % 4
            bm.faces.new((a[i], a[j], b[j], b[i]))
    bm.faces.new(list(reversed(rows[0])))
    bm.faces.new(rows[-1])
    return _finish(bm)


def rock(radius, center, seed, squash=(1.0, 0.9, 0.7), subdiv=1, jitter=0.18):
    """Low-Poly-Brocken (verbeulte Ikosphaere)."""
    rnd = random.Random(seed)
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=subdiv, radius=radius)
    for v in bm.verts:
        v.co *= 1.0 + rnd.uniform(-jitter, jitter)
    bmesh.ops.scale(bm, vec=Vector(squash), verts=bm.verts)
    rot = (Matrix.Rotation(rnd.uniform(0, 6.28), 4, "Z")
           @ Matrix.Rotation(rnd.uniform(-0.4, 0.4), 4, "X"))
    return _finish(bm, Matrix.Translation(Vector(center)) @ rot)


# ---------------------------------------------------------------------------
# 2D-Formen
# ---------------------------------------------------------------------------
def stadium(x0, x1, y0, y1, segs=6, round_left=True, round_right=True):
    """Rechteck mit halbrunden Enden (links/rechts)."""
    r = (y1 - y0) / 2
    cy = (y0 + y1) / 2
    pts = []
    if round_right:
        for k in range(segs + 1):
            a = -math.pi / 2 + math.pi * k / segs
            pts.append((x1 - r + r * math.cos(a), cy + r * math.sin(a)))
    else:
        pts += [(x1, y0), (x1, y1)]
    if round_left:
        for k in range(segs + 1):
            a = math.pi / 2 + math.pi * k / segs
            pts.append((x0 + r + r * math.cos(a), cy + r * math.sin(a)))
    else:
        pts += [(x0, y1), (x0, y0)]
    return pts


def rounded_rect(x0, x1, y0, y1, r, segs=3):
    pts = []
    corners = ((x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0),
               (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180))
    for cx, cy, a0 in corners:
        for k in range(segs + 1):
            a = math.radians(a0 + 90 * k / segs)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def chamfer_rect(x0, x1, y0, y1, c, top_only=False):
    if top_only:
        return [(x0, y0), (x1, y0), (x1, y1 - c), (x1 - c, y1), (x0 + c, y1),
                (x0, y1 - c)]
    return [(x0 + c, y0), (x1 - c, y0), (x1, y0 + c), (x1, y1 - c),
            (x1 - c, y1), (x0 + c, y1), (x0, y1 - c), (x0, y0 + c)]


def arrow(length, width, shaft=0.38, head=0.45):
    """Pfeil entlang +u, zentriert. width = Breite der Spitze."""
    h = length * head
    s = width * shaft / 2
    x0, x1 = -length / 2, length / 2
    return [(x0, -s), (x1 - h, -s), (x1 - h, -width / 2), (x1, 0),
            (x1 - h, width / 2), (x1 - h, s), (x0, s)]


def chevron(length, width, thick):
    """Winkel '>' entlang +u."""
    x0 = -length / 2
    return [(x0, -width / 2), (x0 + thick, -width / 2), (x0 + length, 0),
            (x0 + thick, width / 2), (x0, width / 2), (x0 + length - thick, 0)]


def clip_rect(poly, u0, u1, v0, v1):
    """Sutherland-Hodgman: Polygon auf Rechteck zuschneiden."""
    def clip(pts, inside, inter):
        out = []
        for i in range(len(pts)):
            a, b = pts[i - 1], pts[i]
            ia, ib = inside(a), inside(b)
            if ib:
                if not ia:
                    out.append(inter(a, b))
                out.append(b)
            elif ia:
                out.append(inter(a, b))
        return out

    def ix(x):
        return lambda a, b: (x, a[1] + (b[1] - a[1]) * (x - a[0]) / (b[0] - a[0]))

    def iy(y):
        return lambda a, b: (a[0] + (b[0] - a[0]) * (y - a[1]) / (b[1] - a[1]), y)

    pts = poly
    for inside, inter in ((lambda p: p[0] >= u0, ix(u0)),
                          (lambda p: p[0] <= u1, ix(u1)),
                          (lambda p: p[1] >= v0, iy(v0)),
                          (lambda p: p[1] <= v1, iy(v1))):
        if not pts:
            return []
        pts = clip(pts, inside, inter)
    return pts


def hazard_stripes(u0, u1, v0, v1, stripe=0.32, gap=0.32, slope=1.0):
    """Diagonale Streifen (gelb) innerhalb eines Rechtecks."""
    h = v1 - v0
    polys = []
    c = u0 - h * slope - stripe
    while c < u1:
        band = [(c, v0), (c + stripe, v0), (c + stripe + h * slope, v1),
                (c + h * slope, v1)]
        p = clip_rect(band, u0, u1, v0, v1)
        if len(p) >= 3:
            polys.append(p)
        c += stripe + gap
    return polys


# ---------------------------------------------------------------------------
# Rahmen fuer Aufkleber/Flaechen. Liefert Matrix (u, v, w) -> Welt.
# w zeigt immer nach aussen (Flaechennormale).
# ---------------------------------------------------------------------------
def face_frame(normal, pos, center_uv=(0.0, 0.0)):
    """normal in {'-Y','+Y','+X','-X','+Z'}; pos = Koordinate der Flaeche.

    u laeuft (von aussen gesehen) nach rechts, v nach oben (bei +Z: u=x, v=y).
    """
    cu, cv = center_uv
    if normal == "-Y":
        cols = ((1, 0, 0), (0, 0, 1), (0, -1, 0)); org = (cu, pos, cv)
    elif normal == "+Y":
        cols = ((-1, 0, 0), (0, 0, 1), (0, 1, 0)); org = (cu, pos, cv)
    elif normal == "+X":
        cols = ((0, 1, 0), (0, 0, 1), (1, 0, 0)); org = (pos, cu, cv)
    elif normal == "-X":
        cols = ((0, -1, 0), (0, 0, 1), (-1, 0, 0)); org = (pos, cu, cv)
    elif normal == "+Z":
        cols = ((1, 0, 0), (0, 1, 0), (0, 0, 1)); org = (cu, cv, pos)
    else:
        raise ValueError(normal)
    m = Matrix.Identity(4)
    for c in range(3):
        for r in range(3):
            m[r][c] = cols[c][r]
    m[0][3], m[1][3], m[2][3] = org
    return m


def frame_at(origin, u_dir, v_dir):
    u = Vector(u_dir).normalized()
    v = Vector(v_dir).normalized()
    w = u.cross(v)
    m = Matrix.Identity(4)
    for r in range(3):
        m[r][0], m[r][1], m[r][2], m[r][3] = u[r], v[r], w[r], origin[r]
    return m


# ---------------------------------------------------------------------------
# Modell-Sammler
# ---------------------------------------------------------------------------
class Model:
    def __init__(self, name):
        self.name = name
        self.parts = {}

    def add(self, bm, mat, group=None):
        key = (group, mat)
        if key not in self.parts:
            self.parts[key] = bmesh.new()
        tmp = bpy.data.meshes.new("_tmp")
        bm.to_mesh(tmp)
        bm.free()
        self.parts[key].from_mesh(tmp)
        bpy.data.meshes.remove(tmp)

    def add_many(self, bms, mat, group=None):
        for bm in bms:
            self.add(bm, mat, group)

    def decal(self, polys, frame, w0, w1, mat, group=None):
        for p in polys:
            self.add(prism(p, w0, w1, frame), mat, group)

    def build(self, location=(0, 0, 0), collection=None):
        coll = collection or bpy.context.scene.collection
        objs = []
        for (group, mat), bm in sorted(self.parts.items(),
                                       key=lambda kv: (kv[0][0] or "", kv[0][1])):
            name = self.name + ("_" + group if group else "") + "_" + mat
            me = bpy.data.meshes.new(name)
            bm.to_mesh(me)
            bm.free()
            for p in me.polygons:
                p.use_smooth = False
            me.materials.append(get_mat(mat))
            ob = bpy.data.objects.new(name, me)
            ob.location = location
            coll.objects.link(ob)
            ob["gmt_model"] = self.name
            ob["gmt_group"] = group or "Body"
            ob["gmt_material"] = mat
            objs.append(ob)
        self.parts = {}
        return objs


def tri_count(objs):
    n = 0
    for o in objs:
        for p in o.data.polygons:
            n += len(p.vertices) - 2
    return n


# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------
def export_fbx(objs, path):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.export_scene.fbx(filepath=path, use_selection=True,
                             apply_unit_scale=True,
                             apply_scale_options="FBX_SCALE_ALL",
                             object_types={"MESH"}, mesh_smooth_type="FACE",
                             use_mesh_modifiers=True, add_leaf_bones=False,
                             bake_anim=False, path_mode="AUTO")


def save_blend(path):
    bpy.ops.wm.save_as_mainfile(filepath=path, compress=True)


# ---------------------------------------------------------------------------
# Vorschau-Renders (Cycles, CPU) – nur zum Vergleichen mit den Referenzbildern
# ---------------------------------------------------------------------------
def setup_render(res=(1000, 700), samples=24):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = samples
    try:
        sc.cycles.use_denoising = True
    except Exception:
        pass
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.film_transparent = False
    sc.view_settings.view_transform = "Standard"
    sc.render.image_settings.file_format = "PNG"
    world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
    sc.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    bg.inputs[0].default_value = (0.62, 0.62, 0.64, 1)
    bg.inputs[1].default_value = 0.85
    if "Sun_Key" not in bpy.data.objects:
        for name, rot, energy in (("Sun_Key", (50, 10, -35), 3.2),
                                  ("Sun_Fill", (60, -15, 150), 0.9)):
            ld = bpy.data.lights.new(name, "SUN")
            ld.energy = energy
            ld.angle = math.radians(8)
            lo = bpy.data.objects.new(name, ld)
            lo.rotation_euler = [math.radians(a) for a in rot]
            sc.collection.objects.link(lo)
    # Boden, der nur Schatten zeigt
    if "PreviewGround" not in bpy.data.objects:
        bm = box((400, 400, 0.02), (0, 0, -0.011))
        me = bpy.data.meshes.new("PreviewGround")
        bm.to_mesh(me)
        g = bpy.data.objects.new("PreviewGround", me)
        try:
            g.is_shadow_catcher = True
        except Exception:
            pass
        sc.collection.objects.link(g)


def bounds(objs):
    pts = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
    mn = Vector([min(p[i] for p in pts) for i in range(3)])
    mx = Vector([max(p[i] for p in pts) for i in range(3)])
    return mn, mx


def render_view(objs, path, view, margin=1.12, azimuth=-45.0, elevation=30.0,
                res=None, focus=None, scale=None):
    """view: iso | front | back | side | left | top | custom."""
    sc = bpy.context.scene
    if res:
        sc.render.resolution_x, sc.render.resolution_y = res
    mn, mx = bounds(objs)
    center = (mn + mx) / 2 if focus is None else Vector(focus)
    size = mx - mn
    cam_data = bpy.data.cameras.new("PreviewCam")
    cam_data.type = "ORTHO"
    cam = bpy.data.objects.new("PreviewCam", cam_data)
    sc.collection.objects.link(cam)
    sc.camera = cam
    dist = 200.0
    if view == "front":
        d = Vector((0, -1, 0)); fit = (size.x, size.z)
    elif view == "back":
        d = Vector((0, 1, 0)); fit = (size.x, size.z)
    elif view == "side":
        d = Vector((1, 0, 0)); fit = (size.y, size.z)
    elif view == "left":
        d = Vector((-1, 0, 0)); fit = (size.y, size.z)
    elif view == "top":
        d = Vector((0, -0.0001, 1)); fit = (size.x, size.y)
    else:
        az, el = math.radians(azimuth), math.radians(elevation)
        d = Vector((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el),
                    math.sin(el)))
        diag = size.length
        fit = (diag, diag * 0.75)
    cam.location = center + d.normalized() * dist
    if view == "top":
        cam.rotation_euler = (0.0, 0.0, 0.0)  # Blick nach unten, +Y oben im Bild
    else:
        cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
    aspect = sc.render.resolution_x / sc.render.resolution_y
    need = max(fit[0], fit[1] * aspect) * margin
    cam_data.ortho_scale = scale or need
    cam_data.clip_end = 1000
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(cam)
    bpy.data.cameras.remove(cam_data)


def out_dirs():
    here = os.path.dirname(os.path.abspath(__file__))
    models = os.environ.get("GMT_OUT_DIR", os.path.dirname(here))
    os.makedirs(models, exist_ok=True)
    preview = os.environ.get("GMT_PREVIEW_DIR", os.path.join(models, "vorschau"))
    os.makedirs(preview, exist_ok=True)
    return models, preview


# ---------------------------------------------------------------------------
# Ring-Koerper (Trichter, Rahmen, Bullaugen, Schuessel)
# ---------------------------------------------------------------------------
def loft_rings(rings, closed=True):
    """Verbindet Ringe gleicher Punktzahl zu einem Koerper.

    Typisch 4 Ringe: aussen unten, aussen oben, innen oben, innen unten ->
    geschlossener Ring mit Wandstaerke.
    """
    bm = bmesh.new()
    vs = [[bm.verts.new(p) for p in r] for r in rings]
    n = len(rings[0])
    last = len(vs) if closed else len(vs) - 1
    for a in range(last):
        b = (a + 1) % len(vs)
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((vs[a][i], vs[a][j], vs[b][j], vs[b][i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def rect_ring(x0, x1, y0, y1, z):
    return [(x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z)]


def circle_ring(r, z, n=20, center=(0, 0)):
    return [(center[0] + r * math.cos(2 * math.pi * k / n),
             center[1] + r * math.sin(2 * math.pi * k / n), z) for k in range(n)]


def poly_ring(poly, w, frame):
    """2D-Polygon im Rahmen (u, v) bei Tiefe w -> Liste von Weltpunkten."""
    return [tuple(frame @ Vector((u, v, w))) for u, v in poly]


def transform_bm(bm, matrix):
    bmesh.ops.transform(bm, matrix=matrix, verts=bm.verts)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def bar2d(p, q, width):
    """Rechteck-Polygon (Strebe) von p nach q mit Breite width."""
    p, q = Vector(p), Vector(q)
    d = (q - p).normalized()
    n = Vector((-d.y, d.x)) * width / 2
    return [tuple(p - n), tuple(q - n), tuple(q + n), tuple(p + n)]
