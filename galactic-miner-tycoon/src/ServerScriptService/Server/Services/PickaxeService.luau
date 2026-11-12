--!strict
-- Handabbau mit der Spitzhacke (spiel/16-raeume-und-spitzhacke.md, Entscheidungen 016, 017, 020).
-- Der Client meldet einen Schlag auf ein Vorkommen, der Server prüft alles und gibt das Erz
-- in den Tragevorrat. Vorkommen werden beim Handabbau nicht leer.
--
-- Prüfungen je Schlag: Welt geladen, Vorkommen gehört zur Welt, Spieler nah genug, Schlagtempo
-- eingehalten, Spitzhacke stark genug, Kasten für das Erz gekauft, Tragevorrat nicht voll.
--
-- Remotes (ReplicatedStorage.GMT_Remotes):
--   SwingPickaxe   Client → Server (nodeId)
--   PickaxeResult  Server → Client (nodeId, gained, carriedTotal, capacity, reason)
--     reason: "ok" | "full" | "cooldown" | "too_far" | "too_hard" | "no_bin" | "unknown"

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Config = ReplicatedStorage:WaitForChild("Shared"):WaitForChild("Config")
local Ores = require(Config:WaitForChild("Ores"))
local Bins = require(Config:WaitForChild("Bins"))
local BaseLayout = require(Config:WaitForChild("BaseLayout"))

local Modules = script.Parent.Parent:WaitForChild("Modules")
local WorldData = require(Modules:WaitForChild("WorldData"))
local PlayerState = require(Modules:WaitForChild("PlayerState"))
local Remotes = require(Modules:WaitForChild("Remotes"))
local DataService = require(script.Parent:WaitForChild("DataService"))
local ResourceNodeService = require(script.Parent:WaitForChild("ResourceNodeService"))

type World = WorldData.World

-- Etwas Spielraum beim Tempo, weil Netzwerk-Pakete schwanken (0,85 = 15 % schneller erlaubt).
local SWING_TOLERANCE = 0.85

local PickaxeService = {}

local lastSwingAt: { [Player]: number } = {}
local resultEvent: RemoteEvent

-- Erz pro Schlag mit Härte-Malus, auf ganze Zahlen gerundet, mindestens 1.
function PickaxeService.OrePerHit(orePerHit: number, hardness: number): number
	return math.max(1, math.floor(orePerHit * hardness + 0.5))
end

local function reply(player: Player, nodeId: string, gained: number, total: number, capacity: number, reason: string)
	resultEvent:FireClient(player, nodeId, gained, total, capacity, reason)
end

local function onSwing(player: Player, nodeId: any)
	if type(nodeId) ~= "string" or #nodeId > 64 then
		return
	end
	local world = DataService.GetWorld(player)
	local stats = DataService.GetStats(player)
	if not world or not stats then
		return
	end

	local capacity = PlayerState.carryCapacity(stats)
	local total = PlayerState.carriedTotal(stats)

	local node = ResourceNodeService.FindNode(world, nodeId)
	if not node then
		reply(player, nodeId, 0, total, capacity, "unknown")
		return
	end

	local character = player.Character
	local root = character and character:FindFirstChild("HumanoidRootPart")
	if not root or not root:IsA("BasePart") then
		return
	end
	local dx, dz = root.Position.X - node.x, root.Position.Z - node.z
	if math.sqrt(dx * dx + dz * dz) > BaseLayout.nodes.interactDistance then
		reply(player, nodeId, 0, total, capacity, "too_far")
		return
	end

	local pick = PlayerState.pickaxeLevel(stats)
	local now = os.clock()
	local last = lastSwingAt[player]
	if last and now - last < pick.swingSeconds * SWING_TOLERANCE then
		reply(player, nodeId, 0, total, capacity, "cooldown")
		return
	end

	local ore = (Ores.byId :: any)[node.ore]
	if ore.minPickaxeLevel == nil or ore.handHardness == nil or pick.level < ore.minPickaxeLevel then
		reply(player, nodeId, 0, total, capacity, "too_hard")
		return
	end
	if world.progress.bins[(Bins.byOre :: any)[node.ore]] == nil then
		reply(player, nodeId, 0, total, capacity, "no_bin")
		return
	end
	if total >= capacity then
		reply(player, nodeId, 0, total, capacity, "full")
		return
	end

	lastSwingAt[player] = now
	local gained = math.min(capacity - total, PickaxeService.OrePerHit(pick.orePerHit, ore.handHardness))
	stats.carried[node.ore] = (stats.carried[node.ore] or 0) + gained
	PlayerState.refreshCarry(player, stats)
	reply(player, nodeId, gained, total + gained, capacity, "ok")
end

function PickaxeService.Init()
	resultEvent = Remotes.event("PickaxeResult")
	Remotes.event("SwingPickaxe").OnServerEvent:Connect(onSwing)
end

function PickaxeService.Start()
	DataService.OnPlayerReady(function(player: Player, _world: World)
		local stats = DataService.GetStats(player)
		if stats then
			PlayerState.refreshCarry(player, stats)
		end
	end)
	game:GetService("Players").PlayerRemoving:Connect(function(player)
		lastSwingAt[player] = nil
	end)
end

return PickaxeService
