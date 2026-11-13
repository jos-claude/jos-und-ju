--!strict
-- Speichern/Laden der Spielstände PRO WELT (Entscheidung 014, technik/datenspeicherung.md).
-- Beim Beitritt wird die letzte Welt des Spielers geladen; beim ersten Spielstart wird
-- automatisch die Standard-Welt angelegt.
-- In Roblox Studio läuft IMMER der Mock-Speicher (SaveStore.luau): echte Spielstände
-- werden beim Testen nie gelesen oder überschrieben.
--
-- Für andere Services:
--   DataService.GetWorld(player)  → World? (die Tabelle direkt ändern, sie wird mitgespeichert)
--   DataService.GetStats(player)  → MemberStats? (Spitzhacke, Rucksack, Getragenes)
--   DataService.OnPlayerReady(fn) → fn(player, world) sobald die Welt geladen ist
--   DataService.SaveWorld(worldId)
--   DataService.GetPlayTimeSeconds(world) → Spielzeit inkl. laufender Sitzung
--   DataService.GetPlayersInWorld(worldId) → { Player }
--
-- Attribute am Player (zum Prüfen und für den Client): WorldId, DataReady, SaveStoreKind.

local Players = game:GetService("Players")
local RunService = game:GetService("RunService")

local Modules = script.Parent.Parent:WaitForChild("Modules")
local SaveStore = require(Modules:WaitForChild("SaveStore"))
local WorldData = require(Modules:WaitForChild("WorldData"))
local WorldRepository = require(Modules:WaitForChild("WorldRepository"))

type World = WorldData.World
type MemberStats = WorldData.MemberStats

local WORLD_STORE_NAME = "GMT_Worlds_v1"
local PLAYER_STORE_NAME = "GMT_Players_v1"
local AUTOSAVE_SECONDS = 60

local DataService = {}

local repository: WorldRepository.WorldRepository
local worldsById: { [string]: World } = {}
local worldIdByPlayer: { [Player]: string } = {}
local playTimeMarks: { [string]: number } = {} -- WorldId → os.clock() der letzten Spielzeit-Zählung
local readyCallbacks: { (Player, World) -> () } = {}

local function log(message: string)
	print(`[DataService] {message}`)
end

local function addPlayTime(world: World)
	local now = os.clock()
	local mark = playTimeMarks[world.worldId]
	if mark then
		world.playTimeSeconds += now - mark
	end
	playTimeMarks[world.worldId] = now
end

local function isWorldInUse(worldId: string): boolean
	for _, id in worldIdByPlayer do
		if id == worldId then
			return true
		end
	end
	return false
end

function DataService.GetWorld(player: Player): World?
	local worldId = worldIdByPlayer[player]
	return if worldId then worldsById[worldId] else nil
end

function DataService.GetStats(player: Player): MemberStats?
	local world = DataService.GetWorld(player)
	return if world then world.memberStats[tostring(player.UserId)] else nil
end

-- Gesamte Spielzeit der Welt in Sekunden, inklusive der laufenden Sitzung (für "+1 Vorkommen alle 5 Minuten").
function DataService.GetPlayTimeSeconds(world: World): number
	local mark = playTimeMarks[world.worldId]
	return world.playTimeSeconds + (if mark then os.clock() - mark else 0)
end

-- Alle Spieler, die gerade in dieser Welt sind.
function DataService.GetPlayersInWorld(worldId: string): { Player }
	local result = {}
	for player, id in worldIdByPlayer do
		if id == worldId then
			table.insert(result, player)
		end
	end
	return result
end

function DataService.OnPlayerReady(callback: (Player, World) -> ())
	table.insert(readyCallbacks, callback)
	-- Spieler, die schon fertig geladen sind, bekommen den Aufruf sofort.
	for player, worldId in worldIdByPlayer do
		local world = worldsById[worldId]
		if world then
			task.spawn(callback, player, world)
		end
	end
end

