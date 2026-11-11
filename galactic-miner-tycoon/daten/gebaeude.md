# Gebäude (Basis)

Status: **M1-Vorschlag, nicht bestätigt**. Währung sind Rohstoffe (Entscheidung 006). Preisformel: `Preis(n) = Basispreis × 1,15^n`, n = schon gekaufte Gebäude dieser Art.

## M1
| ID | Name | Kosten | Wirkung | Voraussetzung |
|---|---|---|---|---|
| `drill_iron` | Eisen-Bohrer | 1. gratis, danach 20 Eisenerz (Basis) | 1,0 Eisenerz/s | – |
| `drill_copper` | Kupfer-Bohrer | 40 Eisenerz (Basis) | 0,5 Kupfererz/s | Eisen-Bohrer 2 gekauft |

Maximal 3 Eisen- und 3 Kupfer-Bohrer (6 Slots).

## Später (M2 und weiter, noch leer)
| ID | Name | Kosten | Wirkung | Voraussetzung |
|---|---|---|---|---|
| `conveyor` | Förderband | _ | verbindet | Bohrer |
| `factory_basic` | Fabrik | _ | verarbeitet | Förderband |
| `silo_basic` | Silo | _ | Lager +_ | – |
| `rocket_pad` | Raketenstartplatz | _ | Reisen | Silo, Fabrik |
| `research_lab` | Forschungslabor | _ | Forschung | Raketenstartplatz |
