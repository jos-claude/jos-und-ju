# 17 – Bewegung und Physik

- **Status:** in Arbeit. Wunsch von Jos (12.11.2026): Man soll sich wie auf einem anderen Planeten bewegen. Die Zahlen sind ein **Vorschlag** und noch nicht in Studio getestet.
- **Zuletzt geändert:** 12.11.2026
- **Mindmap-Ast:** –

## Worum geht es?
Wie sich der Spieler auf Insel 1 bewegt. Es soll sich anfühlen wie auf einem fremden Planeten: etwas leichter als auf der Erde, aber nicht so extrem wie auf dem Mond.

## Das Gefühl (Jos)
- Man springt etwas langsamer ab und ist etwas länger in der Luft, aber nicht ewig.
- Die Schwerkraft ist geringer als auf der Erde, geht in Richtung Mond, ist aber viel weniger extrem.
- Auch das Laufen soll dazu passen, damit man wirklich merkt, dass man auf einem anderen Planeten ist.

## Was eingebaut ist (Code, Vorschlag)
| Was | Wirkung | Wo im Code |
|---|---|---|
| **Geringere Schwerkraft** | Alles fällt langsamer: Spieler, Erzbrocken, später der Rover | `MovementService` (Server) |
| **Sprung** | Etwas höher als normal, aber langsamer. Man ist ca. 0,8 s in der Luft statt 0,54 s | `MovementService` (Server) |
| **Trägheit am Boden** | Man läuft sanft an und rutscht beim Loslassen ca. 2 Studs nach, wie auf losem Sand | `MovementController` (Client) |
| **Schwung in der Luft** | In der Luft lenkt man nur langsam um. Wer rennend abspringt, fliegt weiter. Loslassen bremst nicht sofort | `MovementController` (Client) |
| **Landestaub** | Bei einer richtigen Landung pufft eine Staubwolke in der Farbe des Bodens auf. Kleine Stufen stauben nicht | `MovementController` (Client) |

Die Laufgeschwindigkeit bleibt beim Roblox-Standard (16). Die Insel ist groß (Radius 2000), langsamer laufen würde nur nerven. Schneller wird man über das Training (Raum 5) und den Rover.

Alle Zahlen: `../daten/bewegung.md`. Im Code: `../src/ReplicatedStorage/Shared/Config/Movement.luau`.

## So testest du es in Studio
1. `rojo serve` starten und in Studio verbinden (`../checklisten/roblox-studio-setup.md`).
2. **Play** drücken. In der Ausgabe stehen „Server started“ und „Client started“. Eine Warnung `[MovementController] …` heißt, dass die Trägheit nicht läuft.
3. Hüpfen, rennend abspringen, in der Luft die Richtung wechseln, von etwas Hohem springen.
4. Zu schwebend? `gravity` in `Movement.luau` erhöhen (z. B. 130). Zu schwer? Senken (z. B. 90). Zu rutschig? `groundDecelTime` kleiner machen. Danach `../daten/bewegung.md` mitändern.

## Offene Fragen
- [ ] Passt das Gefühl? (Jos und Ju in Studio testen)
- [ ] Bekommt jede Insel ihre eigene Schwerkraft (z. B. Lava schwerer, Eis rutschiger)? Dann bekommt jede Insel ein eigenes Profil in `Movement.luau`.
- [ ] Der Rover (Raum 4) fährt mit derselben geringen Schwerkraft und hüpft dadurch über Hügel. Gewollt (Mondauto-Gefühl) oder abschwächen?
- [ ] Sounds für Sprung und Landung (`15-optik-und-audio.md`).

## Verknüpft mit
`02-heimatplanet.md`, `16-raeume-und-spitzhacke.md` (Rover, Training), `../entscheidungen/017-leichte-schwerkraft.md`, `../daten/upgrades.md` (`walk_speed`)
