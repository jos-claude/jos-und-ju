# 16 – Räume, Spitzhacke und Garage (Vorschlag)

- **Status:** Vorschlag (Claude, 12.11.2026). Noch nichts davon ist abgestimmt.
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
| 2 | Schmiede | 50 Eisen | Spitzhacke verbessern, **Teleportfeld zur Lobby** | Kupfer-Vorkommen |
| 3 | Maschinenhalle | 100 Eisen + 15 Kupfer | Förderbänder kaufen, Bohrer aufwerten | Kohle-Vorkommen |
| 4 | Trainingsraum | 150 Eisen + 60 Kupfer + 20 Kohle | Stärke (trägt mehr) und Geschwindigkeit | Kristall-Vorkommen |
| 5 | Garage | 250 Eisen + 120 Kupfer + 60 Kohle + 20 Kristall | Rover kaufen und verbessern | Titan-Vorkommen |
| 6 | Forschungslabor | 400 Kupfer + 200 Kohle + 80 Kristall + 20 Titan | Techbaum: bessere Bohrer, Bänder, größere Lager | – |
| 7 | Raketen-Hangar | 800 Kupfer + 400 Kohle + 200 Kristall + 100 Titan | Rakete bauen und betreten, danach nächste Insel | – |

Die Garage kommt bewusst **genau dann, wenn Titan erscheint**: Titan liegt ab 1600 Studs, der Rover macht den Weg erträglich. Raum 7 ersetzt Werft und Startplatz (vorher 6 Räume). Die Raumschiff-Teile entstehen im Hangar, damit es nicht noch einen Raum mehr gibt.

## Spitzhacke (Vorschlag)
- **Abbau von Hand:** Man schlägt auf ein Erzvorkommen, das Erz geht direkt in den Tragevorrat (Start 20). Dann zum Lager laufen und in den Kasten legen (wie in 003).
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

## Offene Fragen (mit Empfehlung)
1. **7 statt 6 Räume?** Empfehlung: ja, 7.
2. **Härte-System** (hartes Erz nur mit besserer Spitzhacke von Hand)? Empfehlung: ja.
3. **Vorkommen unendlich** beim Handabbau? Empfehlung: ja.
4. **Welcher Raum bekommt die Teleport-Funktion?** Empfehlung: die Schmiede (Raum 2), weil sie ohnehin als erste dazukommt.

## Verknüpft mit
`02`, `03`, `10`, `../entscheidungen/014-lobby-und-spielstaende.md`, `../daten/gebaeude.md`
