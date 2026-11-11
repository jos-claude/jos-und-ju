# Galactic Miner Tycoon – Regeln für die Claudes

Gilt zusätzlich zur `CLAUDE.md` im Repo-Hauptordner. Sprache der Doku: Deutsch. Code (Luau) und Namen im Code: Englisch (siehe `technik/namenskonventionen.md`).

## Vor jeder Arbeit
1. `git pull`.
2. `STATUS.md` und `spiel/00-vision.md` lesen – die Vision ist der Maßstab für jede Idee.
3. Offene Aufträge in `auftraege/offen/` lesen und dem Nutzer sagen, welche an ihn gerichtet sind.

## Wo gehört was hin?
- **Neue Idee, noch unklar** → `ideen/README.md` (Tabelle ergänzen).
- **Idee wird verbindlich / Konzept ändert sich** → passende Datei in `spiel/` ändern **und** einen Eintrag in `entscheidungen/` anlegen (Vorlage dort), dann in `entscheidungen/README.md` eintragen.
- **Zahlen** (Preise, Raten, Planeten, Ressourcen) → `daten/`. Der Code in `src/ReplicatedStorage/Shared/Config/` muss dazu passen.
- **Aufgabe an den anderen** → Auftrag in `auftraege/offen/` (Vorlage nutzen, Nummer hochzählen, ganzes Repo prüfen).
- **Fortschritt** → Häkchen in `checklisten/` setzen, `STATUS.md` aktuell halten.
- **Begriffe** → `referenz/glossar.md`. Immer dieselben Wörter für dieselben Dinge benutzen.

## Grundregeln fürs Konzept
- Eine Datei pro Thema in `spiel/`. Jede hat oben einen **Status** (Entwurf / in Arbeit / abgestimmt) und unten **Offene Fragen**.
- Nichts als „abgestimmt“ markieren, was die Nutzer nicht bestätigt haben. Eigene Vorschläge klar als **Vorschlag** kennzeichnen.
- Widerspricht etwas der Vision oder einer Entscheidung: nicht stillschweigend ändern, sondern nachfragen.
- Alles, was in einem Roblox-Place zusammenläuft (siehe `technik/zusammenarbeit-roblox-studio.md`): Nie beide gleichzeitig am selben Script oder Model arbeiten lassen.
