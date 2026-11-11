# Ressourcen

Status: **abgestimmt für M1 (11.11.2026, Ju), Zahlen dürfen später angepasst werden**. Namen sind frei erfunden und änderbar. Regeln: Entscheidungen 010 und 011.

## Rohstoffe auf dem Heimatplaneten
Vorkommen sind zufällig verteilt, ungefährlich und haben einen **Mindestradius** um die Basis. Sie erscheinen erst mit dem Fortschritt des Spielers.

| ID | Name | Mindestradius (Studs) | Maximalradius (Kartenrand) | Stufe |
|---|---|---|---|---|
| `iron_ore` | Eisenerz | 10 | 500 | 1 |
| `copper_ore` | Kupfererz | 80 | 500 | 2 |
| `coal` | Kohle | 150 | 500 | 3 |
| `crystal` | Kristall | 250 | 500 | 4 |
| `titanium_ore` | Titanerz | 400 | 500 | 5 |

## Wann erscheinen Vorkommen? (Vorschlag)
Der **Auslöser** ist der Fortschritt des Spielers, nicht die Uhrzeit allein.

| Erz | Erste Vorkommen erscheinen, wenn … | Danach |
|---|---|---|
| Eisen | Spielstart: 3 Vorkommen | +1 alle 5 Minuten Spielzeit bis 10 |
| Kupfer | Raum 2 freigeschaltet | 2 sofort, dann +1 alle 5 Minuten bis 8 |
| Kohle | Raum 3 freigeschaltet | 2 sofort, dann +1 alle 5 Minuten bis 6 |
| Kristall | Raum 4 freigeschaltet | 1 sofort, dann +1 alle 10 Minuten bis 5 |
| Titan | Raum 5 freigeschaltet | 1 sofort, dann +1 alle 10 Minuten bis 4 |

Ein neues Vorkommen erscheint zufällig im erlaubten Ring (zwischen Mindestradius und Kartenrand) und nicht auf einem anderen Vorkommen. Es wird im Spielstand gespeichert.

## Rohstoffe anderer Planeten
| ID | Name | Herkunft | Stufe |
|---|---|---|---|
| `obsidian` | Obsidian | Lava-Planet | 6 |
| `ice_crystal` | Eiskristall | Eis-Welt | 6 |
| `bio_fiber` | Biofaser | Dschungel-Welt | 6 |

## Verarbeitete Materialien (Advanced Materials)
| ID | Name | Rezept (Vorschlag) |
|---|---|---|
| `iron_bar` | Eisenbarren | 3 Eisenerz |
| `circuit` | Schaltkreis | 2 Kupfererz + 1 Kristall |
| `heat_plate` | Hitzeschild-Platte | 2 Obsidian + 1 Eisenbarren |
| `coolant` | Kühlmittel | 2 Eiskristall + 1 Kristall |
| `plasma_cell` | Plasmazelle | 1 Biofaser + 1 Schaltkreis + 1 Kühlmittel |

## Offen
- Verkaufen? (Vorschlag: in M1 nicht, Rohstoffe sind die Währung, Entscheidung 006)
- Gibt es seltene Zufalls-Ressourcen?
