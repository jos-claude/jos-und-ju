# Entscheidung 011: Mindestradius und Spawn nach Fortschritt

- **Status:** Beschlossen (Regeln). Zahlen sind Vorschläge.
- **Datum:** 11.11.2026
- **Von:** Ju (Jos bitte gegenlesen)
- **Ergänzt:** 010

## Entscheidung
1. **Jedes Erz hat einen Mindestradius um die Basis.** Ein Vorkommen darf nie näher an der Basis erscheinen, auch wenn es zufällig platziert wird. Seltene Erze haben einen großen Mindestradius.
2. **Vorkommen sind nicht von Anfang an da.** Sie erscheinen mit dem Fortschritt des Spielers, nach und nach.
3. Von den Vorschlägen aus der letzten Runde gelten:
   - **Offline-Ertrag gibt es.** Er ist durch die Kasten-Kapazität begrenzt: Sind die Kästen voll, passiert nichts mehr (korrigiert 11.11.2026, Ju).
   - **Eigene Karte pro Spieler**, einmal zufällig erzeugt und gespeichert.
   - **Bänder verlegt man Punkt für Punkt** (Antippen), auch am Handy.
4. **Noch offen:** Dürfen Bänder abzweigen und zusammenlaufen? (siehe `../spiel/03`)

## Folgen
- `../spiel/02`, `03`, `../daten/ressourcen.md` (Radien und Spawn-Regeln).
- Technisch: Spawn-Logik pro Spieler (`ResourceNodeService`), Zufall mit gespeichertem Seed, siehe `../technik/architektur.md`.

## Hinweis
Der Offline-Punkt war zuerst falsch eingetragen (ich hatte „kein Offline-Ertrag“ angenommen). Ju hat korrigiert: Offline-Ertrag ja, begrenzt durch die vollen Kästen.
