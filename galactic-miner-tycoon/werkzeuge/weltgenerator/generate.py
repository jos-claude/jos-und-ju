"""Weltgenerator: erzeugt Insel 1 und schreibt Luau-Daten + Vorschau-Daten.

    python3 generate.py            # Seed 1
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
    ap.add_argument("--seed", type=int, default=island1.SEED)
    ap.add_argument("--no-luau", action="store_true")
    ap.add_argument("--debugmap", action="store_true", help="Draufsicht als PNG nach out/debug_top.png")
    args = ap.parse_args()
    t0 = time.time()
    world = island1.build(args.seed)
    print(f"Welt erzeugt in {time.time() - t0:.1f} s: {len(world.placements)} Objekte, {len(world.templates)} Vorlagen, "
          f"{len(world.terrain_ops)} Zusatzformen")
    parts = sum(len(world.templates[p[0]].parts) for p in world.placements)
    lights = sum(sum(1 for q in world.templates[p[0]].parts if q.light) for p in world.placements)
    print(f"Teile gesamt: {parts}, PointLights: {lights}")
    for line in getattr(world, "report", []):
        print(line)
    export_preview.export(world, PREVIEW_OUT)
    print(f"Vorschau-Daten: {PREVIEW_OUT}")
    from worldgen import debugmap
    (HERE / "out" / "shots").mkdir(parents=True, exist_ok=True)
    debugmap.render_build(world, world.checks["build"], HERE / "out" / "shots" / "karte_bauzonen.png",
                          getattr(world.ctx, "deco_zone", None))
    if args.debugmap:
        debugmap.render(world, HERE / "out" / "debug_top.png")
    if not args.no_luau:
        stats = export_luau.export(world, LUAU_OUT)
        print(f"Luau-Daten: {LUAU_OUT / 'Data'} {stats}")
    print(f"Fertig in {time.time() - t0:.1f} s")


if __name__ == "__main__":
    main()
