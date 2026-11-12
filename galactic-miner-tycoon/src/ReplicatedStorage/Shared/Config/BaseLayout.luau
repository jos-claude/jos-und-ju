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
		spawnClearRadius: number, -- um den Spawnpunkt (0, 0) frei lassen
		keepOutPadding: number, -- Abstand zu Halle und Lager
		maxAttempts: number, -- Versuche pro Vorkommen, bevor aufgegeben wird
		interactDistance: number, -- Server: so nah (waagerecht) muss man zum Hacken sein
		promptDistance: number, -- ProximityPrompt-Reichweite
	},

	-- Platzhalter-Farben der Erze (bis Jos' Modelle da sind).
	oreColors: { [string]: Color3 },
}

local BaseLayout: BaseLayoutConfig = {
	FOLDER_NAME = "GMT_Gameplay",

	hall = {
		centerX = 0,
		centerZ = 30,
		width = 40,
		depth = 28,
		wallHeight = 14,
		wallThickness = 1,
	},

	storage = {
		binX = 0,
		binZ = 40,
		binWidth = 8,
		binHeight = 10,
		binDepth = 5,
		dropZoneX = 0,
		dropZoneZ = 32,
		dropZoneWidth = 12,
		dropZoneDepth = 7,
		dropZoneHeight = 8,
	},

	nodes = {
		minSpacing = 24,
		spawnClearRadius = 12,
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
}

return BaseLayout
