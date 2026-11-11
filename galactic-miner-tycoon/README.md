# Galactic Miner Tycoon

> Du startest auf einem Heimatplaneten, baust per Button-Klick eine Raumstation/Basis aus, lässt Rohstoffe automatisch abbauen und verarbeiten – und fliegst mit deiner Rakete auf fremde Planeten, um seltene Materialien zu holen, mit denen du Basis und Raumschiff immer weiter verbesserst.

Das ist das **zentrale Verzeichnis für dieses Spiel**. Alles, was das Spiel betrifft (Vision, Entscheidungen, Aufgaben, Daten, Code), liegt hier drin und ist miteinander verlinkt.

**Neu hier? Lies in dieser Reihenfolge:** `STATUS.md` → `spiel/00-vision.md` → `spiel/01-spielablauf.md` → offene Aufträge in `auftraege/offen/`.

## Ordnerkarte

| Ordner / Datei | Wofür | Wer pflegt |
|---|---|---|
| `STATUS.md` | Aktueller Stand, nächste Schritte, offene Kernfragen | beide |
| `spiel/` | **Konzept**: Vision, Spielablauf, alle Systeme (eine Datei pro Thema) | beide |
| `entscheidungen/` | **Entscheidungslog**: Was haben wir warum entschieden? | beide |
| `ideen/` | **Ideenspeicher**: Ungeordnete Ideen, bevor sie ins Konzept kommen | beide |
| `auftraege/` | **Aufgaben** an uns gegenseitig (`offen/` → `erledigt/`) | beide |
| `checklisten/` | Meilensteine, Roblox-Studio-Setup, Release-Check | beide |
| `daten/` | **Zahlen & Listen**: Ressourcen, Planeten, Upgrades, Balancing | beide |
| `referenz/` | Mindmap, Glossar, Inspiration, Roblox-Links | beide |
| `technik/` | Code-Architektur, Namensregeln, Zusammenarbeit in Roblox Studio | beide |
| `assets/` | Liste der Modelle, Sounds, Bilder (mit Roblox-IDs) | beide |
| `src/` | **Der Spielcode** (Luau, per Rojo in Roblox Studio synchronisiert) | siehe `technik/` |
| `default.project.json` | Rojo-Projektdatei (verbindet `src/` mit dem Place) | technik |

## Wie hängt alles zusammen?

```
 Idee (ideen/)  ──►  Konzept (spiel/)  ──►  Zahlen (daten/)  ──►  Code (src/)
      │                    │                      │                   │
      └──── Entscheidung (entscheidungen/) hält fest, warum ────────┘
                           │
          Aufträge (auftraege/) verteilen die Arbeit,
          Checklisten (checklisten/) zeigen den Fortschritt
```

Faustregel: **Konzept steht in `spiel/`, Zahlen stehen in `daten/`, der Code liest sie nur.** Ändert sich eine Zahl, ändern wir `daten/` und `src/.../Config/` zusammen.
