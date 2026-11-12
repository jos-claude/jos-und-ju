"""Fester Aufbau von Insel 1 (Slots aus referenz/welt-design-insel-1.md).

Alle Hoehen hier sind Roblox-y: Basis-Plateau auf y = 0 (Vorgabe-Hoehe h minus 48).
Azimut 0 = Norden = -Z, 90 = Osten = +X (im Uhrzeigersinn von oben).
Der Seed verschiebt nur innerhalb der erlaubten Toleranzen (Washes +-10 Grad, Landmarken +-8 Grad / +-60).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

H0 = 48.0                      # Vorgabe-Hoehe des Plateaus (wird ueberall abgezogen)
WIND_FROM = 250.0              # Wind kommt aus WSW
LEE_DIR = 70.0                 # Lee-Richtung / Schattenrichtung / Neigung der Pflanzen
SUN_AZ, SUN_EL = 250.0, 22.0
STRATA_PERIOD = 240
STRATA_BASE = 48               # y_eff = y + 48 -> Baender liegen wie in der Vorgabe (Plateau h 48)
DIP_DEG = 3.0                  # globale Neigung der Schichten (Fall nach ONO, Azimut 70)

RING_EDGES = [0, 250, 600, 1100, 1600, 2000]
RING_NAMES = ["A", "B", "C", "D", "E"]

WASH_AZ = [40.0, 100.0, 160.0, 220.0, 280.0, 340.0]
BALCONY_AZ = [45.0, 150.0, 245.0, 330.0]


def pol(az_deg: float, r: float):
    a = math.radians(az_deg)
    return r * math.sin(a), -r * math.cos(a)


def az_of(x, z):
    return np.degrees(np.arctan2(x, -z)) % 360.0


def dir_of(az_deg: float):
    a = math.radians(az_deg)
    return math.sin(a), -math.cos(a)


def ang_diff(a, b):
    """Kleinster Winkelabstand in Grad (vektorisiert)."""
    return (np.asarray(a) - b + 180.0) % 360.0 - 180.0


@dataclass
class Slot:
    key: str
    az: float
    r: float
    data: dict = field(default_factory=dict)

    @property
    def xz(self):
        return pol(self.az, self.r)


@dataclass
class Layout:
    seed: int
    washes: list[float]
    slots: dict[str, Slot]
    spawn: tuple
    base_size: tuple = (120.0, 30.0, 60.0)


def make_layout(seed: int) -> Layout:
    rng = np.random.default_rng(seed * 31 + 7)

    def j(deg):
        return float(rng.uniform(-deg, deg))

    washes = [a + j(6.0) for a in WASH_AZ]
    s: dict[str, Slot] = {}

    def add(key, az, r, **data):
        s[key] = Slot(key, az % 360.0, r, data)

    # L0 Abendbank: flacher Aussichtsfels mit Rampe (Vorgabe h 62 -> y 14)
    add("L0", 250 + j(3), 232 + j(10), top=14.0)
    # L1 Saturn-Tor: zwei geschichtete Mesas. Abweichung von der Vorgabe (28/52 Grad):
    # 22/57 Grad, damit die Luecke ~90 Studs breit ist und der Blick Az 40 frei bleibt.
    add("L1a", 22 + j(1.5), 300 + j(8), diam=120.0, top=82.0)
    add("L1b", 57 + j(1.5), 332 + j(8), diam=95.0, top=57.0)
    # L2 Zwillingstuerme
    add("L2", 140 + j(4), 560 + j(25), tops=(102.0, 72.0), diams=(34.0, 28.0), gap=40.0)
    # L3 Nadelgarten (Hoodoo-Wald), Mitte des Gebiets
    add("L3", 297 + j(3), 500 + j(15))
    # L4 Bogen (Duenenland). Lichte Hoehe 38 verlangt einen hoeheren Scheitel als h 70.
    add("L4", 200 + j(3), 820 + j(25), span=60.0, clear=38.0)
    # L5 Vulkanzwerg Rauchfang. Abweichung: Az 34 statt 20 (sonst verdeckt das Saturn-Tor den Kegel).
    add("L5", 34 + j(2), 905 + j(20), top=122.0, crater=110.0)
    # L6 Regenbogen-Kamm (Hauptkamm, 3 Gipfel)
    add("L6", 108 + j(2), 1340 + j(20), peaks=(172.0, 142.0, 112.0), length=430.0)
    # L7 Sinterterrassen "Silberstufen"
    add("L7", 255 + j(3), 1235 + j(20), basins=14, width=160.0, length=220.0)
    # L8 Kristallkathedrale
    add("L8", 195 + j(3), 1420 + j(20), top=82.0)
    # L9 Titan-Spiegelturm
    add("L9", 15 + j(3), 1760 + j(15), top=272.0)
    for i, a in enumerate(BALCONY_AZ):
        add(f"L10_{i}", a, 1960.0)
    # Becken / Quellen
    add("pond", 215 + j(3), 212 + j(6), diam=56.0, depth=3.0)
    add("spring", 190 + j(4), 382 + j(15), diam=50.0, depth=2.5)
    add("T2", 95 + j(3), 1480 + j(15), basins=6, width=110.0, length=130.0)
    add("T3", 330 + j(3), 1355 + j(15), basins=9, width=130.0, length=160.0)
    # Salzpfannen (Ring C 1, Ring D 4)
    add("playaC", 150 + j(4), 955 + j(20), diam=180.0)
    for i, (a, r, d) in enumerate([(172, 1300, 300), (186, 1440, 200), (204, 1330, 240), (212, 1450, 150)]):
        add(f"playaD{i}", a + j(3), r + j(20), diam=d + j(30))
    # Spawn wie im Place (Jus Code): (0, 0, 20); Start-Halle liegt bei x ~ 0, z 30-58 (hinter dem Spieler bei Blick Az 40)
    return Layout(seed=seed, washes=washes, slots=s, spawn=(0.0, 0.0, 20.0))
