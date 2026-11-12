#!/usr/bin/env python3
"""Testlauf fuer den Luau-WorldBuilder ohne Roblox (Lune + nachgebaute Roblox-Umgebung).

    python3 tests/run_luau_check.py            # alles
    python3 tests/run_luau_check.py --builder PFAD/init.luau   # gepatchte Kopie statt der echten Datei testen

Ablauf: synthetische Welt (make_world.py) -> export_luau.export -> Lune fuehrt init.luau (Skript-Baum-Mock),
das Bundle (ModuleScript-Modus und Skript-Modus) und die Dekoder-Einzeltests aus -> Vergleich mit reference.py.
Exit-Code 0 = alles bestanden.
"""
from __future__ import annotations

import argparse
import base64
import importlib.util
import json
import random
import shutil
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
TOOL = HERE.parent
sys.path.insert(0, str(TOOL))
sys.path.insert(0, str(HERE))

from worldgen import codec, export_luau  # noqa: E402
from worldgen.world import CELL, HALF, N, VOID  # noqa: E402

import make_world  # noqa: E402
import reference  # noqa: E402

REAL_SRC = TOOL.parent.parent / "src" / "ServerStorage" / "WorldBuilder"
OUT = HERE / "out"
TIMEOUT = int(__import__("os").environ.get("LUNE_TIMEOUT", "60"))  # Sekunden je Lune-Lauf (ein kaputter Dekoder erzeugt sonst riesige Tabellen)
LUNE = shutil.which("lune") or str(Path.home() / ".cargo/bin/lune")

RESULTS: list[tuple[str, str, bool, str]] = []  # (Bereich, Name, ok, Detail)
INFO: list[str] = []


def check(area, name, ok, detail=""):
    RESULTS.append((area, name, bool(ok), detail))
    return ok


def close(a, b, tol):
    if isinstance(a, (list, tuple)):
        return len(a) == len(b) and all(close(x, y, tol) for x, y in zip(a, b))
    if isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool):
        return abs(a - b) <= tol
    return a == b


def run_lune(args, label):
    t = time.time()
    try:
        p = subprocess.run([LUNE, "run", *map(str, args)], capture_output=True, text=True, cwd=HERE, timeout=TIMEOUT)
    except subprocess.TimeoutExpired:
        print(f"[{label}] Zeitueberschreitung nach {TIMEOUT} s (Endlosschleife oder riesige Tabellen?)")
        return subprocess.CompletedProcess(args, 124, "", "timeout"), time.time() - t
    if p.returncode != 0:
        print(f"[{label}] Lune-Fehler:\n{p.stdout}\n{p.stderr}")
    return p, time.time() - t


# ------------------------------------------------------------------ Vorbereitung

def export_world(world, name, builder_src, settings_src, chunk_chars=None):
    d = OUT / name / "WorldBuilder"
    if d.parent.exists():
        shutil.rmtree(d.parent)
    d.mkdir(parents=True)
    orig = codec.to_base64_chunks
    if chunk_chars:
        codec.to_base64_chunks = lambda data, chunk_chars_=chunk_chars: orig(data, chunk_chars_)
    try:
        stats = export_luau.export(world, d)
    finally:
        codec.to_base64_chunks = orig
    shutil.copy(builder_src, d / "init.luau")
    shutil.copy(settings_src, d / "Settings.luau")
    return d, stats


