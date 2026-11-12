--!strict
-- Planeten-Physik: Schwerkraft für die ganze Welt und Grundwerte für jeden Charakter.
-- Das Planeten-Gefühl beim Steuern (Trägheit, Schwung, Staub) macht der MovementController auf dem Client.
-- Konzept: spiel/17-bewegung-und-physik.md · Zahlen: Shared/Config/Movement.luau

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Movement = require(ReplicatedStorage.Shared.Config.Movement)

local MovementService = {}

local function applyToCharacter(character: Model)
	local humanoid = character:WaitForChild("Humanoid", 10)
	if not humanoid or not humanoid:IsA("Humanoid") then
		return
	end
	humanoid.UseJumpPower = false
	humanoid.JumpHeight = Movement.jumpHeight
	humanoid.WalkSpeed = Movement.walkSpeed
end

local function onPlayerAdded(player: Player)
	player.CharacterAdded:Connect(applyToCharacter)
	if player.Character then
		task.spawn(applyToCharacter, player.Character)
	end
end

function MovementService.Init()
	-- Gilt für alles, was nicht verankert ist (Spieler, Erzbrocken, später der Rover).
	-- Der Wert wird automatisch an alle Clients übertragen.
	workspace.Gravity = Movement.gravity
end

function MovementService.Start()
	Players.PlayerAdded:Connect(onPlayerAdded)
	for _, player in Players:GetPlayers() do
		onPlayerAdded(player)
	end
end

return MovementService
