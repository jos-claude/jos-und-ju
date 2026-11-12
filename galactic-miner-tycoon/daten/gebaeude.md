# Gebäude (Basis)

Status: **abgestimmt für M1 (11.11.2026, Ju), Zahlen dürfen später angepasst werden**. Richtung: Entscheidungen 009 und 010. Währung sind Erze (006). Bohrer-Preis: `Preis(n) = Basispreis × 1,15^n`, n = schon gekaufte Bohrer dieses Erzes.

## Lager-Kästen (schalten das Erz frei)
| ID | Kasten für | Kosten | Start-Kapazität |
|---|---|---|---|
| `bin_iron` | Eisen | gratis (steht schon) | 100 |
| `bin_copper` | Kupfer | 40 Eisen | 100 |
| `bin_coal` | Kohle | 60 Eisen + 30 Kupfer | 100 |
| `bin_crystal` | Kristall | 100 Kupfer + 50 Kohle | 100 |
| `bin_titanium` | Titan | 150 Kohle + 60 Kristall | 100 |

**Kapazitäts-Upgrade (je Kasten):** Stufe 2 / 3 / 4 / 5 = Kapazität 250 / 500 / 1000 / 2500. Kosten: das Erz des Kastens selbst, 50 / 100 / 200 / 400.

## Bohrer (werden auf Vorkommen platziert)
Beliebig viele, solange Vorkommen da sind und man bezahlen kann.

| ID | Name | Kosten (Basis) | Wirkung | Voraussetzung |
|---|---|---|---|---|
| `drill_iron` | Eisen-Bohrer | 20 Eisen (nicht mehr gratis, Entscheidung 016) | 1,0 Eisen/s, Puffer 50 | – |
| `drill_copper` | Kupfer-Bohrer | 40 Eisen | 0,8 Kupfer/s | `bin_copper` |
| `drill_coal` | Kohle-Bohrer | 40 Eisen + 20 Kupfer | 0,6 Kohle/s | `bin_coal` |
| `drill_crystal` | Kristall-Bohrer | 60 Kupfer + 30 Kohle | 0,4 Kristall/s | `bin_crystal` |
| `drill_titanium` | Titan-Bohrer | 80 Kohle + 40 Kristall | 0,3 Titan/s | `bin_titanium` |

## Förderband
| ID | Name | Kosten | Wirkung |
|---|---|---|---|
| `belt_segment` | Förderband-Segment (4 Studs) | 2 Eisen (ab Raum 4 zusätzlich 1 Kupfer) | transportiert bis zu 5 Erz/s Richtung Lager |

Beispiel: 80 Studs Band sind 20 Segmente = 40 Eisen.

## Räume (feste Kosten, Entscheidung 016)
Kupfer-Vorkommen erscheinen mit Raum 2, Kohle mit 3, **Kristall mit 4 (Garage)**, Titan mit 5.

| Raum | Name | Kosten | Was man dort tut |
|---|---|---|---|
| 1 | Start-Halle | gratis | Lager, Bohrer kaufen |
| 2 | Schmiede | 50 Eisen | Spitzhacke und Rucksack verbessern, Teleportfeld zur Lobby |
| 3 | Maschinenhalle | 100 Eisen + 15 Kupfer | Förderbänder kaufen, Bohrer aufwerten |
| 4 | **Garage** | 150 Eisen + 60 Kupfer + 20 Kohle | Rover kaufen und verbessern |
| 5 | Trainingsraum | 250 Eisen + 120 Kupfer + 60 Kohle + 20 Kristall | Geschwindigkeit (weitere Spielerwerte später) |
| 6 | Forschungslabor | 400 Kupfer + 200 Kohle + 80 Kristall + 20 Titan | Techbaum: bessere Bohrer, Bänder, größere Lager |
| 7 | Raketen-Hangar | 800 Kupfer + 400 Kohle + 200 Kristall + 100 Titan | Rakete bauen und betreten |

Die Garage kostet absichtlich **kein Kristall**, weil Kristall erst mit ihr erscheint.

## Rover und Garage (Entscheidung 016)
| ID | Name | Kosten (Basis) | Wirkung |
|---|---|---|---|
| `rover` | Mondauto (Rover) | 150 Eisen + 80 Kupfer + 30 Kohle | fahrbar, ca. 60 Studs/s |
| `rover_motor` | Motor (4 Stufen) | 100 Kupfer + 40 Kohle | +15 Studs/s je Stufe |
| `rover_cargo` | Laderaum (4 Stufen) | 120 Eisen + 60 Kupfer | trägt +50 Erz je Stufe, nimmt Erz aus Bohrern mit |
| `rover_boost` | Turbo (3 Stufen) | 80 Kohle + 30 Kristall | kurzer Geschwindigkeitsschub mit Abkühlzeit |
| `rover_scanner` | Erz-Scanner | 60 Kristall | Pfeil zum nächsten Vorkommen eines Erzes |

## Später
| ID | Name | Kosten | Wirkung |
|---|---|---|---|
| `factory_basic` | Fabrik | _ | verarbeitet |

## Band-Zusammenführung (später, Entscheidung 012)
| ID | Name | Kosten | Wirkung |
|---|---|---|---|
| `belt_merger` | Sammler/Verteiler | _ (kaufbar in der Förderband-Werkstatt) | führt mehrere Bänder zu einem zusammen |

## Rakete (Ziel der Insel, Entscheidung 013)
| ID | Name | Kosten | Wirkung |
|---|---|---|---|
| `rocket` | Rakete | _ sehr viel von allen Erzen, am meisten Titan (Balancing mit Test, Ziel: Insel dauert ca. 1 Stunde) | Betreten bringt zur nächsten Insel |
