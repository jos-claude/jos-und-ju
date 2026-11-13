--!strict
-- Lage der Spielobjekte an der Basis (Greybox-Platzhalter, Schritt 3 in checklisten/code-fortschritt.md).
-- Basis = (0, 0). Norden = -Z (referenz/welt-design-insel-1.md). Die Höhe (y) kommt immer
-- aus einem Raycast nach unten auf das Gelände von Jos (Terrain), nie aus dieser Datei.
-- Alles hier ist Platzhalter-Layout und darf geändert werden, ohne das Konzept zu ändern.

export type Rect = { minX: number, maxX: number, minZ: number, maxZ: number }

export type BaseLayoutConfig = {
	FOLDER_NAME: string, -- eigener Ordner im Workspace (gehört Ju, nicht Jos)

	-- Start-Halle (Raum 1). Offene Seite zeigt nach Norden (-Z), zum Spawn.
	hall: {
		centerX: number,
		centerZ: number,
		width: number, -- in X
		depth: number, -- in Z
		wallHeight: number,
		wallThickness: number,
	},

	-- Lager mit Eisen-Kasten in der Halle, davor das Abladefeld.
	storage: {
		binX: number,
		binZ: number,
		binWidth: number,
		binHeight: number,
		binDepth: number,
		dropZoneX: number,
		dropZoneZ: number,
		dropZoneWidth: number,
		dropZoneDepth: number,
		dropZoneHeight: number, -- so hoch über dem Boden zählt man noch als "auf dem Feld"
	},

	-- Regeln für Erz-Vorkommen (zusätzlich zum Ring aus Ores.luau).
	nodes: {
		minSpacing: number, -- Mindestabstand Mitte zu Mitte zwischen zwei Vorkommen
		spawnClearRadius: number, -- um jeden Spawnpunkt frei lassen
		-- Alter Spawn (0, 0) und Spawn des WorldBuilders (0, 20) (Auftrag 001, Nachtrag Jos 12.11.)
		spawnPoints: { { x: number, z: number } },
		keepOutPadding: number, -- Abstand zu Halle und Lager
		maxAttempts: number, -- Versuche pro Vorkommen, bevor aufgegeben wird
		interactDistance: number, -- Server: so nah (waagerecht) muss man zum Hacken sein
		promptDistance: number, -- ProximityPrompt-Reichweite
	},

	-- Platzhalter-Farben der Erze (bis Jos' Modelle da sind).
	oreColors: { [string]: Color3 },

	-- Kauffelder (Schritt 5 und 6): drauflaufen = kaufen. x/z = Mitte, size = Kantenlänge.
	pads: {
		size: number,
		height: number, -- so hoch über dem Boden zählt man noch als "auf dem Feld"
		drillIron: { x: number, z: number }, -- in der Start-Halle
		forgeRoom: { x: number, z: number }, -- vor der Tür der Schmiede
		pickaxe: { x: number, z: number }, -- in der Schmiede
		backpack: { x: number, z: number }, -- in der Schmiede
		lobby: { x: number, z: number }, -- Platzhalter "Lobby (später)" in der Schmiede
	},

	-- Schmiede (Raum 2) neben der Start-Halle, Front mit Tür nach Norden (-Z) wie die Halle.
	forge: {
		centerX: number,
		centerZ: number,
		width: number,
		depth: number,
		wallHeight: number,
		wallThickness: number,
		doorWidth: number,
		doorHeight: number,
	},

	-- Bohrer (Greybox): so nah (waagerecht) muss man zum Aufstellen und Abholen sein.
	drills: {
		interactDistance: number,
		promptDistance: number,
	},
}

local BaseLayout: BaseLayoutConfig = {
	FOLDER_NAME = "GMT_Gameplay",

	-- Front der Halle bei z = 30: 10 Studs Platz vor dem Spawn des WorldBuilders (0, 0, 20).
	hall = {
		centerX = 0,
		centerZ = 44,
		width = 40,
		depth = 28,
		wallHeight = 14,
		wallThickness = 1,
	},

	storage = {
		binX = 0,
		binZ = 54,
		binWidth = 8,
		binHeight = 10,
		binDepth = 5,
		dropZoneX = 0,
		dropZoneZ = 46,
		dropZoneWidth = 12,
		dropZoneDepth = 7,
		dropZoneHeight = 8,
	},

	nodes = {
		minSpacing = 24,
		spawnClearRadius = 12,
		spawnPoints = { { x = 0, z = 0 }, { x = 0, z = 20 } },
		keepOutPadding = 6,
		maxAttempts = 60,
		interactDistance = 14,
		promptDistance = 10,
	},

	oreColors = {
		iron_ore = Color3.fromRGB(196, 104, 60),
		copper_ore = Color3.fromRGB(64, 176, 160),
		coal = Color3.fromRGB(40, 36, 44),
		crystal = Color3.fromRGB(190, 110, 240),
		titanium_ore = Color3.fromRGB(200, 214, 228),
	},

	-- Halle: x -20..20, z 30..58. Abladefeld x -6..6, z 42,5..49,5.
	pads = {
		size = 7,
		height = 8,
		drillIron = { x = -12, z = 40 },
		forgeRoom = { x = 44, z = 23 },
		pickaxe = { x = 36, z = 44 },
		backpack = { x = 52, z = 44 },
		lobby = { x = 44, z = 53 },
	},

	-- Schmiede: x 28..60, z 30..58 (8 Studs Lücke zur Halle).
	forge = {
		centerX = 44,
		centerZ = 44,
		width = 32,
		depth = 28,
		wallHeight = 14,
		wallThickness = 1,
		doorWidth = 10,
		doorHeight = 10,
	},

	drills = {
		interactDistance = 14,
		promptDistance = 10,
	},
}

return BaseLayout
