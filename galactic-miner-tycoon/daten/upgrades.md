# Upgrades

Status: **Spieler- und Bohrer-Upgrades abgestimmt für M1 (11.11.2026, Ju); Schiff, Forschung und Werkzeuge werden in M3/M4 gefüllt**.

## Schiff
| ID | Name | Wirkung | Stufen |
|---|---|---|---|
| `engine` | Triebwerk | Reisezeit −, weitere Planeten | _ |
| `shield` | Schild | Schutz vor Gefahren | _ |

## Forschung (Techbaum)
| ID | Zweig | Wirkung |
|---|---|---|
| `advanced_drills` | Advanced Drills | höhere Bohrer-Rate |
| `advanced_tech` | Advanced Tech | bessere Fabriken/Silos |
| `plasma_tech` | Plasma Tech | Endgame-Technik |

## Werkzeuge
| ID | Name | Wirkung |
|---|---|---|
| `laser_pick` | Laserpickel | Abbau |
| `terraform_tool` | Terraforming-Werkzeug | Gelände verändern |
| `geo_scanner` | Geologischer Scanner | Vorkommen anzeigen |

## Preiskurve (Vorschlag)
`Preis(n) = Basispreis × 1,15^n`


## Rucksack (Schmiede, Raum 2, Entscheidung 017)
Ohne Rucksack trägt man **10** Erz in den Händen. Den Rucksack baut man in der Schmiede und verbessert ihn dort. Der Preis ist fest je Stufe.

| Stufe | Name | Tragevorrat | Kosten |
|---|---|---|---|
| 0 | Hände | 10 | – (Start) |
| 1 | Stoff-Rucksack | 25 | 30 Eisen |
| 2 | Metall-Rucksack | 40 | 60 Eisen |
| 3 | Verstärkter Rucksack | 60 | 100 Eisen + 20 Kupfer |
| 4 | Profi-Rucksack | 90 | 60 Kupfer + 20 Kohle |
| 5 | Titan-Rucksack | 130 | 150 Kupfer + 60 Kohle + 20 Kristall |

ID im Code: `backpack`. Der Rover-Laderaum (Garage) kommt zusätzlich dazu.

## Bohrer-Upgrades (abgestimmt für M1; Entscheidung 012)
Gilt je Bohrer, Level 1 bis 5. Jedes Level: +50 % der Grundrate und größerer Puffer.

| Level | Rate (Faktor) | Puffer | Kosten Eisen-Bohrer |
|---|---|---|---|
| 1 | ×1,0 | 50 | – |
| 2 | ×1,5 | 75 | 25 Eisen |
| 3 | ×2,0 | 100 | 50 Eisen + 10 Kupfer |
| 4 | ×2,5 | 150 | 100 Eisen + 30 Kupfer |
| 5 | ×3,0 | 200 | 200 Eisen + 60 Kupfer + 20 Kohle |

Bei den anderen Erzen gilt dieselbe Staffel: Kosten = Kaufpreis des Bohrers × 1,25 / 2,5 / 5 / 10 (Stufe 2 bis 5), ab Level 3 zusätzlich eine Kleinigkeit vom nächsten Erz.

## Spitzhacke (Schmiede, Raum 2, Entscheidung 016)
Abbau von Hand. Hartes Erz braucht eine bessere Spitzhacke und liefert weniger pro Schlag: **Härte-Malus** auf Erz pro Schlag (Eisen ×1,0, Kupfer ×0,8, Kohle ×0,6, Kristall ×0,4). **Titan kann man nur mit Bohrern gewinnen**, nicht von Hand. Vorkommen werden durch Handabbau nicht leer (Entscheidung 019).

| Stufe | Name | Erz pro Schlag | Schlagtempo | Kosten | Kann abbauen |
|---|---|---|---|---|---|
| 1 | Rost-Spitzhacke | 1 | 1,0 s | – (Start) | Eisen |
| 2 | Eisen-Spitzhacke | 2 | 1,0 s | 30 Eisen | + Kupfer |
| 3 | Stahl-Spitzhacke | 3 | 0,9 s | 80 Eisen + 30 Kupfer | + Kohle |
| 4 | Kristall-Spitzhacke | 4 | 0,8 s | 150 Kupfer + 60 Kohle | + Kristall |
| 5 | Titan-Spitzhacke | 6 | 0,7 s | 120 Kohle + 80 Kristall | nur schneller (Titan geht nur mit Bohrern) |

Die Rover-Upgrades stehen in `gebaeude.md`.
