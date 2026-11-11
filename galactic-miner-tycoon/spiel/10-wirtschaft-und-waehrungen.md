# 10 – Wirtschaft & Währungen

- **Status:** Entwurf – M1-Vorschlag steht unten, wartet auf Bestätigung
- **Zuletzt geändert:** 11.11.2026
- **Mindmap-Ast:** Credits, Gems (siehe Entscheidung 006: keine Credits)

## Worum geht es?
Womit der Spieler bezahlt und wie schnell Preise steigen.

## Beschlossen
- **Es gibt keine Credits.** Gebäude und Upgrades auf dem eigenen Planeten werden mit Rohstoffen bezahlt (Entscheidung 006).
- Gems gibt es vorerst nicht. Monetarisierung bleibt Entwurf (`12-monetarisierung.md`).

## Vorschlag für M1 (noch nicht bestätigt)
- **Eisenerz** bezahlt neue Bohrer. **Kupfererz** bezahlt Bohrer-Upgrades. So braucht der Spieler beide Rohstoffe.
- **Kein Verkaufen** in M1: Rohstoffe werden nur ausgegeben.
- Preise steigen mit jedem Kauf: `Preis(n) = Basispreis × 1,15^n` (n = bisherige Käufe dieser Art, auf ganze Zahl gerundet).
- Zahlen stehen in `../daten/gebaeude.md` und `../daten/upgrades.md`.

## Offene Fragen
- [ ] Rohstoffe der Planeten später auch als Kosten für Schiff und Forschung (M3/M4)?
- [ ] Wird später doch etwas verkauft?
- [ ] Wie kommt Monetarisierung ohne Gems aus?

## Verknüpft mit
`11`, `12`, `../daten/upgrades.md`, `../daten/gebaeude.md`
