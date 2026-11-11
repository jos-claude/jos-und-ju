# Bild-Prompts für KI-Referenzbilder (ChatGPT / Gemini)

- **Status:** Vorschlag (Stil ist noch nicht abgestimmt, siehe `../spiel/15-optik-und-audio.md`)
- **Zuletzt geändert:** 11.11.2026

Ziel: Mit diesen Prompts erzeugen wir Referenzbilder, die als Vorlage für die 3D-Modelle in Roblox dienen. Die Prompts sind auf Englisch, weil die Bild-KIs damit bessere Ergebnisse liefern.

## So benutzt du sie

1. **Reihenfolge in einer Nachricht: Stil-Block (A) + Multi-Ansichten-Layout (B) + Prompt des Objekts.** Für alles, was ich in Blender nachbauen soll (Schiff, Gebäude, Items, Werkzeuge, Astronaut), ist B Pflicht. Nur Planeten-Szenen (C) und der Hintergrund kommen ohne B aus.
2. **Pro Objekt ein eigenes Bild.** Gefällt es nicht, schreib einfach „mach es …“ (z. B. „eckiger“, „bunter“, „weniger Details“).
3. **Im selben Chat bleiben**, damit der Stil einheitlich bleibt. Beim ersten Bild den Stil-Block nutzen, danach reicht „Gleicher Stil wie vorher“.
4. **Gute Bilder speichern** unter `referenz/bilder/<kategorie>/<name>.png` (z. B. `schiff/rakete-01.png`) und mir den Pfad nennen.
5. **Tipp für 3D:** Lieber wenig Details. Je einfacher die Form, desto leichter baue ich sie in Roblox nach. Das Layout (B) liefert alle Seiten auf einem Bild, so kann ich Maße und Proportionen direkt ablesen. Prüfe das Ergebnis: Sehen alle Felder wirklich nach demselben Objekt aus? Wenn nicht, schreib „make all panels show exactly the same object“.

---

## A – Stil-Block (immer vorne dranhängen)

```
Art style: colorful cartoon low-poly 3D game asset, chunky simple shapes, flat faceted surfaces,
bold saturated colors, soft clean lighting, slight rim light, no realistic textures,
friendly and kid-appropriate, like a polished Roblox tycoon game. Single object only,
plain light grey background, centered, full object visible, no text, no logos, no watermark.
```

## B – Multi-Ansichten-Layout (für jedes Modell, das wir in Blender bauen)

Ein Bild = ein Objekt aus allen Seiten, im Raster mit dünnen weißen Trennlinien. Layout: oben große 3/4-Ansicht, Vorderansicht, Seitenansicht; unten Draufsicht, Detail-Nahaufnahme und zwei kleine Detail-Ausschnitte.

```
Layout: a single model sheet divided into a grid of 7 panels separated by thin white lines, all panels show
the exact same object with identical design, proportions and colors, on a plain light grey background:
Top row: (1) large isometric 3/4 perspective view from front-left above, (2) straight orthographic front view,
(3) straight orthographic side view.
Bottom row: (4) straight top-down view, (5) medium close-up 3/4 view of the most important part,
(6) and (7) two small macro close-ups of the smaller details (moving parts, ornaments, small items on it).
Orthographic views must be perfectly straight with no perspective distortion, so the shapes can be measured
and rebuilt in Blender. Soft even lighting with gentle shadows, no text, no labels, no arrows, no people.
```

**Variante mit Rück- und Unteransicht** (für Objekte, die von hinten anders aussehen, z. B. Schiff, Fabrik):
```
Same layout as described, but replace panel (7) with a straight orthographic back view,
and panel (6) with a bottom view.
```

## C – Szenen-Zusatz (für Planeten / Basis-Überblick)

```
Show it as an isometric game scene seen from above at 45 degrees, floating diorama-style island,
clean readable layout, no UI.
```

---

## 1. Raumschiff

**Starter-Rakete (Stufe 1)**
```
A small cute starter rocket for a space mining game. Stubby rounded body, red and white paint,
round porthole window, three small fins, a single simple engine nozzle, cargo hatch on the side,
slightly dented and homemade look.
```

**Ausgebautes Schiff (späte Stufe)**
```
A large upgraded mining spaceship, evolved from a small rocket: sleek metallic hull in white and blue
with orange accents, twin big engines with glowing blue exhausts, glowing energy shield emitter on the nose,
large cargo containers attached to the sides, small mining arm underneath.
```

**Upgrade-Teile (Triebwerk / Schild / Laderaum)**
```
Three separate spaceship upgrade parts shown side by side: 1) a glowing blue engine module,
2) a round shield generator with a cyan energy ring, 3) a stackable cargo container with yellow stripes.
```

## 2. Basis-Gebäude (Heimatplanet)

**Einfacher Bohrer** (`drill_basic`)
```
A small ground drill machine for mining ore: stout yellow-orange body, big spinning drill bit pointing down,
small exhaust pipe, rubber tracks, a little output chute at the side.
```

**Förderband** (`conveyor`)
```
A short straight conveyor belt segment: dark grey belt with yellow arrow markings, metal side rails,
two support legs, ready to be chained together. Show one segment and one curved corner segment.
```

**Fabrik** (`factory_basic`)
```
A small compact factory building for processing ore: blocky grey and blue building,
one tall chimney with soft steam, a large input hatch on one side and an output hatch on the other,
glowing orange window, a gear symbol painted on the wall.
```

