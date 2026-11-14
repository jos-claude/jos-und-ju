# Auftrag 002: Skybox von Insel 1 hochladen und eintragen

- **Von:** Jos (geschrieben von Jos' Claude)
- **An:** Ju
- **Datum:** 14.11.2026
- **Status:** offen
- **Meilenstein:** M1

> **Nachtrag 14.11. (Jos' Claude):** Die 6 Bilder wurden in Runde 3 neu gerendert (Horizont ohne dunkles Band). Bitte die aktuelle Version aus `assets/himmel/` hochladen.

## Ziel
Der Weltraum-Himmel von Insel 1 (Saturn, Monde, Nebelband) ist im Place zu sehen statt des blauen Roblox-Standardhimmels.

## Kontext
- Die 6 Bilder sind fertig: `assets/himmel/sky_Bk.png`, `sky_Dn.png`, `sky_Ft.png`, `sky_Lf.png`, `sky_Rt.png`, `sky_Up.png` (je 1024², Zuordnung in `assets/himmel/README.md`).
- Bei Jos' Claude lehnt Studio den Upload per Open Cloud ab (Ordner-Freigabe greift nicht). Bei dir hat der Modell-Upload geklappt, und der Place gehört dir – deshalb bitte du.
- Der Himmel ist der größte Unterschied zum freigegebenen KI-Zielbild (`referenz/bilder/welt/ki-ziel/insel1-ziel-v1.png`), an das Jos' Claude die Welt gerade in Runden heranführt.

## Betroffene Dateien / Bereiche
- Upload: 6 **Image**-Assets (nicht Decal) auf dein Konto.
- `src/ServerStorage/WorldBuilder/Settings.luau`: die 6 IDs eintragen (`Bk = "rbxassetid://…"` usw.). Die Datei darf von Hand geändert werden.
- `assets/asset-liste.md`: IDs in der Skybox-Zeile ergänzen.
- **Nicht** selbst `Build()` ausführen – Jos' Claude baut die Welt nach deinem Push neu (dein Rojo bringt die Settings in den Place).

## Das ist fertig, wenn …
- [ ] 6 Image-IDs in `Settings.luau` und `asset-liste.md`, committet und gepusht.
- [ ] Kurze Notiz hier unter „Ergebnis“.

## Ergebnis
(wird vom Bearbeiter ausgefüllt, wenn der Auftrag fertig ist)
