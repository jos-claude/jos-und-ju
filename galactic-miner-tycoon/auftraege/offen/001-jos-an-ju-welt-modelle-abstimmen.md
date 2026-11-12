# Auftrag 001: Welt, Modelle und Physik-Fix – wer macht was im Place

- **Von:** Jos (geschrieben von Jos' Claude, lokal mit Studio verbunden)
- **An:** Ju
- **Datum:** 12.11.2026
- **Status:** offen
- **Meilenstein:** M1 (siehe `checklisten/meilensteine.md`, `checklisten/code-fortschritt.md`)

> **Nachtrag 12.11., ca. 21 Uhr (Jos' Claude):** Danke für die Anpassung von Schritt 3! Dein Rojo hat den WorldBuilder nach deinem Pull noch **nicht** in den Place gebracht (`ServerStorage.WorldBuilder` fehlt). Bitte **`rojo serve` einmal neu starten und in Studio neu verbinden**, weil `default.project.json` einen neuen Eintrag hat. Danach baut Jos' Claude die Welt.
>
> **Nachtrag 21:08 (Jos' Claude):** Gemeinsamer Play-Test mit deinem Schritt 3: Halle, Lager und 3 Vorkommen werden gebaut, Schwerkraft 60 / Sprung 12 / Trägheit aktiv, keine Fehler unserer Skripte (nur Plugin „Smooth Cam“ und eine fremde Asset-Warnung 203785492, beide nicht aus dem Spiel). `Ground.luau` passt perfekt zum WorldBuilder. **Der WorldBuilder fehlt aber weiter im Place** – Rojo bitte neu starten (`rojo serve` beenden, neu starten, in Studio neu verbinden). Hinweis für später: Der WorldBuilder setzt die SpawnLocation auf (0, 0, 20), deine Start-Halle steht bei z ≈ 30 – bitte prüfen, ob das zusammenpasst.

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
- [ ] Ju hat `main` gepullt und Rojo hat `ServerStorage.WorldBuilder` und den neuen `MovementController` im Place.
- [ ] Schritt 3 baut auf dem WorldBuilder-Gelände auf (oder Ju schreibt hier unten, warum nicht).
- [ ] Ju hat kurz bestätigt, dass die Aufteilung oben passt (oder Änderungen hier eingetragen).

## Ergebnis
(wird vom Bearbeiter ausgefüllt, wenn der Auftrag fertig ist)
