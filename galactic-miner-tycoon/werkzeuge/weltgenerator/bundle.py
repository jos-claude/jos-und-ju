"""Packt den WorldBuilder samt Daten in EIN Luau-Skript: galactic-miner-tycoon/welt/BuildIsland1.luau

    python3 bundle.py        # nach python3 generate.py ausfuehren

Das Einzel-Skript funktioniert ohne Rojo:
- als ModuleScript:  require(game.ServerStorage.BuildIsland1).Build()
- als Code in der Befehlsleiste / per loadstring: baut sofort (script ist dort nil)
"""
from __future__ import annotations

from pathlib import Path

HERE = Path(__file__).resolve().parent
GAME = HERE.parent.parent
SRC = GAME / "src" / "ServerStorage" / "WorldBuilder"
OUT = GAME / "welt" / "BuildIsland1.luau"

BEGIN = "-- BEGIN LOADER"
END = "-- END LOADER"


def module_key(path: Path) -> str:
    return path.relative_to(SRC).with_suffix("").as_posix()


def main():
    init = (SRC / "init.luau").read_text(encoding="utf-8")
    a = init.index(BEGIN)
    b = init.index(END) + len(END)
    head, tail = init[:a], init[b:]

    files = [SRC / "Settings.luau"] + sorted((SRC / "Data").rglob("*.luau"))
    lines = [
        BEGIN + " (eingebettet von werkzeuge/weltgenerator/bundle.py)",
        "local MODULES: { [string]: () -> any } = {}",
        "",
    ]
    for f in files:
        body = f.read_text(encoding="utf-8").rstrip("\n")
        if f.name == "Settings.luau":
            lines.append("-- >>> Einstellungen: Skybox-IDs hier eintragen (siehe assets/himmel/README.md)")
        lines.append(f'MODULES["{module_key(f)}"] = function()')
        lines.append(body)
        lines.append("end")
        lines.append("")
    lines += [
        "local moduleCache: { [string]: any } = {}",
        "local function loadData(path: string): any",
        "\tlocal value = moduleCache[path]",
        "\tif value == nil then",
        "\t\tlocal loader = MODULES[path]",
        "\t\tassert(loader, \"Daten fehlen: \" .. path)",
        "\t\tvalue = loader()",
        "\t\tmoduleCache[path] = value",
        "\tend",
        "\treturn value",
        "end",
        "",
        "local function listData(path: string): { string }",
        "\tlocal names = {}",
        "\tfor name in MODULES do",
        "\t\tif string.sub(name, 1, #path + 1) == path .. \"/\" then",
        "\t\t\ttable.insert(names, name)",
        "\t\tend",
        "\tend",
        "\ttable.sort(names)",
        "\treturn names",
        "end",
        END,
    ]
    tail = tail.rstrip()
    assert tail.endswith("return WorldBuilder"), "init.luau muss mit 'return WorldBuilder' enden"
    tail = tail[: -len("return WorldBuilder")] + (
        "-- Als ModuleScript: liefert WorldBuilder zurueck. Als Script/Befehlsleiste: baut sofort.\n"
        "if script ~= nil and script:IsA(\"ModuleScript\") then\n"
        "\treturn WorldBuilder\n"
        "end\n"
        "WorldBuilder.Build()\n"
    )
    header = (
        "-- BuildIsland1.luau – AUTOMATISCH ERZEUGT (werkzeuge/weltgenerator/bundle.py). Nicht von Hand aendern,\n"
        "-- ausser den Skybox-IDs im Einstellungs-Block. Anleitung: welt/README.md\n"
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(header + head + "\n".join(lines) + tail, encoding="utf-8")
    print(f"{OUT} ({OUT.stat().st_size / 1e6:.2f} MB, {len(files)} Module)")


if __name__ == "__main__":
    main()
