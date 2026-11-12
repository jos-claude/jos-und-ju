#!/usr/bin/env python3
"""Selbsttest des Testlaufs: baut absichtlich fehlerhafte Kopien von init.luau und prueft, dass der Test sie erkennt.

    python3 tests/run_mutants.py
Jede Mutante muss mindestens eine fehlgeschlagene Pruefung ausloesen (sonst ist der Test an der Stelle blind).
"""
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import patches  # noqa: E402

REAL = patches.OUT   # Grundlage: echte init.luau plus bekannte Patch-Vorschlaege (patches.py), damit die Grundlinie gruen ist
OUT = HERE / "out" / "mutants"

def _details(out):
    """Fehlertexte der fehlgeschlagenen Pruefungen (Zeile nach [FEHLER])."""
    lines = out.splitlines()
    return [lines[i + 1].strip() for i, l in enumerate(lines) if "[FEHLER]" in l and i + 1 < len(lines)]


MUTANTS = [
    ("Vorhersage: oben-links addieren statt abziehen", "- buffer.readu16(q, (idx - n - 1) * 2)", "+ buffer.readu16(q, (idx - n - 1) * 2)"),
    ("Null-Lauf um 1 zu kurz", "zeros = (t - 1) // 2 - 1", "zeros = (t - 1) // 2"),
    ("RLE: Lauf um 1 zu kurz gefuellt", "buffer.fill(out, idx, value, run)", "buffer.fill(out, idx, value, run - 1)"),
    ("Base64: Padding '==' liefert 2 statt 1 Byte", "buffer.writeu8(out, o, n // 65536)\n\t\t\to += 1", "buffer.writeu8(out, o, n // 65536)\n\t\t\to += 2"),
    ("Varint: Stellenwert 64 statt 128", "mult *= 128", "mult *= 64"),
    ("Belegung durch 8 statt 4", "local occ = math.min(1, (h - yb) / cell)", "local occ = math.min(1, (h - yb) / (cell * 2))"),
    ("Schichtband ohne Voxelmitte", "math.floor(yb + cell * 0.5 + off) % period", "math.floor(yb + off) % period"),
    ("Schichtband mit math.abs bei negativen Hoehen", "math.floor(yb + cell * 0.5 + off) % period", "math.abs(math.floor(yb + cell * 0.5 + off)) % period"),
    ("Schichtversatz S ignoriert", "local off = buffer.readu8(S, idx) + strataBase", "local off = strataBase"),
    ("Deckschicht <= statt <", "elseif depth < topDepth then", "elseif depth <= topDepth then"),
    ("Unterboden: subDepth vertauscht", "elseif depth < subDepth then", "elseif depth < topDepth then"),
    ("Fluessigkeit nur oberhalb der Oberkante (Ufer-Voxel fehlt)", "if waterLevel > h and yb < waterLevel and yb + cell > h then", "if waterLevel > h and yb < waterLevel and yb >= h then"),
    ("Fluessigkeit ohne Bedingung Stand > Oberkante (Befund)", "if waterLevel > h and yb < waterLevel", "if yb < waterLevel"),
    ("Fluessigkeitswert durch 8", "liquid[ix][iy][iz] = math.min(1, (waterLevel - yb) / cell)", "liquid[ix][iy][iz] = math.min(1, (waterLevel - yb) / (cell * 2))"),
    ("Kanal LiquidOccupancy bekommt feste Belegung", "LiquidOccupancy = liquid,", "LiquidOccupancy = occupancy,"),
    ("Rueckfall: Wasser ueberschreibt feste Voxel", "if oRow[iz] == 0 and lRow[iz] > 0 then", "if lRow[iz] > 0 then"),
    ("Rueckfall nicht dauerhaft", "useChannels = false\n", "useChannels = true\n"),
    ("Neubau: Attribut wird nicht erkannt", 'child:GetAttribute("WorldBuilder") then', 'child:GetAttribute("WorldBuilderX") then'),
    ("Neubau: eigene Effekte ohne Attribut", 'inst:SetAttribute("WorldBuilder", true)', 'inst.Name = inst.Name'),
    ("Fuelltiefe addiert statt subtrahiert", "local bottom = h - buffer.readu8(D, idx) * cell", "local bottom = h - (buffer.readu8(D, idx) + 1) * cell"),
    ("Region3 zu klein (sz-1)", "Vector3.new(origin + (cx + sx) * cell, y0 + ny * cell, origin + (cz + sz) * cell)", "Vector3.new(origin + (cx + sx) * cell, y0 + ny * cell, origin + (cz + sz - 1) * cell)"),
    ("Hoehe ohne hmin", "local h = q / hq + hmin\n\t\t\t\t\t\t\tlocal bottom", "local h = q / hq\n\t\t\t\t\t\t\tlocal bottom"),
    ("Drehreihenfolge vertauscht", "CFrame.Angles(0, ry, 0) * CFrame.Angles(rx, 0, rz)", "CFrame.Angles(rx, 0, rz) * CFrame.Angles(0, ry, 0)"),
    ("Teil-Lage ohne Maßstab", "cf[1] * s, cf[2] * s, cf[3] * s,", "cf[1], cf[2], cf[3],"),
    ("Groesse ohne Maßstab", "Vector3.new(size[1] * s, size[2] * s, size[3] * s)", "Vector3.new(size[1], size[2], size[3])"),
    ("Licht ohne 60er-Grenze", "math.min(60, light.Range * s)", "light.Range * s"),
    ("Rotationsmatrix transponiert", "cf[4], cf[5], cf[6],\n\t\t\t\t\t\t\tcf[7], cf[8], cf[9],", "cf[4], cf[7], cf[10],\n\t\t\t\t\t\t\tcf[5], cf[8], cf[11],"),
    ("Zusatzform Block: Groesse vertauscht", "Vector3.new(op.size[1], op.size[2], op.size[3]), m)\n\t\telseif op.op == \"Cylinder\"", "Vector3.new(op.size[3], op.size[2], op.size[1]), m)\n\t\telseif op.op == \"Cylinder\""),
    ("Zylinder: height/r vertauscht", "op.height, op.r, m", "op.r, op.height, m"),
]


