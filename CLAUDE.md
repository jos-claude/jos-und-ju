# Jos und Ju – Gemeinsames Spielprojekt

Hier konzipieren Jos und Ju zusammen Roblox-Spiele. Jedes Spiel hat einen eigenen Oberordner. Wir teilen jedes Spiel in einzelne Markdown-Dateien auf und geben uns über Aufträge gegenseitig Aufgaben. Unsere Claudes lesen und bearbeiten diese Dateien.

Sprache: Deutsch (Doku). Code und Namen im Code: Englisch.

## Spiele
- `galactic-miner-tycoon/` – Spiel 1: Tycoon + Weltraum-Abbau. **Einstieg: `galactic-miner-tycoon/README.md`, `STATUS.md` und die dortige `CLAUDE.md`.**

## Ordner pro Spiel (Beispiel `galactic-miner-tycoon/`)
- `spiel/` – das Konzept, aufgeteilt in einzelne MD-Dateien (eine Datei pro Thema, nummeriert, mit `00-vision.md`).
- `entscheidungen/` – Entscheidungslog (was, warum, wann).
- `ideen/` – Ideenspeicher.
- `auftraege/offen/` – Aufträge, die noch zu erledigen sind.
- `auftraege/erledigt/` – fertige Aufträge.
- `auftraege/_VORLAGE.md` – Vorlage für neue Aufträge.
- `checklisten/` – Meilensteine, Studio-Setup, Release.
- `daten/` – Zahlen und Listen (Ressourcen, Planeten, Upgrades).
- `referenz/` – Mindmap, Glossar, Inspiration, Links.
- `technik/` – Architektur, Namensregeln, Zusammenarbeit in Roblox Studio.
- `assets/` – Liste der Modelle, Sounds, Bilder.
- `src/` + `default.project.json` – der Spielcode (Luau, Rojo).

## Regeln für beide Claudes
1. **Vor jedem Start `git pull`**, damit die neuesten Aufträge und Änderungen da sind.
2. **Zuerst die offenen Aufträge lesen** (`<spiel>/auftraege/offen/`) und dem Nutzer sagen, welche an ihn gerichtet sind.
3. **Jeder ändert nur seine eigenen Dateien oder die, die im Auftrag genannt sind.** So gibt es keine Konflikte. Fremde Dateien nie ungefragt umschreiben.
4. **Nach jeder fertigen Arbeit committen und `git push`.** Kurze, klare Commit-Nachricht auf Deutsch.
5. **Ist ein Auftrag fertig:** unten in der Auftragsdatei einen Abschnitt „Ergebnis“ ergänzen, die Datei nach `auftraege/erledigt/` verschieben, pushen.
6. **Neue Aufträge** immer mit der Vorlage anlegen. Dateiname: `NNN-von-an-titel.md`, z. B. `001-jos-an-ju-shop-system.md`. Die Nummer zählt hoch (über `offen/` und `erledigt/` hinweg).
7. Bei einem Merge-Konflikt: nichts überschreiben, dem Nutzer erklären, was kollidiert, und fragen.
8. **Entscheidungen festhalten:** Was verbindlich wird, kommt in `entscheidungen/`. Nicht beschlossene Dinge nie als beschlossen darstellen.

## Wer ist wer
- **Jos** – GitHub-Account `jos-claude`
- **Ju** – (GitHub-Name hier eintragen, sobald bekannt)
