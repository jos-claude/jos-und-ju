--!strict
-- Basis auf Insel 1: Start-Halle (Raum 1) und Lager mit Eisen-Kasten als Greybox in Workspace.GMT_Gameplay.
-- Konzept: spiel/02-heimatplanet.md, spiel/16-raeume-und-spitzhacke.md, daten/gebaeude.md (Kästen).
-- Die Höhe kommt aus dem Gelände von Jos (Raycast); fehlt es, steht alles auf der alten Baseplate (y = 0).
--
-- Für andere Services:
--   BaseService.RefreshBins(world) → Kasten-Anzeige und Attribute aller Spieler der Welt neu setzen

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Config = ReplicatedStorage:WaitForChild("Shared"):WaitForChild("Config")
local BaseLayout = require(Config:WaitForChild("BaseLayout"))
local Bins = require(Config:WaitForChild("Bins"))
local Ores = require(Config:WaitForChild("Ores"))

local Modules = script.Parent.Parent:WaitForChild("Modules")
local WorldData = require(Modules:WaitForChild("WorldData"))
local Greybox = require(Modules:WaitForChild("Greybox"))
local Ground = require(Modules:WaitForChild("Ground"))
local GameplayFolder = require(Modules:WaitForChild("GameplayFolder"))
local PlayerState = require(Modules:WaitForChild("PlayerState"))
local DataService = require(script.Parent:WaitForChild("DataService"))

type World = WorldData.World

local IRON_BIN_ID = "bin_iron"

local BaseService = {}

local displayedWorldId: string? = nil
local ironBin: Greybox.StorageBin? = nil
local groundY = 0

local function log(message: string)
	print(`[BaseService] {message}`)
end

local function oreName(oreId: string): string
	return ((Ores.byId :: any)[oreId]).displayName
end

local function updateBinDisplay(world: World)
	if not ironBin or displayedWorldId ~= world.worldId then
		return
	end
	local state = world.progress.bins[IRON_BIN_ID]
	local ore = Bins.byId[IRON_BIN_ID].ore
	if state then
		Greybox.setBinFill(ironBin, "Eisen", state.amount, PlayerState.binCapacity(IRON_BIN_ID, state))
	else
		Greybox.setBinFill(ironBin, "Eisen", 0, 0)
	end
	ironBin.model:SetAttribute("Ore", ore)
end

function BaseService.RefreshBins(world: World)
	updateBinDisplay(world)
	for _, player in DataService.GetPlayersInWorld(world.worldId) do
		PlayerState.refreshBins(player, world)
	end
end

function BaseService.GetGroundY(): number
	return groundY
end

local function buildBase()
	local root = GameplayFolder.get()
	local hall = BaseLayout.hall
	local hit
	groundY, hit = Ground.heightAt(hall.centerX, hall.centerZ)
	if not hit then
		warn(`[BaseService] Kein Gelände unter der Halle gefunden, nehme y = {groundY}`)
	end
	Greybox.buildHall(root, hall, groundY)
	local ore = Bins.byId[IRON_BIN_ID].ore
	ironBin = Greybox.buildStorage(
		root,
		BaseLayout.storage,
		IRON_BIN_ID,
		oreName(ore),
		BaseLayout.oreColors[ore] or Color3.new(1, 1, 1),
		groundY
	)
	if ironBin then
		Greybox.setBinFill(ironBin, "Eisen", 0, 0)
	end
	log(`Start-Halle und Lager gebaut (Boden y = {string.format("%.2f", groundY)}, Gelände gefunden: {hit})`)
end

local function onPlayerReady(player: Player, world: World)
	if displayedWorldId == nil then
		displayedWorldId = world.worldId
	end
	BaseService.RefreshBins(world)
	PlayerState.refreshBins(player, world)
end

function BaseService.Init()
	-- In Init (läuft vor allen Start()), damit kein anderer Service schon etwas hineingebaut hat.
	GameplayFolder.reset()
end

function BaseService.Start()
	buildBase()
	DataService.OnPlayerReady(onPlayerReady)
end

return BaseService
