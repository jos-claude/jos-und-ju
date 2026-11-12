# Architektur

Status: **Vorschlag**. Der Server entscheidet alles Wichtige (Geld, Gebäude, Fortschritt), der Client zeigt nur an und schickt Wünsche – so kann niemand schummeln.

## Ordner in `src/` und wo sie im Place landen
| Repo-Pfad | Roblox-Ort | Inhalt |
|---|---|---|
| `src/ReplicatedStorage/Shared/` | `ReplicatedStorage.Shared` | Code & Daten für Server **und** Client |
| `src/ReplicatedStorage/Shared/Config/` | `…Shared.Config` | Zahlen/Listen (Ressourcen, Planeten, Währungen) – spiegeln `daten/` |
| `src/ReplicatedStorage/Shared/Modules/` | `…Shared.Modules` | Gemeinsame Hilfsfunktionen |
| `src/ReplicatedStorage/Shared/Types/` | `…Shared.Types` | Typ-Definitionen |
| `src/ReplicatedStorage/Assets/` | `ReplicatedStorage.Assets` | Modelle/UI-Vorlagen (`.rbxm`) |
| `src/ServerScriptService/Server/` | `ServerScriptService.Server` | Server-Start (`init.server.luau`) |
| `…/Server/Services/` | | Ein Service je Aufgabe (siehe unten) |
| `…/Server/Modules/` | | Server-Hilfscode |
| `src/StarterPlayer/StarterPlayerScripts/Client/` | `StarterPlayerScripts.Client` | Client-Start (`init.client.luau`) |
| `…/Client/Controllers/` | | Ein Controller je Aufgabe (siehe unten) |
| `…/Client/UI/` | | UI-Code |

Die **Welt** (Heimatplanet, Planeten, Rakete) und **UI-Layouts** werden in Studio gebaut und nicht in `src/` abgelegt.

## Geplante Server-Services (`Server/Services/`)
| Service | Aufgabe | Konzept |
|---|---|---|
| `DataService` | Speichern/Laden der Spielerdaten | – |
| `CurrencyService` | Credits/Gems verwalten | `spiel/10` |
| `PlotService` | Bauplatz pro Spieler zuweisen | `spiel/02` |
| `BuildService` | Gebäude per Button kaufen/platzieren | `spiel/02` |
| `MiningService` | Bohrer/Förderbänder, Förderraten | `spiel/03` |
| `ProcessingService` | Fabriken, Rezepte | `spiel/04` |
| `StorageService` | Silos, Lagerbestand | `spiel/04` |
| `ShipService` | Schiff und Upgrades | `spiel/05` |
| `TravelService` | Zonenwechsel (Heimatplanet ↔ Planeten) | `spiel/05`, `spiel/06` |
| `ToolService` | Werkzeuge beim Abbau | `spiel/07` |
| `ResearchService` | Techbaum und Forschung | `spiel/08` |
| `HazardService` | Gefahren auf Planeten | `spiel/09` |
| `MovementService` | Schwerkraft, Sprunghöhe, Laufgeschwindigkeit (**fertig**) | `spiel/17` |

Ein Service ist ein ModuleScript mit `Init()` und `Start()` (siehe `Services/DataService.luau` als Vorlage). Der Server-Start lädt alle Services automatisch.

## Geplante Client-Controller (`Client/Controllers/`)
`HudController` (Credits/Gems anzeigen), `BuildController` (Kauf-Buttons), `ShipController`, `ToolController`, `TravelController` (Planetenauswahl), `AudioController`, `MovementController` (Trägheit, Schwung in der Luft, Landestaub; **fertig**, `spiel/17`).

## Datenfluss (Beispiel: Bohrer kaufen)
1. Spieler drückt Kauf-Button in der Welt → Client schickt Wunsch `BuyBuilding("drill_basic")` per RemoteEvent.
2. `BuildService` prüft (genug Credits? Voraussetzung erfüllt?), zieht Credits ab (`CurrencyService`), stellt Gebäude hin.
3. `DataService` speichert. Client bekommt neue Werte und aktualisiert HUD.

## Offene Fragen
- Förderbänder: echte Items oder Rate-Berechnung? (`spiel/03`)
- Ein Place oder mehrere? (`entscheidungen/004-ein-place.md`)
