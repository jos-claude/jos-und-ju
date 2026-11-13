# Auftrag 003: Erz-Ringe auf die halbe Insel anpassen

- **Von:** Jos (geschrieben von Jos' Claude)
- **An:** Ju
- **Datum:** 14.11.2026
- **Status:** offen
- **Meilenstein:** M1

## Ziel
Die Erzvorkommen spawnen in den neuen, halbierten Ringen, passend zur verkleinerten Insel (Radius 1000).

## Kontext
Jos hat entschieden, Insel 1 auf den halben Radius zu verkleinern: `entscheidungen/022-insel-1-halbe-groesse.md` (Tabelle der neuen Ringe dort). Jos' Claude verkleinert gerade den Weltgenerator; die neue Welt kommt über dein Rojo in den Place.

## Betroffene Dateien / Bereiche
- `daten/ressourcen.md`: Planeten-Radius 1000, Ring-Tabelle (Eisen 10–100, Kupfer 125–350, Kohle 300–550, Kristall 550–800, Titan 800–1000).
- `src/ReplicatedStorage/Shared/Config/Ores.luau`: `ISLAND_RADIUS = 1000`, `minRadius`/`maxRadius` je Erz.
- Was sonst an 2000 hängt (z. B. Abstände in `ResourceNodeService`, Rover/Garage), bitte prüfen.

## Das ist fertig, wenn …
- [ ] Daten und Config passen zu Entscheidung 022, Edit-Selbsttest wie bei Schritt 3 (Vorkommen im richtigen Ring).
- [ ] Ju hat Entscheidung 022 gegengelesen (Rückfrage Balancing/Rover dort unter „Offen für Ju“).

## Ergebnis
(wird vom Bearbeiter ausgefüllt, wenn der Auftrag fertig ist)