def make_bundle(wb_dir: Path, out_file: Path):
    """bundle.py auf den Testordner umbiegen (die echte Datei welt/BuildIsland1.luau bleibt unberuehrt)."""
    spec = importlib.util.spec_from_file_location("bundle_under_test", TOOL / "bundle.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.SRC = wb_dir
    mod.OUT = out_file
    out_file.parent.mkdir(parents=True, exist_ok=True)
    mod.main()


def lune_scenario(mode, path, name, scenario):
    res = OUT / f"result_{name}.json"
    p, secs = run_lune([HERE / "lune_check.luau", mode, path, res, scenario], name)
    if p.returncode != 0 or not res.exists():
        return None, secs
    return json.loads(res.read_text()), secs


# ------------------------------------------------------------------ Dekoder-Einzeltests

def decoder_vectors():
    rng = random.Random(1234)
    b64, varint, rle, heights = [], [], [], []
    for L in list(range(0, 70)) + [300, 301, 302]:
        data = bytes(rng.randrange(256) for _ in range(L))
        s = base64.b64encode(data).decode()
        chunks = [s]
        if len(s) >= 8:   # an zufaelligen 4er-Grenzen teilen (wie to_base64_chunks)
            cut = 4 * rng.randrange(1, len(s) // 4)
            chunks = [s[:cut], s[cut:]]
        b64.append({"data": list(data), "chunks": chunks})
    vals = [0, 1, 2, 126, 127, 128, 129, 255, 256, 16383, 16384, 65535, 2**21 - 1, 2**21, 2**28, 2**31 - 1, 2**31, 2**32 + 7, 2**40 + 12345]
    out = bytearray()
    for v in vals:
        codec._varint(out, v)
    varint.append({"bytes": list(out), "count": len(vals), "values": vals})
    for trial in range(40):
        n = rng.choice([1, 2, 5, 127, 128, 129, 400, 1000])
        a = []
        while len(a) < n:
            v = rng.choice([0, 0, 1, 4, 32, 53, 127, 128, 200, 255])
            a += [v] * rng.choice([1, 1, 2, 3, 126, 127, 128, 129, 300])
        a = np.array(a[:n], np.uint8)
        rle.append({"bytes": list(codec.encode_rle(a)), "total": n, "values": a.tolist()})
    # RLE endet vorzeitig / hoert nach total auf: Puffer kuerzer als total -> Rest 0
    for n in [1, 2, 3, 4, 7, 16, 33]:
        for kind in ["rand", "smooth", "void", "const", "checker", "extreme", "noise_void"]:
            if kind == "rand":
                q = np.array([[rng.randrange(0, 65536) for _ in range(n)] for _ in range(n)])
            elif kind == "smooth":
                q = np.fromfunction(lambda r, c: 2000 + 3 * r + 5 * c + (r * c) % 4, (n, n)).astype(int)
            elif kind == "void":
                q = np.zeros((n, n), int)
            elif kind == "const":
                q = np.full((n, n), 1234)
            elif kind == "checker":
                q = np.fromfunction(lambda r, c: ((r + c) % 2) * 65535, (n, n)).astype(int)
            elif kind == "extreme":
                q = np.array([[rng.choice([0, 1, 65535, 32768]) for _ in range(n)] for _ in range(n)])
            else:
                q = np.array([[0 if rng.random() < 0.7 else rng.randrange(1, 300) for _ in range(n)] for _ in range(n)])
            heights.append({"n": n, "bytes": list(codec.encode_heights(q)), "values": q.ravel().tolist()})
    return {"b64": b64, "varint": varint, "rle": rle, "heights": heights}


def run_decoder_tests(builder: Path):
    vec = decoder_vectors()
    inp, outp = OUT / "decoders_in.json", OUT / "decoders_out.json"
    inp.write_text(json.dumps(vec))
    p, _ = run_lune([HERE / "decoders_check.luau", builder, inp, outp], "decoders")
    if p.returncode != 0:
        check("Dekoder", "Lune-Lauf", False, p.stderr[-500:])
        return
    res = json.loads(outp.read_text())
    bad = [i for i, (c, r) in enumerate(zip(vec["b64"], res["b64"])) if r.get("err") or r.get("n") != len(c["data"]) or (r.get("bytes") or []) != c["data"]]
    check("Dekoder", f"Base64 (Laengen 0..69,300..302; Padding 0/1/2; geteilt an 4er-Grenze; {len(vec['b64'])} Faelle)", not bad, f"falsche Faelle {bad[:5]} {res['b64'][bad[0]] if bad else ''}"[:300])
    r = res["varint"][0]
    check("Dekoder", "Varint bis 2^40", not r.get("err") and r["values"] == vec["varint"][0]["values"], str(r)[:300])
    bad = [i for i, (c, r) in enumerate(zip(vec["rle"], res["rle"])) if r.get("err") or (r.get("values") or []) != c["values"]]
    check("Dekoder", f"RLE (Laeufe 126..300, Werte 0..255; {len(vec['rle'])} Faelle)", not bad, f"falsche Faelle {bad[:5]}")
    bad = [(i, vec["heights"][i]["n"]) for i, r in enumerate(res["heights"]) if r.get("err") or r.get("values") != vec["heights"][i]["values"]]
    check("Dekoder", f"Hoehen Vorhersage/Null-Laeufe (n=1..33, rand/glatt/void/Extremwerte; {len(vec['heights'])} Faelle)", not bad, f"falsche Faelle (idx,n) {bad[:6]}")


# ------------------------------------------------------------------ Vergleiche

def voxel_dict(calls):
    d, bad_air, bad_zero = {}, 0, 0
    for c in calls:
        if c["m"] != "WriteVoxels":
            continue
        bad_air += c["badAirOcc"]
        bad_zero += c["badSolidZero"]
        for x, y, z, m, o in zip(c["vx"], c["vy"], c["vz"], c["mat"], c["occ"]):
            if (x, y, z) in d:
                d.setdefault("__dup__", []).append((x, y, z))
            d[(x, y, z)] = (m, o)
    return d, bad_air, bad_zero


def compare_terrain(area, build, world, exp_vox, void_water):
    calls = build["terrain"]
    writes = [c for c in calls if c["m"] == "WriteVoxels"]
    check(area, "Build fehlerfrei", build["ok"], str(build.get("err"))[:600])
    if not build["ok"]:
        return
    names = [c["m"] for c in calls]
    check(area, "Terrain:Clear() genau einmal, vor dem ersten WriteVoxels", names.count("Clear") == 1 and names.index("Clear") < names.index("WriteVoxels"), str(names[:6]))
    # Regionen: 16x16-Spalten, Raster, Auflösung
    ok = all(c["dims"][0] == 16 and c["dims"][2] == 16 and (c["min"][0] - (-HALF)) % 64 == 0 and (c["min"][2] - (-HALF)) % 64 == 0 for c in writes)
    check(area, "Region3: 64x64 Studs am Raster, Y-Hoehe = dims[2]*4 (Mock prueft Array-Masse [x][y][z])", ok)
    ok = all(abs((c["max"][1] - c["min"][1]) - c["dims"][1] * 4) < 1e-9 for c in writes)
    check(area, "Region3-Y-Groesse passt zur Array-Hoehe", ok)
    keyset = {(c["min"][0], c["min"][2]) for c in writes}
    check(area, "keine doppelt geschriebenen Bloecke", len(keyset) == len(writes))
    act, bad_air, bad_zero = voxel_dict(calls)
    dups = act.pop("__dup__", [])
    check(area, "keine Voxel doppelt belegt", not dups, str(dups[:3]))
    check(area, "Belegung: Feststoff/Wasser nie mit Belegung 0", bad_zero == 0, f"solid0={bad_zero}")
    n_air_cols = int(((world.mat & 31) == 0)[(world.h > VOID) & ((world.mat & 32) == 0)].sum())
    INFO.append(f"[{area}] Air-Voxel mit Belegung>0 geschrieben: {bad_air} (erwartet aus {n_air_cols} Spalte(n) mit Material-Index 0 ohne Schicht-Flag; die Weltdaten sollten das nie enthalten)")
    vw = set(void_water)
    act_f = {k: v for k, v in act.items() if (k[0], k[2]) not in vw}
    exp_f = {k: v for k, v in exp_vox.items() if (k[0], k[2]) not in vw}
    missing = [k for k in exp_f if k not in act_f]
    extra = [k for k in act_f if k not in exp_f]
    wrong_mat = [k for k in exp_f if k in act_f and act_f[k][0] != exp_f[k][0]]
    wrong_occ = [k for k in exp_f if k in act_f and abs(act_f[k][1] - exp_f[k][1]) > 1e-9]
    check(area, f"Voxel vollstaendig ({len(exp_f)} erwartet, {len(act_f)} geschrieben)", not missing and not extra,
          f"fehlen {len(missing)} {missing[:3]}; zuviel {len(extra)} {extra[:3]}")
    check(area, "Voxel-Material (Deckschicht/Unterboden/Grundgestein/Schichtbaender/Wasser)", not wrong_mat,
          f"{len(wrong_mat)} falsch, z.B. {[(k, act_f[k][0], exp_f[k][0]) for k in wrong_mat[:3]]}")
    check(area, "Voxel-Belegung (Viertel-Studs, Wasserstand)", not wrong_occ,
          f"{len(wrong_occ)} falsch, z.B. {[(k, act_f[k][1], exp_f[k][1]) for k in wrong_occ[:3]]}")
    kinds = {}
    for k, (m, o) in exp_f.items():
        kinds[m] = kinds.get(m, 0) + 1
    INFO.append(f"[{area}] Materialien in Erwartung: " + ", ".join(f"{m}:{n}" for m, n in sorted(kinds.items())))
    # Wasser ueber VOID: Beobachtung (README definiert nichts)
    for (vx, vz), lvl in void_water.items():
        col = [(k, v) for k, v in act.items() if (k[0], k[2]) == (vx, vz)]
        if len(void_water) < 10:
            ys = sorted(k[1] for k, _ in col)
            INFO.append(f"[{area}] Wasser ueber VOID-Spalte ({vx},{vz}) Stand {lvl}: Luau schrieb {len(col)} Voxel"
                        + (f" (y-Index {ys[0]}..{ys[-1]}, also {ys[0]*4}..{ys[-1]*4+4} Studs)" if col else " -> Wasser fehlt (Block ohne Terrain wird uebersprungen oder Stand liegt ueber dem Block)"))
    # Zusatzformen
    exp_ops = []
    for op in world.terrain_ops:
        if op["op"] == "Ball":
            exp_ops.append(("FillBall", op["c"], op["r"], op["material"]))
        elif op["op"] == "Block":
            exp_ops.append(("FillBlock", op["cf"], op["size"], op["material"]))
        elif op["op"] == "Cylinder":
            exp_ops.append(("FillCylinder", op["cf"], [op["height"], op["r"]], op["material"]))
        elif op["op"] == "Wedge":
            exp_ops.append(("FillWedge", op["cf"], op["size"], op["material"]))
    got = [c for c in calls if c["m"].startswith("Fill")]
    okc = len(got) == len(exp_ops)
    detail = f"{len(got)} statt {len(exp_ops)}"
    if okc:
        for g, e in zip(got, exp_ops):
            gd = [g.get("c") or g.get("cf"), g.get("r") if g["m"] == "FillBall" else (g.get("size") or [g.get("height"), g.get("r")])]
            if g["m"] != e[0] or g["mat"] != e[3] or not close(gd[0], e[1], 2e-3) or not close(gd[1], e[2], 2e-3):
                okc = False
                detail = f"Abweichung {g} gegen {e}"
                break
    check(area, "Zusatzformen: Reihenfolge, Argumente, Material (inkl. Air; unbekannte Operation uebersprungen)", okc, detail[:400])
    # Last: erst Hoehenkarte, dann Zusatzformen
    idx = [i for i, c in enumerate(calls) if c["m"] == "WriteVoxels"]
    idf = [i for i, c in enumerate(calls) if c["m"].startswith("Fill")]
    check(area, "Zusatzformen laufen nach der Hoehenkarte", not idx or not idf or max(idx) < min(idf))
    # Material-Farben
    sm = [c for c in calls if c["m"] == "SetMaterialColor"]
    exp_c = {k: [v / 255 for v in rgb] for k, rgb in world.meta["materialColors"].items()}
    check(area, "SetMaterialColor je Eintrag", {c["mat"]: c["color"] for c in sm}.keys() == exp_c.keys() and all(close(c["color"], exp_c[c["mat"]], 1e-9) for c in sm))
    tp = build["terrainProps"]["props"]
    ok = all(k in tp for k in world.meta["water"]) and close(tp["WaterColor"], [v / 255 for v in world.meta["water"]["WaterColor"]], 1e-9) and tp["WaterTransparency"] == 0.9
    check(area, "Terrain-Wassereigenschaften gesetzt", ok, str(tp))
    return act


def compare_props(area, build, world):
    check(area, "Build fehlerfrei", build["ok"], str(build.get("err"))[:600])
    if not build["ok"]:
        return
    islands = build["islands"]
    check(area, "genau ein Ordner Workspace.Island1 (alter wurde ersetzt)", len(islands) == 1 and not any(k["name"] == "AlterInhalt" for k in islands[0]["kids"]),
          f"{len(islands)} Ordner")
    if len(islands) != 1:
        return
    isl = islands[0]
    cats, unknown = reference.expected_models(world)
    got_cats = {k["name"]: k["kids"] for k in isl["kids"]}
    check(area, "Kategorie-Ordner (Reihenfolge des ersten Auftretens)", [k["name"] for k in isl["kids"]] == list(cats.keys()), str([k["name"] for k in isl["kids"]]))
    warns = [l["m"] for l in build["logs"] if l["k"] == "warn"]
    check(area, "Warnung nur fuer unbekannte Vorlage", warns == [f"[WorldBuilder] Unbekannte Vorlage: {u}" for u in unknown], str(warns[:4]))
    problems = {"Struktur": [], "Teil-Eigenschaften": [], "CFrame/Groesse": [], "Licht": [], "Mesh": [], "Pivot": []}
    nparts = nmodels = 0
    for cat, exp_models in cats.items():
        got_models = got_cats.get(cat, [])
        if len(got_models) != len(exp_models):
            problems["Struktur"].append(f"{cat}: {len(got_models)} Modelle statt {len(exp_models)}")
            continue
        for mi, (gm, em) in enumerate(zip(got_models, exp_models)):
            nmodels += 1
            if gm["name"] != em["name"] or gm["class"] != "Model" or len(gm["kids"]) != len(em["parts"]):
                problems["Struktur"].append(f"{cat}[{mi}] {gm['name']} {len(gm['kids'])} Teile statt {em['name']} {len(em['parts'])}")
                continue
            if not close(gm["props"].get("WorldPivot", []), em["pivot"], 2e-3):
                problems["Pivot"].append(f"{cat}[{mi}] {gm['props'].get('WorldPivot')} vs {em['pivot']}")
            for pi, (gp, ep) in enumerate(zip(gm["kids"], em["parts"])):
                nparts += 1
                pr = gp["props"]
                tag = f"{cat}[{mi}].{pi}({ep['name']})"
                if gp["class"] != ep["class"] or gp["name"] != ep["name"]:
                    problems["Teil-Eigenschaften"].append(f"{tag} Klasse {gp['class']}/{gp['name']}")
                if not close(pr.get("Size"), ep["size"], 2e-3):
                    problems["CFrame/Groesse"].append(f"{tag} Size {pr.get('Size')} vs {ep['size']}")
                if not close(pr.get("CFrame"), ep["cframe"], 4e-3):
                    problems["CFrame/Groesse"].append(f"{tag} CFrame {pr.get('CFrame')} vs {ep['cframe']}")
                if not close(pr.get("Color"), ep["color"], 1e-6):
                    problems["Teil-Eigenschaften"].append(f"{tag} Farbe {pr.get('Color')} vs {ep['color']}")
                shape = pr.get("Shape")
                okshape = (shape == ep["shape"]) if ep["shape"] else shape in (None, "Enum.PartType.Block")
                flags = (pr.get("Material") == ep["material"], pr.get("Transparency", 0) == ep["transparency"], pr.get("Reflectance", 0) == ep["reflectance"],
                         pr.get("CastShadow") == ep["castShadow"], pr.get("CanCollide") == ep["collide"], pr.get("CanQuery") == ep["collide"],
                         pr.get("CanTouch") is False, pr.get("Anchored") is True, pr.get("TopSurface") == "Enum.SurfaceType.Smooth",
                         pr.get("BottomSurface") == "Enum.SurfaceType.Smooth", okshape)
                if not all(flags):
                    problems["Teil-Eigenschaften"].append(f"{tag} Flags {flags} {pr}")
                kids = {k["class"]: k for k in gp["kids"]}
                if ep["mesh"] != ("SpecialMesh" in kids) or (ep["mesh"] and kids["SpecialMesh"]["props"].get("MeshType") != "Enum.MeshType.Sphere"):
                    problems["Mesh"].append(f"{tag} SpecialMesh {list(kids)}")
                if ep["light"] is None:
                    if "PointLight" in kids:
                        problems["Licht"].append(f"{tag} unerwartetes Licht")
                else:
                    lp = kids.get("PointLight", {}).get("props")
                    if not lp or not close(lp.get("Range"), ep["light"]["range"], 1e-6) or lp.get("Brightness") != ep["light"]["brightness"] \
                            or lp.get("Shadows") is not False or not close(lp.get("Color"), ep["light"]["color"], 1e-6):
                        problems["Licht"].append(f"{tag} Licht {lp} vs {ep['light']}")
    check(area, f"Struktur: Ordner/Modelle/Teilanzahl ({nmodels} Modelle, {nparts} Teile)", not problems["Struktur"], "; ".join(problems["Struktur"][:3]))
    check(area, "Teil-Lage: Size = size*s und CFrame = place * CFrame.new(pos*s, R)", not problems["CFrame/Groesse"], f"{len(problems['CFrame/Groesse'])}x z.B. " + "; ".join(problems["CFrame/Groesse"][:2]))
    check(area, "Model.WorldPivot = place (Reihenfolge CFrame.Angles(0,ry,0)*Angles(rx,0,rz))", not problems["Pivot"], "; ".join(problems["Pivot"][:2]))
    check(area, "Teil-Eigenschaften (Form, Farbe/Variante inkl. Fallback, Material, Transparenz, Kollision ...)", not problems["Teil-Eigenschaften"], f"{len(problems['Teil-Eigenschaften'])}x z.B. " + "; ".join(problems["Teil-Eigenschaften"][:2])[:500])
    check(area, "Ellipsoid = Block + SpecialMesh(Sphere)", not problems["Mesh"], "; ".join(problems["Mesh"][:2]))
    check(area, "PointLight (Range*s, max 60, Farbe aus Rolle bzw. 'color')", not problems["Licht"], "; ".join(problems["Licht"][:2])[:500])


def compare_lighting(area, build, world, skybox=None):
    check(area, "Build fehlerfrei", build["ok"], str(build.get("err"))[:600])
    if not build["ok"]:
        return
    cfg = world.meta["lighting"]
    lt = build["lighting"]
    kids = {k["name"]: k for k in lt["kids"]}
    expect = {"Atmosphere": ("WorldAtmosphere", "Atmosphere"), "Bloom": ("WorldBloom", "BloomEffect"), "ColorCorrection": ("WorldColorCorrection", "ColorCorrectionEffect"),
              "SunRays": ("WorldSunRays", "SunRaysEffect"), "DepthOfField": ("WorldDepthOfField", "DepthOfFieldEffect"), "Sky": ("WorldSky", "Sky")}
    ok = True
    detail = []
    for key, (nm, cls) in expect.items():
        k = kids.get(nm)
        if not k or k["class"] != cls:
            ok = False
            detail.append(f"{nm} fehlt")
            continue
        for prop, val in cfg[key].items():
            exp = [c / 255 for c in val] if isinstance(val, tuple) and len(val) == 3 and not isinstance(val, str) else str(val) if str(val).startswith("Enum.") else val
            if not close(k["props"].get(prop), exp, 1e-9):
                ok = False
                detail.append(f"{nm}.{prop}={k['props'].get(prop)} statt {exp}")
    check(area, "Lighting-Kinder (Atmosphere, Bloom, ColorCorrection, SunRays, DepthOfField, Sky) mit Eigenschaften", ok, "; ".join(detail[:4]))
    ok, detail = True, []
    for prop, val in cfg["Lighting"].items():
        exp = [c / 255 for c in val] if isinstance(val, tuple) and not isinstance(val, str) else str(val) if str(val).startswith("Enum.") else val
        if not close(lt["props"].get(prop), exp, 1e-9):
            ok = False
            detail.append(f"{prop}={lt['props'].get(prop)} statt {exp}")
    check(area, "Lighting-Eigenschaften (inkl. Technology-Enum)", ok, "; ".join(detail[:4]))
    warns = [l["m"] for l in build["logs"] if l["k"] == "warn"]
    check(area, "keine Warnungen beim Setzen von Eigenschaften", not [w for w in warns if "nicht gesetzt" in w], str(warns[:3]))
    bk = {k["name"] for k in (build["backup"] or {"kids": []})["kids"]}
    check(area, "alte Sky/Atmosphere/Bloom nach ServerStorage.WorldBuilderBackup gesichert, fremde Kinder bleiben", {"OldSky", "OldAtmosphere", "OldBloom"} <= bk and "KeepMe" in kids, str(bk))
    if skybox:
        sky = kids["WorldSky"]["props"]
        got = {k: sky.get("Skybox" + k) for k in skybox}
        check(area, "Skybox-IDs aus Settings in Sky gesetzt", got == skybox, str(got))
    else:
        sky = kids["WorldSky"]["props"]
        check(area, "ohne Skybox-IDs: keine Skybox-Eigenschaften gesetzt + Hinweis geloggt", not any(k.startswith("Skybox") for k in sky) and any("Hinweis" in l["m"] for l in build["logs"]), str(sky))


def compare_misc(area, build, world, hidden=True):
    bp = build["baseplate"]["props"]
    tex = build["baseplate"]["kids"][0]["props"]
    if hidden:
        ok = bp.get("Transparency") == 1 and bp.get("CanCollide") is False and bp.get("CanQuery") is False and bp.get("CanTouch") is False and bp.get("CastShadow") is False and tex.get("Transparency") == 1
        check(area, "Baseplate nur ausgeblendet (Transparenz, Kollision, Textur), nicht verschoben", ok and "Part:Baseplate" in build["workspaceKids"], str(bp))
    else:
        check(area, "hideBaseplate=false laesst die Baseplate unberuehrt", bp.get("Transparency", 0) == 0 and bp.get("CanCollide") is True, str(bp))
    sp = build["spawn"]["props"]["CFrame"]
    s = world.meta["spawn"]
    check(area, "SpawnLocation auf spawn + halbe Hoehe gesetzt", close(sp[:3], [s[0], s[1] + 0.5, s[2]], 1e-9), str(sp[:3]))
    check(area, "ChangeHistoryService:SetWaypoint aufgerufen", build["history"] == ["WorldBuilder"], str(build["history"]))


# ------------------------------------------------------------------ Hauptprogramm

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--builder", default=str(REAL_SRC / "init.luau"), help="zu testende init.luau (Standard: die echte Datei)")
    ap.add_argument("--settings", default=str(REAL_SRC / "Settings.luau"))
    ap.add_argument("--skip-bundle", action="store_true")
    args = ap.parse_args()
    args.builder = str(Path(args.builder).resolve())
    args.settings = str(Path(args.settings).resolve())
    OUT.mkdir(exist_ok=True)
    t0 = time.time()

    print("1) Test-Welt bauen ...")
    world = make_world.build_world()
    exp_vox, void_water = reference.expected_voxels(world)
    print(f"   {len(exp_vox)} erwartete Voxel, {len(world.placements)} Platzierungen")

    print("2) Exportieren ...")
    wb, stats = export_world(world, "world", args.builder, args.settings)
    wb_chunks, stats2 = export_world(world, "world_chunks", args.builder, args.settings, chunk_chars=20)
    nchunks = json.loads("{}") or None
    meta_chunks = {n: len(list((wb_chunks / "Data" / "Terrain").glob(f"{n}_*.luau"))) for n in "HMWSD"}
    INFO.append(f"Export: {stats}; kleine Stuecke (20 Zeichen) je Kanal: {meta_chunks}")
    sky_ids = {"Bk": "rbxassetid://111", "Dn": "rbxassetid://222", "Ft": "rbxassetid://333", "Lf": "rbxassetid://444", "Rt": "rbxassetid://555", "Up": "rbxassetid://666"}
    wb_sky, _ = export_world(world, "world_sky", args.builder, args.settings)
    (wb_sky / "Settings.luau").write_text("return { skybox = { " + ", ".join(f'{k} = "{v}"' for k, v in sky_ids.items()) + " } }\n")
    # Kopien der Daten sparen: world_sky braucht nur Lichter -> trotzdem eigener Export (billig)

    print("3) Dekoder-Einzeltests ...")
    run_decoder_tests(Path(args.builder))

    print("4) Lune-Laeufe ...")
    # (a) init.luau, Skript-Baum-Mock, Standard-Chunks: voller Build zweimal
    r_full, secs = lune_scenario("init", wb, "init_full", "full")
    INFO.append(f"init_full: {secs:.1f} s")
    if r_full is None:
        check("init.luau", "Lune-Lauf", False, "siehe Ausgabe")
    else:
        check("init.luau", "kein Laufzeitfehler im Mock-Lauf (Syntax, nil-Zugriffe, Mock-Roblox-API-Pruefungen)", r_full.get("error") is None and all(b["ok"] for b in r_full["builds"]),
              str(r_full.get("error") or [b["err"] for b in r_full["builds"] if not b["ok"]])[:800])
        if r_full["builds"] and r_full["builds"][0]["ok"]:
            b1 = r_full["builds"][0]
            compare_terrain("init.luau/Terrain", b1, world, exp_vox, void_water)
            compare_props("init.luau/Deko", b1, world)
            compare_lighting("init.luau/Licht", b1, world)
            compare_misc("init.luau/Sonstiges", b1, world)
            if len(r_full["builds"]) > 1:
                b2 = r_full["builds"][1]
                a1, _, _ = voxel_dict(b1["terrain"])
                a2, _, _ = voxel_dict(b2["terrain"])
                a1.pop("__dup__", None); a2.pop("__dup__", None)
                check("init.luau/Neubau", "zweiter Build() liefert dieselben Voxel", b2["ok"] and a1 == a2)
                check("init.luau/Neubau", "zweiter Build(): weiterhin genau ein Island1, Lighting ohne doppelte Effekte",
                      b2["ok"] and len(b2["islands"]) == 1 and sorted(k["name"] for k in b2["lighting"]["kids"]) == sorted(k["name"] for k in b1["lighting"]["kids"]),
                      str([k["name"] for k in b2["lighting"]["kids"]]))
                n1 = len(b1["backup"]["kids"]); n2 = len((b2["backup"] or {"kids": []})["kids"])
                INFO.append(f"Backup-Ordner: nach Build 1: {n1} Kinder, nach Build 2: {n2} (eigene alte World*-Effekte werden mit weggesichert)")
            for n in r_full["notes"]:
                INFO.append("Mock-Notiz: " + n)
    # Terrain mit kleinen Base64-Stuecken
    r_ch, secs = lune_scenario("init", wb_chunks, "init_chunks", "terrain_only")
    INFO.append(f"init_chunks: {secs:.1f} s")
    if r_ch is None:
        check("Base64-Stuecke", "Lune-Lauf", False, "")
    else:
        a = voxel_dict(r_ch["builds"][0]["terrain"])[0] if r_ch["builds"] and r_ch["builds"][0]["ok"] else None
        if a is not None:
            a.pop("__dup__", None)
            vw = set(void_water)
            af = {k: v for k, v in a.items() if (k[0], k[2]) not in vw}
            ef = {k: v for k, v in exp_vox.items() if (k[0], k[2]) not in vw}
            check("Base64-Stuecke", "Terrain identisch bei 20-Zeichen-Stuecken (viele Stueck-Grenzen, Padding im letzten Stueck)", af == ef, f"{len(af)} vs {len(ef)}")
        else:
            check("Base64-Stuecke", "Build fehlerfrei", False, str(r_ch["builds"][0]["err"] if r_ch["builds"] else r_ch.get("error"))[:500])
    # Optionen
    r_t, _ = lune_scenario("init", wb, "init_terrain_off", "terrain_off")
    if r_t and r_t["builds"] and r_t["builds"][0]["ok"]:
        b = r_t["builds"][0]
        check("Optionen", "Build{terrain=false, lighting=false}: kein Terrain-Aufruf, Deko da, Licht unberuehrt",
              not b["terrain"] and len(b["islands"]) == 1 and b["islands"][0]["kids"] and not any(k["name"].startswith("World") for k in b["lighting"]["kids"]))
    else:
        check("Optionen", "terrain=false lief", False, str(r_t and (r_t.get("error") or r_t["builds"][0]["err"]))[:400])
    r_p, _ = lune_scenario("init", wb, "init_props_off", "props_off")
    if r_p and r_p["builds"] and r_p["builds"][0]["ok"]:
        b = r_p["builds"][0]
        check("Optionen", "Build{props=false, hideBaseplate=false}: Terrain da, alter Island1 unberuehrt, Baseplate sichtbar",
              any(c["m"] == "WriteVoxels" for c in b["terrain"]) and len(b["islands"]) == 1 and b["islands"][0]["kids"][0]["name"] == "AlterInhalt")
        compare_misc("Optionen", b, world, hidden=False)
    else:
        check("Optionen", "props=false lief", False, str(r_p and (r_p.get("error") or r_p["builds"][0]["err"]))[:400])
    r_s, _ = lune_scenario("init", wb_sky, "init_sky", "lighting_only")
    if r_s and r_s["builds"] and r_s["builds"][0]["ok"]:
        compare_lighting("Skybox", r_s["builds"][0], world, skybox=sky_ids)
    else:
        check("Skybox", "lighting_only lief", False, str(r_s and (r_s.get("error") or r_s["builds"][0]["err"]))[:400])

    # (b) Bundle
    if not args.skip_bundle:
        bundle = OUT / "bundle" / "BuildIsland1.luau"
        make_bundle(wb, bundle)
        INFO.append(f"Bundle: {bundle.stat().st_size/1e3:.0f} KB")
        for mode in ("bundle-module", "bundle-script"):
            r, secs = lune_scenario(mode, bundle, mode.replace("-", "_"), "full")
            INFO.append(f"{mode}: {secs:.1f} s")
            area = mode
            if r is None:
                check(area, "Lune-Lauf", False, "")
                continue
            check(area, "kein Laufzeitfehler", r.get("error") is None and r["builds"] and all(b["ok"] for b in r["builds"]), str(r.get("error") or [b["err"] for b in r["builds"] if not b["ok"]])[:800])
            if r["builds"] and r["builds"][0]["ok"]:
                b1 = r["builds"][0]
                compare_terrain(area + "/Terrain", b1, world, exp_vox, void_water)
                compare_props(area + "/Deko", b1, world)
                compare_lighting(area + "/Licht", b1, world)
                compare_misc(area + "/Sonstiges", b1, world)

    # ---- Bericht
    print()
    areas = []
    for a, n, ok, d in RESULTS:
        if a not in areas:
            areas.append(a)
    failed = 0
    for a in areas:
        print(f"== {a}")
        for aa, n, ok, d in RESULTS:
            if aa == a:
                print(f"   [{'OK ' if ok else 'FEHLER'}] {n}" + ("" if ok else f"\n           {d}"))
                failed += (not ok)
    print("\nInfos:")
    for i in INFO:
        print("  -", i)
    total = len(RESULTS)
    print(f"\n{total - failed}/{total} Pruefungen bestanden ({time.time() - t0:.0f} s)")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
