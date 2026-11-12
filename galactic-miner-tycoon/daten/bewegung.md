# Bewegung und Physik

Status: **Vorschlag (12.11.2026, Jos)**, noch nicht in Studio getestet. Konzept: `../spiel/17-bewegung-und-physik.md`, Entscheidung 017.
Code-Gegenstück: `../src/ReplicatedStorage/Shared/Config/Movement.luau`

## Insel 1
| Name im Code | Wert | Roblox-Standard | Bedeutung |
|---|---|---|---|
| `gravity` | 110 | 196,2 | Schwerkraft in Studs/s² (Mond wäre 32,7) |
| `jumpHeight` | 9 | 7,2 | Sprunghöhe in Studs |
| `walkSpeed` | 16 | 16 | Laufgeschwindigkeit in Studs/s (Training: +2 je Stufe, `upgrades.md`) |
| `groundAccelTime` | 0,25 s | sofort | Anlaufen am Boden |
| `groundDecelTime` | 0,35 s | sofort | Abbremsen am Boden (ca. 2 Studs Nachrutschen) |
| `airControlTime` | 0,9 s | sofort | Umlenken in der Luft |
| `landingDust` | an | – | Staubwolke bei der Landung |
| `landingDustMinSpeed` | 18 Studs/s | – | Erst ab dieser Fallgeschwindigkeit staubt es |

Die Zeiten bedeuten: Nach dieser Zeit folgt die Bewegung zu ca. 95 % der Eingabe.

## Was die Zahlen bewirken
| | Absprung (Studs/s) | Zeit in der Luft | 20 Studs tief fallen |
|---|---|---|---|
| Roblox-Standard (196,2 / 7,2) | 53 | 0,54 s | 0,45 s |
| **Insel 1 (110 / 9)** | **44** | **0,81 s** | **0,60 s** |
| zum Vergleich: schwerer (130 / 9) | 48 | 0,74 s | 0,55 s |
| zum Vergleich: leichter (90 / 9) | 40 | 0,89 s | 0,67 s |
| zum Vergleich: Mond (32,7 / 9) | 24 | 1,48 s | 1,11 s |
