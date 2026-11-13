# Bauplan: Spitzhacke (5 Stufen)

- **Status:** Vorschlag (Jos' Claude, 14.11.2026). Wartet auf das OK von Jos und Ju. Der Blender-Bau kommt danach.
- **Modelle:** `PickaxeRust`, `PickaxeIron`, `PickaxeSteel`, `PickaxeCrystal`, `PickaxeTitan`
- **Spiel-Werte:** `../../../spiel/16-raeume-und-spitzhacke.md`, `../../../daten/upgrades.md`, Code `src/ReplicatedStorage/Shared/Config/Pickaxe.luau`
- **3D-Vorschau zum Drehen:** Link im Abschnitt „Vorschau“ unten
- **Gehört zu:** `schmiede-einrichtung.md` (Schmiede, Raum 2)

## Route: Blender-Skript, nicht Tripo
Die Spitzhacke ist ein mechanisches Werkzeug aus einfachen Formen (Stiel, Block, zwei Keile). Wir brauchen fünf Stufen mit fast gleicher Form, und unser Stil ist „flache Farben ohne Texturen“ (`../README.md`). Tripo liefert texturierte Einzel-Meshes und passt deshalb nicht. Gebaut wird später mit einem Skript `blender-skripte/build_pickaxe.py` auf Basis von `gmt_lib.py`, wie Förderband und Lager-Kasten.

## Die Idee in einem Satz
**Ein Gerüst, fünf Häute:** Alle Stufen haben denselben Aufbau (Knauf, Griff, Stiel, Kragen, Kopf-Block, Spitze, Flachende). Von Stufe zu Stufe wird die Hacke etwas größer, das Kopf-Material ändert sich, es kommen Warnringe und **cyanfarbene Stufen-Lichter** dazu (Stufe 1 hat keins, Stufe 5 hat vier). Dazu hat jede Stufe **ein Erkennungsmerkmal**. So sieht man die Stufe auf einen Blick, auch klein in der Hand.

Stil-Anker: wie der Bohrer (`../../../referenz/bilder/gebaeude/bohrer-01.jpg`) und der Lager-Kasten (`../vorschau/ore_bin.png`): Orange als Marken-Farbe am Kopf-Block, Stahlgrau, Warnstreifen Gelb/Schwarz, cyanfarbene Lichter, dicke Fasen, spielzeughaft. Die Spitze ist **stumpf** (Kinder-Spiel, nichts Spitzes, Gefährliches).

## Einheiten und Ausrichtung (wie alle unsere Modelle)
- 1 Blender-Einheit = 1 Stud.
- Die Hacke **steht aufrecht**: Stiel entlang +Z, Unterkante Knauf bei z = 0.
- **Spitze zeigt nach −Y** (Vorderseite), Flachende nach +Y, die schmale Seite liegt in X.
- Zum Vergleich: Eine Roblox-Figur (R15) ist etwa 5 Studs groß, die Hand hängt bei etwa 2,5 Studs. Die Hacke ist mit 3,4 bis 4,3 Studs absichtlich groß (Simulator-Look, gut lesbar).

## Maße je Stufe

`Lc` = Höhe der Kopf-Mitte, `P` = Länge der Spitze, `Q` = Länge des Flachendes (jeweils ab der Block-Kante).

| Stufe | Modell | Lc | P | Q | Gesamthöhe | Spannweite Kopf | Kopf-Block (X × Y × Z) |
|---|---|---|---|---|---|---|---|
| 1 Rost | `PickaxeRust` | 3,0 | 1,05 | 0,55 | 3,4 | 2,5 | 0,6 × 0,9 × 0,8 |
| 2 Eisen | `PickaxeIron` | 3,2 | 1,20 | 0,60 | 3,7 | 2,7 | 0,6 × 0,9 × 0,8 |
| 3 Stahl | `PickaxeSteel` | 3,4 | 1,40 | 0,70 | 3,9 | 3,0 | 0,6 × 0,9 × 0,8 |
| 4 Kristall | `PickaxeCrystal` | 3,6 | 1,55 | 0,75 | 4,1 | 3,2 | 0,6 × 0,9 × 0,8 |
| 5 Titan | `PickaxeTitan` | 3,8 | 1,75 | 0,85 | 4,3 | 3,6 | 0,66 × 1,0 × 0,88 (+10 %) |

Gesamthöhe = Lc + halber Block + Deckplatte. Spannweite = Block-Tiefe + P + Q.

## Teile (Gerüst, gilt für alle Stufen)

Alle Zylinder 8-eckig (wie gedrechselt, low-poly), Fasen klein halten.

| # | Teil | Form (gmt_lib) | Maße | Lage | Material |
|---|---|---|---|---|---|
| 1 | Knauf | `cylinder`, 8 Seg. | r 0,27, Höhe 0,30, Fase 0,05 | z 0 – 0,30 | SteelDark |
| 2 | Griff | `cylinder`, 8 Seg. | r 0,21 | z 0,30 – 1,40 | Belt (Gummi) |
| 2a | Griff-Rillen | 3 × `cylinder`, 8 Seg. | r 0,235, Höhe 0,08 | z 0,60 / 0,90 / 1,20 | wie Griff |
| 3 | Stiel | `cylinder`, 8 Seg. | r 0,15 | z 1,40 – Lc (endet im Block) | SteelDark |
| 4 | Warnringe | `cylinder`, 8 Seg., je Höhe 0,10 | r 0,18 | direkt unter dem Kragen, von unten: Gelb, Schwarz, Gelb | Yellow / Black |
| 5 | Kragen | `cylinder`, 8 Seg. | r 0,22, Höhe 0,25 | z Lc − 0,65 – Lc − 0,40 | SteelDark |
| 6 | Kopf-Block | `box`, Fase 0,08 | siehe Tabelle | Mitte (0, 0, Lc) | Orange (Rost: RustDark) |
| 7 | Deckplatte | `box`, Fase 0,02 | 0,46 × 0,70 × 0,08 | oben auf dem Block | SteelDark |
| 8 | Bolzen | je X-Seite 4 × `cylinder` (Achse X), 8 Seg. | r 0,07, Tiefe 0,05 | y ±0,30, z Lc ± 0,25 | SteelLight |
| 9 | Stufen-Lichter | `box` | 0,04 × 0,10 × 0,10 | beide X-Seiten, z = Lc, in einer Reihe, Abstand 0,15, mittig | Cyan (Neon) |
| 10 | Spitze | Loft aus 3 Querschnitten (XZ-Ebene) | siehe unten | nach −Y | Kopf-Material der Stufe |
| 11 | Flachende | Loft aus 2 Querschnitten | siehe unten | nach +Y | Kopf-Material der Stufe |

**Spitze (Teil 10)**, Querschnitte als Rechtecke in der XZ-Ebene, relativ zur Kopf-Mitte (0, 0, Lc). Die Spitze biegt sich leicht nach unten, wie bei einer echten Hacke. R0 sitzt an der Block-Kante (y = ±0,45, bei Titan ±0,50):

| Querschnitt | y | Breite X | Höhe Z | Mitte z (relativ) |
|---|---|---|---|---|
| R0 (am Block) | −0,45 | 0,50 | 0,60 | 0 |
| R1 (Mitte) | −0,45 − 0,55·P | 0,36 | 0,40 | −0,08 |
| R2 (Spitze) | −0,45 − P | 0,10 | 0,10 | −0,28 |

**Flachende (Teil 11)**, wird breiter und flacher (Meißel-Form):

| Querschnitt | y | Breite X | Höhe Z | Mitte z (relativ) |
|---|---|---|---|---|
| R0 (am Block) | +0,45 | 0,50 | 0,60 | 0 |
| R1 (Schneide) | +0,45 + Q | 0,70 | 0,14 | −0,12 |

`gmt_lib.loft_rings` nimmt Ringe in der XY-Ebene. Für Spitze und Flachende braucht das Skript eine kleine Hilfsfunktion `rect_ring_xz(w, h, y, zc)`, die die vier Ecken in der XZ-Ebene liefert.

## Was jede Stufe anders macht

| Stufe | Kopf-Material | Kopf-Block | Warnringe | Stufen-Lichter | Erkennungsmerkmal | Leuchten in Roblox |
|---|---|---|---|---|---|---|
| 1 Rost | Rust | RustDark | keine | 0 | **Zusammengeflickt:** Griff mit Klebeband (Cream statt Gummi), Stiel RustDark, Flicken-Platte (SteelGrey, 0,42 × 0,06 × 0,30, um 10° gekippt, 2 Bolzen) auf der +X-Seite, je Seite nur 2 statt 4 Bolzen (über Kreuz), keine Deckplatte, Spitze abgestumpft (R2: 0,20 × 0,18) | – |
| 2 Eisen | SteelGrey | Orange | 1 (nur Gelb) | 1 | **Ehrliches Werkzeug:** sauber, nichts Besonderes. Die erste „richtige“ Hacke. | – |
| 3 Stahl | SteelLight | Orange | 3 (Gelb/Schwarz/Gelb) | 2 | **Kupfer-Bolzen** (Copper statt SteelLight), cyanfarbener Status-Punkt auf der Deckplatte (0,12 × 0,12 × 0,04, Neon) | – |
| 4 Kristall | Spitze: Crystal; Flachende: SteelLight | Orange | 3 | 3 | **Kristall-Spitze:** Statt des Lofts eine 6-eckige Kristall-Pyramide (r 0,24, Länge P, Achse −Y) in einem Halte-Ring (SteelLight, r 0,30, Tiefe 0,15, bei y −0,50). Kleiner Kristall-Einsatz oben auf dem Flachende (0,08 × 0,35 × 0,05, längs). | PointLight violett, Range 5 |
| 5 Titan | Titan | Orange, 10 % größer | 3 | 4 | **Leuchtkante:** Cyan-Neonstreifen (0,08 breit, 0,04 hoch) auf dem Rücken von Spitze und Flachende, Cyan-Leuchtring um den Knauf (r 0,28, Höhe 0,06, bei z 0,15) | PointLight cyan, Range 5 |

Warum Orange für den Kopf-Block ab Stufe 2: Orange ist die Farbe unserer Maschinen (Bohrer, Basis, Lager). Die Hacke gehört so sichtbar zur Kolonie. Die Stufe erkennt man an Kopf-Material, Lichtern und Merkmal.

## Neue Farben für `gmt_materials.py` (Vorschlag)
Stimmen mit den Erzfarben im Code überein (`Config/BaseLayout.luau`, `oreColors`).

| Name | Farbe | Typ | Wofür |
|---|---|---|---|
| `Rust` | `#A65A35` | paint | Kopf der Rost-Hacke |
| `RustDark` | `#5E3524` | paint | Block und Stiel der Rost-Hacke |
| `Copper` | `#D9853F` | steel | Bolzen der Stahl-Hacke |
| `Crystal` | `#BE6EF0` | neon | Kristall-Spitze (= Erzfarbe Kristall) |
| `Titan` | `#C8D6E4` | steel | Kopf der Titan-Hacke (= Erzfarbe Titan) |

Vorhandene Farben, die benutzt werden: Orange, Yellow, Black, Cream, SteelGrey, SteelDark, SteelLight, Belt, Cyan.

## Objekte in Blender → Teile in Roblox
Wie bei allen Modellen: **ein Objekt pro (Gruppe, Material)**, z. B. `PickaxeIron_SteelDark`, `PickaxeIron_Orange`.

- **Gruppe `Handle`:** nur der Griff mit den Rillen (`PickaxeIron_Handle_Belt`). Das Setup-Skript benennt ihn in Roblox in **`Handle`** um, alle anderen Teile werden daran geschweißt. Der Griff ist genau da, wo die Hand hält.
- **Gruppe `Glow`:** alle Neon-Teile (Stufen-Lichter, Status-Punkt, Kristall, Leuchtkante). So kann der Code sie beim Schlag kurz aufblitzen lassen.
- **Griffpunkt:** Mitte des Griffs bei (0, 0, 0,85). Weil das die Mitte der `Handle`-MeshPart ist, braucht `Tool.Grip` keine Verschiebung, nur die Drehung (Kopf oben, Spitze nach vorn). Die Drehung bitte einmal im Play einstellen, das Ergebnis hier eintragen.
- **Budget:** höchstens 1.500 Dreiecke je Stufe (Erwartung: etwa 900 bis 1.300). Das ist wenig, weil die Hacke jeder Spieler ständig in der Hand hat.
- **Export:** eine `.fbx`/`.glb` mit allen 5 Stufen nebeneinander (x = 0, 3, 6, 9, 12), wie bei den Erzbrocken.
- **Icons:** Das Skript kann mit `-- --render` zusätzlich je Stufe ein quadratisches Icon (512²) für den Shop rendern.

## Wie die Hacke im Spiel auftaucht (offen, betrifft Jus Code)
Im Moment sieht man beim Hacken keine Hacke (`PickaxeController` arbeitet nur mit dem Prompt). Vorschlag: Die Hacke ist ein Roblox-`Tool`, das beim Hacken automatisch in die Hand kommt, mit einer kurzen Schlag-Animation pro Schlag (Ausholen 0,15 s, Schlag 0,1 s). Das entscheidet Ju zusammen mit Jos.

## Referenzbild für Gemini
Wie bei Bohrer und Lager-Kasten kann Jos vorher ein Referenzbild machen. Die Prompts stehen in `../../../referenz/bild-prompts.md` unter „8. Spitzhacke“. Ohne Bild geht es auch: Dieser Bauplan reicht für den Blender-Bau.

## Vorschau
Eine drehbare 3D-Vorschau (grobe Klötzchen nach genau diesen Maßen, noch ohne Fasen) liegt als Artifact bei Jos. Sie ersetzt nicht den Blender-Bau, sie zeigt nur Proportionen und Farben.

## Offene Fragen
- [ ] Passen Größe (3,4 bis 4,3 Studs) und die 5 Erkennungsmerkmale? (Jos, Ju)
- [ ] Orange-Block ab Stufe 2 oder lieber je Stufe eine eigene Block-Farbe?
- [ ] Wie hält der Spieler die Hacke: `Tool` oder fest an der Hand, nur beim Hacken sichtbar? (Ju, Code)
- [ ] Referenzbild erst in Gemini machen oder direkt nach diesem Plan bauen? (Jos)
