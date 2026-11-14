"""Fester Aufbau von Insel 1 (Slots aus referenz/welt-design-insel-1.md).

Alle Hoehen hier sind Roblox-y: Basis-Plateau auf y = 0 (Vorgabe-Hoehe h minus 48).
Azimut 0 = Norden = -Z, 90 = Osten = +X (im Uhrzeigersinn von oben).
Der Seed verschiebt nur innerhalb der erlaubten Toleranzen (Washes +-10 Grad, Landmarken +-8 Grad / +-60).

Runde 2 (Entscheidung 022, 14.11.2026): Insel 1 halb so gross (Radius 1000 statt 2000). Alle radialen Masse (Ringe,
Slots, Washes, Randgebirge, Rauschen entlang der Ringe) leiten sich ueber WORLD_SCALE aus den alten Werten ab:
sr(1500) = 750. Objektgroessen (Tafelberge, Hoodoos, Baeume, Kristalle, Brocken) bleiben. Ausnahme ist das
Basis-Plateau: Jus Basis braucht weiter eine flache, freie Flaeche bis r 110 (PLATEAU_R).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

H0 = 48.0                      # Vorgabe-Hoehe des Plateaus (wird ueberall abgezogen)
WIND_FROM = 250.0              # Wind kommt aus WSW
LEE_DIR = 70.0                 # Lee-Richtung / Schattenrichtung / Neigung der Pflanzen
SUN_AZ, SUN_EL = 250.0, 30.0       # Review: Sonne 30 Grad (vorher 22) fuer helleren Boden
STRATA_PERIOD = 240
STRATA_BASE = 4                # Review: Korall-Doppelband (Mud 24 + 16) liegt bei y -28..+12 = Bodenhoehe -> Berge wachsen
                               # aus einem korallfarbenen Sockel
DIP_DEG = 1.5                  # globale Neigung der Schichten (Fall nach ONO, Azimut 70); Review: 1,5-2 statt 3

# ---------------------------------------------------------------- Massstab (Entscheidung 022)
WORLD_SCALE = 0.5              # radiale Masse: neu = alt x 0,5
PROFILE_SCALE = 0.3            # Hoehen des Ringprofils (Stufen, Becken, Hochland): kuerzere Rampen (Bauzonen Ring D/E)
ISLAND_R = 1000.0              # Erz-Ringe bis r 1000 (Titan 800-1000)
PLATEAU_R = 116.0              # Basis-Plateau flach (+-0,5) und frei; Jus Basis braucht r <= 110
PLATEAU_FREE_R = 120.0         # bis hier nur kniehohe Deko ohne Kollision
BUILD_MAX_R = 950.0            # Bauzonen (Erz-Spawn) bis hier; dahinter beginnt das Randgebirge


def sr(v):
    """Alter Radius (Insel r 2000) -> neuer Radius (Insel r 1000)."""
    return v * WORLD_SCALE


def sh(v):
    """Alte Profil-Hoehe -> neue (Ringprofil, nicht Objekte)."""
    return v * PROFILE_SCALE


# Erz-Ringe aus Entscheidung 022 (Eisen 10-100, Kupfer 125-350, Kohle 300-550, Kristall 550-800, Titan 800-1000)
RING_EDGES = [0, 125, 300, 550, 800, 1000]
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

    # Runde 2: Ring A (0-125) ist jetzt ganz Basis-Plateau. Was vorher in der Pfirsichebene (r 200-300) stand
    # (Abendbank, Saturn-Tor, Teich), rueckt an den Plateau-Rand (r 160-240) statt auf r 100-150.
    # L0 Abendbank: flacher Aussichtsfels mit Rampe (Vorgabe h 62 -> y 14); Runde 2: y 12
    add("L0", 250 + j(3), 182 + j(5), top=12.0)
    # L1 Saturn-Tor: zwei geschichtete Mesas. Abweichung von der Vorgabe (28/52 Grad):
    # 22/57 Grad, damit die Luecke ~90 Studs breit ist und der Blick Az 40 frei bleibt.
    # Runde 2: r 220/235 statt sr(300/332) - die grosse Mesa (Oe 134) braucht Abstand zum Plateau (r 110)
    add("L1a", 22 + j(1.5), 222 + j(4), diam=120.0, top=78.0)
    add("L1b", 57 + j(1.5), 238 + j(4), diam=95.0, top=57.0)
    # L2 Zwillingstuerme
    add("L2", 140 + j(4), sr(560) + j(10), tops=(102.0, 72.0), diams=(34.0, 28.0), gap=40.0)
    # L3 Nadelgarten (Hoodoo-Wald), Mitte des Gebiets
    add("L3", 297 + j(3), sr(500) + j(6))
    # L4 Bogen (Duenenland). Lichte Hoehe 38 verlangt einen hoeheren Scheitel als h 70.
    add("L4", 200 + j(3), sr(820) + j(10), span=60.0, clear=38.0)
    # L5 Vulkanzwerg Rauchfang. Abweichung: Az 34 statt 20 (sonst verdeckt das Saturn-Tor den Kegel).
    # Runde 2: Kegel 86 statt 122 hoch und steiler (30 statt 25 Grad), sonst ist der Fuss breiter als Ring C
    add("L5", 34 + j(2), sr(905) + j(8), top=86.0, crater=80.0)
    # L6 Regenbogen-Kamm (Hauptkamm, 3 Gipfel). Runde 2: ~30 % niedriger (Becken jetzt y -10), Laenge 280
    add("L6", 108 + j(2), sr(1340) + j(8), peaks=(124.0, 102.0, 82.0), length=280.0, base=-10.0)
    # L7 Sinterterrassen "Silberstufen"
    add("L7", 255 + j(3), sr(1235) + j(8), basins=12, width=130.0, length=180.0)
    # L8 Kristallkathedrale
    add("L8", 195 + j(3), sr(1420) + j(8), top=72.0)
    # L9 Titan-Spiegelturm. Runde 2: 215 statt 272 (Randgebirge ist jetzt auch ~30 % niedriger)
    add("L9", 15 + j(3), sr(1760) + j(6), top=215.0)
    for i, a in enumerate(BALCONY_AZ):
        add(f"L10_{i}", a, sr(1960))
    # Becken / Quellen. Runde 2: Teich ausserhalb des Plateaus (r 165 statt sr(212))
    add("pond", 215 + j(3), 168 + j(4), diam=50.0, depth=3.0)
    add("spring", 190 + j(4), sr(382) + j(6), diam=46.0, depth=2.5)
    # Runde 2: T2 entfaellt (Ring D ist nur noch 250 tief; L7 und T3 bleiben)
    add("T3", 330 + j(3), sr(1355) + j(6), basins=6, width=96.0, length=112.0)
    # Salzpfannen (Ring C 1, Ring D 2); Runde 2: Durchmesser x 0,6, zwei Pfannen weniger
    add("playaC", 150 + j(4), sr(955) + j(8), diam=110.0)
    for i, (a, r, d) in enumerate([(172, 1300, 300), (206, 1350, 240)]):
        add(f"playaD{i}", a + j(3), sr(r) + j(8), diam=0.6 * (d + j(30)))
    # Spawn wie im Place (Jus Code): (0, 0, 20); Start-Halle liegt bei x ~ 0, z 30-58 (hinter dem Spieler bei Blick Az 40)
    return Layout(seed=seed, washes=washes, slots=s, spawn=(0.0, 0.0, 20.0))
