"""Datenmodell der Welt: Hoehen-Raster, Materialien, Wasser, Zusatzformen, Deko."""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

# Reihenfolge ist Teil des Datenformats (Index im Material-Kanal). Nur hinten anfuegen!
TERRAIN_MATERIALS = [
    "Air", "Grass", "LeafyGrass", "Ground", "Sand", "Sandstone", "Limestone", "Slate",
    "Rock", "Basalt", "CrackedLava", "Salt", "Mud", "Snow", "Glacier", "Ice",
    "Pavement", "Asphalt", "Concrete", "Cobblestone", "Brick", "WoodPlanks",
]
MAT = {name: i for i, name in enumerate(TERRAIN_MATERIALS)}
STRATA_FLAG = 32  # Bit im Material-Kanal: Spalte benutzt Gesteinsschichten nach Hoehe

CELL = 4.0          # Studs pro Spalte (= Roblox-Voxelgroesse)
HALF = 2304.0       # Karte reicht von -HALF bis +HALF in X und Z
N = int(2 * HALF / CELL)  # 1152 Spalten je Achse
HMIN = -512.0       # kleinste speicherbare Hoehe
HQ = 4.0            # Hoehen-Quantisierung: 1/4 Stud
VOID = HMIN         # Hoehe <= VOID bedeutet: kein Terrain in dieser Spalte


class RGB(tuple):
    """Farbe 0..255. Wird in Luau zu Color3.fromRGB, im JSON zu [r, g, b]."""

    def __new__(cls, r, g=None, b=None):
        if g is None:  # Hex-String "#RRGGBB"
            h = str(r).lstrip("#")
            r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        return super().__new__(cls, (int(r), int(g), int(b)))


class Enum(str):
    """Roblox-Enum-Wert, z. B. Enum("Technology", "Future")."""

    def __new__(cls, enum_type, value):
        obj = super().__new__(cls, f"Enum.{enum_type}.{value}")
        obj.enum_type = enum_type
        obj.value = value
        return obj


def rot_y(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def rot_x(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def rot_z(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def angles(rx, ry, rz):
    """Wie Roblox CFrame.Angles(rx, ry, rz) = Rx * Ry * Rz."""
    return rot_x(rx) @ rot_y(ry) @ rot_z(rz)


@dataclass
class PartDef:
    shape: str                    # Block | Ball | Cylinder | Wedge | Ellipsoid
    size: tuple                   # (x, y, z) in Studs (Cylinder: Laenge entlang X)
    pos: tuple = (0.0, 0.0, 0.0)  # Lage relativ zum Fusspunkt des Modells
    rot: np.ndarray = field(default_factory=lambda: np.eye(3))
    role: str = "main"            # Farbrolle (Farbe kommt aus der Variante)
    material: str = "SmoothPlastic"
    transparency: float = 0.0
    reflectance: float = 0.0
    cast_shadow: bool = True
    collide: bool = False
    light: dict | None = None     # {"range":, "brightness":, "role" oder "color":}
    particles: dict | None = None  # Wunsch an den Builder: ParticleEmitter (z. B. Dampf), siehe README


@dataclass
class Template:
    name: str
    category: str
    parts: list[PartDef]
    variants: list[dict]          # [{role: (r, g, b) 0..255}]


@dataclass
class World:
    seed: int
    h: np.ndarray = field(default_factory=lambda: np.full((N, N), VOID))     # [iz, ix]
    mat: np.ndarray = field(default_factory=lambda: np.zeros((N, N), np.uint8))
    water: np.ndarray = field(default_factory=lambda: np.zeros((N, N), np.uint8))
    strata_off: np.ndarray = field(default_factory=lambda: np.zeros((N, N), np.uint8))  # Studs, modulo Periode (0..239)
    depth: np.ndarray = field(default_factory=lambda: np.full((N, N), 4, np.uint8))     # Einheit 4 Studs
    water_levels: list[float] = field(default_factory=list)
    terrain_ops: list[dict] = field(default_factory=list)
    templates: dict[str, Template] = field(default_factory=dict)
    placements: list[tuple] = field(default_factory=list)  # (name, x, y, z, ry, rx, rz, s, variant)
    meta: dict = field(default_factory=dict)

    @staticmethod
    def coords():
        c = -HALF + CELL / 2 + CELL * np.arange(N)
        x, z = np.meshgrid(c, c)  # x[iz, ix], z[iz, ix]
        return x, z

    def height_at(self, x, z):
        """Bilineare Hoehe an Weltposition (fuer Deko-Platzierung)."""
        fx = (np.asarray(x) + HALF - CELL / 2) / CELL
        fz = (np.asarray(z) + HALF - CELL / 2) / CELL
        ix = np.clip(np.floor(fx).astype(int), 0, N - 2)
        iz = np.clip(np.floor(fz).astype(int), 0, N - 2)
        tx = np.clip(fx - ix, 0, 1)
        tz = np.clip(fz - iz, 0, 1)
        h = self.h
        a = h[iz, ix] * (1 - tx) + h[iz, ix + 1] * tx
        b = h[iz + 1, ix] * (1 - tx) + h[iz + 1, ix + 1] * tx
        return a * (1 - tz) + b * tz

    def index_of(self, x, z):
        ix = np.clip(((np.asarray(x) + HALF) / CELL).astype(int), 0, N - 1)
        iz = np.clip(((np.asarray(z) + HALF) / CELL).astype(int), 0, N - 1)
        return iz, ix

    def add_template(self, t: Template):
        self.templates[t.name] = t

    def place(self, name, x, y, z, ry=0.0, rx=0.0, rz=0.0, s=1.0, variant=0):
        self.placements.append((name, float(x), float(y), float(z), float(ry), float(rx), float(rz), float(s), int(variant)))

    def add_water_level(self, level: float) -> int:
        self.water_levels.append(float(level))
        return len(self.water_levels)  # Kanalwert (0 = kein Wasser)

    def finalize_depth(self, extra=12.0, min_depth=12.0):
        """Wie tief jede Spalte gefuellt wird: bis unter den tiefsten Nachbarn (keine Loecher in Steilwaenden)."""
        h = self.h
        p = np.pad(h, 1, mode="edge")
        mn = h.copy()
        for dz in (-1, 0, 1):
            for dx in (-1, 0, 1):
                mn = np.minimum(mn, p[1 + dz:1 + dz + N, 1 + dx:1 + dx + N])
        mn = np.where(mn <= VOID, h, mn)
        d = np.maximum(h - mn + extra, min_depth)
        cur = self.depth.astype(np.float64) * CELL
        d = np.maximum(d, cur)
        self.depth = np.clip(np.ceil(d / CELL), 1, 255).astype(np.uint8)
