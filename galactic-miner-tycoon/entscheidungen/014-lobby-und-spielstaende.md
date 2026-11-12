# Entscheidung 014: Lobby-Raumschiff und Spielstände (Welten) mit Koop

- **Status:** Beschlossen (12.11.2026, Ju)
- **Datum:** 12.11.2026
- **Von:** Jos und Ju (aufgeschrieben von Claude)
- **Betrifft:** 005, 008 (dort stand „Koop später“), `../spiel/13-multiplayer.md`

## Idee der Nutzer
- Beim Betreten des Spiels landet man in einer **Lobby**: ein großes interstellares **Raumschiff**.
- Statt eines Computers gibt es ein **begehbares Feld (Pad) wie in klassischen Roblox-Spielen**: Man geht hinein und kann dort **Spielstände (Welten) erstellen und laden**. (Korrektur 12.11.2026, Jos und Ju)
- In einer Welt kann man **Freunde einladen** und **gemeinsam an einer Basis** bauen.
- Aus der Welt kommt man jederzeit **zurück zum Raumschiff** (teleportieren oder hinfliegen).
- In der Lobby kann man **mit Fremden schreiben** und sich **gegenseitig zu seiner Welt einladen**, um zusammen zu bauen.

## Vorschlag zur Umsetzung (technisch, nicht bestätigt)
- **Lobby = eigener Place** (passt zu 005). Jede Insel bleibt ein eigener Place.
- **Spielstand-Pad:** Beim Betreten des Felds öffnet sich ein Menü mit den Spielständen (Neu erstellen, Laden, Freunde einladen). Das passt zu Handy und Controller, weil man nur hineinläuft. Mehrere Pads sind möglich (z. B. eins pro Spielstand-Platz).
- **Eine Welt = ein Spielstand** mit eigener ID, Besitzer, Mitgliederliste, Insel-Fortschritt, Basis-Daten und Karten-Seed. Gespeichert wird **pro Welt**, nicht mehr pro Spieler. Das ändert den `DataService`.
- **Zugang:** Pro Welt und Insel ein privater Server (Roblox „Reserved Server“). Der Besitzer lädt ein, Mitglieder kommen per Teleport hinein.
- **Chat in der Lobby:** Roblox-Standardchat (automatisch gefiltert). Einladen über einen Knopf, nicht über freie Links.
- **Offline-Ertrag** (011) wird beim Laden der Welt aus der Zeit seit dem letzten Speichern berechnet.

## Risiken
- **Größerer Aufwand:** Lobby, Welten-Verwaltung, Einladungen und Rechte sind ein eigenes Teilprojekt, größer als M1.
- **Sicherheit (Zielgruppe 8 bis 16):** Kontakt mit Fremden braucht klare Regeln (siehe Fragen).
- **Zerstören durch Mitspieler:** Es braucht Rechte, damit niemand fremde Basen kaputt macht.

## Festlegungen (Ju, 12.11.2026)
1. **Zeitpunkt und Ablauf (beschlossen):** Ein neuer Spieler spawnt **direkt auf Insel 1**, nicht in der Lobby. Nach dem Tutorial (ca. 2 bis 3 Minuten, mit kurzer Cutscene) kauft er die **erste Basiserweiterung (Raum 2)**. Darin steht ein **Teleportfeld zur Lobby**. Das kommt **vor den Förderbändern** (Raum 3). Ab dem nächsten Beitritt spawnt der Spieler **zuerst in der Lobby** und wählt dort seine Welten.
   - Daten werden von Anfang an als „Welt mit ID“ gespeichert. Die erste Welt wird beim ersten Spielstart automatisch angelegt.
   - Umfang (bestätigt, Ju, 12.11.2026): Die Lobby braucht ab M1 mindestens das Spielstand-Pad (2 Plätze). Einladen, gemeinsames Bauen, Rechte und Chat folgen im nächsten Meilenstein (M1b).
2. **Spielstände:** **2 pro Spieler.** Weitere Plätze kann man später **mit Robux kaufen** (Monetarisierung, noch nicht gebaut, siehe `../spiel/12-monetarisierung.md`).
3. **Spieler pro Welt:** **bis zu 4.**
4. **Rechte:** Der Besitzer lädt ein und kann Mitglieder entfernen. Alle Mitglieder dürfen bauen und kaufen, das Lager ist gemeinsam. Nur der Besitzer startet die Rakete.
5. **Rucksack, Spitzhacke und ähnliche Stats (früher: Stärke, Geschwindigkeit, siehe 018)** (durch Upgrades und Loot): Sie **gehören zum Spielstand**, nicht zum Spieler überhaupt. Wer eine neue Welt startet, beginnt wieder bei null. Geht man zurück in die alte Welt, sind die Stats dort wieder da. Annahme von Claude: Die Stats gelten über alle Inseln derselben Welt.
6. **Fremde:** Beitritt **nur auf Einladung** des Besitzers. Chat ist der gefilterte Roblox-Standardchat.

## Folgen (wenn bestätigt)
- `../spiel/13-multiplayer.md`, `../spiel/01-spielablauf.md`, `../technik/datenspeicherung.md` (Daten pro Welt und pro Spieler in der Welt), `../technik/architektur.md`, `../checklisten/meilensteine.md`.
- 008 („Koop später“) wird ersetzt: Koop ist ein Kernmerkmal.
- Entscheidung 013: Die Annahme „Spieler-Upgrades bleiben auf Insel 2“ gilt nur innerhalb derselben Welt.
