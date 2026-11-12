# Entscheidung 014: Lobby-Raumschiff und Spielstände (Welten) mit Koop

- **Status:** Vorschlag (Wunsch von Jos und Ju, Details noch offen)
- **Datum:** 12.11.2026
- **Von:** Jos und Ju (aufgeschrieben von Claude)
- **Betrifft:** 005, 008 (dort stand „Koop später“), `../spiel/13-multiplayer.md`

## Idee der Nutzer
- Beim Betreten des Spiels landet man in einer **Lobby**: ein großes interstellares **Raumschiff**.
- Dort gibt es einen **Computer/Terminal**, an dem man **Spielstände (Welten) erstellen und laden** kann.
- In einer Welt kann man **Freunde einladen** und **gemeinsam an einer Basis** bauen.
- Aus der Welt kommt man jederzeit **zurück zum Raumschiff** (teleportieren oder hinfliegen).
- In der Lobby kann man **mit Fremden schreiben** und sich **gegenseitig zu seiner Welt einladen**, um zusammen zu bauen.

## Vorschlag zur Umsetzung (technisch, nicht bestätigt)
- **Lobby = eigener Place** (passt zu 005). Jede Insel bleibt ein eigener Place.
- **Eine Welt = ein Spielstand** mit eigener ID, Besitzer, Mitgliederliste, Insel-Fortschritt, Basis-Daten und Karten-Seed. Gespeichert wird **pro Welt**, nicht mehr pro Spieler. Das ändert den `DataService`.
- **Zugang:** Pro Welt und Insel ein privater Server (Roblox „Reserved Server“). Der Besitzer lädt ein, Mitglieder kommen per Teleport hinein.
- **Chat in der Lobby:** Roblox-Standardchat (automatisch gefiltert). Einladen über einen Knopf, nicht über freie Links.
- **Offline-Ertrag** (011) wird beim Laden der Welt aus der Zeit seit dem letzten Speichern berechnet.

## Risiken
- **Größerer Aufwand:** Lobby, Welten-Verwaltung, Einladungen und Rechte sind ein eigenes Teilprojekt, größer als M1.
- **Sicherheit (Zielgruppe 8 bis 16):** Kontakt mit Fremden braucht klare Regeln (siehe Fragen).
- **Zerstören durch Mitspieler:** Es braucht Rechte, damit niemand fremde Basen kaputt macht.

## Offene Fragen (mit Empfehlung)
1. **Wann bauen?** Empfehlung: M1 zuerst als einzelne Welt ohne Lobby, aber die Daten **schon pro Welt** anlegen. Die Lobby wird danach ein eigener Meilenstein.
2. **Wie viele Spielstände pro Spieler?** Empfehlung: 3.
3. **Wie viele Spieler pro Welt?** Empfehlung: bis 4.
4. **Rechte:** Empfehlung: Besitzer lädt ein und kann Mitglieder entfernen. Alle Mitglieder dürfen bauen und kaufen, das Lager ist gemeinsam. Nur der Besitzer startet die Rakete.
5. **Spieler-Upgrades (Stärke, Geschwindigkeit):** pro Spieler oder pro Welt? Empfehlung: pro Spieler, sie reisen mit.
6. **Fremde:** Empfehlung: Beitritt nur auf Einladung des Besitzers, Chat nur der gefilterte Roblox-Standardchat, Meldefunktion von Roblox nutzen.

## Folgen (wenn bestätigt)
- `../spiel/13-multiplayer.md`, `../spiel/01-spielablauf.md`, `../technik/datenspeicherung.md` (Daten pro Welt), `../technik/architektur.md`, `../checklisten/meilensteine.md`.
- 008 („Koop später“) wird ersetzt: Koop ist ein Kernmerkmal.