**Silo** (`silo_basic`)
```
A round storage silo for resources: tall cylinder with domed top, metallic silver with a blue stripe,
a small ladder on the side, a glowing resource level window.
```

**Raketenstartplatz** (`rocket_pad`)
```
A rocket launch pad: round concrete platform with hazard stripes, four metal support arms,
a small control tower with a glowing window, landing lights around the edge. Empty, without a rocket.
```

**Forschungslabor** (`research_lab`)
```
A research laboratory building: white dome with a big glass window, a small satellite dish on the roof,
glowing green and blue tubes visible inside, a rotating atom symbol on a sign.
```

**Basis-Überblick (früh vs. spät)**
```
Two images of the same home base: 1) early game - just a few drills, a short conveyor, a tiny silo and a rocket pad;
2) late game - a big busy factory complex with many conveyors, tall silos, a research dome and a large rocket pad.
Same green grassy planet island, same camera angle.
```
(am Ende zusätzlich den Szenen-Zusatz C anhängen)

## 3. Planeten

Alle als **Oberflächen-Landschaft** (Szenen-Zusatz C) oder als **Kugel-Ansicht** erzeugen lassen. Wir brauchen beides.

**Heimatplanet** (`home`)
```
A friendly green home planet: bright grass meadows, a few round trees, gentle hills, small ponds,
scattered chunks of iron ore (grey-brown), copper ore (orange-green) and a few glowing pink crystals.
```

**Lava-Planet** (`lava`)
```
A volcanic lava planet: dark rocky ground, rivers of glowing orange-red lava, a small erupting volcano,
shiny black obsidian crystals sticking out of the ground, glowing embers in the air.
```

**Eis-Welt** (`ice`)
```
A frozen ice planet: white and light blue snowy terrain, frozen lakes, big ice spikes,
glowing pale blue ice crystals in the ground, light snowfall, northern-light-like sky.
```

**Dschungel-Welt** (`jungle`)
```
A dense alien jungle planet: lush dark green and teal vegetation, huge leaves and glowing flowers,
vines and fibrous plants, a friendly cartoon dinosaur in the background, misty light.
```

**Kugel-Ansicht (für die Planetenauswahl)**
```
Four small planets in a row on a dark starry background, each a simple round low-poly sphere:
a green planet with clouds, a red-orange lava planet, a white-blue ice planet, a dark green jungle planet.
Make the style clean and iconic so they work as menu buttons.
```
(hier den Hintergrund-Teil des Stil-Blocks weglassen, der Weltraum-Hintergrund ist gewollt)

## 4. Rohstoffe & Items (`../daten/ressourcen.md`)

**Rohstoffe** (ein Bild, alle zusammen, damit sie zueinander passen)
```
Six collectible resource items in a 3x2 grid, each a chunky low-poly chunk with a clearly different color:
iron ore (grey with rusty spots), copper ore (orange with green patina), crystal (glowing pink),
obsidian (black, glassy, red glow in cracks), ice crystal (light blue, translucent), bio fiber (green bundle of fibers).
```

**Verarbeitete Materialien**
```
Five crafted material items in a grid: an iron bar (silver ingot), a circuit board (green with gold lines),
a heat shield plate (dark plate with orange edge glow), a coolant canister (blue glowing canister),
a plasma cell (glowing purple energy battery).
```

**Währungen** (Platzhalter, Währungen sind noch nicht festgelegt)
```
Two game currency icons as 3D objects: a gold space coin with a star on it, and a rare glowing blue gem.
```

## 5. Spieler & Werkzeuge (optional)

**Spieler-Astronaut**
```
A cute blocky astronaut miner in the style of a Roblox character: white and orange space suit,
round helmet with reflective visor, small backpack, thick boots. T-pose for modeling.
```

**Handwerkzeuge** (`../spiel/07-werkzeuge.md`)
```
Three hand mining tools in a row: a basic pickaxe, a laser mining tool with a glowing blue tip,
and a heavy plasma drill with an orange glowing core.
```

## 6. Weltraum & Stimmung

**Hub / Planetenauswahl-Hintergrund**
```
A colorful cartoon space background with a deep purple and blue gradient, many small stars, soft nebula clouds,
and a few distant planets. Wide landscape format, no objects in the center so UI can be placed on top.
```

---

## Wenn die Ergebnisse nicht passen

| Problem | Zusatz im Prompt |
|---|---|
| Zu realistisch | „flat shaded, toy-like, no realistic textures“ |
| Zu detailreich | „very simple shapes, max 10 distinct parts“ |
| Hintergrund stört | „isolated on plain light grey background“ |
| Schief / abgeschnitten | „centered, whole object visible, orthographic view“ |
| Ansichten stimmen nicht überein | „all 7 panels must show the identical object, same colors, same details“ |
| Ansichten nicht gerade | „orthographic, no perspective, exactly 90 degrees“ |
| Text im Bild | „no text, no letters, no numbers“ |

## Offene Fragen

- [ ] Bunt-comichaft (wie in der Mindmap) oder lieber ruhiger? Das entscheiden wir mit den ersten Referenzbildern.
- [ ] Welche Bild-KI nehmen wir als Standard (ChatGPT oder Gemini), damit der Stil einheitlich bleibt?

## Verknüpft mit
`../spiel/15-optik-und-audio.md`, `../daten/planeten.md`, `../daten/ressourcen.md`, `../daten/gebaeude.md`, `../assets/asset-liste.md`