def main():
    patches.main_write() if hasattr(patches, "main_write") else None
    patches.OUT.parent.mkdir(parents=True, exist_ok=True)
    patches.OUT.write_text(patches.apply(patches.REAL.read_text(encoding="utf-8")), encoding="utf-8")
    src = REAL.read_text(encoding="utf-8")
    OUT.mkdir(parents=True, exist_ok=True)
    blind = 0
    base = subprocess.run([sys.executable, str(HERE / "run_luau_check.py"), "--builder", str(REAL), "--skip-bundle"], capture_output=True, text=True, env={**__import__("os").environ, "LUNE_TIMEOUT": "12"})
    mb = re.search(r"(\d+)/(\d+) Pruefungen bestanden", base.stdout)
    base_failed = int(mb.group(2)) - int(mb.group(1))
    base_names = set(re.findall(r"\[FEHLER\] (.+)", base.stdout))
    print(f"Grundlinie (echte init.luau): {base_failed} Pruefung(en) schlagen an (bekannte Befunde)")
    only = sys.argv[1] if len(sys.argv) > 1 else ""   # optional: nur Mutanten, deren Name diesen Text enthaelt
    for i, (name, old, new) in enumerate(MUTANTS):
        if only not in name:
            continue
        if old not in src:
            print(f"[?] {name}: Muster nicht gefunden (init.luau wurde geaendert?)")
            blind += 1
            continue
        f = OUT / f"mutant_{i:02d}.luau"
        f.write_text(src.replace(old, new), encoding="utf-8")
        p = subprocess.run([sys.executable, str(HERE / "run_luau_check.py"), "--builder", str(f), "--skip-bundle"], capture_output=True, text=True, env={**__import__("os").environ, "LUNE_TIMEOUT": "12"})
        m = re.search(r"(\d+)/(\d+) Pruefungen bestanden", p.stdout)
        names = set(re.findall(r"\[FEHLER\] (.+)", p.stdout))
        # erkannt: neue fehlgeschlagene Pruefung ODER bei bereits fehlerhafter Pruefung ein anderer Detailtext
        failed = not m or bool(names - base_names) or p.stdout.count("FEHLER") > base.stdout.count("FEHLER") or _details(p.stdout) != _details(base.stdout)
        status = "erkannt " if failed else "UEBERSEHEN"
        blind += not failed
        print(f"[{status}] {name}" + (f"  ({int(m.group(2)) - int(m.group(1))} Pruefungen schlagen an)" if m else ""))
    print(f"\n{len(MUTANTS) - blind}/{len(MUTANTS)} Mutanten erkannt")
    sys.exit(1 if blind else 0)


if __name__ == "__main__":
    main()
