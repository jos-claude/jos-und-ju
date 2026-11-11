# 03 – Abbau & Automatisierung

- **Status:** Richtung beschlossen (Entscheidungen 009, 010), Zahlen sind Vorschlag
- **Zuletzt geändert:** 11.11.2026
- **Mindmap-Ast:** Automated Mining (Automated Drills, Conveyor Belts, Banner Drills)

## Worum geht es?
Der Spieler setzt immer mehr Bohrer auf Erzvorkommen und verbindet sie mit Förderbändern zum Lager.

## Beschlossen (009, 010)
1. **Vorkommen:** Eisen, Kupfer, Kohle usw. gibt es an vielen zufälligen Stellen.
2. **Bohrer** kauft man und platziert ihn selbst auf einem Vorkommen. Er fördert in einen eigenen Puffer.
3. **Von Hand:** Der Spieler nimmt das Erz aus dem Puffer, trägt es zum Lager und legt es in den passenden Kasten.
4. **Förderbänder** verlegt der Spieler selbst, vom Bohrer zum Kasten. Sie kosten Material. Ein Band füllt den Kasten automatisch.
5. **Lager-Kästen** haben ein Limit und müssen aufgerüstet werden. Ist ein Kasten voll, wird nichts mehr eingelagert.
6. Neues Erz geht erst, wenn sein Kasten gekauft ist.

## Vorschlag (Zahlen noch nicht bestätigt)
- Bohrer-Rate: Eisen 1,0/s. Puffer 50 Einheiten, dann stoppt er.
- Der Spieler trägt anfangs 20 Einheiten. Das Upgrade „Stärke“ erhöht das.
- Förderband in Segmenten (Raster), ein Segment kostet Material. Das Band ist Logik im Hintergrund plus Optik, keine echten Items (Performance). Durchsatz z. B. 5/s.
- Ein Band führt nur zu dem Kasten, der zum Erz des Bohrers passt.
- **Offline-Ertrag: ja** (Entscheidung 011). Begrenzt durch die Kasten-Kapazität: Sind die Kästen voll, passiert nichts mehr. Vorschlag: Beim Einloggen wird aus der Zeit seit dem letzten Speichern berechnet, was Bohrer mit Band geliefert hätten (höchstens bis die Kästen voll sind). Bohrer ohne Band füllen nur ihren Puffer (50).

## Offene Fragen
- Bänder verlegt man Punkt für Punkt per Antippen (011). Zusätzlich schlägt das Spiel eine Route vor (Vorschau mit Preis), die man annehmen oder durch eigenes Verlegen ersetzen kann (012).
- Zusammenführen von Bändern: später kaufbar mit Materialien (Entscheidung 012). Anfangs nur Einzelbänder.
- [ ] Sind Vorkommen unendlich oder versiegen sie?
- Bohrer sind aufwertbar (012), siehe `../daten/upgrades.md`.

## Verknüpft mit
`04`, `08-forschung-und-techbaum.md`, `../daten/gebaeude.md`
