"""Patch-Vorschlaege fuer init.luau (nur Kopien unter tests/out/patched, die echte Datei bleibt unveraendert).

    python3 tests/patches.py        # schreibt tests/out/patched/init.luau
    python3 tests/run_luau_check.py --builder tests/out/patched/init.luau
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent
REAL = HERE.parent.parent.parent / "src" / "ServerStorage" / "WorldBuilder" / "init.luau"
OUT = HERE / "out" / "patched" / "init.luau"

PATCHES = [
    # Fluessigkeit nur, wenn der Wasserstand ueber der Terrain-Oberkante liegt (README: "Wasser fuellt von der Oberkante bis zum Stand")
    ("if yb < waterLevel and yb + cell > h then", "if waterLevel > h and yb < waterLevel and yb + cell > h then"),
]


def apply(src: str) -> str:
    for old, new in PATCHES:
        src = src.replace(old, new)   # fehlt das Muster (Patch schon eingebaut), passiert nichts
    return src


if __name__ == "__main__":
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(apply(REAL.read_text(encoding="utf-8")), encoding="utf-8")
    print(OUT)
