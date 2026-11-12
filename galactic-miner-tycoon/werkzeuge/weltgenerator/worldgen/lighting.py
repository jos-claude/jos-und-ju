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
            "ClockTime": 16.5,
            "GeographicLatitude": 0,
            "Brightness": 2.4,
            "Ambient": RGB("#6A5878"),
            "OutdoorAmbient": RGB("#B28C8A"),
            "ColorShift_Top": RGB("#FFD9A8"),
            "ColorShift_Bottom": RGB("#7A6FB0"),
            "EnvironmentDiffuseScale": 0.6,
            "EnvironmentSpecularScale": 0.3,
            "ExposureCompensation": 0.2,
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
        "Sky": {"CelestialBodiesShown": False, "StarCount": 0},
    }
