"""Materialtabelle fuer alle Modelle (Farben und Material-Typen).

Flache Farben ohne Texturen (Comic-Look), mit kraeftigem Kontrast. Der Typ
bestimmt nur, welches Roblox-Material das Setup-Skript setzt:
- paint / steel / tread / rubber / rock -> SmoothPlastic
- neon  -> Neon (Leuchten)
- glass -> Glass (durchsichtig)
"""

TILE_STUDS = 4.0      # Kachelgroesse fuer die UV-Koordinaten (Studs)

MATERIALS = {
    # Name: (Farbe, Typ)
    "Orange": ("#F08A1C", "paint"),       # Beine, Waende (gebranntes Orange)
    "OrangeLight": ("#FFAE3D", "paint"),  # Dachbloecke der Raeume, Rolltor-Kasten
    "Amber": ("#F2A626", "paint"),        # Seitenfelder Lager-Kasten
    "Yellow": ("#FFD200", "paint"),       # Pfeile, Warnstreifen
    "Black": ("#141416", "paint"),        # Warnstreifen, Loecher
    "White": ("#EEEBE5", "paint"),        # Schild-Rahmen
    "Cream": ("#E6DCC2", "paint"),        # leere Anzeige-Roehre
    "GaugeOrange": ("#FF6A00", "paint"),  # Fuellstand
    "Slate": ("#36475C", "paint"),        # Verbindungsgaenge der Basis
    "DarkGrey": ("#2A2E34", "paint"),     # Tueren, Rolltore, Unterbau
    "SteelGrey": ("#7A848E", "steel"),    # Rahmen, Schienen, Pfeiler
    "SteelDark": ("#3F454C", "steel"),    # Sockel, Innenraum
    "SteelLight": ("#C3C8CD", "steel"),   # Bolzen, Fasen, Trichter innen
    "Gunmetal": ("#4A423D", "steel"),     # Trichter Lager-Kasten, Schuessel
    "TreadPlate": ("#A9ADB0", "tread"),   # Rampe, Fussplatten
    "Belt": ("#23262B", "rubber"),        # Bandoberflaeche
    "OreRock": ("#8A766A", "rock"),       # Erzbrocken
    "OreRockDark": ("#3E3631", "rock"),   # Erzhaufen-Grundkoerper
    "Cyan": ("#3FF5E3", "neon"),
    # Spitzhacke (bauplaene/spitzhacke.md), passend zu oreColors im Code
    "Rust": ("#A65A35", "paint"),         # Kopf der Rost-Hacke
    "RustDark": ("#5E3524", "paint"),     # Block und Stiel der Rost-Hacke
    "Copper": ("#D9853F", "steel"),       # Bolzen der Stahl-Hacke
    "Crystal": ("#BE6EF0", "neon"),       # Kristall-Spitze (= Erzfarbe Kristall)
    "Titan": ("#C8D6E4", "steel"),        # Kopf der Titan-Hacke (= Erzfarbe Titan)
    "SteelMid": ("#5E656D", "steel"),     # Stiel der Spitzhacke (zwischen SteelDark und SteelGrey)
    "Glass": ("#BFD3DC", "glass"),
    "GlassDark": ("#4E5D66", "glass"),
}

# Werte fuer Blender (matt wie Plastik, Comic-Look)
TYPE_DEFAULTS = {
    "paint": {"metal": 0.0, "rough": 0.5},
    "steel": {"metal": 0.0, "rough": 0.45},
    "tread": {"metal": 0.0, "rough": 0.45},
    "rubber": {"metal": 0.0, "rough": 0.7},
    "rock": {"metal": 0.0, "rough": 0.8},
    "neon": {"metal": 0.0, "rough": 0.5},
    "glass": {"metal": 0.0, "rough": 0.05},
}

# Alpha in Blender (1 = deckend). Bullaugen fast deckend, Lager-Glas durchsichtig.
TRANSPARENCY = {"Glass": 0.85, "GlassDark": 0.3}
