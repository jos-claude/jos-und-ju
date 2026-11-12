-- AUTOMATISCH ERZEUGT vom Weltgenerator (werkzeuge/weltgenerator). Nicht von Hand aendern.
return {
	name = "Insel 1 (Platzhalter)",
	seed = 1,
	layers = {
		topDepth = 5,
		subDepth = 14,
		bedrock = "Sandstone",
		subsoil = {
			Ground = "Mud",
		},
	},
	strata = {
		base = 0,
		bands = {
			{
				"Sandstone",
				24,
			},
			{
				"Limestone",
				8,
			},
			{
				"Slate",
				24,
			},
		},
	},
	materialColors = {
		Ground = Color3.fromRGB(242, 160, 124),
		Sandstone = Color3.fromRGB(244, 169, 196),
		Limestone = Color3.fromRGB(249, 231, 163),
		Slate = Color3.fromRGB(169, 155, 224),
		Mud = Color3.fromRGB(217, 121, 95),
	},
	water = {
		WaterColor = Color3.fromRGB(95, 227, 214),
	},
	lighting = {
		Lighting = {
			ClockTime = 16.5,
			Technology = Enum.Technology.ShadowMap,
		},
	},
	spawn = {0, 0, 20},
	grid = {
		n = 1152,
		cell = 4,
		origin = -2304,
		hmin = -512,
		hq = 4,
	},
	materials = {
		"Air",
		"Grass",
		"LeafyGrass",
		"Ground",
		"Sand",
		"Sandstone",
		"Limestone",
		"Slate",
		"Rock",
		"Basalt",
		"CrackedLava",
		"Salt",
		"Mud",
		"Snow",
		"Glacier",
		"Ice",
		"Pavement",
		"Asphalt",
		"Concrete",
		"Cobblestone",
		"Brick",
		"WoodPlanks",
	},
	chunks = {
		H = 4,
		M = 1,
		W = 1,
		S = 1,
		D = 1,
	},
	waterLevels = {},
}
