"""Materialtabelle fuer alle Modelle (ohne bpy, damit auch make_textures.py sie nutzt).

Jedes Material hat eine Farbe (sRGB) und einen Typ. Der Typ bestimmt Textur,
Metall-Anteil und Rauheit:
- paint  lackiertes Metall mit Kratzern/Abplatzern (leicht metallisch)
- steel  gebuersteter Stahl (metallisch)
- tread  Riffelblech (metallisch, Rautenmuster)
- rubber Gummiband (matt, Querrillen)
- rock   Erz/Stein (matt, Rostflecken)
- neon   Leuchte (keine Textur, in Roblox Neon)
- glass  Glas (keine Textur, in Roblox Glass)
"""

TILE_STUDS = 4.0      # eine Textur-Kachel = 4 x 4 Studs
TEX_SIZE = 512

MATERIALS = {
    # Name: (Farbe, Typ)
    "Orange": ("#D9862A", "paint"),       # Beine, Waende (gebranntes Orange)
    "OrangeLight": ("#E8A445", "paint"),  # Dachbloecke der Raeume, Rolltor-Kasten
    "Amber": ("#DC9B32", "paint"),        # Seitenfelder Lager-Kasten
    "Yellow": ("#F2C80F", "paint"),       # Pfeile, Warnstreifen
    "Black": ("#1B1B1D", "paint"),        # Warnstreifen, Loecher
    "White": ("#DAD5CD", "paint"),        # Schild-Rahmen
    "Cream": ("#D3C7AD", "paint"),        # leere Anzeige-Roehre
    "GaugeOrange": ("#EB6A11", "paint"),  # Fuellstand
    "Slate": ("#425367", "paint"),        # Verbindungsgaenge der Basis
    "DarkGrey": ("#363B42", "paint"),     # Tueren, Rolltore, Unterbau
    "SteelGrey": ("#6F7A83", "steel"),    # Rahmen, Schienen, Pfeiler
    "SteelDark": ("#464D54", "steel"),    # Sockel, Innenraum
    "SteelLight": ("#999EA1", "steel"),   # Bolzen, Fasen, Trichter innen
    "Gunmetal": ("#5B524D", "steel"),     # Trichter Lager-Kasten, Schuessel
    "TreadPlate": ("#A0A3A2", "tread"),   # Rampe, Fussplatten
    "Belt": ("#2F3237", "rubber"),        # Bandoberflaeche
    "OreRock": ("#7C6C63", "rock"),       # Erzbrocken
    "OreRockDark": ("#4A423D", "rock"),   # Erzhaufen-Grundkoerper
    "Cyan": ("#45EEDC", "neon"),
    "Glass": ("#B4C0C6", "glass"),
    "GlassDark": ("#556169", "glass"),
}

TEXTURED_TYPES = ("paint", "steel", "tread", "rubber", "rock")

# Werte fuer Blender-Vorschau, wenn keine Textur geladen ist
TYPE_DEFAULTS = {
    "paint": {"metal": 0.2, "rough": 0.48},
    "steel": {"metal": 0.85, "rough": 0.43},
    "tread": {"metal": 0.85, "rough": 0.42},
    "rubber": {"metal": 0.0, "rough": 0.85},
    "rock": {"metal": 0.05, "rough": 0.9},
    "neon": {"metal": 0.0, "rough": 0.5},
    "glass": {"metal": 0.0, "rough": 0.05},
}

TRANSPARENCY = {"Glass": 0.35, "GlassDark": 0.3}


def tex_names(material):
    """Dateinamen (ohne Ordner) der Texturen eines Materials."""
    _, typ = MATERIALS[material]
    return {
        "color": f"{material}_color.jpg",
        "rough": f"{typ}_rough.jpg",
        "metal": f"{typ}_metal.jpg",
        "normal": f"{typ}_normal.png",
    }
