--!strict
-- Basis auf Insel 1: Start-Halle (Raum 1) und Lager mit Eisen-Kasten als Greybox in Workspace.GMT_Gameplay.
-- Konzept: spiel/02-heimatplanet.md, spiel/16-raeume-und-spitzhacke.md, daten/gebaeude.md (Kästen).
-- Die Höhe kommt aus dem Gelände von Jos (Raycast); fehlt es, steht alles auf der alten Baseplate (y = 0).
-- Abladefeld vor dem Kasten: drauflaufen = Getragenes wandert in den Kasten (Schritt 4).
--
-- Für andere Services:
--   BaseService.RefreshBins(world) → Kasten-Anzeige und Attribute aller Spieler der Welt neu setzen

local Players = game:GetService("Players")
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
local Remotes = require(Modules:WaitForChild("Remotes"))
local DataService = require(script.Parent:WaitForChild("DataService"))

type World = WorldData.World

local IRON_BIN_ID = "bin_iron"
local DEPOSIT_CHECK_SECONDS = 0.2 -- so oft wird geprüft, ob jemand auf dem Abladefeld steht
local FULL_NOTICE_SECONDS = 2 -- "Kasten voll" höchstens alle 2 s melden

-- DepositResult  Server → Client (oreId, moved, binAmount, binCapacity, reason "ok" | "bin_full")
local depositEvent: RemoteEvent

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

-- Abladefeld (Schritt 4): Wer mit Erz auf dem Feld steht, legt alles in die passenden Kästen,
-- bis der Kasten voll ist (Entscheidung 010, Punkt 5). Ohne Kasten bleibt das Erz in der Hand.
local function isOnDropZone(player: Player): boolean
	local character = player.Character
	local root = character and character:FindFirstChild("HumanoidRootPart")
	if not root or not root:IsA("BasePart") then
		return false
	end
	local s = BaseLayout.storage
	local rel = root.Position - Vector3.new(s.dropZoneX, groundY, s.dropZoneZ)
	return math.abs(rel.X) <= s.dropZoneWidth / 2 + 1
		and math.abs(rel.Z) <= s.dropZoneDepth / 2 + 1
		and rel.Y >= -2
		and rel.Y <= s.dropZoneHeight
end

local lastFullNoticeAt: { [Player]: number } = {}

local function tryDeposit(player: Player)
	local world = DataService.GetWorld(player)
	local stats = DataService.GetStats(player)
	if not world or not stats or PlayerState.carriedTotal(stats) <= 0 then
		return
	end
	if not isOnDropZone(player) then
		return
	end
	local changed = false
	for _, oreId in Ores.order do
		local carried = stats.carried[oreId] or 0
		local binId = (Bins.byOre :: any)[oreId]
		local state = world.progress.bins[binId]
		if carried > 0 and state then
			local capacity = PlayerState.binCapacity(binId, state)
			local moved = math.min(carried, capacity - state.amount)
			if moved > 0 then
				state.amount += moved
				stats.carried[oreId] = carried - moved
				changed = true
				local reason = if stats.carried[oreId] > 0 then "bin_full" else "ok"
				depositEvent:FireClient(player, oreId, moved, state.amount, capacity, reason)
			else
				local now = os.clock()
				if not lastFullNoticeAt[player] or now - lastFullNoticeAt[player] > FULL_NOTICE_SECONDS then
					lastFullNoticeAt[player] = now
					depositEvent:FireClient(player, oreId, 0, state.amount, capacity, "bin_full")
				end
			end
		end
	end
	if changed then
		PlayerState.refreshCarry(player, stats)
		BaseService.RefreshBins(world)
	end
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
	depositEvent = Remotes.event("DepositResult")
end

function BaseService.Start()
	buildBase()
	DataService.OnPlayerReady(onPlayerReady)
	Players.PlayerRemoving:Connect(function(player)
		lastFullNoticeAt[player] = nil
	end)
	task.spawn(function()
		while true do
			task.wait(DEPOSIT_CHECK_SECONDS)
			for _, player in Players:GetPlayers() do
				tryDeposit(player)
			end
		end
	end)
end

return BaseService
