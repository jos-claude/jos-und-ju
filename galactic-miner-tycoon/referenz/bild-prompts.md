# Bild-Prompts für KI-Referenzbilder (ChatGPT / Gemini)

- **Status:** Stil bestätigt (Ju, 11.11.2026)
- **Zuletzt geändert:** 11.11.2026

Ziel: Referenzbilder als Vorlage für die 3D-Modelle, die Claude in Blender nachbaut. Die Prompts sind auf Englisch, weil die Bild-KIs damit bessere Ergebnisse liefern.

## So benutzt du sie
1. **Ein Prompt = ein Objekt.** Jeder Block unten ist komplett und fertig: den ganzen Block kopieren und in Gemini einfügen. Du musst nichts zusammensetzen.
2. **Im selben Chat bleiben**, damit der Stil einheitlich bleibt. Gefällt etwas nicht, schreib „mach es …“ (z. B. „eckiger“, „weniger Details“, „orange statt gelb“).
3. **Prüfen:** Zeigen alle 7 Felder wirklich dasselbe Objekt? Wenn nicht: „make all 7 panels show exactly the same object“.
4. **Gute Bilder speichern** unter `referenz/bilder/<kategorie>/<name>.jpg` (z. B. `gebaeude/bohrer-01.jpg`) und mir den Pfad nennen.
5. **Reihenfolge für M1:** zuerst 1 Bohrer, 2 Lager-Kasten, 3 Förderband, dann 4 Basis, 5 Vorkommen, 6 Erz-Brocken, 7 Heimatplanet. Alle sieben Bilder sind fertig.

Stil in einem Satz: **Satisfactory, aber als fröhliche Weltraum-Kolonie im Roblox-Spielzeug-Look** (Orange, Gelb, Stahlgrau, Cyan-Leuchten, Warnstreifen, dicke einfache Formen).

---

## M1 – Heimatplanet

### 1. Bohrer (Eisen)
_`drill_iron`, steht auf einem Erzvorkommen. Kupfer und Kohle bekommen später nur andere Akzentfarben._

```
Art style: stylized low-poly 3D game asset inspired by the chunky industrial factory design of the game Satisfactory, translated into a cheerful space-colony look for a Roblox tycoon game. Chunky simple geometric shapes, thick steel frames, bolted panels, hazard stripes, a warm palette of orange, yellow and steel grey with white and soft cyan-teal glowing accents. Flat faceted surfaces, soft clean lighting, no realistic textures, toy-like and friendly for kids, not futuristic and not overly complicated. Maximum about 15 distinct parts so it can be rebuilt in Blender from basic shapes (boxes, cylinders, wedges). Plain light grey background, no text, no letters, no logos, no watermark, no people.

Layout: one single model sheet divided into a grid of 7 panels separated by thin white lines. All 7 panels show the exact same object with identical design, proportions and colors. Top row: (1) large isometric 3/4 perspective view from front-left above, (2) straight orthographic front view, (3) straight orthographic side view. Bottom row: (4) straight orthographic top-down view, (5) medium close-up 3/4 view of the most important part, (6) and (7) two small macro close-ups of the smaller details. Orthographic views must be perfectly straight with no perspective distortion, exactly 90 degrees, so the shapes can be measured and rebuilt in Blender.

Object: A mining drill machine standing on an iron ore patch: chunky orange-yellow body on a thick steel base plate, a big drill bit pointing down into a small mound of grey-brown rock with rusty ore chunks, a squat motor housing on top with a vent and a small cyan status light, a small transparent glass buffer tank on the side showing collected iron ore chunks, a round output port on the side where a conveyor belt connects, hazard stripes on the base plate, bolted panels.
```

### 2. Lager-Kasten (Erz-Behälter)
_`bin_iron`: ein Kasten pro Erz, dient als Inventar. Die Glaswand zeigt den Füllstand._

```
Art style: stylized low-poly 3D game asset inspired by the chunky industrial factory design of the game Satisfactory, translated into a cheerful space-colony look for a Roblox tycoon game. Chunky simple geometric shapes, thick steel frames, bolted panels, hazard stripes, a warm palette of orange, yellow and steel grey with white and soft cyan-teal glowing accents. Flat faceted surfaces, soft clean lighting, no realistic textures, toy-like and friendly for kids, not futuristic and not overly complicated. Maximum about 15 distinct parts so it can be rebuilt in Blender from basic shapes (boxes, cylinders, wedges). Plain light grey background, no text, no letters, no logos, no watermark, no people.

Layout: one single model sheet divided into a grid of 7 panels separated by thin white lines. All 7 panels show the exact same object with identical design, proportions and colors. Top row: (1) large isometric 3/4 perspective view from front-left above, (2) straight orthographic front view, (3) straight orthographic side view. Bottom row: (4) straight orthographic top-down view, (5) medium close-up 3/4 view of the most important part, (6) and (7) two small macro close-ups of the smaller details. Orthographic views must be perfectly straight with no perspective distortion, exactly 90 degrees, so the shapes can be measured and rebuilt in Blender.

Object: A large storage bin for ore, one of many standing in a row: a big rectangular steel container with a huge transparent glass front wall so the fill level is visible, filled about half with a heap of grey-brown iron ore chunks, thick steel corner frame with bolts, hazard stripes along the bottom edge, an intake funnel on top where conveyor belts deliver ore, a vertical orange level gauge bar next to the glass, and an upgrade plate on the side with three small glowing cyan lights. Panels (6) and (7) show the same bin completely empty and completely full.
```

