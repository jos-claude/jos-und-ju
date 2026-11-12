# Weltgenerator und WorldBuilder (Insel 1)

- **Status:** Entwurf (Werkzeug steht, Welt-Design ist ein Vorschlag, siehe `../referenz/welt-design-insel-1.md`)
- **Zuletzt geändert:** 12.11.2026

## Worum geht es?
Die Welt von Insel 1 (Gelände, Felsen, Pflanzen, Kristalle, Licht, Himmel) wird **nicht von Hand** in Studio gebaut, sondern von einem Generator als Daten erzeugt. Ein Luau-Skript baut daraus die Welt in Studio auf. Vorteil: Die Claudes können die Welt ändern, und man kann sie jederzeit neu bauen.

```
werkzeuge/weltgenerator (Python)  ──►  Luau-Daten  ──►  Studio: Welt bauen
                                  └──►  Vorschau-Bilder (zum Prüfen ohne Studio)
```

## Zwei Wege, die Welt in Studio zu bauen
**A) Mit Rojo (normaler Weg bei uns):** Rojo synchronisiert `src/ServerStorage/WorldBuilder` nach `ServerStorage.WorldBuilder`. Dann im **Edit-Modus** (nicht im Play-Test) in der Befehlsleiste (View → Command Bar):
```lua
require(game.ServerStorage.WorldBuilder).Build()
```
**B) Ohne Rojo:** das Einzel-Skript `../welt/BuildIsland1.luau` als ModuleScript in `ServerStorage` legen und `require(game.ServerStorage.BuildIsland1).Build()` ausführen. Anleitung: `../welt/README.md`.

Beide Wege bauen dasselbe. Das Bauen dauert etwa 1–3 Minuten (Fortschritt in der Ausgabe). Danach den Place speichern.

| Was | Wohin |
|---|---|
| Gelände | `Workspace.Terrain` (wird vorher gelöscht) |
| Felsen, Pflanzen, Kristalle | `Workspace.Island1` (wird vorher gelöscht) |
| Licht, Atmosphere, Bloom, Farbkorrektur, Sonnenstrahlen, Himmel | `Lighting` (alte Effekte werden nach `ServerStorage.WorldBuilderBackup` verschoben) |
| Baseplate | bleibt, wird nur ausgeblendet |
| SpawnLocation | wird auf den Spawnpunkt an der Basis gesetzt |

Nur Teile neu bauen: `Build({ terrain = false })` (nur Deko + Licht), `Build({ props = false })` (nur Gelände + Licht), `Build({ lighting = false })`.

## Himmel (Skybox)
Die 6 Himmelsbilder liegen in `../assets/himmel/`. Roblox-Skripte können keine Bilder hochladen, deshalb einmal von Hand: Bilder in Studio hochladen und die IDs in `src/ServerStorage/WorldBuilder/Settings.luau` (bzw. im Einstellungs-Block von `BuildIsland1.luau`) eintragen, dann `Build({ terrain = false, props = false })`. Schritte: `../assets/himmel/README.md`.

## Welt ändern (für die Claudes)
1. `werkzeuge/weltgenerator/` – siehe dortige `README.md` (Datenformat, Befehle).
2. `python3 generate.py` → schreibt `src/ServerStorage/WorldBuilder/Data/` und die Vorschau-Daten.
3. `node shoot.js` → Vorschau-Bilder in `out/shots/` ansehen und mit dem Referenzbild vergleichen.
4. `python3 bundle.py` → erneuert `welt/BuildIsland1.luau`.
5. Committen, pushen, in Studio neu bauen.

**Wichtig:** Die Daten in `src/ServerStorage/WorldBuilder/Data/` und `welt/BuildIsland1.luau` nie von Hand ändern, sie werden überschrieben. Änderungen gehören in den Generator.

## Offene Fragen
- [ ] Sollen Erz-Vorkommen später nur auf den „Bauzonen“ des Generators spawnen? (Der Generator kennt sie; ein Export für das Spiel wäre einfach.)
- [ ] Welt bei jedem Spieler gleich (fester Seed, Vorschlag) oder je Spieler anders (Entscheidung 011 betrifft bisher nur die Erz-Verteilung)?
