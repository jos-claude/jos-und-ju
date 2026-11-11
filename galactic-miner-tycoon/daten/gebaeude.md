# Gebäude (Basis)

Status: **Vorschlag, Zahlen nicht bestätigt**. Richtung: Entscheidung 009. Währung sind Erze (006). Preisformel für Bohrer: `Preis(n) = Basispreis × 1,15^n`, n = schon gekaufte Bohrer.

## Bohrer und Kiste
| ID | Name | Kosten | Wirkung | Voraussetzung |
|---|---|---|---|---|
| `chest_main` | Kiste | gratis (steht schon) | Abgabe ins Inventar | – |
| `drill_iron` | Eisen-Bohrer | 1. gratis, dann 20 Eisen (Basis) | 1,0 Eisen/s, Puffer 50 | – |
| `drill_copper` | Kupfer-Bohrer | 40 Eisen (Basis) | 0,8 Kupfer/s, Puffer 50 | Raum 2 |
| `drill_coal` | Kohle-Bohrer | 40 Eisen + 20 Kupfer (Basis) | 0,6 Kohle/s, Puffer 50 | Raum 3 |
| `drill_crystal` | Kristall-Bohrer | 60 Kupfer + 30 Kohle (Basis) | 0,4 Kristall/s | Raum 4 |
| `drill_titanium` | Titan-Bohrer | 80 Kohle + 40 Kristall (Basis) | 0,3 Titan/s | Raum 5 |

## Räume (feste Kosten)
| Raum | Kosten | Enthält (Vorschlag) |
|---|---|---|
| 1 | gratis | Start-Halle, Kiste |
| 2 | 50 Eisen | Werkbank (Upgrades Geschwindigkeit/Stärke) |
| 3 | 100 Eisen + 15 Kupfer | Förderband-Station |
| 4 | 150 Eisen + 60 Kupfer + 20 Kohle | Raumschiff-Werft |
| 5 | 250 Eisen + 120 Kupfer + 60 Kohle + 20 Kristall | Forschungslabor |
| 6 | 400 Kupfer + 200 Kohle + 80 Kristall + 20 Titan | Raketenstartplatz |

## Förderbänder
| ID | Name | Kosten | Wirkung |
|---|---|---|---|
| `belt_route` | Förderstrecke (je Erzfeld) | 5 Eisen je 10 Studs Entfernung, ab Kohle zusätzlich 2 Kupfer je 10 Studs | liefert bis zu 5 Erz/s in die Kiste |

Beispiel: Kupferfeld in 80 Studs Entfernung kostet 40 Eisen.

## Später
| ID | Name | Kosten | Wirkung |
|---|---|---|---|
| `factory_basic` | Fabrik | _ | verarbeitet |
| `silo_basic` | Silo | _ | Lager +_ |
