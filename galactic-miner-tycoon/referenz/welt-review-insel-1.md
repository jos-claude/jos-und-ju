# Welt-Review Insel 1 – Warum es noch nicht wie *ein* Planet wirkt

- **Status:** Review (Vorschlag)
- **Von:** Art-Director-Review (Claude, frischer Blick), 12.11.2026, auf Wunsch von Jos
- **Grundlage:** Referenzbild `bilder/welt/heimatplanet-02-orange.jpg`, echter Roblox-Screenshot `bilder/screenshots/2026-11-12-insel1-play-erster-stand.jpg`, Vorschau-Renderings `bilder/welt/vorschau-insel-1/*`, Daten `src/ServerStorage/WorldBuilder/Data/Meta.luau` und `Templates.luau`, Generator `werkzeuge/weltgenerator/worldgen/` (`materials.py`, `catalog.py`, `lighting.py`, `landforms.py`, `placement.py`).
- **Nichts davon ist beschlossen.** Alle Zahlen sind Startwerte. Farben müssen in Studio kalibriert werden (Abschnitt 2f), weil Roblox-Texturen die Farben verändern.
- Was gut ist und bleiben soll: der Großaufbau (Ringe, Washes, Landmarken, Sichtachsen), die Formen der Tafelberge und Hoodoos, die Idee „Kausalität“ aus der Design-Vorgabe. Das Problem ist fast nur die **Oberfläche** (Farbe, Helligkeit, Material, Übergänge), nicht die Struktur.

---

## 0. Kurzfassung

**Die 5 wichtigsten Ursachen**
1. **Helligkeits-Kluft:** In Roblox ist der Boden dunkel-rostig (L ≈ 0,51), die Berge sind hell-pastellig (L ≈ 0,79–0,86). Im Referenzbild liegen beide bei L ≈ 0,75. Gründe: dunkle Ground-Textur, flache Sonne (22°), kühles Umgebungslicht.
2. **Zwei Farbwelten:** Die Gesteinsbänder spannen 200° Farbton auf (Mint, Blau-Lavendel, Mauve, Bonbon-Rosa, Creme). Der Boden (Korall/Rost) kommt in den Bergen praktisch nicht vor. Im Referenzbild liegen alle Gesteine in einem warmen Bogen (Rosa → Pfirsich → Butter) und der Boden ist ihre Mischung.
3. **Drei Oberflächen-Sprachen:** Boden = fotorealistische Erd-Textur, Bänder = sechs verschiedene eingebaute Gesteins-Texturen, Deko = textur- und strukturloses SmoothPlastic (338 Teile-Vorlagen). Ellipsoide (SpecialMesh) zeigen **gar kein** Material.
4. **Kein geologischer Übergang Berg → Boden:** Die Schutthalden sind sehr kurz (0,17–0,25 × Höhe statt 0,5–0,7) und aus dunklem Mud, was wie ein „Brandsaum“ aussieht. Kiesel in Zufallsfarben wirken wie Konfetti. Rinnen, Fächer und Staub fehlen.
5. **Bäume wie Plastik:** glänzende, perfekte Kugeln, zu satte Farben (plus Saturation +0,18), dicke rosa Stämme mit sichtbaren Stufen, eine Teller-Wurzel, kein Bodenkontakt.

**Die 5 wirksamsten Maßnahmen**
1. **Eine Geologie, drei Zustände:** neue, warme Palette mit 4 Gesteinsfarben + Schutt + Boden. Der Boden ist die Mischfarbe der Gesteine. Bänder mindestens 8 Studs dick, kein Mint und kein Weiß im Stapel (2a).
2. **Licht für den Boden:** Sonne auf 30° Elevation. Die Skybox ist noch nicht hochgeladen, die Änderung kostet also nur ein Neu-Rendern. Dazu wärmeres, helleres Umgebungslicht und kaum Sky-Reflexe. Danach kalibrieren: Boden und Fels im gleichen Helligkeitsband (2c, 2f).
3. **Schutt-Schürzen:** lange, konkave Halden in Gesteinsfarbe, die an der Unterkante in den Boden zerfasern. Dazu Rinnen mit Mini-Fächern und Windfahnen im Lee (2d).
4. **Deko ohne Plastik:** Plastik-Glanz wird zu matten, texturierten Materialien. Ellipsoide werden zu Kugel, Keil oder Block, oder gleich zu Terrain (Moos). Kronen bekommen eine Wolkenform mit dunkler Unterseite. Stämme werden dünn, dunkel und aus Holz (2b).
5. **Eigene MaterialVariants (2. Stufe):** ein ruhiger, heller Boden und **ein** gemeinsamer Gesteins-Look für alle Bänder. Das bringt Fels, Schutt und Kiesel in dieselbe „Pinselsprache“ (2e).

---

## 1. Diagnose (sortiert nach Wirkung)

### Messwerte (Mittelwerte aus den Bildern, L = Helligkeit 0–1 nach HSL)
| Fläche | Roblox-Screenshot | Referenzbild | Eingestellte Farbe (Meta.luau) |
|---|---|---|---|
| Boden nah, Sonne | **#BB6B4A, L 0,51** (rostbraun) | **#FBBE88, L 0,76** (Pfirsich) | Ground #F2A07C, L 0,72 |
| Boden zweiter Ton | – | #EE8672, L 0,69 (Korall-Flecken) | – |
| Tafelberg, lila Band | #E1B3BF, L 0,79 | Lavendel beleuchtet #DAA3B8, L 0,75; im Schatten #A67FB0 | Slate #B3A9DE |
| Tafelberg, Kappe | #F2C6C2, L 0,86 | Butter #EDC996, L 0,76 | Limestone #F9E7A3 |
| Krone Limette | #96BC72 (mit blauem Himmelsglanz) | #DAEE73, matt | #A6E04A |
| Stamm | rosa, so hell wie die Felsen | dunkles Mauve-Braun, L ≈ 0,4–0,5 | #C97A86, L 0,63 |

