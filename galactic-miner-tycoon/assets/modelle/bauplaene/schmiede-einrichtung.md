# Bauplan: Einrichtung der Schmiede (Raum 2)

- **Status:** Vorschlag (Jos' Claude, 14.11.2026). Wartet auf das OK von Jos und Ju. Der Blender-Bau kommt danach.
- **Spiel-Werte:** `../../../spiel/16-raeume-und-spitzhacke.md` (Schmiede: Spitzhacke und Rucksack verbessern, Teleportfeld zur Lobby)
- **Raum im Code:** `src/ReplicatedStorage/Shared/Config/BaseLayout.luau` (`forge`, `pads`), Greybox in `GreyboxShop.buildForge`
- **Gehört zu:** `spitzhacke.md`

## Route: Blender-Skript, nicht Tripo
Alles hier sind Möbel und Maschinen mit festen Maßen (Amboss, Werkbank, Ofen, Plattform). Das ist prozedural, wie Lager-Kasten und Basis. Geplant ist ein Skript `blender-skripte/build_forge.py` mit **einem Modell pro Möbelstück**. Die Raumhülle (Wände, Dach, Tür) gehört **nicht** zu diesem Bauplan.

## Die Idee
Die Schmiede ist der erste Raum, den man kauft. Sie soll sich wie eine **kleine Werkstatt der Kolonie** anfühlen: warm (Glut aus dem Ofen), laut (Amboss), aber im selben Spielzeug-Industrie-Look wie Bohrer und Lager.

- **Westseite = Schmied-Ecke:** Esse (Ofen), Kohlekiste, Amboss-Station für die **Spitzhacke**, Kühlbecken. Warmes Orange-Licht.
- **Ostseite = Werkbank-Ecke:** Rucksack-Werkbank, Werkzeugwand. Kühleres Licht.
- **Hinten in der Mitte:** Teleporter zur Lobby, gut sichtbar von der Tür aus. Cyan-Licht.
- **Beide Upgrade-Stationen haben denselben Rahmen** (Sockel + Rückwand mit X-Streben wie am Lager-Kasten). Nur die Mitte ist anders: Amboss mit Vitrine oder Werkbank mit Rucksack-Ständer. Das spart Arbeit und sieht zusammengehörig aus.

## Grundriss (von oben, Norden = Tür oben)

Raum: x 28 bis 60, z 30 bis 58, Wandhöhe 14. Ein Zeichen = 1 Stud breit, eine Zeile = 2 Studs.

```
###########==========###########   ← Tür (Norden, z = 30)
#                              #
#                          CCC #
#QQQ                       CCC #
#QQQ                           #
#QQQ........        ........   #
#AAA........        ........RRR#
#AAA........        ........RRR#
#AAA........        ........RRR#
#   ........        ........   #
#           ........           #
#FFFFF      .TTTTTT.           #
#FFFFF KK   .TTTTTT.           #
#FFFFF KK  ||.TTTT.||WWWWWWWWWW#
################################   ← Rückwand (Süden, z = 58)
x = 28                       x = 60
```

`.` = die drei Kauffelder aus dem Code (bleiben, wo sie sind) · `A` Amboss-Station · `Q` Kühlbecken · `F` Esse · `K` Kohlekiste · `T` Teleporter-Plattform · `||` Teleporter-Bogen · `W` Werkzeugwand · `R` Rucksack-Werkbank · `C` Kistenstapel. Zwei Hängelampen hängen über den beiden Upgrade-Kauffeldern.

Wer durch die Tür reinkommt (Blick nach Süden), hat die Spitzhacken-Ecke **rechts** und die Rucksack-Ecke **links**.

## Möbelliste

Positionen in **Roblox-Koordinaten** (Mitte der Grundfläche, Boden = Bodenhöhe der Schmiede). „Blickt nach“ = Seite, die zum Spieler zeigt. In Blender baut jedes Möbel wie immer: Boden bei z = 0, Vorderseite nach −Y.

| Prio | Modell | Was | Mitte (x, z) | Blickt nach | Breite × Tiefe × Höhe | Budget |
|---|---|---|---|---|---|---|
| 1 | `ForgeAnvilStation` | Amboss + Vitrine mit der nächsten Spitzhacke | (30,6, 44) | Osten | 6 × 3,2 × 4,6 | 3.000 |
| 1 | `ForgeBackpackBench` | Werkbank + Rucksack-Ständer | (57,4, 44) | Westen | 6 × 3,2 × 4,6 | 3.000 |
| 1 | `ForgeTeleporter` | Runde Plattform + Bogen zur Lobby | Plattform (44, 53), Bogen bei z 56 | Norden | 8,9 × 7 × 7,5 | 2.500 |
| 1 | `ForgeFurnace` | Esse mit Glut und Schornstein | (31,5, 54,5) | Norden | 5 × 5 × 14 (mit Schornstein) | 4.000 |
| 2 | `ForgeToolRack` | Werkzeugwand mit allen 5 Spitzhacken | (53,8, 56,8) | Norden | 10 × 0,4 × 3,6 (ab Höhe 1,4) | 600 + Hacken |
| 2 | `ForgeQuenchTank` | Kühlbecken mit Wasser | (30,4, 37,5) | Osten | 3 × 2,4 × 1,3 | 800 |
| 2 | `ForgeCoalCrate` | Kohlekiste mit Kohlehaufen | (35,8, 55,6) | Norden | 2,4 × 2,4 × 1,6 | 1.000 |
| 2 | `ForgeLamp` | Hängelampe (2 Stück) | (36, 44) und (52, 44), Schirm bei Höhe 11,5 | unten | Ø 2 × 2,5 | 300 |
| 2 | `ForgeCrates` | Kistenstapel als Deko | (56,5, 34,5) | – | 3 × 3 × 3,6 | 800 |
| 2 | (Parts in Studio) | 2 gelbe Gehweg-Linien von der Tür zur Plattform | x 42,2 und 45,8, z 31,5 bis 49,5 | – | 0,25 breit | – |

Zusammen höchstens etwa 16.000 Dreiecke ohne die Hacken an der Wand.

Prio 1 ist das, was man für das Spielgefühl braucht (die drei Kauffelder bekommen ein Gesicht, der Ofen macht die Stimmung). Prio 2 ist Deko und kann später kommen.

## Prio 1 im Detail

### `ForgeAnvilStation` (Spitzhacke verbessern)
Gemeinsamer **Stations-Rahmen** (gleich bei der Rucksack-Werkbank):

| Teil | Form | Maße | Lage | Material |
|---|---|---|---|---|
| Sockel | `box`, Fase 0,08 | 5,8 × 3,0 × 0,6 | Mitte (0, 0,1), z 0 – 0,6 | SteelDark |
| Warnstreifen | `hazard_stripes` auf der Vorderseite | Band 0,4 hoch | z 0,1 – 0,5 | Yellow / Black |
| Rückwand | `box`, Fase 0,06 | 5,8 × 0,25 × 3,8 | y +1,45, z 0,6 – 4,4 | Orange |
| Rahmen + X-Streben | 4 Rahmenleisten + 2 Diagonalen, 0,18 dick | auf der Rückwand | wie am Lager-Kasten | SteelGrey |
| Leuchtleiste | `box` | 5,4 × 0,10 × 0,10 | Oberkante Rückwand | Cyan (Neon) |

Mitte:

| Teil | Form | Maße | Lage | Material |
|---|---|---|---|---|
| Amboss-Fuß | `box`, Fase 0,06 | 1,8 × 1,3 × 0,5 | Mitte x −0,8, z 0,6 – 1,1 | SteelGrey |
| Amboss-Taille | `frustum_box` | unten 1,2 × 0,8, oben 0,9 × 0,6 | z 1,1 – 1,7 | SteelGrey |
| Amboss-Bahn | `box`, Fase 0,06 | 2,2 × 1,0 × 0,5 | z 1,7 – 2,2 | SteelLight |
| Amboss-Horn | `cylinder` Achse X, 8 Seg., r 0,42 → 0,06 | Länge 0,9 | links an der Bahn, x −1,9 bis −2,8, z 1,95 | SteelLight |
| Schmiedehammer | Kopf `box` 0,5 × 0,28 × 0,28 + Stiel `cylinder` r 0,07, Länge 1,0 | liegt auf der Bahn, Stiel ragt 0,3 über die Kante | z 2,2 – 2,5 | SteelDark + Belt |
| Vitrinen-Podest | `cylinder`, 12 Seg., Fase 0,06 | r 0,85 | Mitte x +1,7, z 0,6 – 1,6 | Orange |
| Leuchtring | `cylinder`, 12 Seg. | r 0,90, Höhe 0,08 | z 1,6 – 1,68 | Cyan (Neon) |
| Glashaube | `cylinder`, 12 Seg. | r 0,75 | z 1,68 – 3,6 | Glass |
| Haubendeckel | `cylinder`, 12 Seg. | r 0,85, Höhe 0,2 | z 3,6 – 3,8 | SteelGrey |

**In der Vitrine** dreht sich die **nächste** Spitzhacken-Stufe (Modell aus `spitzhacke.md`, Maßstab 0,4, Mitte bei z 2,64). Das setzt der Code ein, es ist nicht Teil des Meshes. Bei Stufe 5 steht dort die eigene Titan-Hacke.

### `ForgeBackpackBench` (Rucksack verbessern)
Gleicher Stations-Rahmen wie oben. Mitte:

| Teil | Form | Maße | Lage | Material |
|---|---|---|---|---|
| Tischplatte | `box`, Fase 0,04 | 3,4 × 1,6 × 0,25 | Mitte x −0,9, z 2,0 – 2,25 | TreadPlate |
| Tischbeine | 4 × `box` | 0,25 × 0,25 × 1,4 | x −0,9 ± 1,45, y ± 0,6, z 0,6 – 2,0 | SteelGrey |
| Schürze | `box` | 3,4 × 0,12 × 0,4 | Vorderkante, z 1,6 – 2,0 | Orange |
| Gurtrollen | 2 × `cylinder` Achse X, 12 Seg. | r 0,3, Länge 0,6 | liegen auf dem Tisch | Slate, Orange |
| Nietpresse | `box` 0,5 × 0,6 × 0,8 + Arm `cylinder` r 0,08 | | hinten rechts auf dem Tisch | Orange + SteelGrey |
| Ständer-Fuß | `cylinder`, 12 Seg. | r 0,7, Höhe 0,15 | Mitte x +1,9, z 0,6 – 0,75 | SteelDark |
| Ständer-Ring | `cylinder`, 12 Seg. | r 0,75, Höhe 0,05 | z 0,75 – 0,8 | Cyan (Neon) |
| Ständer-Stange | `cylinder`, 8 Seg. | r 0,1 | z 0,75 – 3,4 | SteelGrey |
| Schulterbügel | `box` | 1,2 × 0,15 × 0,15 | z 3,3 | SteelGrey |

**Am Ständer hängt der nächste Rucksack.** Die Rucksack-Modelle (5 Stufen) sind ein **eigener Bauplan**, der noch fehlt. Bis dahin ein Platzhalter-Kasten (1,4 × 0,8 × 1,8, Orange).

### `ForgeTeleporter` (zur Lobby)

| Teil | Form | Maße | Lage | Material |
|---|---|---|---|---|
| Plattform | `cylinder`, 16 Seg., Fase 0,08 | r 3,4 | z 0 – 0,4 | SteelDark |
| Innenfläche | `cylinder`, 16 Seg. | r 2,7, Höhe 0,05 | z 0,4 – 0,45 | Slate |
| Leuchtring | `annular_sector` 0° – 360° | innen 2,75, außen 3,05 | z 0,4 – 0,48 | Cyan (Neon) |
| Pfeiler-Füße | 2 × `box` | 1,3 × 1,3 × 0,6 | x ±4,0, y +3,0 | SteelDark |
| Pfeiler | 2 × `box`, Fase 0,08 | 0,9 × 0,9 × 6,5 | x ±4,0, y +3,0, z 0 – 6,5 | SteelGrey |
| Leuchtstreifen | 2 × `box` | 0,12 × 0,3 × 5,6 | Innenseite der Pfeiler, z 0,6 – 6,2 | Cyan (Neon) |
| Querbalken | `box`, Fase 0,08 | 8,9 × 1,0 × 1,0 | z 6,5 – 7,5 | Orange |
| Warnstreifen | `hazard_stripes` | vorn am Querbalken | | Yellow / Black |

Die Pfeiler stehen knapp **außerhalb** des Kauffelds (x 40,5 bis 47,5), damit man frei auf die Plattform laufen kann. Der Bogen steht 1 Stud vor der Rückwand.

### `ForgeFurnace` (Esse, das Herz des Raums)

| Teil | Form | Maße | Lage | Material |
|---|---|---|---|---|
| Sockel | `box`, Fase 0,08 | 5,0 × 5,0 × 0,6 | z 0 – 0,6 | SteelDark |
| Warnstreifen | `hazard_stripes` | vorn, 0,4 hoch | z 0,1 – 0,5 | Yellow / Black |
| Ofen-Körper | `box`, Fase 0,15 | 4,4 × 4,0 × 3,6 | z 0,6 – 4,2 | Orange |
| Eckpfosten | 4 × `box` | 0,4 × 0,4 × 3,6 | an den Ecken | SteelGrey |
| Ofenmaul-Rahmen | Rahmen aus 4 `box`, Fase 0,04 | außen 2,5 × 2,0, innen 2,0 × 1,5, steht 0,15 vor | Vorderseite, z 1,2 – 2,7 | SteelLight |
| Ofenmaul innen | `box` | 2,0 × 0,4 × 1,5, 0,3 zurückgesetzt | | Black |
| Glut | `box` | 1,8 × 0,2 × 0,5 | unten im Maul, z 1,2 – 1,7 | Ember (Neon) |
| Kohlen | 5 × `rock` | r 0,2 – 0,3 | auf der Glut | Coal |
| Temperatur-Anzeige | Röhre `box` 0,3 × 0,2 × 2,4 + Füllung | wie am Lager-Kasten | +X-Seite (zur Raummitte), vorn, z 1,2 – 3,6 | Cream + GaugeOrange |
| Haube | `frustum_box` | unten 4,6 × 4,2, oben 1,8 × 1,8 | z 4,2 – 5,6 | SteelGrey |
| Schornstein | `cylinder`, 12 Seg. | r 0,7 | z 5,6 – 14 (bis zum Dach) | SteelDark |
| Schornstein-Bänder | 2 × `cylinder` | r 0,78, Höhe 0,3 | z 7 und z 11 | Orange |

**In Roblox dazu (Code, kein Mesh):** PointLight orange im Maul (Range 14, Brightness 2), Funken-Partikel aus dem Maul, Rauch oben am Schornstein über dem Dach, leises Knistern als Loop.

## Prio 2 kurz

| Modell | Aufbau | Materialien |
|---|---|---|
| `ForgeToolRack` | Brett 10 × 0,3 × 3,6 (z 1,4 – 5,0), Rahmen 0,2, fünf Haken (0,15 × 0,5 × 0,15) im Abstand 2,0 bei z 4,6, darunter je eine runde Lampe (r 0,12). An den Haken hängen die 5 Spitzhacken im Maßstab 0,55 (Spannweite höchstens 2,0, passt). | Slate, SteelGrey, SteelLight, Cyan |
| `ForgeQuenchTank` | Wanne 3 × 2,4 × 1,3 (Fase 0,1), Rand oben 0,15, Wasserfläche bei z 1,1 | SteelGrey, Orange, Water |
| `ForgeCoalCrate` | Kiste 2,4 × 2,4 × 1,2, vier Eckbeschläge, Haufen aus 6 bis 8 `rock` bis z 1,6 | Gunmetal, Orange, Coal |
| `ForgeLamp` | Kabel r 0,05 von der Decke (z 14) bis z 12,2, Schirm `cylinder` r 0,25 → 1,0, Höhe 0,7, Birne r 0,35 | SteelDark, Orange, LampWarm |
| `ForgeCrates` | Kiste 2,2³ und darauf Kiste 1,6³, um 15° gedreht, je mit Eckbeschlägen und einem Warnstreifen | SteelDark, Orange, Yellow / Black |

**Werkzeugwand als Fortschritts-Anzeige (Vorschlag):** Hacken, die man noch nicht hat, sind dunkle Silhouetten (DarkGrey) mit ausgeschalteter Lampe. Mit jedem Kauf wird eine Hacke bunt und ihre Lampe leuchtet. Der Spieler sieht so in jedem Besuch, was noch kommt. Das schaltet der Code um, das Modell bleibt gleich.

## Neue Farben für `gmt_materials.py` (Vorschlag)
Zusätzlich zu denen aus `spitzhacke.md`:

| Name | Farbe | Typ | Wofür |
|---|---|---|---|
| `Ember` | `#FF7A1A` | neon | Glut im Ofen |
| `Coal` | `#28242C` | rock | Kohlen (= Erzfarbe Kohle im Code) |
| `Water` | `#6ACFE6` | glass | Kühlbecken (Transparenz 0,4) |
| `LampWarm` | `#FFE7B0` | neon | Birnen der Hängelampen |

## Licht im Raum (Vorschlag, Code/Studio)
- Ofen: warmes Orange, stärkstes Licht im Raum.
- Teleporter: Cyan, mittelstark.
- Hängelampen: warmes Weiß über den beiden Kauffeldern, damit die Stationen gut zu lesen sind.
- Das Dach macht den Raum dunkler als draußen (wie im Greybox). Dadurch wirken Glut und Cyan stärker.

## Was der Code dafür braucht (betrifft Ju)
- Möbel einsetzen statt Greybox (Positionen oben, `BaseLayout.luau` bleibt gleich).
- Nächste Hacke in die Vitrine setzen und drehen lassen, nächsten Rucksack an den Ständer hängen.
- Werkzeugwand je nach Spitzhacken-Stufe einfärben.
- Licht und Partikel (Ofen, Teleporter).

Dafür schreibt Jos' Claude nach dem OK einen Auftrag an Ju.

## Offene Fragen
- [ ] Passt die Aufteilung (Westen Schmied-Ecke, Osten Werkbank, hinten Teleporter)? (Jos, Ju)
- [ ] Werkzeugwand als Fortschritts-Anzeige: ja oder nein?
- [ ] Wer baut die Raumhülle (Wände, Dach, Tür) als Modell, und im Stil von `BaseRoom`? Nicht Teil dieses Bauplans.
- [ ] Rucksack-Modelle (5 Stufen): eigener Bauplan nötig. Sollen sie wie die Hacke „ein Gerüst, fünf Häute“ werden?
