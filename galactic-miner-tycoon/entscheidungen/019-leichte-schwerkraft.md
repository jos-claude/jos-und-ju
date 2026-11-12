# Entscheidung 019: Leichte Schwerkraft und Planeten-Bewegung

- **Status:** Beschlossen (Grundsatz, Jos, 12.11.2026; Ju bitte gegenlesen). Die Zahlen sind ein Vorschlag und werden in Studio getestet.
- **Datum:** 12.11.2026
- **Von:** Jos

## Frage
Wie soll sich der Spieler auf Insel 1 bewegen?

## Entscheidung
1. Auf Insel 1 gilt eine **geringere Schwerkraft** als auf der Erde. Sie geht in Richtung Mond, ist aber deutlich weniger extrem.
2. Man springt **etwas langsamer ab** und ist **etwas länger in der Luft**, aber nicht ewig.
3. Auch das **Laufen passt dazu**: leichte Trägheit am Boden, Schwung in der Luft, Staubwolke bei der Landung.
4. Die **Laufgeschwindigkeit bleibt beim Standard** (16). Schneller ist man mit dem Rover (Entscheidung 018).
5. **Nachtrag (Jos, 12.11.2026):** Die Wirkung soll **deutlich spürbar** sein. Die erste Stufe (Schwerkraft 110) war zu schwach, jetzt gilt 60 mit Sprunghöhe 12 (ca. 1,3 s in der Luft).

## Warum
Man soll wirklich merken, dass man auf einem anderen Planeten ist (Wunsch von Jos). Mond-Schwerkraft wäre zu extrem und würde das Bauen und Laufen nerven.

## Folgen
- Konzept: `../spiel/17-bewegung-und-physik.md`
- Zahlen: `../daten/bewegung.md`, Code: `../src/ReplicatedStorage/Shared/Config/Movement.luau`
- Code: `MovementService` (Server), `MovementController` (Client), siehe `../technik/architektur.md`
- Die Schwerkraft gilt für alles Lose in der Welt, also auch für den Rover (Entscheidung 016).