**Wichtig:** Auf dem Papier liegen Boden (L 0,72) und Bänder (L 0,66–0,81) im selben Helligkeitsband. Erst Roblox reißt sie auseinander. Die Palette wurde mit flachen Farben im three.js-Nachbau abgestimmt, nicht mit Roblox-Texturen. Gemessen dunkelt Roblox den Ground hier um den Faktor (0,77 / 0,67 / 0,60) für R/G/B ab. Weil Blau am stärksten fällt, wird aus Pfirsich **Rost**.

### D1 Helligkeits-Kluft Boden ↔ Berge (größte Wirkung)
- **Textur:** Die Ground-Textur (2022-Material „Dirt Ground“) ist dunkel und körnig, Sandstone, Limestone und Salt sind hell. Dieselbe Farbe wird auf Ground also dunkler.
- **Sonnenwinkel:** Bei 22° Elevation bekommt flacher Boden nur sin 22° = 37 % des direkten Sonnenlichts. Eine Wand, die zur Sonne schaut, bekommt bis zu 93 %. Die Wände sind also **2,5 × heller beleuchtet** als der Boden. Das Referenzbild schaut von oben auf einen hell beschienenen Boden.
- **Licht-Tönung:** `ColorShift_Top` #FFC890 (orange) × Korall × dunkle Textur = Mars-Rost. `OutdoorAmbient` #9A8CB4 ist kühl-grau-lila und macht den Schatten am Boden grau-braun statt rosé.
- Folge: Die Berge „leuchten“ wie Zuckerwatte über einem dunklen Acker. Das ist genau Jos' Satz: „Die Berge haben nichts mit dem Boden zu tun.“

### D2 Zwei Farbwelten statt einer Geologie
- Farbtöne der Bänder heute: Sandstone 338° (kühles Bonbon-Rosa), Slate 251° (Blau-Lavendel), Rock 306° (Mauve), Concrete 161° (Mint), Limestone 47°, Salt (Weiß), Mud 13°. Das sind **8 Farben über 200° Farbton**.
- Die Bodenfarbe (Ground 18°) taucht im Fels nur als Mud-Band auf (30 von 240 Studs). Auf Plateau-Höhe liegt aber gerade Slate (Lavendel), dann Salt (Weiß) (y_eff 48–56). Jeder Tafelberg beginnt also mit einem **lila-weißen Sockel** auf **rostigem** Boden.
- Im Referenzbild liegen die Gesteinsfarben in einem engen, warmen Bogen: Rosa 355°, Pfirsich 10–28°, Butter 31–35°, Lavendel-Rosé 330–340° (beleuchtet). Kühles Violett gibt es nur im Schatten. Der Boden (Pfirsich) ist erkennbar die **Mischung** der Felsfarben. Daher wirkt alles wie aus einem Stück.
- Mint ist bei uns Farbe für Leben und Kristalle (Farbskript 4.5). Als Gesteinsband verwischt sie die Rollen.

### D3 Drei Oberflächen-Sprachen + Plastik-Glanz
- **Boden:** fotorealistische Erde mit Körnung im Stud-Maßstab (im Screenshot vorne deutlich zu sehen).
- **Fels:** Jedes Band hat ein anderes eingebautes Material (Mud, Sandstone, Limestone, Slate, Salt, Rock, Concrete), also ein anderes Muster. Die Bänder wirken wie Flicken, nicht wie ein Gestein in verschiedenen Farben.
- **Deko:** 338 SmoothPlastic- und 141 Neon-Teile-Definitionen. SmoothPlastic hat keine Struktur und spiegelt den Himmel (`EnvironmentSpecularScale` 0,3; im Screenshot blauer Glanz auf den Kronen).
- **Technischer Haken:** Teile mit `SpecialMesh` (bei uns alle „Ellipsoid“: Moos, Kiesel-Formen 0/1, Pilzhüte, Kupferfels, Wurzelteller, Nebel) **ignorieren das Material** und zeigen keine Textur (DevForum, mehrere Threads; API-Doku SpecialMesh). Der „Slate“-Kiesel als Ellipsoid ist also trotzdem Plastik.
- Das Referenzbild hat **eine** Sprache: matt, Low-Poly-Facetten, weicher Verlauf, für Boden, Felsen und Pflanzen gleich.

### D4 Kein Übergang Berg → Boden (Geologie: Woher kommt der Boden?)
- Die Halden sind zu kurz: Tafelberge `tal_l = 0,17–0,25 × Höhe` (`landforms.py` Z. 147), Kämme `T = 0,17 × crest`. Die Vorgabe 3.1 nennt 0,5–0,7. Ergebnis: ein schmaler Saum statt einer Schürze.
- Die Halden sind aus **Mud #D9795F**, dunkler und röter als Boden und Fels. In `mesa_close` sieht das aus wie Flammen am Bergfuß.
- Kiesel: Farbe meist Zufall (`placement.py`, `rng.integers(0, 6)`), verstreut auf freier Fläche (Screenshot: lila, creme und rosa Splitter vor dem Spawn). Echte Steine stammen vom Fels darüber und liegen am Fuß.
- Rinnen gibt es nur an den Danxia-Kämmen, nicht an den Tafelbergen. Es fehlen Mini-Fächer, Staubfahnen und Wüstenlack. Der Berg „steht auf“ dem Boden, statt in ihn zu zerfallen.

