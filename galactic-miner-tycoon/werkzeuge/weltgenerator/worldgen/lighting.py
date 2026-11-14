"""Licht, Atmosphaere, Nachbearbeitung, Himmel (Vorgabe Abschnitt 6) als Meta-Daten."""
from __future__ import annotations

import math

from .layout import SUN_AZ, SUN_EL
from .world import RGB, Enum


def roblox_clock_lat(az=SUN_AZ, el=SUN_EL):
    """ClockTime/GeographicLatitude fuer die Sonnenrichtung (Formel des Himmels-Agenten in sky.py, in Roblox gemessen)."""
    try:
        from .sky import solve_roblox_sun
        ct, lat = solve_roblox_sun(az, el)
        return round(ct, 4), round(lat, 2)
    except Exception:  # noqa: BLE001 - sky.py fehlt oder aendert sich: alte Werte
        return 16.45, 42.0


def sun_direction(az=SUN_AZ, el=SUN_EL):
    a, e = math.radians(az), math.radians(el)
    return [round(math.sin(a) * math.cos(e), 5), round(math.sin(e), 5), round(-math.cos(a) * math.cos(e), 5)]


def lighting_meta():
    ct, lat = roblox_clock_lat()
    return {
        "Lighting": {
            # Sonne Az 250 / El 30 (Review). Werte aus sky.solve_roblox_sun; der Himmels-Agent liefert ggf. neue.
            "ClockTime": ct,
            "GeographicLatitude": lat,
            "Brightness": 3.0,
            "Ambient": RGB("#5A4A66"),
            "OutdoorAmbient": RGB("#AC92AC"),        # Rose-Lavendel: Schatten auf Pfirsich werden mauve-korall
            "ColorShift_Top": RGB("#FFD8AE"),        # weniger Orange, sonst Rost
            "ColorShift_Bottom": RGB("#8A74B0"),
            "EnvironmentDiffuseScale": 0.15,         # dunkle Skybox wuerde Schatten tuerkis-grau ziehen
            "EnvironmentSpecularScale": 0.08,        # kein Himmels-Spiegel auf Pflanzen
            "ExposureCompensation": 0.2,
            "GlobalShadows": True,
            "ShadowSoftness": 0.4,
            "Technology": Enum("Technology", "ShadowMap"),
        },
        "Atmosphere": {
            # Runde 1 (Art-Director): weniger Dunst, mauve-rosa statt Staubfarbe -> Mittelfeld und Rand bleiben kontrastreich
            # Runde 3 (Horizont): Offset 0,2 -> 0,35 und Lavendel-Rose, damit der Dunst das Void hinter dem Kamm deckt
            "Density": 0.17, "Offset": 0.35, "Color": RGB("#CDB8DA"), "Decay": RGB("#7C6AA0"), "Glare": 0.25, "Haze": 1.0,
        },
        "Bloom": {"Intensity": 0.35, "Size": 30, "Threshold": 1.5},
        "ColorCorrection": {"Brightness": 0.0, "Contrast": 0.14, "Saturation": 0.12, "TintColor": RGB("#FFF2E8")},
        "SunRays": {"Intensity": 0.05, "Spread": 0.6},
        "DepthOfField": {"Enabled": False, "FarIntensity": 0.08, "FocusDistance": 200, "InFocusRadius": 400, "NearIntensity": 0},
        "Sky": {"CelestialBodiesShown": False, "StarCount": 0},  # SkyboxOrientation bleibt Standard (0, 0, 0)
    }
