# Bauplan: Spitzhacke (5 Stufen)

- **Status:** Vorschlag (Jos' Claude). **v2 in Blender gebaut (14.11.2026)** nach den Higgsfield-Bildern. Wartet auf das OK von Jos und Ju, Import in Studio offen.
- **Modelle:** `PickaxeRust`, `PickaxeIron`, `PickaxeSteel`, `PickaxeCrystal`, `PickaxeTitan`
- **Dateien:** `../pickaxe.glb`, `../pickaxe.fbx`, `../pickaxe.blend`, Skript `../blender-skripte/build_pickaxe.py`
- **Vorschau:** `../vorschau/pickaxe_vergleich.jpg` (oben Higgsfield-Bild, unten Blender), `../vorschau/pickaxe.png` (schräg), `../vorschau/pickaxe_side.png` (Seite), Shop-Icons `../vorschau/pickaxe_<stufe>_icon.png`
- **Referenzbilder (Higgsfield, 14.11.):** `../../../referenz/bilder/ausruestung/spitzhacken-reihe-01.jpg` (Hauptvorlage), `spitzhacke-stahl-01.jpg` (Modellblatt Stahl), `spitzhacken-koepfe-01.jpg` (Köpfe)
- **Spiel-Werte:** `../../../spiel/16-raeume-und-spitzhacke.md`, `../../../daten/upgrades.md`, Code `src/ReplicatedStorage/Shared/Config/Pickaxe.luau`
- **Gehört zu:** `schmiede-einrichtung.md` (Schmiede, Raum 2)

## Route: Blender-Skript, nicht Tripo
Die Spitzhacke ist ein mechanisches Werkzeug aus einfachen Formen. Wir brauchen fünf Stufen mit fast gleicher Form, und unser Stil ist „flache Farben ohne Texturen“ (`../README.md`). Tripo liefert texturierte Einzel-Meshes und passt deshalb nicht. Neu bauen: `blender -b -P build_pickaxe.py -- --render`.

## Die Idee in einem Satz
**Ein Gerüst, fünf Häute:** Alle Stufen haben denselben Aufbau (Knauf, Griff, Stiel, Warnringe, Kragen, Kopf-Block mit Kappe, Sichel-Spitze, Hammer-Ende). Von Stufe zu Stufe wird die Hacke etwas größer, das Kopf-Material ändert sich, und es kommen **cyanfarbene Stufen-Lichter** dazu (Stufe 1 hat keins, Stufe 5 hat vier). Dazu hat jede Stufe **ein Erkennungsmerkmal**.

Die Spitze ist **stumpf** (Kinder-Spiel, nichts Spitzes).

## Was sich durch die Bilder geändert hat (v1 → v2)
| Teil | v1 (Plan) | v2 (gebaut, wie im Bild) |
|---|---|---|
| Spitze | fast gerade, schnell dünn | **Sichel:** setzt oben am Block an, macht einen kleinen Buckel und biegt deutlich nach unten, bleibt lange dick |
| Rückseite | breites, flaches Meißel-Ende | **kurzes Hammer-Ende:** dunkler Hals und ein etwas größeres Schlagstück mit Fasen |
| Kappe | flache Platte | **achteckige Kappe**, ab Stahl mit Cyan-Licht oben |
| Stiel | dünn, dunkel | dicker, mittleres Grau (`SteelMid`) |
| Griff | 3 schmale Rillen | 4 dicke Gummi-Ringe, darunter Knauf mit orangem Endring |
| Lichter | in einer Reihe | 1 = Mitte, 2 = nebeneinander, 3 = Reihe, 4 = 2×2, jeweils mit hellem Rahmen |
| Bolzen | alle Stufen | nur Stahl (Kupfer) und Kristall (hell), wie im Bild |
| Länge der Spitze | 1,05 bis 1,75 | 1,00 bis 1,55 (Spannweite etwa zwei Drittel der Höhe, wie im Bild) |

## Einheiten und Ausrichtung (wie alle unsere Modelle)
- 1 Blender-Einheit = 1 Stud.
- Die Hacke **steht aufrecht**: Stiel entlang +Z, Unterkante Knauf bei z = 0.
- **Spitze zeigt nach −Y** (Vorderseite), Hammer-Ende nach +Y, die schmale Seite liegt in X.
- Eine Roblox-Figur (R15) ist etwa 5 Studs groß. Die Hacke ist mit 3,4 bis 4,3 Studs absichtlich groß (Simulator-Look, gut lesbar).

## Maße je Stufe (gebaut)
`h` = Gesamthöhe ohne Licht auf der Kappe, `P` = Länge der Spitze, `Q` = Länge des Hammer-Endes (jeweils ab Block-Kante). Kopf-Mitte `Lc = h − 0,15 − Blockhöhe/2`.

| Stufe | Modell | h | P | Q | Kopf-Block (X × Y × Z) | Spannweite | Dreiecke |
|---|---|---|---|---|---|---|---|
| 1 Rost | `PickaxeRust` | 3,4 | 1,00 | 0,50 | 0,60 × 0,66 × 0,84 | 2,18 | 704 |
| 2 Eisen | `PickaxeIron` | 3,7 | 1,15 | 0,50 | 0,62 × 0,68 × 0,88 | 2,33 | 724 |
| 3 Stahl | `PickaxeSteel` | 3,9 | 1,30 | 0,55 | 0,62 × 0,68 × 0,90 | 2,53 | 1.016 |
| 4 Kristall | `PickaxeCrystal` | 4,1 | 1,40 | 0,55 | 0,62 × 0,68 × 0,90 | 2,65 | 1.148 |
| 5 Titan | `PickaxeTitan` | 4,3 | 1,55 | 0,60 | 0,68 × 0,75 × 0,98 | 2,93 | 1.000 |

Budget war höchstens 1.500 Dreiecke je Stufe, alle liegen darunter.

## Teile (Gerüst, gilt für alle Stufen)
Alle Zylinder 8-eckig.

| Teil | Maße | Lage (z) | Material |
|---|---|---|---|
| Endring | r 0,285, Höhe 0,07 | 0 – 0,07 | Orange (Titan: Cyan, Rost: keiner) |
| Knauf | r 0,28, Fase 0,04 | bis 0,40 | SteelDark (Titan: Titan) |
| Griff (Gruppe `Handle`) | r 0,215 | 0,40 – 1,35 | Belt (Rost: Cream = Klebeband) |
| Griff-Ringe (Gruppe `Handle`) | 4 × r 0,26, je 0,16 hoch | Mitte bei 0,52 / 0,76 / 1,00 / 1,24 | wie Griff |
| Stiel | r 0,19 | 1,35 – Lc | SteelMid (Rost: RustDark) |
| Kragen | r 0,27, Höhe 0,20 | direkt unter dem Block | SteelDark (Rost: RustDark) |
| Warnringe | r 0,245, Gelb 0,10 / Schwarz 0,07 hoch | unter dem Kragen, von oben Gelb, Schwarz, Gelb | Yellow / Black |
| Kopf-Block | siehe Tabelle, Fase 0,08 | Mitte Lc | Orange (Rost: RustDark) |
| Kappe | r 0,24, Höhe 0,15 (Rost r 0,18) | auf dem Block | SteelDark (Rost: RustDark) |
| Kappen-Licht (ab Stahl) | r 0,08 (Titan 0,10) | oben auf der Kappe | Cyan |
| Stufen-Lichter | 0,13 × 0,13 (ab 3 Lichtern 0,11), heller Rahmen 0,06 größer | beide X-Seiten, um Lc | Cyan, Rahmen SteelLight |
| Spitze | Loft aus 5 Querschnitten (Achteck) entlang einer Bezier-Kurve: Ansatz (y −Block/2, z Lc + 0,08·Blockhöhe), Buckel +0,10 bei halber Länge, Ende 0,46·P tiefer. Querschnitt 0,42 × 0,56 am Block bis 0,09 × 0,10 an der Spitze (Rost 0,17 × 0,16, stumpf) | nach −Y | Kopf-Material |
| Hammer-Ende | Hals 0,30 × 0,55·Q × 0,34 (dunkel), Schlagstück 0,38 × 0,45·Q × 0,44 mit Fase 0,06 | nach +Y, Mitte knapp über Lc | Hals SteelDark, Schlagstück Kopf-Material |

## Was jede Stufe anders macht
| Stufe | Kopf-Material | Ringe | Lichter | Erkennungsmerkmal |
|---|---|---|---|---|
| 1 Rost | Rust (Block RustDark) | keine | 0 | **Zusammengeflickt:** Klebeband-Griff, brauner Stiel, graue Flicken-Platte mit 2 Bolzen auf der +X-Seite, stumpfe Spitze, kleine Kappe |
| 2 Eisen | SteelGrey | 1 Gelb | 1 | **Ehrliches Werkzeug:** sauber, nichts Besonderes, oranger Endring |
| 3 Stahl | SteelLight | Gelb/Schwarz/Gelb | 2 | **Kupfer-Bolzen** in den Block-Ecken, Cyan-Licht auf der Kappe |
| 4 Kristall | Spitze Crystal, Rest SteelLight | Gelb/Schwarz/Gelb | 3 | **Kristall-Spitze:** 6-eckiger Kristall in einem hellen Halte-Ring, kleiner Kristall auf der Schlagfläche, helle Bolzen |
| 5 Titan | Titan, Block 10 % größer | Gelb/Schwarz/Gelb | 4 (2×2) | **Leuchtkante** oben auf der Sichel, Cyan-Streifen auf der Schlagfläche, Titan-Knauf mit Cyan-Endring |

Leuchten in Roblox (macht das Setup-Skript oder Jus Code): Kristall PointLight violett, Titan PointLight cyan, je Range 5.

## Farben in `gmt_materials.py`
Neu am 14.11.: `Rust` `#A65A35`, `RustDark` `#5E3524`, `Copper` `#D9853F`, `Crystal` `#BE6EF0` (Neon, = Erzfarbe), `Titan` `#C8D6E4` (= Erzfarbe), `SteelMid` `#5E656D` (Stiel).

## Objekte in Blender → Teile in Roblox
Wie bei allen Modellen: **ein Objekt pro (Gruppe, Material)**, z. B. `PickaxeIron_SteelMid`, `PickaxeIron_Orange`.

- **Gruppe `Handle`:** Griff mit den 4 Ringen (`PickaxeIron_Handle_Belt`). Das Setup-Skript benennt ihn in Roblox in **`Handle`** um, alle anderen Teile werden daran geschweißt.
- **Gruppe `Glow`:** alle Neon-Teile (Lichter, Kappen-Licht, Kristall, Leuchtkante, Titan-Endring). So kann der Code sie beim Schlag kurz aufblitzen lassen.
- **Griffpunkt:** Mitte des Griffs bei (0, 0, 0,875). Weil das die Mitte der `Handle`-MeshPart ist, braucht `Tool.Grip` keine Verschiebung, nur die Drehung (Kopf oben, Spitze nach vorn). Die Drehung bitte einmal im Play einstellen und hier eintragen.
- **Export:** eine `.glb`/`.fbx` mit allen 5 Stufen nebeneinander (x = 0, 3, 6, 9, 12), wie bei den Erzbrocken.

## Wie die Hacke im Spiel auftaucht (offen, betrifft Jus Code)
Im Moment sieht man beim Hacken keine Hacke (`PickaxeController` arbeitet nur mit dem Prompt). Vorschlag: Die Hacke ist ein Roblox-`Tool`, das beim Hacken automatisch in die Hand kommt, mit einer kurzen Schlag-Animation pro Schlag (Ausholen 0,15 s, Schlag 0,1 s). Das entscheidet Ju zusammen mit Jos.

## Offene Fragen
- [ ] Passt v2 so (Form, Größe 3,4 bis 4,3 Studs, Erkennungsmerkmale)? (Jos, Ju)
- [ ] Lichter: gebaut nach der Regel „Stufe minus 1“ (0 bis 4). Das Higgsfield-Bild zeigt bei Stahl und Kristall je eins weniger. Regel behalten?
- [ ] Wie hält der Spieler die Hacke: `Tool` oder fest an der Hand, nur beim Hacken sichtbar? (Ju, Code)
- [ ] Wer importiert in Studio (Upload über Open Cloud auf Jus Konto, wie bei den anderen Modellen)?
