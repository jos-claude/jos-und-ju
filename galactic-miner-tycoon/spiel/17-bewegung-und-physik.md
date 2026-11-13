# 17 – Bewegung und Physik

- **Status:** in Arbeit. Wunsch von Jos (12.11.2026): Man soll sich wie auf einem anderen Planeten bewegen, und zwar **deutlich spürbar**. Die Zahlen sind ein **Vorschlag**.
- **Zuletzt geändert:** 12.11.2026
- **Mindmap-Ast:** –

## Worum geht es?
Wie sich der Spieler auf Insel 1 bewegt. Es soll sich anfühlen wie auf einem fremden Planeten: etwas leichter als auf der Erde, aber nicht so extrem wie auf dem Mond.

## Das Gefühl (Jos)
- Man springt etwas langsamer ab und ist etwas länger in der Luft, aber nicht ewig.
- Die Schwerkraft ist geringer als auf der Erde, geht in Richtung Mond, ist aber viel weniger extrem.
- Auch das Laufen soll dazu passen, damit man wirklich merkt, dass man auf einem anderen Planeten ist.
- **Nachtrag (Jos, 12.11.2026):** Die erste Stufe war zu schwach. Die Physik soll **deutlich stärker** sein, damit man sofort merkt, dass es eigene Physik gibt.

## Was eingebaut ist (Code, Vorschlag)
| Was | Wirkung | Wo im Code |
|---|---|---|
| **Geringere Schwerkraft** | Alles fällt langsamer: Spieler, Erzbrocken, später der Rover | `MovementService` (Server) |
| **Sprung** | Höher als normal, aber langsamer. Man ist ca. 1,3 s in der Luft statt 0,54 s | `MovementService` (Server) |
| **Trägheit am Boden** | Man läuft sanft an und rutscht beim Loslassen ca. 3 Studs nach, wie auf losem Sand | `MovementController` (Client) |
| **Schwung in der Luft** | In der Luft lenkt man nur langsam um. Wer rennend abspringt, fliegt weiter. Loslassen bremst nicht sofort | `MovementController` (Client) |
| **Landestaub** | Bei einer richtigen Landung pufft eine Staubwolke in der Farbe des Bodens auf. Kleine Stufen stauben nicht | `MovementController` (Client) |

Die Laufgeschwindigkeit bleibt beim Roblox-Standard (16). Die Insel ist groß (Radius 1000, Entscheidung 022), langsamer laufen würde nur nerven. Ein Upgrade für die Laufgeschwindigkeit gibt es nicht, schneller ist man mit dem Rover (Entscheidung 018).

Alle Zahlen: `../daten/bewegung.md`. Im Code: `../src/ReplicatedStorage/Shared/Config/Movement.luau`.

## So testest du es in Studio
1. `rojo serve` starten und in Studio verbinden (`../checklisten/roblox-studio-setup.md`).
2. **Play** drücken. In der Ausgabe stehen „Server started“, „Client started“, `[MovementService] Planeten-Physik aktiv …` und `[MovementController] Trägheit und Schwung aktiv`. Fehlen die beiden letzten, ist der neue Code nicht im Place (Rojo verbunden? `git pull` gemacht?). Eine Warnung `[MovementController] …` heißt, dass nur die Trägheit nicht läuft.
3. Hüpfen, rennend abspringen, in der Luft die Richtung wechseln, von etwas Hohem springen.
4. Zu schwebend? `gravity` in `Movement.luau` erhöhen (z. B. 70). Zu schwer? Senken (z. B. 50). Zu rutschig? `groundDecelTime` kleiner machen. Danach `../daten/bewegung.md` mitändern.

## Offene Fragen
- [ ] Passt das Gefühl? (Jos und Ju in Studio testen)
- [ ] Bekommt jede Insel ihre eigene Schwerkraft (z. B. Lava schwerer, Eis rutschiger)? Dann bekommt jede Insel ein eigenes Profil in `Movement.luau`.
- [ ] Der Rover (Raum 4) fährt mit derselben geringen Schwerkraft und hüpft dadurch über Hügel. Gewollt (Mondauto-Gefühl) oder abschwächen?
- [ ] Sounds für Sprung und Landung (`15-optik-und-audio.md`).

## Verknüpft mit
`02-heimatplanet.md`, `16-raeume-und-spitzhacke.md` (Rover), `../entscheidungen/019-leichte-schwerkraft.md`, `../entscheidungen/018-kein-trainingsraum.md`
