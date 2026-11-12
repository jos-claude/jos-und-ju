# Welt-Design Insel 1 – Bauanleitung für den Welt-Bauer

- **Status:** Vorschlag (Entwurf vom Planeten-Designer, noch nicht von Jos/Ju abgestimmt)
- **Gilt für:** Insel 1 (Heimatplanet, Entscheidung 015). Referenz: `bilder/welt/heimatplanet-02-orange.jpg`
- **Plant NICHT:** Basis, Bohrer, Förderbänder, Lager-Kästen, Erz-Modelle (gibt es schon).
- **Alle Zahlen sind Startwerte.** Die Platzierung der Dinge ist verbindlich gemeint, Feinwerte (Farben, Lichtstärke) im Studio nachjustieren.

## 0. Koordinaten und Konventionen
- Basis = (0, 0). **Azimut 0° = Norden = −Z, 90° = Osten = +X**, im Uhrzeigersinn von oben. Position aus (Azimut a, Radius r): `x = r·sin(a)`, `z = −r·cos(a)`.
- Höhen `h` = Oberkante des Terrains in Studs (y). Basis-Plateau liegt bei **h = 48**. Wasser darf nie tiefer als 4 Studs sein.
- **Fest (nicht vom Seed abhängig):** Basis, Himmel, die 6 Washes (±10° Jitter), alle Landmarken-Slots (Azimut ±8°, Radius ±60), Windrichtung, Sonnenrichtung. **Vom Seed abhängig:** Noise, Deko-Platzierung, Hain-Größen, Nebenformen. So hat jede Spielerkarte denselben Aufbau, aber nie dasselbe Detail (passt zu Entscheidung 011).
- **Wind kommt aus Azimut 250°** (WSW, aus der Sonnenrichtung). Folgen: Dünenkämme quer dazu, Bäume und Nudeln neigen sich 3–6° nach 70°, Pflanzen wachsen im **Lee** (Seite Richtung 70°) dichter, Schatten fallen nach 70°.

---

## 1. Kurzfassung der Recherche

