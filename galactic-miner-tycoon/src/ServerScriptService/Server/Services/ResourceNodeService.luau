--!strict
-- Erz-Vorkommen pro Welt (Entscheidungen 010, 011, 020; daten/ressourcen.md).
-- * Positionen kommen aus dem Seed der Welt (NodePlacement) und werden in der Welt gespeichert
--   (world.progress.nodes). Gespeicherte Vorkommen werden nie neu verteilt.
-- * Eisen: 3 beim Start, dann +1 alle 5 Minuten Spielzeit bis 6.
--   Erze, die erst mit einem Raum kommen (Kupfer usw.), folgen in Schritt 7.
-- * Jedes Vorkommen steht auf dem Boden: Raycast nach unten gegen das Gelände (Ground.luau).
-- * Die Modelle sind Greybox-Platzhalter in Workspace.GMT_Gameplay.OreNodes.
--
-- M1: ein Spieler (eine Welt) pro Server. Kommt eine zweite Welt dazu, wird nur gewarnt.
--
-- Für andere Services:
--   ResourceNodeService.FindNode(world, nodeId) → NodeState?
--   ResourceNodeService.GetNodeModel(nodeId) → Model?

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Shared = ReplicatedStorage:WaitForChild("Shared")
local Ores = require(Shared:WaitForChild("Config"):WaitForChild("Ores"))
local BaseLayout = require(Shared.Config:WaitForChild("BaseLayout"))
local NodePlacement = require(Shared:WaitForChild("Modules"):WaitForChild("NodePlacement"))

local Modules = script.Parent.Parent:WaitForChild("Modules")
local WorldData = require(Modules:WaitForChild("WorldData"))
local Greybox = require(Modules:WaitForChild("Greybox"))
local Ground = require(Modules:WaitForChild("Ground"))
local GameplayFolder = require(Modules:WaitForChild("GameplayFolder"))
local DataService = require(script.Parent:WaitForChild("DataService"))

type World = WorldData.World
type NodeState = WorldData.NodeState

local CHECK_INTERVAL_SECONDS = 10

local ResourceNodeService = {}

local activeWorld: World? = nil
local modelsById: { [string]: Model } = {}

local function log(message: string)
	print(`[ResourceNodeService] {message}`)
end

-- Halle und Lager freihalten (Rechteck um die Halle plus Abstand), Spawn freihalten (Kreis).
function ResourceNodeService.RulesFor(oreId: string): NodePlacement.Rules
	local def = (Ores.byId :: any)[oreId]
	local hall = BaseLayout.hall
	local pad = BaseLayout.nodes.keepOutPadding
	local clearCircles = {}
	for _, spawn in BaseLayout.nodes.spawnPoints do
		table.insert(clearCircles, { x = spawn.x, z = spawn.z, r = BaseLayout.nodes.spawnClearRadius })
	end
	return {
		minRadius = def.minRadius,
		maxRadius = def.maxRadius,
		minSpacing = BaseLayout.nodes.minSpacing,
		maxAttempts = BaseLayout.nodes.maxAttempts,
		clearCircles = clearCircles,
		clearRects = {
			{
				minX = hall.centerX - hall.width / 2 - pad,
				maxX = hall.centerX + hall.width / 2 + pad,
				minZ = hall.centerZ - hall.depth / 2 - pad,
				maxZ = hall.centerZ + hall.depth / 2 + pad,
			},
		},
	}
end

local function countNodes(world: World, oreId: string): number
	local count = 0
	for _, node in world.progress.nodes do
		if node.ore == oreId then
			count += 1
		end
	end
	return count
end

-- Wie viele Vorkommen dieses Erz jetzt haben soll (nur Erze ab Spielstart, siehe oben).
local function desiredCount(oreId: string, playTimeSeconds: number): number
	local def = (Ores.byId :: any)[oreId]
	if def.unlockRoom ~= 1 then
		return 0 -- Schritt 7: erscheinen mit dem Raum
	end
	local extra = math.floor(playTimeSeconds / def.nodeIntervalSeconds)
	return math.min(def.maxNodes, def.initialNodes + extra)