### 3. Förderband
_`conveyor`: Segmente zum Verlegen (gerade, Kurve, Ende)._

```
Art style: stylized low-poly 3D game asset inspired by the chunky industrial factory design of the game Satisfactory, translated into a cheerful space-colony look for a Roblox tycoon game. Chunky simple geometric shapes, thick steel frames, bolted panels, hazard stripes, a warm palette of orange, yellow and steel grey with white and soft cyan-teal glowing accents. Flat faceted surfaces, soft clean lighting, no realistic textures, toy-like and friendly for kids, not futuristic and not overly complicated. Maximum about 15 distinct parts so it can be rebuilt in Blender from basic shapes (boxes, cylinders, wedges). Plain light grey background, no text, no letters, no logos, no watermark, no people.

Layout: one single model sheet divided into a grid of 7 panels separated by thin white lines. All 7 panels show the exact same object with identical design, proportions and colors. Top row: (1) large isometric 3/4 perspective view from front-left above, (2) straight orthographic front view, (3) straight orthographic side view. Bottom row: (4) straight orthographic top-down view, (5) medium close-up 3/4 view of the most important part, (6) and (7) two small macro close-ups of the smaller details. Orthographic views must be perfectly straight with no perspective distortion, exactly 90 degrees, so the shapes can be measured and rebuilt in Blender.

Object: A conveyor belt kit for chaining together: one straight segment (dark grey belt with bright yellow arrow markings, thick steel side rails, two stubby support legs), one 90-degree curved segment and one end segment with a small funnel opening, all in the same size and style, all three shown together in every panel, with a few ore chunks riding on the straight belt.
```

### 4. Basis (Raum-Module)
_Die Basis besteht aus Räumen. Raum 1 ist die Start-Halle, weitere Räume sind noch gesperrt._

```
Art style: stylized low-poly 3D game asset inspired by the chunky industrial factory design of the game Satisfactory, translated into a cheerful space-colony look for a Roblox tycoon game. Chunky simple geometric shapes, thick steel frames, bolted panels, hazard stripes, a warm palette of orange, yellow and steel grey with white and soft cyan-teal glowing accents. Flat faceted surfaces, soft clean lighting, no realistic textures, toy-like and friendly for kids, not futuristic and not overly complicated. Maximum about 15 distinct parts so it can be rebuilt in Blender from basic shapes (boxes, cylinders, wedges). Plain light grey background, no text, no letters, no logos, no watermark, no people.

Layout: one single model sheet divided into a grid of 7 panels separated by thin white lines. All 7 panels show the exact same object with identical design, proportions and colors. Top row: (1) large isometric 3/4 perspective view from front-left above, (2) straight orthographic front view, (3) straight orthographic side view. Bottom row: (4) straight orthographic top-down view, (5) medium close-up 3/4 view of the most important part, (6) and (7) two small macro close-ups of the smaller details. Orthographic views must be perfectly straight with no perspective distortion, exactly 90 degrees, so the shapes can be measured and rebuilt in Blender.

Object: A modular space colony base made of connected chunky room modules in a straight row: a larger central start hall in orange and steel grey with a wide sliding door, round porthole windows, a flat roof with vents and a small antenna, and two smaller side rooms that are still locked with closed grey shutters and orange hazard stripes, a glowing cyan panel next to each door, steel legs lifting the base slightly off the ground, a floor plate around the entrance. The rooms are clearly separate modules so more rooms can be added later.
```

### 5. Erzvorkommen (alle fünf in einem Bild)
_Vorkommen auf der Karte, auf die der Spieler Bohrer setzt._

