# 03 – Abbau & Automatisierung

- **Status:** Entwurf – M1-Vorschlag steht unten, wartet auf Bestätigung
- **Zuletzt geändert:** 11.11.2026
- **Mindmap-Ast:** Automated Mining (Automated Drills, Conveyor Belts, Banner Drills)

## Worum geht es?
Die Basis fördert Rohstoffe selbstständig. Bohrer graben, Förderbänder transportieren später zu Fabriken und Lagern.

## Was wir schon wissen
- Bohrer fördern automatisch, verbesserte Varianten kommen mit der Forschung.
- Förderbänder (M2) sind nur Optik plus Rate-Berechnung im Hintergrund, keine echten Items (spart Performance).

## Vorschlag für M1 (noch nicht bestätigt)
- Ein Bohrer liefert **Rohstoff pro Sekunde** direkt auf das Konto des Spielers. Es gibt kein Lager-Limit (Silos kommen in M2).
- Der Server rechnet einmal pro Sekunde (nicht jeder Bohrer einzeln). Es sind keine echten Items nötig.
- Raten: Eisen-Bohrer 1,0/s, Kupfer-Bohrer 0,5/s auf Level 1. Jedes Level erhöht die Rate um 50 % der Grundrate.
- Maximal 6 Bohrer in M1 (siehe `02`).
- Offline-Ertrag: **nein** in M1 (später klären).

## Offene Fragen
- [ ] Rate-Zahlen ok?
- [ ] Offline-Ertrag später?
- [ ] Müssen Förderbänder selbst verlegt werden? (M2)

## Verknüpft mit
`04`, `08-forschung-und-techbaum.md`, `../daten/gebaeude.md`
