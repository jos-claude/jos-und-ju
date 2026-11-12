"""Licht, Atmosphaere, Nachbearbeitung, Himmel (Vorgabe Abschnitt 6) als Meta-Daten."""
from __future__ import annotations

import math

from .layout import SUN_AZ, SUN_EL
from .world import RGB, Enum


def sun_direction(az=SUN_AZ, el=SUN_EL):
    a, e = math.radians(az), math.radians(el)
    return [round(math.sin(a) * math.cos(e), 5), round(math.sin(e), 5), round(-math.cos(a) * math.cos(e), 5)]


def lighting_meta():
    return {
        "Lighting": {
            # Vom Himmels-Agenten mit der gemessenen Roblox-Sonnenformel bestimmt: ergibt Azimut 250, Elevation 22
            "ClockTime": 16.45,
            "GeographicLatitude": 42,
            # Review Runde 1: mehr Kontrast -> Sonne waermer/staerker, Umgebungslicht schwaecher, Schattenseite lavendel
            "Brightness": 3.0,
            "Ambient": RGB("#4E4466"),
            "OutdoorAmbient": RGB("#9A8CB4"),
            "ColorShift_Top": RGB("#FFC890"),
            "ColorShift_Bottom": RGB("#7468C0"),
            "EnvironmentDiffuseScale": 0.35,
            "EnvironmentSpecularScale": 0.3,
            "ExposureCompensation": 0.1,
            "GlobalShadows": True,
            "ShadowSoftness": 0.25,
            "Technology": Enum("Technology", "ShadowMap"),
        },
        "Atmosphere": {
            "Density": 0.28, "Offset": 0.25, "Color": RGB("#F2B8A0"), "Decay": RGB("#8E6FA8"), "Glare": 0.35, "Haze": 1.6,
        },
        "Bloom": {"Intensity": 0.45, "Size": 24, "Threshold": 1.4},
        "ColorCorrection": {"Brightness": 0.02, "Contrast": 0.12, "Saturation": 0.18, "TintColor": RGB("#FFF1E6")},
        "SunRays": {"Intensity": 0.06, "Spread": 0.8},
        "DepthOfField": {"Enabled": False, "FarIntensity": 0.08, "FocusDistance": 200, "InFocusRadius": 400, "NearIntensity": 0},
        "Sky": {"CelestialBodiesShown": False, "StarCount": 0},  # SkyboxOrientation bleibt Standard (0, 0, 0)
    }
