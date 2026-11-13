# Entscheidung 022: Insel 1 wird halb so groß (Radius 1000 statt 2000)

- **Status:** Beschlossen (Jos, 14.11.2026; Ju bitte gegenlesen – ersetzt die Größenangabe aus 015/020)
- **Datum:** 14.11.2026
- **Von:** Jos

## Frage
Die Welt von Insel 1 wirkt im Place groß, aber leer und leblos. Soll die Insel kleiner werden, damit mehr Details pro Fläche möglich sind?

## Entscheidung
1. **Radius 1000 Studs** statt 2000 (Jos: „Mach die Map mal deutlich kleiner, vielleicht die Hälfte“). Die Fläche wird damit ein Viertel.
2. **Objektgrößen bleiben** (Tafelberge, Hoodoos, Bäume, Kristalle). Nur Abstände, Ringe, Landmarken-Radien und das Randgebirge rücken zusammen. Bei gleichem Teile-Budget (≤ 25 000) steigt die Detail-Dichte etwa auf das Vierfache.
3. **Erz-Ringe werden halbiert** (Mindest- bis Maximalradius):

| Erz | bisher (020) | neu |
|---|---|---|
| Eisen | 10–200 | 10–100 |
| Kupfer | 250–700 | 125–350 |
| Kohle | 600–1100 | 300–550 |
| Kristall | 1100–1600 | 550–800 |
| Titan | 1600–2000 | 800–1000 |

## Warum
Das KI-Zielbild (`../referenz/bilder/welt/ki-ziel/insel1-ziel-v1.png`) zeigt alle 30–60 Studs etwas Lesbares. Bei Radius 2000 reicht das Teile-Budget dafür nicht, die Mitte bleibt leer. Kleinere Fläche = dichtere, lebendigere Welt.

## Folgen
- Weltgenerator (`../werkzeuge/weltgenerator/`, Jos' Claude): Ringe, Washes, Landmarken-Slots, Randgebirge, Kamera „ziel“ auf halben Radius.
- Daten/Code (Ju, Auftrag 003): `../daten/ressourcen.md` (Planeten-Radius, Ring-Tabelle), `src/ReplicatedStorage/Shared/Config/Ores.luau` (`ISLAND_RADIUS`, `minRadius`/`maxRadius`).
- **Offen für Ju:** Wege werden halb so lang. Passt das Balancing (020) noch, und braucht Insel 1 den Rover (016) weiterhin?