```
Art style: stylized low-poly 3D game asset inspired by the chunky industrial factory design of the game Satisfactory, translated into a cheerful space-colony look for a Roblox tycoon game. Chunky simple geometric shapes, flat faceted surfaces, soft clean lighting, no realistic textures, toy-like and friendly for kids, not futuristic and not overly complicated. Plain light grey background, no text, no letters, no logos, no watermark, no people.

Layout: one single image showing five ore deposits in a row from left to right, all the same size, same camera (isometric 3/4 view from above), evenly spaced, each on a small flat round ground patch. Each deposit is a cluster of chunky low-poly rocks with a clearly different color: (1) iron ore - grey-brown rock with rusty orange spots, (2) copper ore - orange rock with green-teal patina, (3) coal - black shiny rock with a few glowing orange cracks, (4) crystal - glowing pink-purple crystals, (5) titanium ore - silvery blue metallic rock with a bright cyan shimmer. Rare ores look slightly bigger and more special than iron. Harmless and friendly, no danger, no lava, no spikes.
```

### 6. Erz-Brocken (Items)
_Die Brocken, die man aus dem Bohrer holt und trägt._

```
Art style: stylized low-poly 3D game asset inspired by the chunky industrial factory design of the game Satisfactory, translated into a cheerful space-colony look for a Roblox tycoon game. Chunky simple geometric shapes, flat faceted surfaces, soft clean lighting, no realistic textures, toy-like and friendly for kids. Plain light grey background, no text, no letters, no logos, no watermark, no people.

Layout: one single image with five collectible ore chunks in a row, each shown large and the same size, isometric 3/4 view: iron ore (grey with rusty spots), copper ore (orange with green patina), coal (black with a faint glow), crystal (glowing pink), titanium ore (silvery blue). Each chunk is one simple faceted shape with at most 8 faces, readable even when very small.
```

### 7. Heimatplanet (Landschaft mit Basis)
_Szene, kein Modell-Blatt._

```
Art style: stylized low-poly 3D game scene inspired by the chunky industrial look of the game Satisfactory, translated into a cheerful space-colony look for a Roblox tycoon game. Flat faceted surfaces, soft clean lighting, warm palette of orange, yellow and steel grey with cyan glowing accents, toy-like and friendly for kids, not futuristic, no text, no logos, no people.

Scene: an isometric game scene seen from above at 45 degrees, a floating diorama-style green home planet surface with bright grass, a few round trees and gentle hills, no dangers at all. In the center a small modular orange-and-grey space base with a wide door and a row of glass-fronted ore storage bins next to it. Around the base, ore deposits are scattered at different distances: grey-brown iron deposits close by, orange copper further out, black coal deposits even further, and pink crystals far at the edge. A few yellow-orange mining drills stand on the nearer deposits with short conveyor belts leading to the storage bins. Clean readable layout, no UI.
```

---

## Später (M2 und weiter)
Diese Prompts sind noch nicht auf den neuen Stil angepasst. Bitte vor der Nutzung mit mir als komplette Einzel-Prompts wie oben schreiben lassen: Fabrik, Silo, Band-Sammler, Raketenstartplatz, Forschungslabor, Werkbank, Raumschiff, Planeten.

## Wenn die Ergebnisse nicht passen
| Problem | Zusatz im Prompt |
|---|---|
| Zu realistisch | „flat shaded, toy-like, no realistic textures“ |
| Zu detailreich | „very simple shapes, max 10 distinct parts“ |
| Zu futuristisch | „simple chunky industrial machines, not sci-fi, no complex details“ |
| Hintergrund stört | „isolated on plain light grey background“ |
| Schief / abgeschnitten | „centered, whole object visible, orthographic view“ |
| Ansichten stimmen nicht überein | „all 7 panels must show the identical object, same colors, same details“ |
| Ansichten nicht gerade | „orthographic, no perspective, exactly 90 degrees“ |
| Text im Bild | „no text, no letters, no numbers“ |

## Offene Fragen
- [x] Stil bestätigt (Ju, 11.11.2026)
- [ ] Welche Bild-KI ist Standard (Gemini)?

## Verknüpft mit
`../spiel/15-optik-und-audio.md`, `../daten/gebaeude.md`, `../daten/ressourcen.md`, `../assets/asset-liste.md`

## Vorhandene Referenzbilder (11.11.2026)
| Objekt | Datei |
|---|---|
| Bohrer (Eisen) | `bilder/gebaeude/bohrer-01.jpg` |
| Lager-Kasten | `bilder/gebaeude/lager-kasten-01.jpg` |
| Förderband | `bilder/gebaeude/foerderband-01.jpg` |
| Basis (Raum-Module) | `bilder/gebaeude/basis-01.jpg` |
| Erzvorkommen (5 Erze) | `bilder/erze/erzvorkommen-01.jpg` |
| Heimatplanet (Szene) | `bilder/welt/heimatplanet-01.jpg` |
| Erz-Brocken (Items) | `bilder/erze/erz-brocken-01.jpg` |

Ein Astronaut ist nicht nötig: Der Spieler behält seinen normalen Roblox-Skin.

---

