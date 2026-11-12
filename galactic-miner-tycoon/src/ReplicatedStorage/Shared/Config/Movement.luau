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
	-- 60 ist knapp ein Drittel: klar spürbar leichter als auf der Erde, aber noch kein Mond.
	gravity = 60,
	-- Sprunghöhe in Studs. Mit gravity 60 dauert ein Sprung ca. 1,3 s (Standard 0,54 s).
	jumpHeight = 12,
	-- Laufgeschwindigkeit in Studs/s. Training (Raum 5) gibt später +2 je Stufe (daten/upgrades.md).
	walkSpeed = 16,

	-- Trägheit: Sekunden, bis die Bewegung zu ca. 95 % dem Eingabewunsch folgt.
	groundAccelTime = 0.4, -- Anlaufen auf dem Boden
	groundDecelTime = 0.55, -- Abbremsen auf dem Boden (man rutscht ca. 3 Studs nach)
	airControlTime = 1.6, -- Lenken in der Luft (Schwung bleibt erhalten)

	-- Staubwolke bei der Landung (nur für den eigenen Charakter).
	landingDust = true,
	landingDustMinSpeed = 18, -- erst ab dieser Fallgeschwindigkeit (Studs/s), kleine Stufen stauben nicht
	landingDustFallbackColor = Color3.fromRGB(240, 170, 120), -- Pfirsich-Orange von Insel 1
}

return Movement
