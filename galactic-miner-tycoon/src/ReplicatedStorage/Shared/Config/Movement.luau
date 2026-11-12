--!strict
-- Bewegung und Physik auf Insel 1. Muss zu daten/bewegung.md passen.
-- Konzept: spiel/17-bewegung-und-physik.md · Entscheidung 017.
-- Roblox-Standard zum Vergleich: Gravity 196,2 · JumpHeight 7,2 · WalkSpeed 16.

export type MovementConfig = {
	gravity: number,
	jumpHeight: number,
	walkSpeed: number,

	groundAccelTime: number,
	groundDecelTime: number,
	airControlTime: number,

	landingDust: boolean,
	landingDustMinSpeed: number,
	landingDustFallbackColor: Color3,
}

local Movement: MovementConfig = {
	-- Schwerkraft in Studs/s². Erde (Roblox-Standard) 196,2, Mond 32,7.
	-- 110 ist gut die Hälfte: deutlich leichter als auf der Erde, aber kein Mond.
	gravity = 110,
	-- Sprunghöhe in Studs. Mit gravity 110 dauert ein Sprung ca. 0,8 s (Standard 0,54 s).
	jumpHeight = 9,
	-- Laufgeschwindigkeit in Studs/s. Training (Raum 5) gibt später +2 je Stufe (daten/upgrades.md).
	walkSpeed = 16,

	-- Trägheit: Sekunden, bis die Bewegung zu ca. 95 % dem Eingabewunsch folgt.
	groundAccelTime = 0.25, -- Anlaufen auf dem Boden
	groundDecelTime = 0.35, -- Abbremsen auf dem Boden (man rutscht ca. 2 Studs nach)
	airControlTime = 0.9, -- Lenken in der Luft (Schwung bleibt erhalten)

	-- Staubwolke bei der Landung (nur für den eigenen Charakter).
	landingDust = true,
	landingDustMinSpeed = 18, -- erst ab dieser Fallgeschwindigkeit (Studs/s), kleine Stufen stauben nicht
	landingDustFallbackColor = Color3.fromRGB(240, 170, 120), -- Pfirsich-Orange von Insel 1
}

return Movement
