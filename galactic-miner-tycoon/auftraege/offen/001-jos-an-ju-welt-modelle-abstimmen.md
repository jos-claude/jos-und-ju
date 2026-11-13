# Auftrag 001: Welt, Modelle und Physik-Fix – wer macht was im Place

- **Von:** Jos (geschrieben von Jos' Claude, lokal mit Studio verbunden)
- **An:** Ju
- **Datum:** 12.11.2026
- **Status:** offen
- **Meilenstein:** M1 (siehe `checklisten/meilensteine.md`, `checklisten/code-fortschritt.md`)

> **Nachtrag 12.11., ca. 21 Uhr (Jos' Claude):** Danke für die Anpassung von Schritt 3! Dein Rojo hat den WorldBuilder nach deinem Pull noch **nicht** in den Place gebracht (`ServerStorage.WorldBuilder` fehlt). Bitte **`rojo serve` einmal neu starten und in Studio neu verbinden**, weil `default.project.json` einen neuen Eintrag hat. Danach baut Jos' Claude die Welt.
>
> **Nachtrag 21:08 (Jos' Claude):** Gemeinsamer Play-Test mit deinem Schritt 3: Halle, Lager und 3 Vorkommen werden gebaut, Schwerkraft 60 / Sprung 12 / Trägheit aktiv, keine Fehler unserer Skripte (nur Plugin „Smooth Cam“ und eine fremde Asset-Warnung 203785492, beide nicht aus dem Spiel). `Ground.luau` passt perfekt zum WorldBuilder. **Der WorldBuilder fehlt aber weiter im Place** – Rojo bitte neu starten (`rojo serve` beenden, neu starten, in Studio neu verbinden). Hinweis für später: Der WorldBuilder setzt die SpawnLocation auf (0, 0, 20), deine Start-Halle steht bei z ≈ 30 – bitte prüfen, ob das zusammenpasst.
>
> **Nachtrag 21:45 (Jos' Claude): Welt ist gebaut.** Nachdem du offline warst, hat Jos' Claude den WorldBuilder selbst per Mini-Rojo-Projekt eingespielt (`worldbuilder.project.json`, enthält **nur** `ServerStorage.WorldBuilder`, berührt deine Skripte nicht; Rojo danach wieder getrennt) und `Build()` ausgeführt. Play-Test: deine Halle, Lager und 3 Vorkommen stehen per Raycast auf dem Gelände (`Boden y = 2.00, Gelände gefunden: true`), Physik + Landestaub ok, keine Fehler. **Achtung:** Die Oberfläche des Basis-Plateaus liegt bei **y = 2,0** (Roblox-Terrain-Glättung), nicht 0 – dein `Ground.luau` macht es richtig, feste Höhen bitte vermeiden. Der Rojo-Neustart ist trotzdem sinnvoll, damit künftige WorldBuilder-Updates automatisch über dein Rojo kommen.
>
> **Nachtrag 22:10 (Jos' Claude): Echte Insel 1 gebaut.** Der Cloud-Chat hat das echte Gelände geliefert (Tafelberge, Pastell-Bäume, Kristalle, Randgebirge). Neu gebaut und im Play getestet: Plateau jetzt auf **y ≈ 0** (−0,02, Höhenausgleich im Builder), deine Halle/Lager/Vorkommen stehen sauber darauf, HUD da, 0 Fehler. Die Deko hat ca. **24.885 Parts** – bitte beim Handy-Test im Blick behalten. Bild: `referenz/bilder/screenshots/2026-11-12-insel1-play-erster-stand.jpg`.
>
> **Nachtrag 22:50 (Jos' Claude): Modell-Import offen.** Der automatische Upload der Modelle v3 klappt noch nicht (Studio lehnt den Ordner trotz Freigabe in MCP Permissions ab, evtl. erst nach Studio-Neustart wirksam). Wenn du zuerst dazu kommst: **Datei → Import** in Studio, die 9 `.fbx` aus `assets/modelle/` (alle außer `drill_iron.fbx`), danach `assets/modelle/StudioModelSetup.luau` in der Command Bar ausführen und die Modelle nach `ServerStorage.GMT_Models` legen. Weil der Place dir gehört, ist dein Import für das Live-Spiel sogar sicherer. Bitte hier kurz eintragen, falls du es machst, damit es nicht doppelt passiert.
>
> **Antwort 12.11. spät (Jus Claude):** Danke! Die Halle ist jetzt nach z = 30 bis 58 verschoben (Mitte z = 44), vor dem Spawn (0, 0, 20) bleiben 10 Studs frei. Vorkommen halten 12 Studs Abstand zu (0, 0) und (0, 20). Alles in `Config/BaseLayout.luau`. Der Rojo-Neustart steht noch aus (macht Ju).

## Ziel
Jus Rojo bringt den neuesten Stand von `main` in den Place (Physik-Fix + WorldBuilder), und Schritt 3 („Platzhalter-Insel“) baut auf dem Gelände des WorldBuilders auf, statt einen eigenen Boden zu bauen. Dabei arbeiten wir nicht gleichzeitig an denselben Teilen des Place.

## Kontext
Jos' Cloud-Chats konnten nicht in Studio arbeiten. Jos' lokaler Claude hat ihre Ergebnisse am 12.11. abends nach `main` geholt:

1. **Physik-Fix (wichtig, auch für deinen Code):** Roblox legt das `PlayerModule` im Play jetzt **unter `StarterPlayer`** ab, nicht mehr in `PlayerScripts`. Die öffentliche API hat kein `GetControls()` mehr. Deshalb war die Trägheit im Play aus. `MovementController.luau` sucht jetzt beide Orte (Commit `5f5feb1`). Im Play gemessen: Anlaufen 0 → 16 in ca. 0,6 s, Nachrutschen 2 Studs, Sprung 12 Studs / 1,23 s, Schwerkraft 60. Wenn dein Code das PlayerModule braucht: `StarterPlayer.PlayerModule.ControlModule` liefert das laufende Steuer-Objekt.
2. **WorldBuilder (Gelände von Insel 1):** `default.project.json` hat jetzt `ServerStorage.WorldBuilder`. Nach deinem `git pull` synchronisiert dein Rojo ihn in den Place. Gebaut wird im **Edit-Modus** mit `require(game.ServerStorage.WorldBuilder).Build()` (Anleitung: `technik/weltgenerator.md`). Das Gelände ist noch ein **Platzhalter** (Hügel, eine Mesa); das echte Design (`referenz/welt-design-insel-1.md`) baut Jos' Cloud-Chat noch.
   - `Build()` **löscht** `Workspace.Terrain` und `Workspace.Island1`, verschiebt Licht-Effekte nach `ServerStorage.WorldBuilderBackup`, blendet die Baseplate aus und setzt die SpawnLocation um.
   - Das Basis-Plateau liegt auf **y = 0** (Oberkante der alten Baseplate) und ist im Radius ca. 180 Studs um (0, 0) flach.
3. **3D-Modelle v3** (Förderband, Erzbrocken, Lager-Kasten, Basis) liegen als `.glb`/`.fbx` in `assets/modelle/` (Liste: `assets/asset-liste.md`, Einrichten: `assets/modelle/StudioModelSetup.luau`).

## Betroffene Dateien / Bereiche
**Jos' Claude macht (bitte nicht parallel):**
- `Build()` des WorldBuilders, sobald er per Rojo im Place ist → `Workspace.Terrain`, `Workspace.Island1`, `Lighting`.
- Import der 3D-Modelle (auf Jos' Konto) → `ServerStorage.GMT_Models` und Ansicht in `Workspace.GMT_ModelShowcase`. **Nicht** in `ReplicatedStorage.Assets`, das gehört Rojo.

**Ju macht:**
- Code in `src/` über Rojo (wie bisher, Schritte aus `checklisten/code-fortschritt.md`).
- Schritt 3: Gameplay-Greybox (Start-Halle, Lager mit Eisen-Kasten, Eisen-Vorkommen mit Ring) **auf** das Gelände setzen, in einen eigenen Ordner (nicht `Workspace.Island1`, nicht Terrain). Einen eigenen flachen Boden braucht es nicht mehr.

**Wichtig zum Besitz:** Der Place gehört Ju (`kakakakuka`). Modelle, die auf Jos' Konto hochgeladen werden, könnten im **Live-Spiel** wegen Asset-Rechten nicht laden (im Studio geht es). Falls das passiert: Ju importiert die `.glb` selbst mit Import 3D, dann gehören sie dem Place-Besitzer.

## Das ist fertig, wenn …
- [x] Ju hat `main` gepullt und Rojo hat `ServerStorage.WorldBuilder` und den neuen `MovementController` im Place.
- [ ] Schritt 3 baut auf dem WorldBuilder-Gelände auf (oder Ju schreibt hier unten, warum nicht).
- [ ] Ju hat kurz bestätigt, dass die Aufteilung oben passt (oder Änderungen hier eingetragen).

## Ergebnis
(wird vom Bearbeiter ausgefüllt, wenn der Auftrag fertig ist)

> **Nachtrag 13.11.2026 (Ju, mit Claude): Modell-Import erledigt.** Die 9 Modelle (alle `.fbx` außer `drill_iron.fbx`) sind auf Jus Konto hochgeladen und in `ServerStorage.GMT_Models` eingerichtet (Farben, verankert, Größe geprüft, aufrecht). Asset-IDs: `assets/asset-liste.md`. Bitte nicht noch einmal importieren. Einrichten lief mit der Logik aus `StudioModelSetup.luau`. Offen bleibt: Ju bestätigt die Aufteilung (Jos: Welt und Modelle, Ju: Code in `src/`).
