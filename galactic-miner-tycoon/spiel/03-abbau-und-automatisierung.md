# 03 – Abbau & Automatisierung

- **Status:** Richtung beschlossen (Entscheidung 009), Zahlen sind Vorschlag
- **Zuletzt geändert:** 11.11.2026
- **Mindmap-Ast:** Automated Mining (Automated Drills, Conveyor Belts, Banner Drills)

## Worum geht es?
Der Spieler baut immer mehr Bohrer. Erst holt er das Erz von Hand, später bringen Förderbänder es automatisch.

## Beschlossen (009)
1. Ein **Bohrer** fördert selbst, sammelt das Erz aber in einem **eigenen Puffer**.
2. Der Spieler **nimmt das Erz aus dem Bohrer** (Taste/Berührung), trägt es zur **Kiste**. Dort landet es im **Inventar**.
3. **Förderbänder** fahren das Erz automatisch vom Bohrer zur Kiste. Sie kosten Materialien.
4. Seltene Erze liegen weiter weg, also braucht man längere Förderbänder.

## Vorschlag (Zahlen noch nicht bestätigt)
- Bohrer-Rate: Eisen 1,0/s. Der Puffer fasst 50 Einheiten. Ist er voll, hört der Bohrer auf.
- Der Spieler trägt anfangs **20 Einheiten** auf einmal. Das Upgrade „Stärke“ erhöht das.
- Ein Bohrer ist ein Bauwerk mit Slot. Weitere Bohrer kosten mehr (×1,15 je Kauf).
- Förderbänder: Eine **Förderstrecke** verbindet ein Erzfeld mit der Kiste und kostet nach Entfernung Materialien. Sie ist nur Optik plus Rate-Berechnung im Hintergrund, keine echten Items (Performance).
- Die Bänder bringen höchstens so viel, wie die Strecke schafft (Durchsatz, z. B. 5/s). Bessere Bänder später.
- Offline-Ertrag: nein.

## Offene Fragen
- [ ] Soll der Spieler Förderbänder selbst verlegen oder nur die Strecke kaufen?
- [ ] Wie viel trägt der Spieler am Anfang?
- [ ] Gibt es ein Inventar-Limit, oder ist die Kiste unbegrenzt?

## Verknüpft mit
`04`, `08-forschung-und-techbaum.md`, `../daten/gebaeude.md`