**Geologie (Vorbilder und was daraus folgt)**
- **Zhangye Danxia (China):** Seen und Flüsse lagerten im Kreide-Zeitalter eisen- und mineralreiche Sedimente ab (rote, gelbe, weiße Schichten). Plattenkollision kippte sie schräg, Frost, Wind und Wasser erodierten sie zu Kämmen, Türmen und Höhlen. → **Schräge Farbbänder auf Kämmen**, Farben kommen aus Eisenoxid/Mineralien. ([LiveScience](https://www.livescience.com/planet-earth/geology/rainbow-mountains-chinas-psychedelic-landscape-created-when-2-tectonic-plates-collided))
- **Bryce Canyon (Hoodoos):** Frostsprengung ist der Haupt-Verwitterer; weicher und harter Fels erodieren verschieden schnell, daraus entstehen Wände, Fenster, dann einzelne Hoodoos; harte Kappen schützen die Spitze; Hoodoos schrumpfen nur 0,6–1,2 m pro Jahrhundert. → **Reihenfolge Plateau → Wand/Finne → Fenster → Hoodoo**, nie wild gemischt. ([NPS](https://home.nps.gov/brca/learn/nature/hoodoos.htm))
- **Monument Valley (Mesa → Butte → Spire):** Eine Mesa ist breiter als hoch, wird sie schmaler als hoch, heißt sie Butte, danach Spitze. Harte Kappe oben, weicher Fels darunter. Am Fuß liegt **Schutt (Talus)** und der Hang ist dort flacher, weil der weiche Fels keine Steilwand hält. → Steilwand oben, **30–35°-Schutthalde unten**. ([Wikipedia Butte](https://en.wikipedia.org/wiki/Butte))
- **Wüstenformen (Schwemmfächer, Playa, Dünen):** Ein Fluss, der aus einer Schlucht tritt, verliert Tempo und lässt erst Brocken, dann Kies, Sand, Schlamm fallen → **Fächer** mit gröbstem Material am Schluchtausgang; Fächer verschmelzen zur Bajada; in abflusslosen Becken verdunstet Wasser zur **Salzpfanne (Playa)**; Wind baut Dünen am Fächerfuß. ([LibreTexts](https://geo.libretexts.org/Courses/Fullerton_College/Introduction_to_Geology/13%3A_Deserts/13.04%3A_Desert_Landforms))
- **Pamukkale (Sinterterrassen):** Kalkreiches, 35–36 °C warmes Quellwasser gibt beim Abkühlen Kalk ab, es entstehen weiße Stufenbecken; helle Beckenböden lassen flaches Wasser türkis leuchten. → **Weiß-cremefarbene Becken-Kaskaden mit türkisem Wasser**, Quelle oben. ([IUGS](https://iugs-geoheritage.org/?p=3409))
- **Geringe Schwerkraft (Mars):** Weniger Schwerkraft erlaubt höhere, schlankere Strukturen (Olympus Mons). → Wir dürfen **Hoodoos, Türme und Randgebirge überhöht und schlank** bauen, ohne unglaubwürdig zu wirken. ([astronomy.com](https://astronomy.com/science/how-did-olympus-mons-get-to-be-so-tall-is-it-because-the-gravity-on-mars-is-weaker-than-that-on-earth))

**Himmel:** Von Titan aus erschiene Saturn etwa 5 bis 5,7° groß (11× Vollmond), die Ringe fast von der Kante. Das ist nur eine Einzelquelle ([scienceblog](https://scienceblog.com/t-titan-saturn-five-degrees-fixed-sky/)). Wir **überhöhen bewusst auf 14°** (Stil, siehe Referenzbild), damit er das Himmelsmotiv wird, und kippen die Ringe auf 20° Öffnung, weil man so die Ringe sieht.

**Spieldesign (Landmarken, Sichtachsen):** Landmarken („Weenies“) orientieren und geben Ziele: erhöht stehen, kontrastierende Silhouette, eigene Farbe/Licht; eine „globale“ Landmarke ist fast überall sichtbar; Farbkonsistenz zeigt Bedeutung ([Game Developer: Taxonomy of Weenies](https://gamedeveloper.com/design/a-taxonomy-of-weenies-the-landmarks-that-define-i-ghost-of-tsushima-i-)). Ehrlicher Hinweis: Die Recherche zu No Man's Sky, Astroneer, Outer Wilds, Journey ergab keine verlässliche Einzelquelle. Die Prinzipien unten (Farbskript, Dichte-Rhythmus, Luftperspektive, Prospect-Refuge) sind **allgemeines Level-Design-Wissen**, kein Zitat aus diesen Spielen.

**Was daraus für uns folgt (Kernideen):**
1. **Kausalität:** Jede Form hat einen Grund (Schichtstapel → Erosion → Schutt → Wasser → Pflanzen). Der Bauer platziert Dinge nach Regeln (Abschnitt 5.1), nicht nach Zufallsstreuung.
2. **Eine Farbe pro Material** zwingt uns zu einer klaren Palette (Abschnitt 4).
3. **Warm → Kalt:** Die Farbstimmung wandert nach außen von Korall über Terrakotta, Schwarz/Sand, Pastell-Regenbogen zu kühlem Silber-Lila. Man merkt „ich komme weiter hinaus“.
4. **Dichte-Inseln statt Teppich:** 85 % der Deko-Teile stehen in ca. 40 Inseln, dazwischen ruhige Fläche (Abschnitt 5.3).

---

## 2. Großaufbau der Karte

### 2.1 Profil in einem Satz
Flache Basis-Plattform (h 48) in einer sanften **Schüssel**: nach außen fällt das Land leicht ab (Ring D als tiefes „Postkartenbecken“ bei h 18–30), steigt dann zum Silberhochland (h 60–90) und zum **Randgebirge** (Kamm h 250–360) an. Von der Basis aus blickt man über niedrigeres Land weit hinaus, Landmarken ragen aus dem Dunst.

### 2.2 Ringe (passend zu den Erz-Ringen)
| Ring | Radius (Studs) | Name | Grundhöhe h | Charakter | Farbwelt |
|---|---|---|---|---|---|
| A | 0–250 | Pfirsichebene (Basis) | Plateau 48 (r 0–180 eben ±0,5), Rampe bis r 250 auf 42 | freundlich, kleinteilig, dichteste Deko, wenig Hindernisse | Korall, Pastell-Mesas, Türkis/Limette |
| B | 250–600 | Terrakotta-Mesaland (Kupfer) | 38 ±4, Washes 30 | Monument-Valley-Gefühl: Mesas, Buttes, Hoodoo-Wald, Schwemmfächer | Terrakotta, Rosa, Kupfer-Türkis-Patina |
| C | 600–1100 | Asche & Dünen (Kohle) | Basalt 46–54, Dünenland 40 + Dünen | **zweigeteilt:** Nord/Ost (Az 300°–120°) Basalt- und Lavafelder, Süd/West (Az 140°–290°) Dünen + „Wave“-Sandstein | Schwarz-Violett, Glutrisse, Sandgelb |
| D | 1100–1600 | Regenbogenland (Kristall) | Becken 18–30, Kämme +80…+260 | **Höhepunkt:** Danxia-Kämme, Sinterterrassen, Salzpfannen, Kristallgärten, Kristalltunnel | volles Pastell, Neon-Kristalle |
| E | 1600–2000 | Silberhochland & Rand (Titan) | 60 → 90 (r 1880), Randgebirge 250–360 ab r 1900 | kühl, ruhig, weit, Nebelbecken, schwebende Felsen jenseits der Kante | Schiefer-Silber, Lavendel, Eisblau |

Übergänge zwischen Ringen: **120–200 Studs breit, mit Noise verwischt** (kein sichtbarer Kreis). Ring-Grenze mit Domain-Warping (Versatz ±80 Studs, Wellenlänge 250).

### 2.3 Sechs Washes (Hauptkorridore, ersetzen „Straßen“)
Washes sind **trockene Flussbetten** (Geologie: Wasser aus den Bergen fließt in Rinnen nach außen und innen). Sie leiten das Auge radial und geben dem Rover freie Fahrt, ohne dass wir Straßen bauen.
- Azimute: **40°, 100°, 160°, 220°, 280°, 340°** (alle ±10°), Breite 100 Studs (Ring A) wachsend auf 160 (Ring D/E), Mäander seitlich ±15° mit Wellenlänge 500.
- Boden: Sand (#F6CF96), Neigung ≤ 4°, 2–4 Studs tiefer als Umland, Ränder weich (Neigung ≤ 15°), kleine Kies-Streifen.
- Zwischen den Washes liegen **60°-Keile** mit Mesas, Dünen, Hainen. Auch die Keile haben ≥ 60 % Bauzone (siehe 2.6).
- **Keine Sackgassen:** jeder Wash geht bis r 1850 durch; Nebenschluchten sind kurz (< 150) und enden in einer **Oase oder Geode-Mulde**, nicht in einer Wand.

### 2.4 Landmarken (Slots, Seed ändert nur Details)
| ID | Name | Azimut | Radius | Höhe h (Spitze) | Beschreibung |
|---|---|---|---|---|---|
| L0 | Aussichtsfels „Abendbank“ | 250° | 230 | 62 | flacher Fels, Rampe, 360°-Blick, Sonne tief |
| L1 | **Saturn-Tor** | 28° und 52° | 300 / 330 | 130 / 105 | zwei geschichtete Mesas (Ø 120 und 95), Lücke 90 Studs; Saturn schwebt darüber |
| L2 | Zwillingstürme | 140° | 560 | 150 / 120 | zwei schlanke Buttes (Ø 34, 28), 40 Studs Abstand |
| L3 | Nadelgarten (Hoodoo-Wald) | 295° | 400–600 | 20–90 | Abschnitt 3.2 |
| L4 | Der Bogen | 200° | 820 | 70 | Felsbogen im Dünenland, Spannweite 60, Lichte Höhe 38 |
| L5 | Vulkanzwerg „Rauchfang“ | 20° | 900 | 170 | Kegel, flacher Krater Ø 110, Dampf, Lavazungen |
| L6 | Regenbogen-Kamm | 105° | 1250–1450 | 220 | Hauptkamm Danxia, Länge 420 |
| L7 | Terrassen-Hang „Silberstufen“ | 255° | 1230 | – | 14 Becken, Gegenlicht zur Sonne |
| L8 | Kristallkathedrale | 195° | 1420 | 130 | Großkristall-Gruppe (Neon, Lichtstrahl) |
| L9 | Titan-Spiegelturm | 15° | 1760 | 320 | silberne Felsnadel, Eisblau-Adern |
| L10 | Balkone (4×) | 45°, 150°, 245°, 330° | 1960 | – | Aussichtsplattformen am Rand |

**Sichtachsen von der Basis aus:**
- **S1 Az 40° (Hauptachse, Spawn-Blick):** Basis → Saturn-Tor (r 310) → Rauchfang L5 (r 900, 7,8° hoch) → Saturn darüber (Az 40°, El 28°).
- S2 Az 105°: Regenbogen-Kamm L6 am Horizont (7° hoch, buntes Band).
- S3 Az 140°: Zwillingstürme L2 (Orientierung „Mitte“).
- S4 Az 195°–200°: Bogen L4, dahinter Kristallkathedrale L8 (Neon-Licht).
- S5 Az 250°: Abendbank L0, Sonnenglitzer auf den Terrassen L7.
- S6 Az 295°: Nadelgarten L3 im Gegenlicht (Randlicht an den Spitzen).
- Alle Achsen: **freier Blick**: nichts Höheres als 25 Studs auf den Wash-Mittellinien in den ersten 250 Studs.

### 2.5 Höhenprofil in Studs (Orientierungswerte)
| r | 0–180 | 250 | 500 | 800 | 1100 | 1350 | 1600 | 1800 | 1880 | 1900–2000 |
|---|---|---|---|---|---|---|---|---|---|---|
| Boden h | 48 | 42 | 38 | 46 | 28 | 22 | 55 | 78 | 90 | Kamm 250–360 |
Basis-Rauschen (Heightmap): Oktave 1 Wellenlänge 300 / Amplitude 6, O2 80/2,5, O3 24/1, O4 8/0,4. Ring A: Amplitude × 0,4 (ruhiger), Ring D-Becken: × 0,6.

### 2.6 Bauzonen und Hindernisse (wichtig für Erz, Bohrer, Rover)
- **Bauzone** = Neigung ≤ 6° (≈ 10 %), keine Hindernis-Deko, kein Wasser tiefer als 0,5. **Jeder Ring muss ≥ 60 % Bauzone haben**, in zusammenhängenden Flecken ≥ 40 × 40 Studs, die über Neigung ≤ 25° mit der Basis verbunden sind (Flood-Fill-Test beim Generieren).
- **Hindernis-Deko** (Bäume, Felsen, Kristall, Hoodoos) nur in **Deko-Zonen** (≤ 40 % der Fläche). In Bauzonen nur kniehohe Dinge (Moos, Gras, Nudeln ≤ 8 Studs hoch, Kiesel).
- **Gassen** zwischen Hindernissen ≥ 40 Studs (Rover ≈ 10 breit, Wende 20). Keine Labyrinthe, Täler offen an beiden Enden.
- **Spawn-Schutz:** Erz-Vorkommen spawnen nur auf Bauzone; um den Spawnpunkt (Radius 12) wird Deko entfernt oder nicht gebaut (Deko darf erst nach der Erz-Verteilung gebaut oder wieder entfernt werden).
- **Neigungslimits:** begehbar/befahrbar ≤ 30° (Wände nur als Zierde, nie als Weg), Rampen 8–20°.
- **Keine Löcher:** alle Mulden, Krater, Geoden haben Innenneigung ≤ 25° und flachen Boden; Wasser ≤ 4 Studs mit Uferneigung ≤ 14° (man kommt immer raus).

### 2.7 Rand des Planeten (Vorschlag: Kombination)
Beste Wirkung, wenn **keine Kante sichtbar ist, bis man sie sucht**:
1. **Randgebirge-Kranz:** Kamm bei r 1900–2000 (Breite 80–140), Höhe 250–360 (Mittel 300), Zacken im Abstand 90–180, Sättel 60–100 tiefer. Schichtfelsen wie im Land, oberhalb h 280 **Snow** (#F2F6FF) als Kappen. Aus dem Inneren wirkt das wie ein riesiger Kraterrand-Gebirgskranz (Silhouette ca. 5–8° hoch von der Basis).
2. **Vier Balkone** (Az 45°, 150°, 245°, 330°, r 1960) sind Lücken im Kamm: flache Felsplattform 60×40 mit Brüstung aus Fels (Höhe 4) und **unsichtbarer Wand** (r 2005, Höhe bis 700). Von dort blickt man in den Weltraum. Zugang über Wash-Rampe ≤ 15°.
3. **Abbruchkante nach außen:** Steilwand 60–80° von h 300 bis ins Nichts. **Unterseite der Plattform** als umgekehrter Fels-Kegel: 8 gestapelte Terrain-Zylinder-Scheiben, Radius 2040 → 1700 → 1300 → 900 → 520 → 240 → 100 (je 60–120 dick), unregelmäßig „angebissen“ (Luft-Kugeln Ø 40–120), Material Basalt/Rock (#3C3150 / #5B4A73), darunter 40 hängende Neon-Kristalle (Teile).
4. **Schwebende Felsen** jenseits der Kante (r 2060–2700, h −150…+280): 60 Stück Ø 20–140 aus Terrain (Kegel nach unten, Gras/Moos oben, 3–5 Kristalle als Teile); 5 Gruppen („Archipele“) und 2 große **Schwebinseln** Ø 300 (Az 60°, r 2400, h 200 und Az 300°, r 2300, h 120) als Fernlandmarken, **unerreichbar**, mit kleinem Hain (max. 120 Teile je).
5. **Wolken/Dunst unter der Plattform:** 12 flache Kugeln (weiß-violett #D8C8F0, Transparenz 0,75, Material SmoothPlastic, Ø 300–700) bei h −300…−500 und starker Dunst im Atmosphere (Abschnitt 6).
- **Keine echte Krümmung nach unten** (Heightmap und Streaming würden leiden). Die „Planetenhaftigkeit“ entsteht durch Kranz, Kegel-Unterseite und schwebende Felsen.

---

## 3. Landschaftsformen

### 3.1 Tafelberge / Schichtfelsen (Mesas, Buttes)
| Ring | Anzahl | Grundfläche (Ø, Achsenverh. 1–1,8) | Höhe über Umland |
|---|---|---|---|
| A | 6 | 50–110 | 20–60 |
| B | 28 | 50–220 | 40–140 |
| C | 14 (nur Sektor Dünen/Basalt-Rand) | 60–180 | 30–110 |
| D | 22 (zusätzlich zu den Kämmen) | 60–200 | 50–150 |
| E | 10 | 60–160 | 40–120 |
- **Form-Regeln:** 3–7 sichtbare Stufen (Stufenhöhe = 1–2 Schichtbänder), Kanten als **Achteck/Polygon** mit leicht gerundeten Ecken (wie im Referenzbild), jede Stufe 4–14 Studs nach innen versetzt (Terrasse), Oberseite leicht gewölbt (Dach), **Wand 75–85° steil** (6–10 Studs horizontal auf 40 vertikal).
- **Schutthalde (Talus) am Fuß:** Neigung 28–35°, Länge 0,5–0,7 × Wandhöhe, Material **Mud** (#D9795F), darauf 8–20 Kiesel-Teile je Mesa in der Farbe des Bandes darüber.
- **Erosionsrinnen:** senkrechte Furchen alle 18–30 Studs in der Wand, Tiefe 3–8, Breite 8–12, oben breiter (Trichter), unten Schwemm-Fächer klein (Ø 30).
- **Mesa → Butte → Spitze:** Verhältnis Breite/Höhe je Mesa so wählen: Mesa > 1,0, Butte 0,5–1,0, Spitze < 0,3. In jeder Gruppe alle drei Stadien mischen (z. B. 1 große Mesa, 2 Buttes, 1 Spitze).
- **Gruppen:** 2–5 Berge, Abstand 40–120, jede Gruppe hat **eine Leitform** (größter) und zwei Begleiter (Rhythmus 1–2–1), Basis-Schnitt der Gruppe unregelmäßig (kein Kreis).
- **Material/Farbe:** Schichtband-Stapel (Abschnitt 4.2), **global über absolute Höhe**: dieselbe Mesa zeigt je nach Grundhöhe andere Bänder (geologisch richtig, gibt Abwechslung).

### 3.2 Hoodoos, Finnen, Felsnadeln (Ring B Hauptgebiet, einzeln auch C–E)
- **Nadelgarten L3** (Az 295°, r 400–600): **6 Gruppen** à 9–22 Hoodoos, Gruppen-Ø 60–120, Abstand zwischen Gruppen 120–250, zwischen Hoodoos 18–35 (Rover fährt durch). Gesamt ca. 110 Hoodoos.
- **Hoodoo-Aufbau (Terrain-Zusatzformen, alle aus Zylinder):** 3–5 Segmente: Fuß Ø 14–20 (Höhe 8–14, nach unten verbreitert), Hals Ø 5–9, Mittelwulst Ø 9–13 (Höhe 6–10), optional zweiter Hals Ø 4–7, **Hut** Ø 10–16 (Höhe 3–5, breiter als Hals = Überhang, deshalb Zylinder statt Heightmap). Gesamthöhe 20–70, einzelne 90 (Schlankheitsverhältnis Höhe : Fußbreite bis 5 : 1, wegen geringer Schwerkraft erlaubt). **Hut-Gestein = gelbes Limestone-Band** (harte Kappe), Hals rosa/lila (weich).
- **Finnen und Fenster:** vor jeder Gruppe 2–3 Felswände (Dicke 6–10, Länge 40–120, Höhe 20–55) mit 1–2 **Fenstern** (Luft-Quader 8 × 12 durch die Wand). 12 Finnen gesamt. Erosionsreihenfolge Plateau → Finne → Fenster → Hoodoo gruppenweise sichtbar machen (die Gruppe am Rand des Mesa-Plateaus beginnt mit Wänden).
- **Felsnadeln (Spires) einzeln:** 40 Stück in Ring B–E, Höhe 30–110, Basis Ø 8–20, Spitze Ø 3–6, Material Schichtbänder.
- **Fuß:** Schuttkranz Ø 1,6 × Fußbreite, Kies, 3–6 Kiesel-Teile.

### 3.3 Canyons, Washes, „Wave“
- **6 Hauptwashes** siehe 2.3. **Nebencanyons (Slots):** 12 Stück, Länge 120–300, Boden-Breite 40–60, Wandhöhe 30–80 (oben breiter, kein V), Sohle Neigung ≤ 6°, Boden Sand, beide Enden offen oder Ende in Oase/Geode.
- **Schwemmfächer:** 8 Stück (Ring B–D) an jedem Wash-Ausgang aus Mesa-Gruppen/Kämmen. Radius 80–220, Öffnungswinkel 70–110°, Neigung 1,5–4°, Sand (#F6CF96) innen, Ground außen, **grobe Brocken (Kiesel-Teile) nahe der Spitze**, **Flechtrinnen** (Breite 8, Tiefe 2, 3–6 pro Fächer).
- **„The Wave“ (Ring C, Az 200°–225°, r 700–860):** geschwungene Sandstein-Rippen, Höhe 8–25, Wellenlänge 40–90, S-förmige Kämme, die Schichtbänder folgen den Höhenlinien (dünne Bänder 3–6 Studs Rosa/Gelb/Lila). Zwischen den Rippen 30–50 breite Sand-Mulden (Bauzone). Rover fährt längs der Rippen.
- **Tafoni/Waben-Wände:** an 8 Steilwänden in Ring C: 6–14 Luft-Kugeln Ø 2–5 (Tiefe 3), Clustern in einer Höhenzone, Material Sandstone-Band.

### 3.4 Becken, Seen, Sinterterrassen, Quellen
- **Spiegelteich** (Az 215°, r 210, Ring A): Ø 56, Tiefe 3, Ufer Neigung 10°, Rand Moos und Schilf, 8–10 Ballon-Bäume im Lee (Richtung 70°).
- **Quellwäldchen** (Az 190°, r 380, Ring B): Ø 50 Teich, Tiefe 2,5, eine Dampfquelle, Hain Ø 140.
- **Sinterterrassen (3 Hänge):**
  - T1 L7 (Az 255°, r 1230): Hang 160 breit × 220 lang, **14 Becken**.
  - T2 (Az 95°, r 1480): 6 Becken. T3 (Az 330°, r 1350): 9 Becken.
  - **Regeln:** Hang 8–12°, Becken elliptisch (breiter quer zum Hang), Radius 10–40, Stufe 2–3,5 Studs, Rand-Wall 1,5 Studs (**Terrain Salt, #F4F1EA**), Wasser 1,5–2,5 tief (Wasserfarbe 4.4), Quelle oben (Dampfquelle), Becken gestaffelt in 3–4 Reihen, einzelne **Überlauf-Kerben** 6 Studs breit. Becken sind begehbar (flach, Rand darf überstiegen werden).
- **Salzpfannen (Playa):** 5 Stück (Ring C: 1 bei Az 150°/r 950, Ring D: 4 bei Az 170°–210°, r 1300–1450). Ø 140–420, tiefste Stelle der Umgebung, Boden **Salt (#FCEFEA)**, Rand konzentrisch Salt → Limestone gelb → Sand (je 20 Studs), **Flachwasser** (Water, Tiefe 0,5–1) auf 30 % der Fläche als **Spiegelflecken**.
- **Geode-Mulden (Ring D):** 7 Stück, Ø 40–90, Tiefe 10–14 (konkav, Innenneigung ≤ 20°), Boden Salt/Concrete-Mint, dichte Kristallcluster am Rand.

### 3.5 Krater, Vulkan, Lavafelder (Ring C Nord/Ost)
- **Einschlagkrater:** 9 Stück (Ring B–E), Ø 60–260, Tiefe 0,10 × Ø (max 26), Rand-Wall Höhe 0,04 × Ø, Innen-/Außenhang ≤ 25°, flacher Boden (Bauzone), 2 davon mit Teich.
- **Vulkanzwerg „Rauchfang“ L5** (Az 20°, r 900): Kegel Ø 400 am Fuß, 170 hoch, Hang 22–30° (befahrbar, Serpentine Rampen), **Krater Ø 110, Tiefe 18, flacher Boden mit CrackedLava (nur Optik, kein Schaden)**, Rand mit Dampfquellen (3), Zugang über Westrampe.
- **Lavafelder:** insgesamt ca. 35 % der Fläche von Ring C-Nordost. Aufbau: **Basaltsäulen-Zellen** (Voronoi, Zellradius 6–10, Höhenversatz 0–3 Studs, Material Basalt), dazwischen **Lavazungen** (Breite 20–50, Länge 150–500, aus Spalten/Kegel), Oberfläche Basalt (#3B3245), **CrackedLava nur in Rissen** (Rissbreite 2–3, Netz aus Voronoi-Kanten, 25–30 % der Zungenfläche). Dazwischen Asche-Ebenen (Basalt/Ground-Mix, Bauzone) und **Oasen** (Ø 100–160, Moos, Pilze, Laternenblumen).
- **Kleinvulkane:** 6 kleine Kegel (Höhe 20–45, Ø 60–110) in den Lavafeldern, Dampfquelle auf der Spitze.

### 3.6 Dünen (Ring C Süd/West)
- Kämme **quer zum Wind (Wind 250° → Kämme verlaufen ungefähr Nord–Süd, Azimut 340°/160°)**, Höhe 6–22, Wellenlänge 70–140, Luvseite (Richtung 250°) 8–12° lang und sanft, Leeseite (Richtung 70°) 28–32° steil mit scharfem Grat, Kämme gebogen (Sichel/Barchan-Ende, Spannweite 60–140). Rippeln: Wellenlänge 12, Amplitude 1 (Heightmap-Auflösung ist 4, also nur Andeutung). Material **Sand (#F6CF96)**, Schatten-Seite (Lee) dunklere Einfärbung gibt der Boden-Noise.
- Zwischen den Dünenfeldern ebene Sand-Pfannen 60–140 Breite (Bauzone) alle 150–250.
- Dünen enden an Fächer-Füßen (Geologie: Fächer liefern den Sand).

### 3.7 Danxia-Kämme und Regenbogenland (Ring D)
- **7 Kämme** (Az 105° Haupt L6, Az 300°, Az 160°, Az 345°, Az 230°, Az 20°, Az 75°), Länge 200–500, Höhe 80–260, Basisbreite 90–200.
- **Form:** asymmetrische „Haifischflosse“: Stirnseite (Schichtköpfe) 55–70° steil, Rückseite 25°, Kammlinie gezackt (Zacken alle 30–60, Höhe 6–18), quer verlaufende **Erosionsfurchen** alle 18–30 (Tiefe 3–8).
- **Schichten:** Fallwinkel 28–40° in Richtung Kammrückseite, sichtbare Streifen 6–14 Studs breit. **Umsetzung:** pro Kamm lokal geneigte Bandfunktion (`y_eff = y + tan(dip)·u`, u = Abstand quer zum Kamm). Falls der Generator nur **global** gleiche Bänder erlaubt: globaler Fallwinkel 3° zu 70°, und die Schräge über Treppenstufen der Kammform andeuten.
- **Hauptkamm L6:** drei Gipfel (220/190/160), zwischen ihnen zwei Sättel mit Wash-Rampen; auf der Westseite (zur Sonne) Gegenlicht, Ostseite im Schatten. Am Fuß Schutthalde und Schwemmfächer nach Süd/Ost.
- **Kristalltunnel:** 4 Stück (durch Kämme, Luft-Quader B 18–24, H 12–16, Länge 40–70, beide Enden offen), innen Kristalle (leuchtend), Boden eben.
- **Kristallgärten:** 10 Stück, Ø 80–200, entlang Verwerfungslinien (Linien 60–200 lang), siehe 5.

### 3.8 Silberhochland (Ring E)
- Ebene Hochfläche (h 55–90) mit breiten Wellen (Wellenlänge 400, Amplitude 10), Boden **Slate/Rock lavendelgrau**, Schneeflecken (Snow) in Mulden, **Nebelbecken** (3 Stück, Ø 250–400, h −10 gegenüber Umland, kein Loch, Dunst-Kugeln Transparenz 0,8 weiß-lila).
- **Titan-Spiegelturm L9:** Felsnadel Ø 70 → 20 (Spitze), Höhe 320 (= 230 über Umland), Silber (#B7C2D6) mit **eisblauen Neon-Adern** (6 Streifen aus Teilen), Lichtstrahl nach oben (Neon-Strahl, Transparenz 0,85, Länge 600, 1 Stück).
- **Eisfelder/Titan-Kristalle:** Ice-Material (#BFE6F5) in 6 Flecken Ø 60–120, Titan-Kristalle: Silber-Prismen (Neon-Anteil niedrig, Farbe #C7D3E8).

---

## 4. Farb- und Materialpalette

### 4.1 Terrain-Materialien
| Material | Verwendung | Hex |
|---|---|---|
| Ground | Hauptboden Ebenen (Ring A, B) | #F2A07C (Korall-Pfirsich) |
| Sand | Washes, Dünen, Fächer, Ringe um Salzpfannen | #F6CF96 |
| Mud | Schutthalden, Sockelband, feuchte Mulden | #D9795F (Terrakotta) |
| Sandstone | Schichtband „Bonbon-Rosa“ | #F4A9C4 |
| Limestone | Schichtband „Butter-Gelb“, Hoodoo-Hüte | #F9E7A3 |
| Slate | Schichtband „Lavendel“, Silberhochland | #A99BE0 |
| Rock | Schichtband „Mauve“, Geröll, Außenwand-Kegel | #C48BBE |
| Salt | dünnes Cremeband, Sinter, Salzpfannen | #FCEFEA |
| Concrete | dünnes Mint-Band, Geode-Böden | #A9E5D2 |
| Basalt | Lava-/Aschefelder, Säulen, Kegel-Unterseite | #3B3245 |
| CrackedLava | Risse in Lavafeldern, Vulkankrater | Startwert #FFB07A, so wählen, dass die Glut orange bleibt |
| Grass | Moos-Wiesen in Hainen und Oasen | #9BE06B (Limette) |
| LeafyGrass | feuchte Mulden, Teichränder | #4FC9B0 (Türkis-Moos) |
| Snow | Gipfelkappen > h 280, Mulden Ring E | #F2F6FF |
| Ice | Eisflecken Ring E | #BFE6F5 |
| Glacier | optional: Blau-Türkis-Akzent am Rand | #A9D8E8 |
| Water | alle Becken, Teiche | siehe 4.4 |
- **Nicht benutzen:** Pavement, Asphalt, Concrete (außer Mint-Band), Cobblestone, Brick, WoodPlanks (wirken künstlich und gemustert; Cobblestone/Pavement nur wenn die Basis-Modelle sie später brauchen).
- Helle Texturen (Salt, Limestone, Sand, Sandstone) zeigen Pastell gut; dunkle Texturen (Slate, Basalt) schlucken Farbe, Slate daher recht hell wählen (#A99BE0). Im Studio mit echten Texturen gegenprüfen.

### 4.2 Schichtband-Stapel (Periode 240 Studs, global über absolute Höhe `y_eff`)
`y_eff = y − tan(3°)·(x·sin(70°) + z·(−cos(70°)))` (Fall 3° nach ONO; im Danxia-Gebiet lokal anders, siehe 3.7). Dann `y_eff mod 240`:
| von–bis | Dicke | Material | Farbe |
|---|---|---|---|
| 0–16 | 16 | Mud | #D9795F |
| 16–40 | 24 | Sandstone | #F4A9C4 |
| 40–48 | 8 | Limestone | #F9E7A3 |
| 48–72 | 24 | Slate | #A99BE0 |
| 72–76 | 4 | Salt | #FCEFEA |
| 76–104 | 28 | Sandstone | #F4A9C4 |
| 104–114 | 10 | Limestone | #F9E7A3 |
| 114–118 | 4 | Concrete | #A9E5D2 |
| 118–150 | 32 | Rock | #C48BBE |
| 150–160 | 10 | Limestone | #F9E7A3 |
| 160–190 | 30 | Slate | #A99BE0 |
| 190–196 | 6 | Salt | #FCEFEA |
| 196–224 | 28 | Sandstone | #F4A9C4 |
| 224–240 | 16 | Mud | #D9795F |
- **Dicke Rhythmus:** dicke Bänder 24–32 (Rosa, Lila, Mauve), dünne Zierbänder 4–10 (Gelb, Creme, Mint), damit auch 40 Studs hohe Mesas 3–5 Bänder haben, 140 hohe 10+.
- **Oberflächen:** Mesa-Oberseiten zeigen das Band (wie im Referenzbild); 15 % der Oberseiten haben Sand-Staubflecken, 10 % Grass-Flecken (Ring A, B).
- **Schutthalden** immer Mud oder Rock, **Kiesel-Teile in der Farbe des Bandes darüber**.

### 4.3 Boden pro Ring (Anteile der Fläche)
| Ring | Ground | Sand | Mud | Gras/Moos | Sonstiges |
|---|---|---|---|---|---|
| A | 70 % | 8 % | 2 % | 12 % (Haine) | Fels-Bänder 8 % |
| B | 50 % | 20 % (Washes, Fächer) | 10 % | 4 % | Schichtfels 16 % |
| C Nord/Ost | 15 % | 5 % | – | 3 % (Oasen) | Basalt 60 %, CrackedLava 8 %, Schichtfels 9 % |
| C Süd/West | 15 % | 60 % (Dünen) | – | 2 % | Schichtfels 20 %, Salt 3 % |
| D | 20 % | 15 % | 5 % | 8 % | Schichtfels 35 %, Salt 12 %, Wasser 5 % |
| E | 8 % (Staub) | 5 % | – | 3 % | Slate/Rock 60 %, Snow 10 %, Ice 4 %, Schichtfels 10 % |

### 4.4 Wasser
- `WaterColor` **#5FE3D6** (Türkis), `WaterTransparency` 0,35, `WaterReflectance` 0,4, `WaterWaveSize` 0,1, `WaterWaveSpeed` 6.
- Sinterbecken: Boden Salt hell, deshalb leuchtet das Wasser; Teiche (Ring A, B) Boden Mud dunkler → wirken tiefer.
- Spiegelflecken in Salzpfannen: Tiefe 0,5–1.

### 4.5 Farbskript (wer bekommt welche Aufmerksamkeit)
- **Boden = ruhig** (Korall/Sand, wenig Kontrast).
- **Wegweiser = hell/leuchtend:** Kristalle (Neon), Laternenblumen, Dampf.
- **Landmarken = höchster Kontrast** zur Umgebung (Pastell-Band vor dunklem Basalt, Neon vor Pastell).
- **Erz-Vorkommen** haben eigene Modelle in Grau/Orange/Türkis: **Deko in der Nähe nie dieselbe Farbe** wie die Erz-Modelle (grau-braune Brocken nur als Kiesel, nie als Haufen).
- Pro Ring wechselt die **Zweitfarbe**: A Türkis/Limette, B Kupfer-Türkis (#3CC8A8) + Pfirsich, C Lavaorange + Violett, D alle Pastelle + Neon, E Eisblau + Lavendel.

---

## 5. Pflanzen- und Deko-Katalog

### 5.1 Ökologie-Regeln (Warum wächst was wo?)
Drei Karten (0–1), vom Bauer aus Gelände und Wasser berechnet:
- **Feuchte F** = 0,5·Wassernähe (1 bei Ufer, 0 ab 150 Studs) + 0,3·Muldigkeit (konkav) + 0,2·Lee (Hang schaut nach 70°).
- **Mineral M** = Nähe zu Verwerfungslinien, Beckenrändern Ring D, Mesa-Füßen und Quellen (Kristalle).
- **Schatten S** = Nordseite hoher Wände und Mulden (Pilze).

| Art | Bedingung | Gruppierung | Wo sonst nie |
|---|---|---|---|
| Ballon-Baum | F > 0,45 | Hain 5–14 | Lavafeld, Dünenkamm, Bauzone (nur am Rand) |
| Nudelpflanze | F 0,15–0,5, Sand/Ground | Feld 20–60 | Gras-Zentrum |
| Moospolster | F > 0,35 | Gruppe 3–12 | trockene Dünen |
| Laternenblume | F 0,3–0,7 | Hain 5–25 | Ring E (außer Oasen) |
| Pilzschirm | F > 0,6 und S > 0,5 | Gruppe 3–9 | Sonnenhang |
| Wedelgras/Schilf | F > 0,8 (Ufer) | Saum | weit vom Wasser |
| Orgelrohr | F < 0,3, Wash-Rand | Gruppe 4–9 | Hain |
| Perlenkaktus | F < 0,2 | einzeln/Paare | feucht |
| Kristall | M > 0,5 (Linien!) | Cluster, Garten | Ring A (nur 1–2 Mini) |
| Dampfquelle | Quelle/Sinter/Vulkan | einzeln | – |
| Fossil | Steilwand im Band Mud/Sandstone | einzeln in Wand | – |
- **Ring-Anteile:** Ring A–B Bäume dominant, Ring C nur Oasen und Orgelrohr/Perlenkaktus, Ring D alles + viel Kristall, Ring E wenige, kleine, kühle Varianten (Ballon Ø × 0,6 in Eisblau/Lavendel).
- **Neigung zum Licht:** Stämme/Stiele neigen sich 3–6° nach Azimut 70°, nicht synchron (Jitter ±4°).
- **Größenvariation:** pro Art 3 Größenklassen (klein 60–80 %, mittel 100 %, groß 130–160 %) im Verhältnis 5 : 4 : 1; Hain hat immer 1 große Leitpflanze und 1–2 Junge (Maßstab zum Spieler!).

### 5.2 Katalog (Aufbau aus einfachen Teilen)
**Allgemein:** SmoothPlastic, `CanCollide` false für alles unter 3 Studs Höhe und alles an Bauzonen-Rändern; Kollision nur an Stämmen/Felsen ab Ø 2. Teile pro Instanz ca.

1. **Ballon-Baum (10–13 Teile).**
   - 1–3 Stämme (im Schnitt 2) pro Baum, Gesamthöhe 14–60 (Hain 14–35, Leitbaum bis 60).
   - Stamm: 4 Zylinder-Segmente, Länge 4–6, Ø 1,0–2,4 (nach oben dünner, 100 % → 65 %), jedes Segment 6–14° gegen das vorige gekippt, S-Kurve, gemeinsame Wurzel (flache Kugel Ø 2,5 × Stamm-Ø).
   - Krone: 1 Kugel Ø 0,35–0,5 × Gesamthöhe (8–22), Knoten-Kugel Ø 1,6 an der Basis der Krone, Zweitballon (50–70 % der Hauptkrone) bei 40 % der Bäume.
   - Farben Krone: Türkis #3FD0D0 (35 %), Limette #A6E04A (35 %), Mint #6FE3B0 (15 %), Himmelblau #5EB8F2 (7 %), Rosa #FF9FB5 (5 %), Gelb #FFE36B (3 %). Stamm: Mauve #C97A86 oder Rosa-Braun #B8707A. Ring E: Eisblau #9AD5F0, Lavendel #B8A8F0, Silber #C7D3E8.
   - Anzahl: **ca. 520** (Ring A 90, B 160, C 40, D 190, E 40). Leuchten: nein.
2. **Nudelpflanze (7 Teile).** 2–3 Ranken, je 3 Zylinder-Segmente (Ø 0,9–1,4, Länge 2,5–4) als sich einrollende Spirale (Radius 3 → 1,2), Endkugel Ø 1,6 an einer Ranke. Höhe 4–14 (meist 5–8, kniehoch/hüfthoch). Farben Gelb #F4E27A, Türkis #5FD3C8, Mint #8FE3C0, Rosa #F7A8C8 (selten, 8 %). Leuchten nein. **ca. 420**, Felder 20–60 auf Sand/Ground in Ring A und B.
3. **Kristall-Cluster (6–10 Teile).** Prisma = Block (Breite b, Länge 3,5–6·b) + 1 Keil als Spitze; 3–5 Prismen pro Cluster, fächerförmig (Winkel 10–35° zueinander). Material **Neon**, Transparenz 0,10–0,25. Größen: klein b 0,6–1,2 (L 3–6), mittel b 1,5–3 (L 8–16), groß b 4–9 (L 30–80, nur Landmarken). Farben: Türkis #7FF3E0, Eisblau #9BD8FF, Pink-Violett #D58BFF, Magenta #FF7FD0 (10 %), Lila #A58CFF. Pro Cluster eine Farbfamilie (2 Töne). Leuchten ja. PointLight nur bei Landmarken/Gärten (max. 40 Lichter gesamt, Range 20–28, Brightness 1,0–1,4, Farbe wie Kristall). **ca. 260 Cluster + 8 Großgruppen**. Verteilung: Ring A 6 (Mini), B 20, C 25, D 160, E 49.
4. **Laternenblume (6 Teile).** 2 Stiel-Segmente (Ø 0,5, Länge 3–9, 8° Knick), Laterne = Kugel Ø 2–4 (Neon, Transparenz 0,3), 3 Kelchblätter (Keile, Länge 1,5–3, Pastell). Höhe 6–18. Farben Gelb-Orange #FFC76B, Pink #FF8FB8, Türkis #6DEBDD. Leuchtet ja; PointLight nur 1 von 8 (Range 14, Brightness 0,6). **ca. 300**, Haine 5–25 an Teichen und Oasen.
5. **Pilzschirm (5–6 Teile).** Stiel Zylinder Ø 1–3, Höhe 4–16; Hut = Ellipsoid (Kugel, Y × 0,5) Ø 3–10; Lamellen = Zylinder-Scheibe Ø 0,85 × Hut, H 0,3, hellere Farbe; 2–3 Flecken (Kugeln Ø 0,6–1,2, #FFF3D6). Hutfarben Violett #B58CF0, Rosa #FF9CC2, Pfirsich #FFB88A, Türkis #7FD8CF. Leuchtet nein. **ca. 160**.
6. **Orgelrohr-Pflanze (9 Teile).** 4–9 Zylinder-Röhren Ø 1,5–3,5, Höhe 6–28 (gestaffelt, 1 Leitröhre), Öffnung = Ring (Zylinder Ø + 0,4, Höhe 0,4, 20 % heller). Farben Koralle-Rosa #F28BA0, Gelb #F4D87A, Mint #7FE0B0. Leuchtet nein. **ca. 120** in Ring B/C an Wash-Rändern.
7. **Moospolster (2 Teile).** Flache Kugel Ø 6–30, Höhe 1,5–4 (Ellipsoid), 1 kleine Beule Ø 0,4 × Hauptteil. Farben Limette #A8E070, Mint #7FE0B0, Lila-Moos #B79BE8 (Ring D/E). **ca. 500**, Gruppen 3–12.
8. **Dampfquelle / Mini-Geysir (8 Teile).** 3 gestapelte Zylinder (Ø 10 → 7 → 4, je H 1,5), Material **Limestone/Salt creme-rosa #F4EBDD**, Wasser-Dot (Zylinder Neon #7FF3E0, H 0,3), 3–4 Randsteine; **ParticleEmitter Dampf** (Bauer), optional Puls alle 25–40 s (nur Optik, harmlos). **ca. 24**: 6 Terrassen, 3 Vulkan, 6 Oasen, 9 verstreut.
9. **Wedelgras / Schilf (6 Teile).** 6 dünne Blöcke 0,3 × 0,3 × 4–10 in 2 Segmenten, leichter Knick nach 70°. Farbe Mint #8FE3C0, Spitzen Gelb #F4E27A. **ca. 160 Büschel** am Ufer.
10. **Perlenkaktus (4 Teile).** Große Kugel Ø 3–7 + 3 kleinere (50–70 %) angedockt, 4 Perlen als Neon-Punkte (Ø 0,4, Rosa #FF9FD0, optional). Farben Mint #8FE3C0, Violett #B592F0. **ca. 200**.
11. **Schwebstein (5 Teile, plus Terrain-Zusatzform).** Terrain-Kegel (Spitze unten) Ø 20–140, oben flach mit Moos, 3–5 Kristalle als Teile (Cluster 5.2 Nr. 3 klein). **ca. 110** (60 jenseits der Kante, 50 als „Lufteinsprengsel“ niedrig über dem Boden: Ø 12–30 in Ring D/E, Höhe 20–60 über Boden, **schweben ≥ 15 über dem Boden und ≥ 25 über Wegen**).
12. **Fossil (5 Teile).** Ammoniten-Spirale: 4–5 Zylinder-Segmente (Ø 0,8, Radius 5 → 1,5) in Wand-Fläche, Farbe Creme #F1E4C8 auf Mud/Sandstone. **ca. 40**, nur in Wänden Ring B–C (erzählt die Geologie-Geschichte: „hier war einmal ein See“).
13. **Kiesel/Geröll (1 Teil).** Kugel/Keil Ø 1–4, Rock/Slate, Farbe = Band darüber (85 %), sonst Mud. **ca. 2 500**, nur an Schutthalden, Fächer-Spitzen, Wash-Rändern.
14. **Kupfer-Patina-Brocken (Deko Ring B).** Fels-Brocken (Kugel + 2 Keile) Ø 4–14 in Orange (#E58A5C) mit türkisen Flecken (#3CC8A8, 3–5 kleine Kugeln), 60 Stück in Ring B als Hinweis „hier gibt es Kupfer“ (Erzmodelle bleiben davon unberührt, Farbe etwas gedämpfter).
15. **Gras-Büschel und Blümchen (nahe Basis).** 1–2 Teile je (Dreieckskeile / kleine Kugeln, Gelb/Rosa/Weiß), **ca. 3 000** in Ring A-Inseln und Plateau-Rand (Maßstab-Detail).

### 5.3 Dichte-Rhythmus und Teile-Budget (Ziel ≈ 25 600 Teile, Reserve ≈ 4 400)
| Ring | Deko-Teile | Inseln | Teile je Insel | Fläche mit Deko-Inseln |
|---|---|---|---|---|
| A (r 0–250) | 6 000 | 6 (Ø 60–100) + Plateau-Rand-Streifen r 150–200 | ca. 800–1 000 | ≤ 20 % |
| B | 6 000 | 10 (Ø 100–180) | ca. 500–600 | ≤ 15 % |
| C | 4 500 | 8 (Oasen, Dünen-Haine, Ø 100–160) | ca. 550 | ≤ 8 % |
| D | 6 000 | 10 (Gärten, Terrassen, Ø 120–200) | ca. 600 | ≤ 8 % |
| E | 2 000 | 5 (Ø 100–160) | ca. 400 | ≤ 3 % |
| Rand-Extras (Unterseite, Balkone, Schwebinseln) | 1 100 | – | – | – |
- **Zwischen den Inseln:** 250–600 Studs ruhiges Gelände (Heightmap-Noise, Schichtfels, wenige Kiesel). Diese Ruhe-Flächen sind Absicht (Erz, Rover, Atmen).
- **Plateau (r < 150):** nur Kiesel und Gras-Büschel, **keine** Hindernisse (Platz für Bohrer, Bänder, Räume).
- Alle Deko-Inseln in **Chunk-Models** (je 200 × 200) ablegen, damit Streaming greift; PointLights insgesamt ≤ 120 (davon Kristalle ≤ 40, Laternenblumen ≤ 40, Dampf ≤ 10, Landmarken ≤ 30).
- Teile gleichen Typs: gleiche Material-/Farbvarianten sparen Speicher (max. 6 Farben pro Art).

---

## 6. Himmel und Licht

### 6.1 Sonne, Zeit
- **Ewige goldene Stunde.** Sonne bei **Azimut 250°, Elevation 22°**, Schatten fallen nach 70° (Länge = 2,5 × Höhe). Kein Tag/Nacht-Wechsel.
- Roblox: `ClockTime` ≈ 16,5 und `GeographicLatitude` 0 als Startwert; danach mit `Lighting:GetSunDirection()` prüfen, ob die Richtung Azimut 250°/Elev. 22° trifft, und im Zweifel `GeographicLatitude`/`ClockTime` anpassen. **Die Skybox-Sonne wird an die Lighting-Sonne angepasst, nicht umgekehrt.**
- Sky: `CelestialBodiesShown` = false, `StarCount` = 0 (Sterne und Sonne kommen aus der Skybox). SunRays bleiben an (sie nutzen die Lighting-Sonnenrichtung).

### 6.2 Skybox (6 Bilder à 2048², vom Bauer gerendert)
**Hintergrund:** Verlauf Zenit **#0A1B2C** (Tiefblau-Schwarz) → Horizont **#1F4F5C** (dunkles Türkis); unter dem Horizont **#2A2440** (Violett-Dunkel), weiterhin Sterne (der Raum geht unten weiter), schwacher Pfirsich-Glow (#F2A07C, Alpha 0,25, Höhe 0–6°) am Horizont zwischen Az 180° und 320°.

**Himmelskörper (Winkelgrößen sind Durchmesser):**
| Körper | Azimut | Elevation | Größe | Farben / Eigenschaften |
|---|---|---|---|---|
| **Sonne** | 250° | 22° | 2,0° Scheibe, Glühen bis 12° | Kern #FFF1D0, Rand #FFE2B0, Glow #FFB070 (Alpha 0,35) |
| **Saturn** | 40° | 28° | **Kugel 14°**, Ringe außen 31,8° breit | Bänder #D9C79B, #C9AE7A, #B89A6A, #E6D9B5, Pole #A8B5A0, Rim-Glow #FFE8C4 |
| Saturn-Ringe | wie Saturn | – | Radien relativ zur Kugel: C-Ring 1,24–1,53 (#6E6A5E, 40 % transparent), B-Ring 1,53–1,95 (#D8C9A3), **Cassini-Lücke 1,95–2,03** (#1A2530), A-Ring 2,03–2,27 (#B9AD93), Encke-Spalt bei 2,21 | **Öffnung 20°** (Ellipse Höhe = 0,34 × Breite ≈ 10,9°), **Roll −14°** (rechte Seite höher, wie im Referenzbild), Vorderseite der Ringe überlappt die Kugel |
| Saturn-Phase | – | – | 93 % beleuchtet | Sonne steht links hinter dem Betrachter: helle Seite links, **sanfter Terminator rechts**; **Ringschatten** als Band auf Südhalbkugel (Breite 0,12 R, #5B4E3E, 55 %); kleiner **Planetenschatten** auf dem rechten Ringteil (0,35 R lang) |
| Mond 1 (grau-bläulich, Krater) | 14° | 40° | 2,0° | #A9B2C0, 58 % beleuchtet, helle Seite links unten |
| Mond 2 (klein, gelblich) | 150° | 50° | 1,1° | #E8D9A8, 41 % beleuchtet (Halbmond), helle Seite rechts unten |
| Eisriese (türkis, ohne Ringe) | 300° | 14° | 3,0° | #6FD0D6 mit Rim-Glow #BFF5F0, **dünne Sichel 17 %**, beleuchtete Seite links oben |
| Sternhaufen | 335° | 42° | 6° | 150 Sterne dicht, Farben #BFE6FF/#FFE9C8 (wie links im Referenzbild) |

**Sterne:** ca. 1 500 kleine (0,04–0,08°), 150 mittlere (0,1°), 25 helle (0,2° mit Glow). Farben warm-weiß #FFF2DC (50 %), blau-weiß #CFE6FF (35 %), leicht pfirsich #FFD6B8 (15 %). Dichter im Nebelband (×1,6).

**Nebelband (Milchstraße):** ein Großkreis, der durch den Zenit läuft (von Az 300° El 0° über den Zenit nach Az 120° El 0°), Breite 20°, Kern #5A8FA8 (Alpha 0,12) mit Magenta-Zügen #9B6BB8 (Alpha 0,08), 40 dunkle Staubfäden. Der Eisriese liegt im Band, Saturn (Az 40°) liegt 80° daneben.

**Kontrolle gegen Gelände:** Das Randgebirge deckt von der Basis aus Elevation bis ca. 7° (Gipfel 300 auf r 1950). Alle Himmelskörper liegen ≥ 14° über dem Horizont. Saturn-Tor deckt maximal 15° (Ring-Unterkante Saturn bei ca. 20°, 5° freier Himmel).

### 6.3 Lighting (Startwerte)
| Eigenschaft | Wert |
|---|---|
| Brightness | 2,4 |
| Ambient | #6A5878 (Violett) |
| OutdoorAmbient | #B28C8A (Pfirsich-Mauve) |
| ColorShift_Top | #FFD9A8 |
| ColorShift_Bottom | #7A6FB0 |
| EnvironmentDiffuseScale | 0,6 |
| EnvironmentSpecularScale | 0,3 |
| ExposureCompensation | 0,2 |
| GlobalShadows | true, ShadowSoftness 0,25 |
| Technology | ShadowMap (Future nur, wenn die Performance reicht) |

### 6.4 Atmosphere (Luftperspektive)
| Eigenschaft | Wert |
|---|---|
| Density | 0,28 |
| Offset | 0,25 |
| Color | #F2B8A0 (Pfirsich-Dunst) |
| Decay | #8E6FA8 (Lila am Horizont) |
| Glare | 0,35 |
| Haze | 1,6 |
- **Ziel (messen, dann nachstellen):** bei 500 Studs ca. 15 % Dunst, bei 1 500 ca. 55 %, bei 2 000 ca. 70 %. **Zenit bleibt klar, Sterne sichtbar**, wenn nicht, Density senken. Dunst färbt ferne Berge Richtung Lila (Luftperspektive: je weiter, desto blasser, kälter, weniger Kontrast).

### 6.5 Nachbearbeitung
| Effekt | Werte |
|---|---|
| Bloom | Intensity 0,45, Size 24, Threshold 1,4 (Kristalle und Lava glühen, Boden nicht) |
| ColorCorrection | Brightness 0,02, Contrast 0,12, Saturation 0,18, TintColor #FFF1E6 |
| SunRays | Intensity 0,06, Spread 0,8 |
| DepthOfField | aus (Stil bleibt klar), optional FarIntensity 0,08 |

---

## 7. Spielgefühl

### 7.1 Die ersten 30 Sekunden an der Basis
- **0–5 s:** Spawn vor dem Basistor, Blick Richtung **Az 40°**: orangefarbene Basis, Korallboden, **Saturn mit Ringen halb rechts oben**, Mond links daneben, Sterne. Lange Schatten der Gebäude nach rechts vorne (Richtung 70°), warm und friedlich.
- **5–15 s:** Das **erste Eisenvorkommen** liegt 25–40 Studs vor der Basis auf freiem Boden (Bauzone), keine Deko im Weg. Im Vordergrund Gras-Büschel, Kiesel, eine kleine Nudelpflanze (Maßstab).
- **15–30 s:** Der Blick wandert durch das **Saturn-Tor** (zwei geschichtete Mesas), davor ein türkis-limettenfarbener **Ballon-Hain**; links schimmert ein **Mini-Kristall** (Pfeil), rechts der Spiegelteich-Hain. Weit hinten Rauchfang (Dampf) unter Saturn. Dreh nach rechts: Regenbogen-Kamm als bunter Strich; dreh nach links: Sonne tief, Hoodoo-Nadeln im Gegenlicht.

### 7.2 Wie lockt die Landschaft nach außen?
- **Leitlinien:** Schatten, Washes (heller Sand), Wash-Mäander zeigen radial nach außen.
- **Fernlicht:** Kristallkathedrale (Neon + Lichtstrahl), Dampfsäulen, Titan-Spiegelturm-Strahl sind von der Basis aus als Lichtpunkte sichtbar.
- **Staffelung:** am Rand jedes Rings sieht man schon die Landmarke des nächsten Rings (B → Bogen, C → Kamm, D → Silberturm).
- **Farbbelohnung:** Jeder Ring hat eine neue Farbtemperatur und eine neue Pflanze; kein Ring wiederholt den vorigen.

### 7.3 Postkartenmotiv je Ring
| Ring | Motiv |
|---|---|
| A | Basis vor dem Saturn-Tor, Ballon-Hain im Vordergrund, Saturn mit Ringen |
| B | Nadelgarten im Gegenlicht (Randlicht an den Hoodoo-Spitzen, lange Schatten) |
| C | Rauchfang mit glühenden Lavazungen unter der linken Ringkante des Saturn; im Süden der Bogen im Dünenmeer |
| D | Silberstufen (Terrassen) mit türkisem Wasser und Spiegelung der Eisriesen-Sichel, dahinter der Regenbogen-Kamm |
| E | Aussichtsbalkon Az 45°: Blick in den Weltraum, Saturn riesig, schwebende Felsen vor den Ringen |

---

## 8. Do & Don't für den Welt-Bauer

**Do**
1. **Nach Regeln platzieren, nicht streuen:** erst Gelände (Schichten, Erosion, Schutt, Wasser), dann Feuchte-/Mineral-/Schattenkarten, dann Pflanzen (5.1).
2. **Zwei Masken:** Bauzone (frei) und Deko-Zone (Hindernisse). Hindernisse nie in Bauzonen, nie auf Erz-Spawn.
3. **Dichte-Inseln und Ruhe:** 85 % der Teile in ca. 40 Inseln, dazwischen leer lassen.
4. **Maßstab zeigen:** in jeder Insel ein großes Leitelement, daneben kleine Dinge (Spieler ist 5 Studs groß, Mesas 40–140, Randgebirge 300).
5. **Silhouetten klar halten:** große Formen aus wenigen, großen Elementen (Dreiklang 1–2–1), Details nahe am Spieler.
6. **Schichten weich und unregelmäßig** (Noise auf der Bandgrenze ±1,5 Studs), nicht wie Lineal-Streifen.
7. **Luftperspektive nutzen:** ferne Berge blasser, bläulicher; Landmarken vor einem Helligkeitssprung stellen.
8. **Lichter sparen:** max. 120 PointLights; Neon-Leuchten ohne Licht reichen für Bloom.
9. **Alles testen mit Flood-Fill:** Bauzonen erreichbar? Gassen ≥ 40? Keine Löcher? Wasser ≤ 4?
10. **Seed-Variation:** Details würfeln, Slots (Landmarken, Washes) fest.

**Don't**
1. **Keine gleichmäßige Streuung** (Zufall pro Quadrat). Das wirkt wie Teppichboden. Cluster, Linien, Leere.
2. **Keine Raster- oder Kreisformen** (Berge, Becken, Ringe sind nie perfekte Kreise, Achsen verzerren 1–1,8).
3. **Nicht alles gleich groß.** Kein Tafelberg sieht wie der andere aus, jeder hat eigene Stufenzahl und Schutthalde.
4. **Keine weiße Neon-Überstrahlung:** Neon nur bei Kristallen, Laternen, Lava; Threshold 1,4 halten.
5. **Keine Hindernisse in den ersten 250 Studs auf den Wash-Mittellinien** (blockiert Sicht und Wege).
6. **Keine Sackgassen und Labyrinthe**, keine Spalten schmaler als 40 Studs auf befahrbaren Wegen.
7. **Keine Wasserbecken tiefer als 4**, keine Mulden mit Wand, keine Löcher, in denen Spieler stecken bleiben.
8. **Keine Farben von Erz-Modellen als Deko-Haufen** (verwechselbar mit Vorkommen).
9. **Kein Verwischen der Ringe zu Brei:** Übergänge weich, aber jeder Ring behält Zweitfarbe und Leitform.
10. **Keine Heightmap-Überhänge erwarten:** Hüte, Bögen, Fenster, Tunnel nur als Zusatzformen (Zylinder, Luft-Quader).
11. **Nicht alles auf einmal bauen:** zuerst Gelände + Himmel + Licht prüfen (ohne Deko), dann Ring A, dann B … so sieht man früh, ob die Stimmung stimmt.
12. **Keine zu geringe Dunstdichte:** ohne Luftperspektive wirkt die 2 000-Studs-Welt flach und leer; mit zu viel verschwinden die Sterne.

---

## Offene Punkte (für Jos/Ju)
- Gefällt die **Ring-Zweiteilung C** (Lava vs. Dünen) und die Ring-Namen? (Alle nur Vorschlag.)
- **Saturn-Größe 14°** (Stil) statt realistischer 5–6°: ok?
- Rand: **Balkone mit unsichtbarer Wand** und schwebende Felsen als reine Optik: ok?
- Sollen die Landmarken-Slots **fest** sein (Vorschlag) oder auch seed-abhängig?