function DataService.SaveWorld(worldId: string): boolean
	local world = worldsById[worldId]
	if not world then
		return false -- nicht (richtig) geladen → nie speichern
	end
	addPlayTime(world)
	local ok, err = repository:saveWorld(world)
	if not ok then
		warn(`[DataService] Speichern fehlgeschlagen ({worldId}): {err}`)
	end
	return ok
end

-- NUR IN STUDIO (Test "Speichern und Laden"): Welt speichern, aus dem Mock-Speicher frisch laden
-- und allen Services wie beim Beitritt melden. So wird der echte Lade-Weg geprüft, ohne das
-- Spiel zu verlassen. Im echten Spiel tut die Funktion nichts.
function DataService.ReloadWorldForTest(player: Player): boolean
	if not RunService:IsStudio() or repository.worldStore.kind ~= "mock" then
		return false
	end
	local worldId = worldIdByPlayer[player]
	if not worldId or not DataService.SaveWorld(worldId) then
		return false
	end
	local result = repository:loadOrCreateForPlayer(player.UserId)
	if not result.ok or not result.world or result.world.worldId ~= worldId then
		warn(`[DataService] Test-Neuladen fehlgeschlagen: {result.error}`)
		return false
	end
	worldsById[worldId] = result.world
	playTimeMarks[worldId] = os.clock()
	log(`{player.Name}: Welt {worldId} für den Test neu geladen`)
	for _, callback in readyCallbacks do
		task.spawn(callback, player, result.world)
	end
	return true
end

local function onPlayerAdded(player: Player)
	player:SetAttribute("SaveStoreKind", repository.worldStore.kind)
	player:SetAttribute("DataReady", false)

	local result = repository:loadOrCreateForPlayer(player.UserId)
	if player.Parent == nil then
		return -- schon wieder weg
	end
	if not result.ok or not result.world then
		warn(`[DataService] Laden fehlgeschlagen ({player.Name}): {result.error}`)
		player:Kick("Dein Spielstand konnte nicht geladen werden. Bitte versuche es gleich noch einmal.")
		return
	end

	local world = result.world
	-- Ist die Welt schon offen (Koop später), dieselbe Tabelle benutzen.
	local existing = worldsById[world.worldId]
	if existing then
		world = existing
	else
		worldsById[world.worldId] = world
		playTimeMarks[world.worldId] = os.clock()
	end
	worldIdByPlayer[player] = world.worldId

	player:SetAttribute("WorldId", world.worldId)
	player:SetAttribute("DataReady", true)
	local how = if result.created then "neue Standard-Welt angelegt" else "Welt geladen"
	log(`{player.Name}: {how} {world.worldId} (Speicher: {repository.worldStore.kind})`)

	for _, callback in readyCallbacks do
		task.spawn(callback, player, world)
	end
end

local function onPlayerRemoving(player: Player)
	local worldId = worldIdByPlayer[player]
	if not worldId then
		return
	end
	worldIdByPlayer[player] = nil
	DataService.SaveWorld(worldId)
	if not isWorldInUse(worldId) then
		worldsById[worldId] = nil
		playTimeMarks[worldId] = nil
	end
end

function DataService.Init()
	repository = WorldRepository.new(SaveStore.open(WORLD_STORE_NAME), SaveStore.open(PLAYER_STORE_NAME))
	if RunService:IsStudio() then
		log("Studio erkannt: Mock-Speicher aktiv, echte Spielstände werden nicht benutzt")
	end
end

function DataService.Start()
	Players.PlayerAdded:Connect(onPlayerAdded)
	Players.PlayerRemoving:Connect(onPlayerRemoving)
	for _, player in Players:GetPlayers() do
		task.spawn(onPlayerAdded, player)
	end

	game:BindToClose(function()
		for worldId in worldsById do
			DataService.SaveWorld(worldId)
		end
	end)

	task.spawn(function()
		while true do
			task.wait(AUTOSAVE_SECONDS)
			for worldId in worldsById do
				DataService.SaveWorld(worldId)
			end
		end
	end)
end

return DataService
