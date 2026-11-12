# Bewegung und Physik

Status: **Vorschlag (12.11.2026, Jos)**. Zweite Runde: deutlich stärker, weil Jos die erste Stufe (110 / 9) zu schwach fand. Konzept: `../spiel/17-bewegung-und-physik.md`, Entscheidung 017.
Code-Gegenstück: `../src/ReplicatedStorage/Shared/Config/Movement.luau`

## Insel 1
| Name im Code | Wert | Roblox-Standard | Bedeutung |
|---|---|---|---|
| `gravity` | 60 | 196,2 | Schwerkraft in Studs/s² (Mond wäre 32,7) |
| `jumpHeight` | 12 | 7,2 | Sprunghöhe in Studs |
| `walkSpeed` | 16 | 16 | Laufgeschwindigkeit in Studs/s (Training: +2 je Stufe, `upgrades.md`) |
| `groundAccelTime` | 0,4 s | sofort | Anlaufen am Boden |
| `groundDecelTime` | 0,55 s | sofort | Abbremsen am Boden (ca. 3 Studs Nachrutschen) |
| `airControlTime` | 1,6 s | sofort | Umlenken in der Luft |
| `landingDust` | an | – | Staubwolke bei der Landung |
| `landingDustMinSpeed` | 18 Studs/s | – | Erst ab dieser Fallgeschwindigkeit staubt es |

Die Zeiten bedeuten: Nach dieser Zeit folgt die Bewegung zu ca. 95 % der Eingabe.

## Was die Zahlen bewirken
| | Absprung (Studs/s) | Zeit in der Luft | 20 Studs tief fallen |
|---|---|---|---|
| Roblox-Standard (196,2 / 7,2) | 53 | 0,54 s | 0,45 s |
| **Insel 1 (60 / 12)** | **38** | **1,26 s** | **0,82 s** |
| erste Stufe, zu schwach (110 / 9) | 44 | 0,81 s | 0,60 s |
| zum Vergleich: etwas schwerer (70 / 11) | 39 | 1,12 s | 0,76 s |
| zum Vergleich: Mond (32,7 / 9) | 24 | 1,48 s | 1,11 s |
