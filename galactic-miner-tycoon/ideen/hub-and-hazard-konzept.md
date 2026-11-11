# Idee: Konzept „Hub & Hazard“ (Co-op Extraction)

- **Status:** Idee (neu) – **nicht abgestimmt**, noch nicht im Konzept (`../spiel/`) übernommen
- **Von:** Ju (grobes Konzeptdokument, hier unverändert übernommen; nur Tippfehler korrigiert)
- **Eingetragen:** 11.11.2026

> **Hinweis für die Claudes:** Dieses Dokument weicht an einigen Stellen von `../spiel/00-vision.md` ab (siehe „Abgleich mit der Vision“ unten). Nichts daraus als beschlossen behandeln, bevor Jos und Ju es bestätigt und in `../entscheidungen/` festgehalten haben.

---

# GAME DESIGN DOKUMENT: PROJEKT „HUB & HAZARD“

## 1. Spielkonzept & Core Loop
- **Genre:** Sci-Fi Co-op Extraction Shooter mit Tycoon-Elementen.
- **Kern-Loop:** Spieler starten in einer sicheren, instanzierten Heimatbasis auf einem Heimatplaneten. Dort wird Ressourcen-Gewinnung automatisiert. Über eine Sternenkarte starten sie Expeditionen zu gefährlichen Planeten (Extract-Zonen). Ziel ist es, in einem vorgegebenen Zeitfenster wertvolle Ressourcen und Artefakte zu sammeln und rechtzeitig zum Schiff zurückzukehren. Bei Ablauf der Zeit oder dem Tod geht der Loot verloren. Zurück in der Basis werden Ressourcen genutzt, um die Basis auszubauen, das Schiff aufzurüsten und neue Technologien für gefährlichere Zonen freizuschalten.

## 2. Säule 1: Der Heimatplanet (Tycoon & Basis)
- **Kern-Gameplay:** Aktive und passive Rohstoffgewinnung. Basisbau und Logistik.
- **Mechaniken:**
  - Abbau von Basiserzen (z. B. Eisenerz, Kupfer) auf der Heimatwelt.
  - Aufbau von Förderbandsystemen, Schmelzöfen und automatisierten Generatoren.
  - Generierung von Basis-Währung durch den Verkauf von verarbeitetem Schrott.
  - Basis-Ausbau: Freischalten neuer Gebäudeflügel (Lager, Forschungslabor, Hangar).

## 3. Säule 2: Die Expeditions-Planeten (Extraction-Zonen)
- **Kern-Gameplay:** Aktives Erkunden, Ressourcen-Risiko-Abwägung, Überleben.
- **Planeten-Variationen:**
  1. **Der Lavaplanet:** Fokus auf Movement-Präzision. Plattform-Passagen über Lavaströmen. Ressource: „Vulkanit“ für Hitzeschutz-Upgrades.
  2. **Die Giftgas-Welt:** Fokus auf Zeitdruck und Stealth. Toxische Atmosphäre erfordert Gasmasken. Sammeln von biologischen Proben/Reagenzien in Laboren.
  3. **Die Kristall-Katakomben:** Labyrinth-Struktur mit Umgebungsrätseln und Fallen. Ressource: Energiereiche Kristalle zur Basis-Optimierung.
  4. **Der Schrottmond:** Einstiegszone. Leichtes Terrain, hohe Dichte an Industrieschrott für Basis-Grundlagen.

## 4. Säule 3: Raumschiff & Progression (Tech-Tree)
- **Kern-Gameplay:** Das Schiff dient als mobile Basis und Schnittstelle zwischen den Welten.
- **Upgrades & Progression:**
  - **Antriebs-Upgrades:** Erhöhen die Reichweite auf der Sternenkarte, um weiter entfernte Planeten anzufliegen.
  - **Schild- & Lebenserhaltungssysteme:** Ermöglichen das Landen in extremeren Umgebungen (z. B. dichtere Giftatmosphäre, größere Hitze).
  - **Ladekapazität:** Erlaubt den Transport von schwerem Loot („Heavy Loot“ wie große Motoren oder Erzblöcke, die den Spieler verlangsamen).
  - **Stat-Boosts:** Permanente Verbesserungen für den Spielercharakter (Laufgeschwindigkeit, Inventargröße).

## 5. Ressourcen-Hierarchie & Wirtschaft
- **Basismaterialien (Tier 1):** Schrott, Basiserze. Dienen als Währung für Munition, Heilung und Basis-Upgrades.
- **Biomspezifische Ressourcen (Tier 2):** Vulkanit, Kristalle. Notwendig für spezifische Technologie-Sprünge.
- **Atmosphärische Schlüssel-Ressourcen (Tier 3):** Hochgiftige Proben, Artefakte. Schalten Highend-Ausrüstung und neue Planeten frei.

## 6. Technische Anforderungen für die Entwicklung (Prompt-Vorlage für Cloud)
- **Modularer Aufbau:** Jedes System (Inventar, Förderband, Sauerstoff-Timer, Sternenkarte) muss als separates, gut dokumentiertes Luau-Skript in Roblox Studio implementiert werden.
- **Datenpersistenz:** Spielerfortschritt (Währung, freigeschaltete Technologien, Inventar) muss sicher über DataStores gespeichert werden.
- **Server-Client-Trennung:** Sämtliche Inventar- und Wirtschafts-Logik muss serverseitig (ServerScriptService) validiert werden, um Exploits zu verhindern. Das UI dient lediglich zur Anzeige und zum Senden von RemoteEvents.

---

## Abgleich mit der Vision (Vorschlag von Claude, nicht entschieden)

**Passt zusammen:**
- Heimatplanet mit automatisiertem Abbau, Sternenkarte, Planeten mit eigenen Ressourcen, Schiff-Upgrades, Tech-Tree.
- Technik (modular, DataStores, serverseitige Validierung) deckt sich mit `../technik/`.
- Das Konzept könnte die offene Frage „Was bedeutet Hub & Hazard?“ beantworten (`../STATUS.md`, `../spiel/09-hub-und-gefahren.md`).

**Widerspricht der aktuellen Vision (`../spiel/00-vision.md`):**
- Vision sagt „Kein Kampfspiel / Shooter“ – dieses Konzept ist ein **Extraction Shooter**.
- Vision sagt „Gefahren kosten Zeit/Ressourcen, nicht den ganzen Fortschritt“ – hier **geht bei Tod/Zeitablauf der Loot verloren**.
- Vision: Tycoon zuerst, ruhiger Wechsel Aufbau/Erkunden – hier steht der riskante Extraction-Teil stark im Vordergrund.
- Vision: Zielgruppe ca. 8–16 Jahre, bunt-comichaft – Extraction/Survival kann härter wirken.
- Co-op / instanzierte Basis berührt die offene Frage „Singleplayer-Basis oder gemeinsame Basis?“ (`../spiel/13-multiplayer.md`).

**Offene Fragen für Jos und Ju:**
- [ ] Bleibt es ein Tycoon mit sanften Gefahren, oder wird es ein Extraction Shooter? (Das ändert die Vision.)
- [ ] Gibt es echte Kämpfe/Waffen („Munition“ steht in Tier 1) oder nur Umweltgefahren?
- [ ] Wie viel Verlust beim Tod ist okay (kompletter Loot-Verlust vs. nur ein Teil)?
- [ ] Co-op: Wie viele Spieler pro Expedition, und teilen sich Spieler eine Basis?
- [ ] Welche Teile sind für beide Richtungen gleich und können sofort gebaut werden (Heimatplanet, Abbau, Schiff)?
