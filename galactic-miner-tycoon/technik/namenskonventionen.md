# Namenskonventionen

Entscheidung: `../entscheidungen/003-sprachen.md`.

| Was | Schreibweise | Beispiel |
|---|---|---|
| Doku/Konzept | Deutsch | – |
| Code, Namen | Englisch | – |
| ModuleScript / Klassen | `PascalCase` | `CurrencyService.luau` |
| Variablen, Funktionen | `camelCase` | `buyBuilding` |
| Konstanten | `UPPER_SNAKE` | `MAX_SILO_LEVEL` |
| IDs in Daten (Ressourcen, Gebäude, Planeten) | `snake_case`, englisch | `iron_ore`, `drill_basic`, `lava` |
| RemoteEvents | `PascalCase`, Verb zuerst | `BuyBuilding`, `StartTravel` |
| Modelle/Assets in Studio | `PascalCase` | `DrillBasic`, `RocketPad` |
| Dateien im Repo (Doku) | `kleinbuchstaben-mit-bindestrich.md` | `spielablauf.md` |

Dateiendung für Code: `.luau`. Jede Datei beginnt mit `--!strict`, wo möglich.