### D5 Bäume (und Pflanzen) sehen aus wie Plastik
- Perfekte Kugeln aus SmoothPlastic, eine Farbe pro Kugel, Glanzpunkt. Es gibt keine dunklere Unterseite, also keinen Volumen- und Kontaktschatten.
- Die Farben sind satt (#A6E04A, #3FD0D0), dazu `ColorCorrection.Saturation` +0,18. Neben dem rostigen Boden springen sie heraus wie aufgeklebt.
- Stämme sind dick und rosa (#C97A86, L 0,63) und haben dieselbe Helligkeit wie die Felsen. Das liest sich als Zuckerstange. Segmente mit Durchmesser-Sprüngen sehen aus wie Bambus (`grove_a`). Die Wurzel ist ein flacher Ellipsoid-Teller.
- Im Referenzbild sind die Stämme dünn und dunkel und die Kronen matt mit Verlauf. Nur so wirkt der Ballon leicht und organisch.
- Unter Hainen liegt ein greller Grass-Fleck (#9BE06B) mit harter Kante, wie ein Teppich.

### D6 Zwei Gebirgs-Sprachen und ein lila Außenring
- Das Randgebirge und die Kammzacken nutzen `ridged`-Noise mit `sharp=2.4`: sägezahn-spitze Grate mit weißen Zickzack-Streifen (`ring_d_ridge`, `ring_e_fog`, `ring_d_terraces`). Die Tafelberge sind dagegen weich, gestuft und achteckig. Das wirkt wie zwei verschiedene Planeten.
- Ring E hat Slate (Blau-Lavendel) als Boden. Auf der Karte gibt es eine harte Kante Korall | Lila. Der Horizont ist rundum eine lila Wand.

### D7 Bänder zu dünn für 4-Stud-Voxel
- Bänder mit 4–6 Studs (Salt 4, Concrete 4, Limestone 6, Mud 6) sind kleiner als 2 Voxel. Folge: Treppchen-Aliasing und Pixel-Flicken (`ring_d_ridge`, Vulkanhang in `ring_c_volcano`). Das wirkt wie „Pixel-Torte“ statt Gestein.

### D8 Licht und Dunst trennen statt verbinden
- Die Atmosphere-Farbe #EEB8BE ist Rosa, nicht die Staubfarbe des Bodens. In der Ferne werden die Berge noch heller und rosiger, während der Boden vorne rostig bleibt.
- `EnvironmentDiffuseScale` 0,35 und `EnvironmentSpecularScale` 0,3 holen Licht und Spiegelungen aus der Skybox. Mit dem **dunklen Weltraum-Himmel** wird beides dunkler und türkis-grau. Der jetzige Screenshot mit Standardhimmel ist also noch nicht das Endbild. Licht erst mit hochgeladener Skybox beurteilen.

### D9 Maßstab: Es fehlt die Mitte
- Riesige einfarbige Ebenen (`hero`) und sehr viel Kleinkram (995 Gras-Büschel = 3 996 Teile, 1 880 Kiesel) liegen direkt nebeneinander. Es fehlt die mittlere Größe: Brocken 2–8 Studs, sanfte Bodenwellen, große Farbflecken.
- Die eingebauten Texturen sind für Menschen-Maßstab gemacht. Auf 100 Studs hohen Wänden wiederholen sie sich klein und „fusselig“, und der Berg wirkt wie ein Kuchen. Große Formen brauchen große Details (Rinnen, Simse, Facetten).

### Was im Referenzbild Einheit stiftet
1. Ein enges Helligkeitsband für alle großen Flächen (L 0,70–0,85). Dunkel sind nur Stämme, Schatten und Lava.
2. Ein warmer Farbbogen für alle Gesteine. Der Boden ist ihre Mischung. Akzente (Türkis, Limette, Neon-Violett) gibt es nur bei Leben und Kristallen.
3. Eine Oberflächen-Sprache: matt, facettiert, weiche Verläufe.
4. Ein warmes Hauptlicht und rosé-lavendelfarbene Schatten (nicht grau).
5. Alles hat Bodenkontakt: Schatten, lavendelfarbener Sockel und Brocken am Fuß.
6. Eine Formfamilie: abgerundete Achtecke (Mesas), Prismen (Kristalle), Kugeln (Kronen). Nichts ist zackig-noisy.

---

## 2. Verbesserungsplan

### (a) Terrain-Palette und Geologie: „ein Gesteinsstapel, drei Zustände“
**Geschichte:** Der Planet besteht aus einem warmen Sediment-Stapel (Rosé, Korall, Butter, Lavendel-Rosé). Daraus wird **Fels** (Bänder), dann **Schutt** (Halden, Kiesel, Brocken), dann **Boden** (Staub = Mischfarbe) und **Sand** (ausgewaschenes Butter-Band). So kann jede Bodenfarbe auf ein Gestein zeigen.

| Material | Rolle neu | Alt | **Neu (Startwert)** | Hinweis |
|---|---|---|---|---|
| Ground | Hauptboden (Staub = Mischfarbe) | #F2A07C | **#F8B68C** (H 23, L 0,76) | Ziel gerendert ≈ #E8A47E. Reicht das nicht (2f), mit #FFC49C nachlegen oder MaterialVariant (2e). |
| Mud | „Korall-Boden“ (Flecken) **und** Korall-Band | #D9795F | **#EC8E74** | Zweiter Bodenton wie im Referenzbild. In Studio prüfen, ob Mud nass glänzt, sonst Rolle an Rock geben. |
| Sand | Washes, Dünen, Fächer, Windfahnen | #F6CF96 | **#F7D5A6** | = ausgewaschenes Butter-Band |
| Sandstone | Hauptband „Rosé“ (warm, nicht Bonbon) | #F4A9C4 | **#EEA0A2** (H 358) | häufigstes Band |
| Limestone | Band „Butter“, harte Kappen, Hoodoo-Hüte | #F9E7A3 | **#F1CF94** | etwas tiefer, damit es im Dunst nicht weiß wird |
| Slate | Band „Lavendel-Rosé“, Boden Ring E | #B3A9DE | **#D2AACE** (H 306, wenig Sättigung) | Slate-Textur ist dunkel, daher hell ansetzen |
| Rock | **Schutt**: Halden, Geröll, Felder Ring E | #C48BBE | **#CDA49E** (staubiges Rosé-Beige) | verbindet Fels und Boden |
| Salt | Salzpfannen, Sinter, max. 1 dünnes Akzentband | #FCEFEA | **#F8ECE2** | nicht mehr 3× im Stapel |
| Concrete | nur Geoden-Böden (Mint) | #A9E5D2 | #B2E0D0 | **raus aus dem Bandstapel** |
| Basalt | Lava-/Aschefelder | #3B3245 | #4A3D50 | warmes Dunkel statt Schwarz-Violett |
| CrackedLava | Glut | #FFB07A | bleibt | |
| Grass | Hain-Wiese (Rand) | #9BE06B | **#B2D08E** | gedämpft, Salbei-Limette |
| LeafyGrass | Hain-Kern, Teichrand, Moos | #4FC9B0 | **#86C2A6** | ersetzt die Moos-Teile (2b) |
| Snow / Ice | Gipfel, Ring E | #F2F6FF / #BFE6F5 | #F6F0F2 / #CFE6EE | leicht warm, sonst „kaltes Weiß“ |

**Neuer Bandstapel** (Periode 240, `materials.py` `BANDS`): 13 Bänder statt 21, Mindestdicke 8, Rhythmus dick–dünn:
`Mud 16 · Sandstone 28 · Limestone 10 · Slate 24 · Sandstone 20 · Limestone 8 · Mud 12 · Sandstone 26 · Salt 8 · Slate 28 · Limestone 12 · Sandstone 24 · Mud 24`
Anteile: Rosé 41 %, Lavendel-Rosé 22 %, Korall 22 %, Butter 12 %, Creme 3 %.
- `STRATA_BASE` von 48 auf **4**. Dann liegt das doppelte Korall-Band (Mud 24 + 16 über die Periodengrenze) bei y ≈ −28 … +12. Das ist genau die Bodenhöhe von Ring A–D. Die meisten Berge wachsen dann **aus einem korallfarbenen Sockel**, der zum Boden passt, und darüber kommt Rosé.
- `DIP_DEG` von 3° auf **1,5–2°**. Bei 3° verschiebt sich der Stapel über die Insel um ±105 Studs, und der Sockel-Effekt geht verloren. Die Danxia-Kämme behalten ihre eigene, lokale Neigung.
- Bandrauschen (`bandnoise`) bleibt bei ±1,5–3 Studs. Das reicht für „nicht wie mit dem Lineal“.

**Übergang Berg → Boden (Regel für den Generator):**
1. **Schutt-Schürze** an jeder Steilwand: Halde in Rock (Schutt), Höhe 0,25–0,35 × Wandhöhe, Länge 0,6–0,9 × Wandhöhe, **konkaves Profil** (oben 32°, unten 4°). Die untere Hälfte wird mit einer Noise-Maske (Zellen 4–8 Studs) mit Ground gemischt, sodass die Kante über 10–20 Studs zerfasert. Roblox blendet benachbarte Voxel-Materialien von selbst weich.
2. **Staubmantel:** Die untersten 4–8 Studs jeder Fels-Spalte über dem lokalen Fuß werden zu Ground (Staub, der an der Wand hochweht). Umsetzung: entweder ein neuer Kanal „Fußhöhe“ für den Builder oder die Schürze so hoch ziehen, dass sie den Sockel bedeckt.
3. **Korall-Bodenflecken** (Mud) auf 20–25 % der Ebenen, Flecken 80–300 Studs, bevorzugt in Mulden und unterhalb von Korall-Bändern, Rand zerfasert. Das gibt die zwei Bodentöne des Referenzbilds.
4. **Haine:** LeafyGrass-Kern (innere 50 %), Grass-Ring, Rand über 8–16 Studs gemischt mit Ground. Keine harte Teppichkante.
5. **Ring E:** Übergang Ground → Slate über **300 Studs** fleckig mischen. Durch das wärmere Slate ist der Farbsprung nur noch Pfirsich → Lavendel-Rosé statt Korall → Blau-Lila.

### (b) Deko: gegen Plastik, Stil bleibt
**Allgemeine Regeln**
- **Kein SpecialMesh** für alles, was nach Material aussehen soll. Ellipsoid nur noch für Nebel, Wolken und Dunst. Sonst Ball, Cylinder, Block oder Wedge (zeigen Material-Texturen) oder Terrain.
- **SmoothPlastic: 0 Teile.** Neon nur für echte Lichtquellen (Laternen, Lit-Kristalle, Lava, Titan-Adern). `Reflectance` 0, außer Kristall-Glas (0,08–0,12) und Titan (0,15).
- **Farbregel:** Große Deko liegt bei L 0,55–0,80 und Sättigung ≤ 0,6. Ausnahme sind Wegweiser (Kristalle, Laternen). Jede Pflanze bekommt eine **dunklere Rolle unten** (Unterseite, Lamellen, Basis), also −15 bis −25 % Helligkeit und 10° kühler. Das ist der eingebaute Kontaktschatten.
- **Material-Kandidaten** für „gemalt-matt“: `Plaster` (hell, ruhig, wenig Muster), `Sand` (feine Körnung, wirkt wie Filz), `LeafyGrass`/`Grass` (Laub/Flaum), `Wood` (Stämme). Endgültige Wahl über die Farbtafel (2f).

| Art (Instanzen) | Form neu | Material | Farben neu | Notiz |
|---|---|---|---|---|
| **Ballon-Baum Krone** (327) | 1 Hauptkugel + 2 Nebenkugeln (0,55–0,7 ×, 25–35 % überlappend, leicht unterhalb) + 1 Unterseiten-Kugel (0,8 ×, 0,25 d tiefer) | Test A: `Sand`, Test B: `LeafyGrass`, Test C: `Plaster` | Türkis #52C6BE, Limette #B8DA6C, Mint #86D4B4, Himmelblau #74B2DC (selten), Rosa #EFA4AE (selten), Gelb #EFD478 (selten). Unterseite jeweils `darker(0,22)` und 10° kühler | Wolkenform statt Murmel. Ring E bleibt kühl (#A8D2EA, #BCAEE8). |
| **Stamm + Knoten** | Ø × 0,6 (≈ 0,9–1,4); Segment-Ende = nächster Segment-Anfang (keine Durchmesser-Sprünge), Gelenk-Kugel nur bei Knick > 10° | `Wood` | Mauve-Braun **#7E5A68** / #6E5262 (L ≈ 0,4) | dunkel = Gewicht und Silhouette wie im Referenzbild |
| **Wurzel** | statt Ellipsoid-Teller: 3 kurze Zylinder (Ø 0,6 × Stamm, 1,5–2,5 lang, 40° geneigt, halb im Boden) + Terrain-Hügel (LeafyGrass, +0,5–1 Stud) | `Wood` | wie Stamm | Baum wächst aus dem Boden |
| **Nudelpflanze** (474) | Form bleibt; unterste Kugel halb im Boden | `Plaster` (Test `Sand`) | Gelb #E8D27E, Türkis #6CC6BC, Mint #94D8BC, Rosa #EBA6BE (8 %); Spitze nur +20 % heller | |
| **Pilz** (138) | Hut = **Ball** (Ø 0,8 × alt, Mitte 0,3 d unter Oberkante) statt Ellipsoid; Lamelle **dunkler** statt heller | `Plaster` | Hut Violett #A98CD8, Rosa #EE9CB8, Pfirsich #F2AE86, Türkis #79C9C0; Stiel #EDE2D2; Flecken #FFF1DC | Unterseite liegt im Schatten, deshalb dunkel |
| **Kristall klein** (408) | Form bleibt + 1–2 Fußbrocken in Bandfarbe | `Glass`, Transparency 0,3, Reflectance 0,08 (Test: `Ice`) | Türkis #8EE8D8, Eisblau #A8D8F2, Violett #CFA0F0, Magenta #F2A0D6, Lila #B2A0F0 | Facetten werden von der Sonne schattiert, kein Neon-Stäbchen-Look. Wächst aus dem Gestein. |
| **Kristall mittel/groß, Lit** | Glas-Hülle (Transp. 0,35) + **Neon-Kern** (0,45 × Breite, 0,8 × Länge, Transp. 0,25) | `Glass` + `Neon` | wie oben, Kern 15 % heller | Leuchten nur, wo es führen soll |
| **Laternenblume** | bleibt | Stiel/Kelch `Plaster`, Lampe `Neon` (Transp. 0,35) | Stiel #86C49A | |
| **Orgelrohr** (93) | + innen versenkter dunkler Zylinder (Ø −0,6, 40 % dunkler) = Loch; Basis 10 % breiter | `Plaster` | #E99AA2, #E8CF86, #8ED6B4 | |
| **Perlenkaktus** | bleibt | `Sand` oder `Plaster` | #94CDB8, #AC9CD2; Perlen Neon ok | |
| **Moospolster** (500 → 0 Teile) | **als Terrain**: LeafyGrass/Grass-Flecken Ø 6–30, Höhe +0,5–1,5 | Terrain | siehe (a) | spart 1 000 Teile, wächst wirklich aus dem Boden |
| **Gras-Büschel** (995) | in Hainen/Oasen durch `Terrain.Decoration` (animiertes Gras auf Grass) ersetzen, Rest als 3 dünne Keil-Halme | `Grass` | #A8C878, #94BE86, #BCCB7C | spart ca. 2 500 Teile; Gras-Farbe = Grass-Terrainfarbe |
| **Kiesel** (1 880) | Ball (35 % versenkt), Wedge, Block (kein Ellipsoid). In Clustern am Halden-Fuß, groß nah am Fels, klein weiter weg | Material **des Bands darüber** (Sandstone/Limestone/Slate/Mud/Rock) | Bandfarbe 12 % dunkler, 15 % entsättigt | Variante nach **nächstem Fels**, nicht Zufall. Nicht auf freie Bauflächen streuen. |
| **Brocken / Kupferfels** (68) | 2–3 gedrehte Blöcke/Keile (Low-Poly-Brocken wie im Referenzbild) statt Ellipsoid | `Sandstone` / `Rock` | Kupfer #C98A6E, Patina-Scheiben (flache Zylinder) #52BCA2 in `Plaster` | Mittelgröße 2–8 Studs, die bisher fehlt (D9) |
| **Schilf** | bleibt | `Grass` | #8CCFB0 / #E8D68A | |
| **Dampfquelle** | Wasser-Punkt statt Neon | `Glass` #7FE0D6 Transp. 0,3 | Sinter `Limestone` #EFE3D2 | |
| **Fossil** | bleibt | `Limestone` | #EAD9BC | |

**Teile-Budget:** heute 24 195. Moos −1 000, Gras −2 500; Kronen +2 Kugeln, Wurzeln, Kristallkerne, Brocken zusammen ca. +2 500. Ergebnis ≈ **23 200**, also unter dem Budget von 25 000.

### (c) Licht, Atmosphere, Nachbearbeitung (Startwerte für den dunklen Weltraum-Himmel)
| Eigenschaft | Jetzt | **Neu** | Warum |
|---|---|---|---|
| Sonne (`sky.py` `solve_roblox_sun`, `layout.py` `SUN_EL`) | Az 250 / El 22 | **Az 250 / El 30** | +33 % Direktlicht auf flachem Boden; Schatten bleiben lang (1,7 × Höhe). Skybox vor dem Upload neu rendern. **Designänderung → Jos fragen.** |
| Brightness | 3,0 | 3,0 | |
| Ambient | #4E4466 | #5A4A66 | etwas wärmer unter Überhängen |
| OutdoorAmbient | #9A8CB4 (kühl, H 261) | **#AC92AC** (Rosé-Lavendel, H 300) | Schatten auf Pfirsich werden mauve-korall statt grau-braun (wie im Referenzbild) |
| ColorShift_Top | #FFC890 | **#FFD8AE** | weniger Orange, sonst Rost |
| ColorShift_Bottom | #7468C0 | #8A74B0 | weniger Blau |
| EnvironmentDiffuseScale | 0,35 | **0,15** | dunkle Skybox würde Schatten türkis-grau ziehen |
| EnvironmentSpecularScale | 0,3 | **0,08** | kein Himmels-Spiegel auf Pflanzen |
| ExposureCompensation | 0,1 | 0,2 | |
| ShadowSoftness | 0,25 | 0,4 | weichere Schatten wie im Referenzbild |
| Technology | ShadowMap | ShadowMap | Future nur als Test (teurer auf Handys) |
| Atmosphere Density / Offset | 0,32 / 0,25 | 0,28 / 0,2 | Ziel: 500 Studs ≈ 15 %, 1 500 ≈ 45 %, Zenit klar |
| Atmosphere Color | #EEB8BE (Rosa) | **#F2BFA6** (Staubfarbe = Mischung Ground/Sandstone) | Ferne verschwimmt in **Planetenstaub**, nicht in Rosa |
| Atmosphere Decay | #8E6FA8 | #7C6AA0 | |
| Glare / Haze | 0,35 / 2,0 | 0,25 / 1,5 | dunkler Himmel bleibt dunkel, Sterne sichtbar |
| ColorCorrection | Br 0,02, Co 0,12, **Sa 0,18**, Tint #FFF1E6 | Br 0, Co 0,08, **Sa 0,04**, Tint #FFF2E8 | Farben in den Daten wählen, nicht global aufpumpen; Sättigung verstärkt den Plastik-Look |
| Bloom | 0,45 / 24 / 1,4 | 0,35 / 30 / 1,5 | nur Neon und Lava glühen |
| SunRays | 0,06 / 0,8 | 0,05 / 0,6 | |

### (d) Landschaft: Formen, Übergänge, Dichte, Maßstab
1. **Halden länger und konkav** (`landforms.py`): Tafelberge `tal_l` 0,17–0,25 → **0,5–0,8 × Höhe**, Kämme `T` 0,17 → **0,28 × crest**. Material Rock + zerfaserter Rand (siehe a).
2. **Erosionsrinnen an Tafelbergen** (wie bei den Kämmen schon vorhanden): alle 20–35 Studs, Tiefe 3–6, oben trichterförmig, darunter je ein Mini-Fächer (Ø 20–40, Sand/Rock). So „fließt“ der Berg in die Ebene.
3. **Windfahnen:** Im Lee (Richtung 70°) jedes Tafelbergs ein heller Sand-Streifen, Länge 3–6 × Bergbreite, Breite 0,6 ×, zum Ende hin zerfasert. Das ist ein starkes Planeten-Signal (wie auf dem Mars) und verbindet Berg und Boden über den Wind.
4. **Boden-Makrorelief:** Wellen mit Amplitude 1–2 Studs und Wellenlänge 60–150 außerhalb der Bau-Kerne. Dazu die Korall-Flecken (a3). Die großen Ebenen sind dann nicht mehr eine einzige Farbe.
5. **Randgebirge und Kammgrate beruhigen:** `ridged` `sharp` 2,4 → 1,3, Zacken-Amplitude × 0,5. Dazu weiche Terrassen (Höhe auf Banddicke stufen, Kante geglättet). Schnee nur auf Flächen < 35° Neigung, dann gibt es keine weißen Zickzack-Streifen. Das Randgebirge wird so zu „Mega-Tafelbergen“ derselben Familie.
6. **Bänder** nach (a): mindestens 8 Studs, keine 4er-Streifen mehr. Das löst das Aliasing.
7. **Ballon-Haine:** Bäume stehen auf leichten Hügeln (Terrain +1–2), Hain mit Leitbaum + 2–3 jungen Bäumen (gibt es schon), Wiese darunter nach (a4).
8. **Mittlere Größe einführen:** 3–8 Brocken-Gruppen pro Deko-Insel (2–8 Studs, aus Schutt-Material). Dafür Kiesel auf freier Fläche um ca. 40 % reduzieren.
9. **Planetengefühl am Horizont (optional):** In den Hauptblickachsen (S1–S6) das Randgebirge um 20–30 % niedriger, damit hinter einer weichen Staublinie der dunkle Himmel beginnt. Dort sieht man schwebende Felsen vor Saturn. Der Rand wirkt dann wie ein Planetenhorizont und weniger wie ein Kessel.

### (e) Eigene MaterialVariants: lohnt sich das?
**Ja, als 2. Stufe**, wenn nach (a)–(d) und der Kalibrierung der Boden immer noch zu körnig oder dunkel ist oder die Bänder wie Flicken wirken. Erzeugt mit Python (numpy + PIL, kachelbar, 1024²), vom Nutzer einmal hochgeladen wie die Skybox, eingetragen in `MaterialService`.

| Variante | BaseMaterial | Look | StudsPerTile | Karten |
|---|---|---|---|---|
| `PlanetSoil` | Ground | fast weiß (Graustufe 0,85–1,0), große weiche Flecken, feine Körnung nur ±3 %, leichte Windrippeln | 40 | Color, Normal (schwach 0,15), Roughness 0,9 |
| `PlanetStrata` (1 Bildsatz für 4 Varianten) | Sandstone, Limestone, Slate, Mud | weiche horizontale Laminierung + **flache Voronoi-Facetten** (Low-Poly-Look wie im Referenzbild) | 28 | Color, Normal (Facetten 0,5), Roughness 0,85 |
| `PlanetScree` | Rock | rundliche Geröll-Zellen, mittelgrob | 12 | Color, Normal, Roughness |
| `PlanetSand` | Sand | Rippeln, sehr ruhig | 16 | Color, Normal |
| `FloraMatt` (für Teile) | Plastic | weißer Grund, sanfter Verlauf ±4 %, keine Struktur | 8 | Color, Roughness 0,85 |

- **Wirkung:** Fels, Schutt und Boden sprechen dieselbe „Pinselsprache“, und nur die Farbe unterscheidet die Bänder. Das ist der stärkste Einheits-Hebel, den Roblox ohne Meshes bietet. Kiesel und Brocken mit `MaterialVariant = "PlanetStrata"` sehen aus wie abgebrochene Stücke der Wand.
- **Aufwand:** ca. 12 Bilder hochladen (Strata teilt sich einen Satz). Generator: neues Modul `textures.py`. Builder: MaterialVariants anlegen und `MaterialService:SetBaseMaterialOverride` setzen.
- **Zu prüfen:** ob die Terrain-Farbe (`SetMaterialColor`) die ColorMap wirklich einfärbt (deshalb Graustufen-ColorMaps). Ob `TerrainDetail` (Oberseite/Seite) für `PlanetSoil` nötig ist (Seite = Strata-Look an Hängen). Ob die Normal-Map-Ausrichtung stimmt (Y+). `MaterialPattern` (Regular/Organic) gegen Kachel-Muster testen.
- **Nicht lohnend:** eigene Varianten für Kristalle, Wasser und Lava (eingebaut reicht).

### (f) Was man nur in Studio beurteilen kann, und wie
1. **Skybox zuerst hochladen.** Ohne sie stimmen Umgebungslicht, Spiegelungen und Dunst nicht. Den jetzigen Screenshot nicht für Lichtentscheidungen nutzen.
2. `MaterialService.Use2022Materials` prüfen (muss **an** sein). Davon hängt ab, welche Texturen wir überhaupt sehen.
3. **Farbtafel-Skript** (kleines Test-Skript, abseits der Insel, z. B. bei x = 3 000): Pro Terrain-Material eine 32 × 32-Fläche flach, eine 45°-Rampe, eine Wand zur Sonne und eine im Schatten, mit den neuen Farben. Pro Deko-Art je 3 Material-Kandidaten nebeneinander. Screenshot von fester Kamera, Farben mit Pipette messen.
   **Ziele:** Boden beleuchtet L 0,66–0,74. Fels beleuchtet L 0,72–0,82. **Abstand Boden ↔ Fels ≤ 0,10.** Schatten L ≥ 0,45 und mauve, nicht grau. Kronen L 0,55–0,70.
4. **Graustufen-Test:** `ColorCorrection.Saturation = -1` kurz einschalten. Bestanden, wenn drei klare Helligkeitsgruppen entstehen: dunkel (Stämme, Basalt, Schatten), mittel (Boden, Kronen, Schutt), hell (beleuchteter Fels, Sand, Salz). Fällt der Boden in „dunkel“, ist D1 nicht gelöst.
5. **Sonnenwinkel vergleichen:** `ClockTime` vorübergehend so stellen, dass die Sonne bei 22°, 30° und 38° steht, und je denselben Screenshot machen. Erst danach die Skybox neu rendern.
6. **Abstände:** Bei 10 / 50 / 200 / 800 / 1 500 Studs auf Kachel-Wiederholung, Band-Aliasing und Dunststärke achten. Sterne im Zenit müssen sichtbar bleiben.
7. **Plastik-Test:** Mit der Kamera auf 6 Studs an einen Baum, einen Pilz und einen Kristall heran. Glanz da? Ist die Textur zu grob?
8. **Grafikqualität 3 und 10 + Handy-Emulator:** Bei niedriger Qualität vereinfacht Roblox Texturen. Ist `Terrain.Decoration` sichtbar und flüssig? MicroProfiler für die Kosten.
9. **Vorher/Nachher:** dieselben Kamerapunkte wie in den Vorschau-Bildern (`spawn_040`, `grove_a`, `mesa_close`, `ring_d_ridge`, `hero`) als Screenshots nach `bilder/screenshots/` legen. Nur echte Roblox-Bilder entscheiden.

### Reihenfolge (Vorschlag)
1. **Stufe 1, nur Daten** (`materials.py` Palette und Bänder, `lighting.py`, `catalog.py` Materialien, Farben, Formen ohne Ellipsoid, `sky.py` Sonne 30°): einspielen, Farbtafel, kalibrieren.
2. **Stufe 2, Formen** (`landforms.py` Halden, Rinnen, Randgebirge; `placement.py` Kiesel nach Fels, Windfahnen, Bodenflecken, Moos als Terrain, Decoration).
3. **Stufe 3, MaterialVariants** (`textures.py` + Builder), nur wenn Stufe 1–2 noch nicht reicht.

## Offene Fragen (für Jos/Ju)
- Sonne von 22° auf **30°** anheben (ändert „ewige goldene Stunde“ leicht, Schatten etwas kürzer)? Das muss vor dem Skybox-Upload entschieden werden.
- **Mint und Weiß raus aus den Felsbändern** (nur noch Rosé, Korall, Butter, Lavendel-Rosé)?
- Baumkronen: eher **Filz/matt** (näher am Referenzbild) oder **Laub** (`LeafyGrass`, realistischer)? Entscheidung nach der Farbtafel.
- Ring E wärmer (Lavendel-Rosé statt Blau-Lila)? Das schwächt das „Warm → Kalt“ etwas ab, hilft aber der Einheit. Kalt bleiben Eis, Schnee und Titan-Kristalle.
- Sind wir bereit, ca. 12 Textur-Bilder hochzuladen (Stufe 3)?

## Quellen (Recherche 12.11.2026; create.roblox.com und devforum.roblox.com waren in dieser Sitzung nicht direkt abrufbar, Angaben aus Suchergebnissen)
- SpecialMesh ignoriert Material: [DevForum: Materials do not work for FileMeshes and SpecialMeshes](https://devforum.roblox.com/t/materials-do-not-work-for-filemeshes-and-specialmeshes/29651), [DevForum: Why file meshes do not follow the material](https://devforum.roblox.com/t/why-file-meshes-do-not-follow-the-material-choice-in-terms-of-texture/849812), [API SpecialMesh](https://developer.roblox.com/api-reference/class/SpecialMesh)
- MaterialVariant / TerrainDetail (StudsPerTile, BaseMaterial muss Terrain-Material sein, max. 3 TerrainDetails je Fläche): [MaterialVariant](https://create.roblox.com/docs/reference/engine/classes/MaterialVariant), [TerrainDetail](https://create.roblox.com/docs/reference/engine/classes/TerrainDetail.md), [Materials-Guide](https://create.roblox.com/docs/parts/materials), [DevForum: Buttes mit MaterialVariant und TerrainDetails](https://devforum.roblox.com/t/creating-buttes-in-roblox-studio-using-materialvariant-and-terraindetails/2840180), [DevForum: Low-Poly-Terrain](https://devforum.roblox.com/t/is-there-any-way-of-make-the-terrain-look-low-poly/2494071)
- 2022-Materialien (realistisch, PBR, `Use2022Materials`): [DevForum: Upgraded Materials, Material Manager](https://devforum.roblox.com/t/upgraded-materials-material-manager-and-more/1786221), [DevForum: New Terrain and Parts Built-In Materials](https://devforum.roblox.com/t/new-terrain-and-parts-and-built-in-materials-oh-my/932576)
- Licht (`EnvironmentDiffuseScale`/`SpecularScale`, `OutdoorAmbient`): [Lighting-Doku](https://create.roblox.com/docs/environment/lighting.md), [Enhance outdoor environments](https://create.roblox.com/docs/en-us/tutorials/use-case-tutorials/lighting/enhance-outdoor-environments), [DevForum: Low-Poly Lighting](https://devforum.roblox.com/t/low-poly-lighting/431891)
- Atmosphere (Density, Offset, Haze/Glare, Sterne): [Atmosphere-Doku](https://create.roblox.com/docs/environment/atmosphere.md), [DevForum: Atmosphere Night Sky issue](https://devforum.roblox.com/t/atmosphere-night-sky-issue/3375132)
- Terrain-Gras (`Decoration`, nur auf Grass, Farbe = Grass-Farbe): [Terrain-Doku](https://create.roblox.com/docs/parts/terrain), [DevForum: Introducing Grass](https://devforum.roblox.com/t/introducing-grass/386129)
- SmoothPlastic-Glanz, matte Alternativen: [DevForum: Reflectance von SmoothPlastic senken](https://devforum.roblox.com/t/how-can-i-lower-the-reflectance-from-smoothplastic/2764770)
