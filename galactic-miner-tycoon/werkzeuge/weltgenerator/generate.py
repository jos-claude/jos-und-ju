"""Weltgenerator: erzeugt Insel 1 und schreibt Luau-Daten + Vorschau-Daten.

    python3 generate.py            # Seed aus der Insel-Datei
    python3 generate.py --seed 7   # anderer Seed
    python3 generate.py --no-luau  # nur Vorschau (schneller)
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from worldgen import export_luau, export_preview, island1  # noqa: E402

GAME = HERE.parent.parent  # galactic-miner-tycoon/
LUAU_OUT = GAME / "src" / "ServerStorage" / "WorldBuilder"
PREVIEW_OUT = HERE / "out" / "preview"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--no-luau", action="store_true")
    args = ap.parse_args()
    t0 = time.time()
    world = island1.build(args.seed)
    print(f"Welt erzeugt in {time.time() - t0:.1f} s: {len(world.placements)} Objekte, {len(world.templates)} Vorlagen, {len(world.terrain_ops)} Zusatzformen")
    parts = sum(len(world.templates[p[0]].parts) for p in world.placements)
    print(f"Teile gesamt: {parts}")
    export_preview.export(world, PREVIEW_OUT)
    print(f"Vorschau-Daten: {PREVIEW_OUT}")
    if not args.no_luau:
        stats = export_luau.export(world, LUAU_OUT)
        print(f"Luau-Daten: {LUAU_OUT / 'Data'} {stats}")
    print(f"Fertig in {time.time() - t0:.1f} s")


if __name__ == "__main__":
    main()
