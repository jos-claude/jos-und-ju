# Jos und Ju – Gemeinsames Spielprojekt

Hier konzipieren Jos und Ju zusammen ein Roblox-Spiel. Wir teilen das Spiel in einzelne Markdown-Dateien auf und geben uns über Aufträge gegenseitig Aufgaben. Unsere Claudes lesen und bearbeiten diese Dateien.

Sprache: Deutsch.

## Ordner
- `spiel/` – das Konzept, aufgeteilt in einzelne MD-Dateien (eine Datei pro Thema, z. B. `01-idee.md`, `02-spielablauf.md`).
- `auftraege/offen/` – Aufträge, die noch zu erledigen sind.
- `auftraege/erledigt/` – fertige Aufträge.
- `auftraege/_VORLAGE.md` – Vorlage für neue Aufträge.

## Regeln für beide Claudes
1. **Vor jedem Start `git pull`**, damit die neuesten Aufträge und Änderungen da sind.
2. **Zuerst die offenen Aufträge lesen** (`auftraege/offen/`) und dem Nutzer sagen, welche an ihn gerichtet sind.
3. **Jeder ändert nur seine eigenen Dateien oder die, die im Auftrag genannt sind.** So gibt es keine Konflikte. Fremde Dateien nie ungefragt umschreiben.
4. **Nach jeder fertigen Arbeit committen und `git push`.** Kurze, klare Commit-Nachricht auf Deutsch.
5. **Ist ein Auftrag fertig:** unten in der Auftragsdatei einen Abschnitt „Ergebnis“ ergänzen, die Datei nach `auftraege/erledigt/` verschieben, pushen.
6. **Neue Aufträge** immer mit der Vorlage anlegen. Dateiname: `NNN-von-an-titel.md`, z. B. `001-jos-an-ju-shop-system.md`. Die Nummer zählt hoch.
7. Bei einem Merge-Konflikt: nichts überschreiben, dem Nutzer erklären, was kollidiert, und fragen.

## Wer ist wer
- **Jos** – GitHub-Account `jos-claude`
- **Ju** – (GitHub-Name hier eintragen, sobald bekannt)

## jos-und-ju/ (gemeinsames Spiel mit Ju)
- Eigenes Git-Repo (in .gitignore). Dort immer zuerst `git pull`.
- Dort gelten die Regeln aus `jos-und-ju/CLAUDE.md` (Aufträge, Commit auf Deutsch usw.).
- Ändere nur Dateien in `jos-und-ju/`. Die anderen Spiele (Stack Your Pets, Rapping-Game, …) dienen als Referenz und werden dafür nicht geändert.
- Wenn es um Vorbilder oder Ideen geht, lies zuerst in den anderen Spielen nach.
