# 16 – Räume, Spitzhacke und Garage (Vorschlag)

- **Status:** abgestimmt (Ju, 12.11.2026) mit einer Änderung: Die Garage kommt früher (Raum 4), damit der Rover schon vor dem Kristall da ist. Zahlen sind änderbar.
- **Ändert, wenn bestätigt:** `02-heimatplanet.md`, `../daten/gebaeude.md`, `../daten/upgrades.md`, `../daten/ressourcen.md`

## Idee der Nutzer
- Der Spieler startet **ohne Bohrer** und baut **per Spitzhacke von Hand** Eisen ab. Den ersten Bohrer muss er sich kaufen, das geht aber schnell.
- Während die Bohrer arbeiten, kann der Spieler weiter von Hand farmen, damit er nie nur zuschaut.
- Es gibt einen **Raum zum Verbessern der Spitzhacke**.
- Eine **Garage** schaltet später ein Mondauto (Rover) frei.

## Die Schleife in einem Satz
Ich hacke Erz, kaufe damit Bohrer und neue Räume, die Bohrer liefern mehr Erz, mit dem ich weiter hinaus komme, bis ich genug für die Rakete habe.

## Die 7 Räume (Vorschlag)
Die Raumnummern bestimmen, wann neue Erze auftauchen (siehe `../daten/ressourcen.md`).

| Raum | Name | Kosten | Was man dort tut | Neu freigeschaltet |
|---|---|---|---|---|
| 1 | Start-Halle | gratis | Lager mit Eisen-Kasten, Bohrer kaufen | Eisen |
| 2 | Schmiede | 50 Eisen | Spitzhacke und **Rucksack** verbessern, **Teleportfeld zur Lobby** | Kupfer-Vorkommen |
| 3 | Maschinenhalle | 100 Eisen + 15 Kupfer | Förderbänder kaufen, Bohrer aufwerten | Kohle-Vorkommen |
| 4 | Garage | 150 Eisen + 60 Kupfer + 20 Kohle | Rover kaufen und verbessern | Kristall-Vorkommen |
| 5 | Trainingsraum | 250 Eisen + 120 Kupfer + 60 Kohle + 20 Kristall | Geschwindigkeit | Titan-Vorkommen |
| 6 | Forschungslabor | 400 Kupfer + 200 Kohle + 80 Kristall + 20 Titan | Techbaum: bessere Bohrer, Bänder, größere Lager | – |
| 7 | Raketen-Hangar | 800 Kupfer + 400 Kohle + 200 Kristall + 100 Titan | Rakete bauen und betreten, danach nächste Insel | – |

Die Garage kommt bewusst **vor dem Kristall**: Kristall liegt ab 1100 Studs und ist zu Fuß schon anstrengend (Änderung von Ju). Sie kostet deshalb kein Kristall. Titan liegt ab 1600 Studs und erscheint mit Raum 5. Raum 7 ersetzt Werft und Startplatz (vorher 6 Räume).

## Spitzhacke (Vorschlag)
- **Abbau von Hand:** Man schlägt auf ein Erzvorkommen, das Erz geht direkt in den Tragevorrat (ohne Rucksack 10, mit Rucksack mehr, siehe `../daten/upgrades.md`). Dann zum Lager laufen und in den Kasten legen (wie in 003).
- **Vorkommen werden durch Handabbau nicht leer** (Vorschlag).
- **Härte:** Hartes Erz braucht eine bessere Spitzhacke, um es von Hand abzubauen. Bohrer haben diese Grenze nicht, sie brauchen nur den Kasten des Erzes. So lohnt sich der Schmiede-Raum auch später.

| Stufe | Name | Erz pro Schlag | Schlagtempo | Kosten | Kann abbauen |
|---|---|---|---|---|---|
| 1 | Rost-Spitzhacke | 1 | 1,0 s | – | Eisen |
| 2 | Eisen-Spitzhacke | 2 | 1,0 s | 30 Eisen | + Kupfer |
| 3 | Stahl-Spitzhacke | 3 | 0,9 s | 80 Eisen + 30 Kupfer | + Kohle |
| 4 | Kristall-Spitzhacke | 4 | 0,8 s | 150 Kupfer + 60 Kohle | + Kristall |
| 5 | Titan-Spitzhacke | 6 | 0,7 s | 120 Kohle + 80 Kristall | + Titan |

Stufe 5 kostet bewusst kein Titan, sonst kann man sie nicht kaufen, weil sie selbst nötig wäre, um Titan abzubauen.

## Bohrer (Änderung zu bisher)
Der erste Bohrer ist **nicht mehr gratis**. Er kostet 20 Eisen (danach ×1,15 je Kauf). Von Hand sind 20 Eisen nach etwa 20 Sekunden zusammen.

## Garage und Rover (Vorschlag)
Der Rover ist ein kleines Mondauto, das man fährt. Er steht in der Garage und folgt dem Spieler nicht von selbst.

| ID | Upgrade | Wirkung | Stufen | Kosten (Basis) |
|---|---|---|---|---|
| `rover` | Rover kaufen | fährt etwa 60 Studs/s | – | 150 Eisen + 80 Kupfer + 30 Kohle |
| `rover_motor` | Motor | +15 Studs/s je Stufe | 4 | 100 Kupfer + 40 Kohle |
| `rover_cargo` | Laderaum | trägt +50 Erz je Stufe, nimmt Erz aus Bohrern mit | 4 | 120 Eisen + 60 Kupfer |
| `rover_boost` | Turbo | kurzer Geschwindigkeitsschub mit Abkühlzeit | 3 | 80 Kohle + 30 Kristall |
| `rover_scanner` | Erz-Scanner | Pfeil zeigt zum nächsten Vorkommen eines Erzes | 1 | 60 Kristall |

Rover-Lackierungen wären später ein kosmetischer Kauf (`12-monetarisierung.md`).

## Tutorial-Ablauf mit der Spitzhacke (Vorschlag)
1. Spawn auf der Insel, kurze überspringbare Cutscene.
2. Der Spieler hat die Spitzhacke und ein Eisenvorkommen direkt vor der Basis. Pfeil: „Schlage das Erz.“
3. Mit etwa 20 Eisen im Lager kauft er den **ersten Bohrer**.
4. Beim zweiten Eisen-Bohrer läuft die erste Automatisierung. Der Spieler hackt weiter von Hand.
5. Mit 50 Eisen kauft er **Raum 2 (Schmiede)**. Dort steht das Teleportfeld zur Lobby.
Dauer etwa 2 bis 3 Minuten, passend zu Entscheidung 014.

## Fragen (alle beantwortet)
1. **7 Räume:** bestätigt.
2. **Härte-System:** bestätigt.
3. **Vorkommen unendlich beim Handabbau:** bestätigt.
4. **Teleportfeld in der Schmiede (Raum 2):** bestätigt.

## Verknüpft mit
`02`, `03`, `10`, `../entscheidungen/014-lobby-und-spielstaende.md`, `../daten/gebaeude.md`