## Heimatplanet: Varianten mit mehr Weltraum-Look (12.11.2026)
Ju und Jos finden, dass Prompt 7 zu sehr nach Erde und Insel aussieht. Hier drei Varianten als **runder Planet im Weltraum** mit bunter, fremder Natur. Jeder Block ist komplett, einzeln kopierbar. Gleicher Stil wie bisher, nur die Welt ist anders. Bitte alle drei erzeugen lassen und die beste auswählen.

### 7a. Pilz-Planet (Violett und Türkis)
```
Art style: stylized low-poly 3D game scene inspired by the chunky industrial look of the game Satisfactory, translated into a cheerful space-colony look for a Roblox tycoon game. Flat faceted surfaces, soft clean lighting, toy-like and friendly for kids, not realistic, no text, no logos, no people.

Scene: a small round low-poly alien planet floating in outer space, seen from slightly above so the curved horizon of the sphere is visible, a deep blue-purple starry sky with soft nebula clouds and two small colorful moons in the background. The ground is violet and magenta with turquoise patches. Strange alien plants everywhere: giant glowing mushrooms in pink and cyan, tall bulb-shaped plants with glowing tips, spiral turquoise grass, floating glowing spores. No trees, nothing looks like Earth. Completely harmless, no danger. On the surface in the middle: a small modular orange-and-grey space base with a wide door and a row of glass-fronted ore storage bins next to it. Around the base, ore deposits are scattered at different distances (grey-brown iron close by, orange copper with green patina further out, black coal with glowing orange cracks even further, pink crystals far away), each clearly readable against the colorful ground. A few yellow-orange mining drills stand on the nearer deposits with short conveyor belts leading to the storage bins. Clean readable layout, no UI.
```

### 7b. Kristall-Wüsten-Planet (Korall und Türkis)
```
Art style: stylized low-poly 3D game scene inspired by the chunky industrial look of the game Satisfactory, translated into a cheerful space-colony look for a Roblox tycoon game. Flat faceted surfaces, soft clean lighting, toy-like and friendly for kids, not realistic, no text, no logos, no people.

Scene: a small round low-poly alien planet floating in outer space, seen from slightly above so the curved horizon of the sphere is visible, a dark teal starry sky with a huge ringed gas planet and a small moon in the background. The ground is warm peach and coral sand with striped layered rock mesas in pink, yellow and lilac. Strange alien plants: balloon-shaped round plants in turquoise and lime, soft glowing crystal spires in turquoise and lilac, curly noodle-like plants, no trees and nothing that looks like Earth. Completely harmless, no danger, no spikes. On the surface in the middle: a small modular orange-and-grey space base with a wide door and a row of glass-fronted ore storage bins next to it. Around the base, ore deposits are scattered at different distances (grey-brown iron close by, copper with strong green-teal patina further out, black coal with glowing orange cracks even further, pink crystals far away), each clearly readable against the sandy ground. A few yellow-orange mining drills stand on the nearer deposits with short conveyor belts leading to the storage bins. Clean readable layout, no UI.
```

### 7c. Blauer Spiral-Dschungel-Planet
```
Art style: stylized low-poly 3D game scene inspired by the chunky industrial look of the game Satisfactory, translated into a cheerful space-colony look for a Roblox tycoon game. Flat faceted surfaces, soft clean lighting, toy-like and friendly for kids, not realistic, no text, no logos, no people.

Scene: a small round low-poly alien planet floating in outer space, seen from slightly above so the curved horizon of the sphere is visible, a deep indigo starry sky with a bright pink nebula and a small golden moon in the background. The ground is deep blue and teal with glowing cyan veins. Strange alien plants: tall spiral-shaped trees with pink and yellow tops, giant curled leaves in orange and magenta, jellyfish-like floating plants hovering slightly above the ground, tiny glowing light bulbs on stalks, no normal trees and nothing that looks like Earth. Completely harmless, no danger. On the surface in the middle: a small modular orange-and-grey space base with a wide door and a row of glass-fronted ore storage bins next to it. Around the base, ore deposits are scattered at different distances (grey-brown iron close by, orange copper with green patina further out, black coal with glowing orange cracks even further, pink crystals far away), each clearly readable against the colorful ground. A few yellow-orange mining drills stand on the nearer deposits with short conveyor belts leading to the storage bins. Clean readable layout, no UI.
```

Nach der Auswahl: Das Bild als `bilder/welt/heimatplanet-02.jpg` speichern, dann passe ich Stil und Farbpalette von Insel 1 (`../spiel/15-optik-und-audio.md`) an.

**Auswahl (12.11.2026):** Insel 1 ist Variante 7b (orange, mit Saturn). Gespeichert als `bilder/welt/heimatplanet-02-orange.jpg`. Variante 7a (violett-pink, Pilze) liegt als `bilder/welt/planet-pilz-violett-01.jpg` für später. Siehe Entscheidung 015.