end

-- Ergänzt fehlende Vorkommen in der Welt (gespeichert). Gibt die neuen zurück.
function ResourceNodeService.EnsureNodes(world: World, playTimeSeconds: number): { NodeState }
	local added: { NodeState } = {}
	for _, oreId in Ores.order do
		local def = (Ores.byId :: any)[oreId]
		local have = countNodes(world, oreId)
		local want = desiredCount(oreId, playTimeSeconds)
		while have < want do
			local index = have + 1
			local point = NodePlacement.pick(world.mapSeed, def.tier, index, ResourceNodeService.RulesFor(oreId), world.progress.nodes)
			if not point then
				warn(`[ResourceNodeService] Kein freier Platz für {oreId} Nr. {index} (Seed {world.mapSeed})`)
				break
			end
			local node: NodeState = { nodeId = `{oreId}_{index}`, ore = oreId, x = point.x, z = point.z }
			table.insert(world.progress.nodes, node)
			table.insert(added, node)
			have += 1
		end
	end
	return added
end

function ResourceNodeService.FindNode(world: World, nodeId: string): NodeState?
	for _, node in world.progress.nodes do
		if node.nodeId == nodeId then
			return node
		end
	end
	return nil
end

function ResourceNodeService.GetNodeModel(nodeId: string): Model?
	return modelsById[nodeId]
end

local function buildModel(world: World, node: NodeState)
	if modelsById[node.nodeId] then
		return
	end
	local def = (Ores.byId :: any)[node.ore]
	local groundY, hit = Ground.heightAt(node.x, node.z)
	if not hit then
		warn(`[ResourceNodeService] Kein Boden unter {node.nodeId} ({node.x}, {node.z}), nehme y = {groundY}`)
	end
	local model = Greybox.buildOreNode(
		node.nodeId,
		node.ore,
		def.displayName,
		node.x,
		node.z,
		groundY,
		-- Form des Felsens: auch aus dem Seed, damit jedes Vorkommen anders aussieht, aber immer gleich bleibt.
		(world.mapSeed + math.floor(node.x * 10) * 31 + math.floor(node.z * 10)) % 2147483647,
		BaseLayout.oreColors[node.ore] or Color3.new(1, 1, 1),
		BaseLayout.nodes.promptDistance
	)
	model.Parent = GameplayFolder.child("OreNodes")
	modelsById[node.nodeId] = model
end

local function clearModels()
	for _, model in modelsById do
		model:Destroy()
	end
	table.clear(modelsById)
end

local function update(world: World)
	local added = ResourceNodeService.EnsureNodes(world, DataService.GetPlayTimeSeconds(world))
	for _, node in world.progress.nodes do
		buildModel(world, node)
	end
	for _, node in added do
		log(`Neues Vorkommen {node.nodeId} bei ({node.x}, {node.z})`)
	end
end

local function onPlayerReady(player: Player, world: World)
	if activeWorld and activeWorld.worldId ~= world.worldId then
		warn(`[ResourceNodeService] {player.Name} hat eine andere Welt; M1 zeigt nur eine Welt pro Server`)
		return
	end
	activeWorld = world
	update(world)
	log(`{#world.progress.nodes} Vorkommen für Welt {world.worldId} (Seed {world.mapSeed})`)
end

local function onPlayerRemoving(_player: Player)
	task.defer(function()
		local world = activeWorld
		if world and #DataService.GetPlayersInWorld(world.worldId) == 0 then
			activeWorld = nil
			clearModels()
		end
	end)
end

function ResourceNodeService.Init() end

function ResourceNodeService.Start()
	DataService.OnPlayerReady(onPlayerReady)
	Players.PlayerRemoving:Connect(onPlayerRemoving)

	task.spawn(function()
		while true do
			task.wait(CHECK_INTERVAL_SECONDS)
			local world = activeWorld
			if world then
				update(world)
			end
		end
	end)
end

return ResourceNodeService
