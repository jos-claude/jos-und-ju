# Himmel (Skybox) – Insel 1

Die sechs Bilder hier sind der Himmel des Heimatplaneten (Vorgabe: `../../referenz/welt-design-insel-1.md`, Abschnitt 6). Sie werden **nicht von Hand gemalt**, sondern erzeugt:

```bash
cd werkzeuge/weltgenerator
python3 render_sky.py        # dauert einige Minuten, schreibt die 6 Bilder hierher
```

Größe: **1024 × 1024** pro Bild. Roblox nutzt für Skybox-Bilder höchstens 1024 Pixel pro Seite (größere Bilder werden beim Hochladen verkleinert); deshalb rendern wir intern doppelt so groß und verkleinern dann.

## Welche Datei gehört in welches Feld?

| Datei | Feld im `Sky`-Objekt | Blickrichtung (Roblox-Welt) | Was man sieht |
|---|---|---|---|
| `sky_Ft.png` | **SkyboxFt** | Norden (−Z) | Saturn oben rechts, Mond 1 und Sternhaufen am oberen Rand |
| `sky_Lf.png` | **SkyboxLf** | Osten (+X) | rechtes Ende der Saturn-Ringe (oben links im Bild) |
| `sky_Bk.png` | **SkyboxBk** | Süden (+Z) | Sterne, Horizont |
| `sky_Rt.png` | **SkyboxRt** | Westen (−X) | Sonne (Az 250°, El 22°), Eisriese, Pfirsich-Glühen am Horizont |
| `sky_Up.png` | **SkyboxUp** | oben (+Y) | Nebelband über den Zenit, Mond 2, Ränder von Saturn und Sternhaufen |
| `sky_Dn.png` | **SkyboxDn** | unten (−Y) | Violett-dunkel mit Sternen |

Achtung, das ist bei Roblox nicht intuitiv: **Lf liegt im Osten (+X), Rt im Westen (−X)**, und Up/Dn sind um eine Vierteldrehung gedreht. Die Bilder sind schon passend gedreht – einfach Datei → gleichnamiges Feld, nichts mehr drehen oder spiegeln. `SkyboxOrientation` muss auf `0, 0, 0` bleiben.

## Hochladen in Roblox Studio

**Variante A – direkt im Sky-Objekt (am einfachsten):**
1. Im Explorer `Lighting` → `WorldSky` auswählen (legt der WorldBuilder an; sonst ein `Sky` in `Lighting` einfügen).
2. Im Eigenschaftsfenster auf das Feld **SkyboxBk** klicken. Es öffnet sich die Bildauswahl; dort **„Add Image…“ / Bild hinzufügen** (je nach Studio-Version auch „Import“) wählen und `sky_Bk.png` hochladen.
3. Das Gleiche für **SkyboxDn, SkyboxFt, SkyboxLf, SkyboxRt, SkyboxUp** mit der jeweils gleichnamigen Datei.

**Variante B – Asset Manager (alle sechs auf einmal):**
1. `Window` (oder Reiter `Home`) → **Asset Manager** öffnen.
2. Auf den **Import**-Knopf klicken und alle sechs PNGs auswählen.
3. Nach dem Hochladen (die Bilder gehen kurz durch die Moderation) mit Rechtsklick auf jedes Bild → **Copy Asset ID** die ID kopieren.

Wichtig: Es muss die **Bild-ID** sein (Asset Manager / Studio liefern die). Eine *Decal*-ID von der Website ist eine andere Nummer.

## IDs eintragen

Damit der WorldBuilder den Himmel bei jedem Aufbau richtig setzt, die sechs IDs in
`src/ServerStorage/WorldBuilder/Settings.luau` eintragen:

```lua
skybox = {
	Bk = "rbxassetid://…",
	Dn = "rbxassetid://…",
	Ft = "rbxassetid://…",
	Lf = "rbxassetid://…",
	Rt = "rbxassetid://…",
	Up = "rbxassetid://…",
},
```

Danach die IDs auch in `../asset-liste.md` eintragen.

## Sonne in Lighting (muss zur Skybox-Sonne passen)

Die Skybox-Sonne ist auf diese Werte gerendert (Vorschlag, noch nicht von Jos/Ju abgestimmt):

| Eigenschaft | Wert | Ergebnis |
|---|---|---|
| `Lighting.ClockTime` | **16.45** (= `TimeOfDay` 16:27:00) | Sonne bei Azimut 250,0°, Elevation 22,0° |
| `Lighting.GeographicLatitude` | **42** | |
| `Sky.CelestialBodiesShown` | `false` | Sonne, Mond, Sterne kommen aus der Skybox |
| `Sky.StarCount` | `0` | |

Woher die Werte kommen: Roblox berechnet `Lighting:GetSunDirection()` (laut zwei an Studio gemessenen Nachbauten des Renderers) als
`(−sin h · cos t,  cos h · cos t,  sin t)` mit `h = (ClockTime − 12) / 24 · 360°` und `t = GeographicLatitude − 23,5°`.
Mit 16,45 und 42 ergibt das Azimut 250,0° und Elevation 22,0°. Zum Prüfen in der Studio-Befehlsleiste:

```lua
local d = game.Lighting:GetSunDirection()
print(math.deg(math.atan2(d.X, -d.Z)) % 360, math.deg(math.asin(d.Y)))  -- erwartet: ~250  ~22
```

Kommt etwas anderes heraus, nicht die Bilder ändern, sondern `ClockTime`/`GeographicLatitude` anpassen und Bescheid sagen – dann wird der Himmel mit der echten Richtung neu gerendert (`SkyModel(sun_dir=…)` in `worldgen/sky.py`).

Hinweis: Die `Atmosphere` (Haze, Glare) legt in Roblox einen Dunst über den unteren Himmel. Wenn die Sterne oder das Nebelband zu sehr verschwinden, `Atmosphere.Density`/`Haze` senken (siehe Abschnitt 6.4).
