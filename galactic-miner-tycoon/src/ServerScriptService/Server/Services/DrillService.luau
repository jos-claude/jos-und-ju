--!strict
-- Bohrer auf Erz-Vorkommen (Schritt 5; spiel/03, Entscheidungen 010, 016, 020; daten/gebaeude.md).
-- * Gekauft wird am Kauffeld (ShopService). Gekaufte, noch nicht aufgestellte Bohrer zählen sich aus
--   world.progress.drillsBought minus aufgestellte Bohrer (kein eigenes Feld nötig).
-- * Aufstellen: am freien Vorkommen "Bohrer aufstellen" (ProximityPrompt, Taste F). Ein Bohrer pro Vorkommen.
-- * Der Bohrer fördert Grundrate × Stufen-Faktor in seinen Puffer, bis der Puffer voll ist (dann stoppt er).
-- * Abholen: am Bohrer "Erz holen" (Taste F) → so viel in den Tragevorrat, wie hineinpasst.
-- * Zustand steht in world.progress.drills (nodeId, drillId, level, buffer) und wird mitgespeichert.
-- Alles prüft der Server. Der Client bekommt nur Rückmeldungen für Ton und Animation.
--
-- Remotes (ReplicatedStorage.GMT_Remotes):
--   DrillResult  Server → Client (kind, nodeId, amount)
--     kind: "placed" | "taken" | "empty" | "full" | "no_drill" | "occupied" | "too_far"
--
-- Attribute am Player: DrillsToPlace (gekauft, noch nicht aufgestellt, alle Erze zusammen)
--
-- Für andere Services:
--   DrillService.CountPlaced(world, drillId), DrillService.CountUnplaced(world, drillId)
--   DrillService.FreeNodeCount(world, oreId) → Vorkommen ohne Bohrer
--   DrillService.Refresh(world) → Prompts und Attribute neu setzen (z. B. nach einem Kauf)

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Config = ReplicatedStorage:WaitForChild("Shared"):WaitForChild("Config")
local Drills = require(Config:WaitForChild("Drills"))
local Ores = require(Config:WaitForChild("Ores"))
local BaseLayout = require(Config:WaitForChild("BaseLayout"))
local Shop = require(Config:WaitForChild("Shop"))

local Modules = script.Parent.Parent:WaitForChild("Modules")
local WorldData = require(Modules:WaitForChild("WorldData"))
local GreyboxDrill = require(Modules:WaitForChild("GreyboxDrill"))
local Ground = require(Modules:WaitForChild("Ground"))
local GameplayFolder = require(Modules:WaitForChild("GameplayFolder"))
local PlayerState = require(Modules:WaitForChild("PlayerState"))
local Remotes = require(Modules:WaitForChild("Remotes"))
local DataService = require(script.Parent:WaitForChild("DataService"))
local ResourceNodeService = require(script.Parent:WaitForChild("ResourceNodeService"))

type World = WorldData.World
type DrillState = WorldData.DrillState
type NodeState = WorldData.NodeState

local TICK_SECONDS = 0.1 -- so oft wird der Puffer weitergezählt
local PROMPT_SYNC_SECONDS = 0.5 -- so oft werden die "Bohrer aufstellen"-Prompts geprüft (neue Vorkommen)
local PLACE_HOLD_SECONDS = 0.3 -- kurz halten, damit man nicht aus Versehen aufstellt

local DrillService = {}

local resultEvent: RemoteEvent
local activeWorld: World? = nil
local modelsByNode: { [string]: GreyboxDrill.DrillModel } = {}
local fraction: { [string]: number } = {} -- NodeId → angefangenes Erz (nicht gespeichert, < 1)
local placePrompts: { [string]: ProximityPrompt } = {} -- NodeId → Prompt am Felsen
local offlineApplied: { [World]: boolean } = setmetatable({}, { __mode = "k" }) :: any

local function log(message: string)
	print(`[DrillService] {message}`)
end

local function drillDef(drillId: string): Drills.DrillDef
	return (Drills.byId :: any)[drillId]
end

local function levelOf(state: DrillState): Drills.DrillLevel
	local def = drillDef(state.drillId)
	return def.levels[state.level] or def.levels[1]
end

local function ratePerSecond(state: DrillState): number
	return drillDef(state.drillId).baseRate * levelOf(state).rateFactor
end

local function capacityOf(state: DrillState): number
	return levelOf(state).buffer
end

local function findDrill(world: World, nodeId: string): DrillState?
	for _, state in world.progress.drills do
		if state.nodeId == nodeId then
			return state
		end
	end
	return nil
end

function DrillService.CountPlaced(world: World, drillId: string): number
	local count = 0
	for _, state in world.progress.drills do
		if state.drillId == drillId then
			count += 1
		end
	end
	return count
end

function DrillService.CountUnplaced(world: World, drillId: string): number
	local bought = world.progress.drillsBought[drillId] or 0
	return math.max(0, bought - DrillService.CountPlaced(world, drillId))
end

function DrillService.FreeNodeCount(world: World, oreId: string): number
	local free = 0
	for _, node in world.progress.nodes do
		if node.ore == oreId and findDrill(world, node.nodeId) == nil then
			free += 1
		end
	end
	return free
end

local function totalUnplaced(world: World): number
	local total = 0
	for _, drillId in Drills.order do
		total += DrillService.CountUnplaced(world, drillId)
	end
	return total
end

local function rootDistance(player: Player, x: number, z: number): number?
	local character = player.Character
	local root = character and character:FindFirstChild("HumanoidRootPart")
	if not root or not root:IsA("BasePart") then
		return nil
	end
	local dx, dz = root.Position.X - x, root.Position.Z - z
	return math.sqrt(dx * dx + dz * dz)
end

-- Modelle ------------------------------------------------------------------------------------------

local function updateDisplay(state: DrillState)
	local drill = modelsByNode[state.nodeId]
	if drill then
		GreyboxDrill.setBuffer(drill, state.buffer, capacityOf(state))
	end
end

local onTake: (Player, string) -> ()

local function buildModel(world: World, state: DrillState)
	if modelsByNode[state.nodeId] then
		return
	end
	local node = ResourceNodeService.FindNode(world, state.nodeId)
	local nodeModel = ResourceNodeService.GetNodeModel(state.nodeId)
	if not node or not nodeModel then
		return -- Vorkommen-Modell noch nicht gebaut; der nächste Sync versucht es wieder
	end
	local groundY = (nodeModel:GetAttribute("GroundY") :: number?) or 0
	local oreColor = BaseLayout.oreColors[node.ore] or Color3.new(1, 1, 1)
	local folder = GameplayFolder.child("Drills")
	local drill: GreyboxDrill.DrillModel? = nil
	local modelName = BaseLayout.drills.modelName
	if modelName then
		-- Fehler beim 3D-Modell dürfen die Bohrer-Schleife nie anhalten: abfangen, dann Greybox.
		local ok, result = pcall(function(): GreyboxDrill.DrillModel?
			-- 3D-Modell: Sockel auf der Außenseite des Felsens (weg von der Basis). Dort stehen sicher keine
			-- Gebäude, weil Vorkommen Abstand zu Halle und Schmiede halten.
			local hall = BaseLayout.hall
			return GreyboxDrill.buildFromModel(
				modelName,
				folder,
				state.nodeId,
				state.drillId,
				node.x,
				node.z,
				Vector3.new(node.x - hall.centerX, 0, node.z - hall.centerZ),
				BaseLayout.drills.modelOffset,
				function(x: number, z: number): number
					return (Ground.heightAt(x, z))
				end,
				oreColor,
				BaseLayout.drills.promptDistance
			)
		end)
		if ok then
			drill = result
		else
			warn(`[DrillService] 3D-Modell {modelName} für {state.nodeId} gescheitert, nehme Greybox: {result}`)
		end
	end
	if not drill then
		drill = GreyboxDrill.buildDrill(
			folder,
			state.nodeId,
			state.drillId,
			node.x,
			node.z,
			groundY,
			oreColor,
			BaseLayout.drills.promptDistance
		)
	end
	assert(drill, "Bohrer-Modell fehlt")
	drill.prompt.Triggered:Connect(function(player: Player)
		onTake(player, state.nodeId)
	end)
	modelsByNode[state.nodeId] = drill
	updateDisplay(state)
end

local function clearModels()
	for _, drill in modelsByNode do
		drill.model:Destroy()
	end
	table.clear(modelsByNode)
	for _, prompt in placePrompts do
		prompt:Destroy()
	end
	table.clear(placePrompts)
	table.clear(fraction)
end

-- Prompts und Attribute ----------------------------------------------------------------------------

local onPlace: (Player, string) -> ()

local function ensurePlacePrompt(node: NodeState): ProximityPrompt?
	local existing = placePrompts[node.nodeId]
	if existing and existing.Parent then
		return existing
	end
	local nodeModel = ResourceNodeService.GetNodeModel(node.nodeId)
	local rock = nodeModel and nodeModel.PrimaryPart
	if not rock then
		return nil
	end
	local prompt = Instance.new("ProximityPrompt")
	prompt.Name = "PlaceDrillPrompt"
	prompt.ActionText = "Bohrer aufstellen"
	prompt.ObjectText = (Ores.byId :: any)[node.ore].displayName
	prompt.HoldDuration = PLACE_HOLD_SECONDS
	prompt.KeyboardKeyCode = Enum.KeyCode.F
	prompt.GamepadKeyCode = Enum.KeyCode.ButtonY
	prompt.MaxActivationDistance = BaseLayout.drills.promptDistance
	prompt.RequiresLineOfSight = false
	prompt.UIOffset = Vector2.new(0, -60)
	prompt.Enabled = false
	prompt.Triggered:Connect(function(player: Player)
		onPlace(player, node.nodeId)
	end)
	prompt.Parent = rock
	placePrompts[node.nodeId] = prompt
	return prompt
end

function DrillService.Refresh(world: World)
	if activeWorld ~= world then
		return
	end
	for _, state in world.progress.drills do
		buildModel(world, state)
	end
	for _, node in world.progress.nodes do
		local prompt = ensurePlacePrompt(node)
		if prompt then
			local drillId = (Drills.byOre :: any)[node.ore]
			local occupied = findDrill(world, node.nodeId) ~= nil
			prompt.Enabled = not occupied and drillId ~= nil and DrillService.CountUnplaced(world, drillId) > 0
		end
	end
	local unplaced = totalUnplaced(world)
	for _, player in DataService.GetPlayersInWorld(world.worldId) do
		player:SetAttribute("DrillsToPlace", unplaced)
	end
end

-- Aufstellen und Abholen (Server prüft alles) ------------------------------------------------------

onPlace = function(player: Player, nodeId: string)
	local world = DataService.GetWorld(player)
	if not world or world ~= activeWorld then
		return
	end
	local node = ResourceNodeService.FindNode(world, nodeId)
	if not node then
		return
	end
	local distance = rootDistance(player, node.x, node.z)
	if not distance or distance > BaseLayout.drills.interactDistance then
		resultEvent:FireClient(player, "too_far", nodeId, 0)
		return
	end
	if findDrill(world, nodeId) then
		resultEvent:FireClient(player, "occupied", nodeId, 0)
		return
	end
	local drillId = (Drills.byOre :: any)[node.ore]
	if not drillId or DrillService.CountUnplaced(world, drillId) <= 0 then
		resultEvent:FireClient(player, "no_drill", nodeId, 0)
		return
	end
	local state: DrillState = { drillId = drillId, nodeId = nodeId, level = 1, buffer = 0 }
	table.insert(world.progress.drills, state)
	fraction[nodeId] = 0
	DrillService.Refresh(world)
	log(`{player.Name} hat {drillId} auf {nodeId} aufgestellt ({#world.progress.drills} Bohrer)`)
	resultEvent:FireClient(player, "placed", nodeId, 0)
end

onTake = function(player: Player, nodeId: string)
	local world = DataService.GetWorld(player)
	local stats = DataService.GetStats(player)
	if not world or not stats or world ~= activeWorld then
		return
	end
	local state = findDrill(world, nodeId)
	local node = ResourceNodeService.FindNode(world, nodeId)
	if not state or not node then
		return
	end
	local distance = rootDistance(player, node.x, node.z)
	if not distance or distance > BaseLayout.drills.interactDistance then
		resultEvent:FireClient(player, "too_far", nodeId, 0)
		return
	end
	if state.buffer <= 0 then
		resultEvent:FireClient(player, "empty", nodeId, 0)
		return
	end
	local space = PlayerState.carryCapacity(stats) - PlayerState.carriedTotal(stats)
	if space <= 0 then
		resultEvent:FireClient(player, "full", nodeId, 0)
		return
	end
	local ore = drillDef(state.drillId).ore
	local moved = math.min(space, state.buffer)
	state.buffer -= moved
	stats.carried[ore] = (stats.carried[ore] or 0) + moved
	PlayerState.refreshCarry(player, stats)
	updateDisplay(state)
	resultEvent:FireClient(player, "taken", nodeId, moved)
end

-- Puffer füllen ------------------------------------------------------------------------------------

local function tick(world: World, dt: number)
	for _, state in world.progress.drills do
		local capacity = capacityOf(state)
		if state.buffer < capacity then
			local acc = (fraction[state.nodeId] or 0) + ratePerSecond(state) * dt
			local whole = math.floor(acc)
			if whole > 0 then
				state.buffer = math.min(capacity, state.buffer + whole)
				acc -= whole
				updateDisplay(state)
			end
			fraction[state.nodeId] = if state.buffer >= capacity then 0 else acc
		else
			fraction[state.nodeId] = 0 -- voll: Bohrer steht still
		end
	end
end

-- Offline: Puffer so füllen, als hätte der Bohrer weitergearbeitet (höchstens bis voll).
local function applyOffline(world: World)
	if offlineApplied[world] or not Shop.OFFLINE_FILLS_DRILL_BUFFER then
		return
	end
	offlineApplied[world] = true
	local seconds = math.max(0, os.time() - (world.lastSavedAt or os.time()))
	if seconds <= 0 then
		return
	end
	for _, state in world.progress.drills do
		state.buffer = math.min(capacityOf(state), state.buffer + math.floor(ratePerSecond(state) * seconds))
	end
	if #world.progress.drills > 0 then
		log(`Offline {seconds} s: Puffer der {#world.progress.drills} Bohrer aufgefüllt`)
	end
end

local function onPlayerReady(player: Player, world: World)
	if activeWorld and activeWorld.worldId ~= world.worldId then
		warn(`[DrillService] {player.Name} hat eine andere Welt; M1 zeigt nur eine Welt pro Server`)
		return
	end
	if activeWorld ~= world then
		-- Neue oder neu geladene Welt: Modelle aus dem Spielstand neu bauen.
		clearModels()
		activeWorld = world
		applyOffline(world)
	end
	DrillService.Refresh(world)
	log(`{#world.progress.drills} Bohrer geladen, {totalUnplaced(world)} noch nicht aufgestellt`)
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

function DrillService.Init()
	resultEvent = Remotes.event("DrillResult")
end

function DrillService.Start()
	DataService.OnPlayerReady(onPlayerReady)
	Players.PlayerRemoving:Connect(onPlayerRemoving)

	task.spawn(function()
		local last = os.clock()
		local sinceSync = 0
		while true do
			task.wait(TICK_SECONDS)
			local now = os.clock()
			local dt = now - last
			last = now
			local world = activeWorld
			if world then
				tick(world, dt)
				sinceSync += dt
				if sinceSync >= PROMPT_SYNC_SECONDS then
					sinceSync = 0
					DrillService.Refresh(world)
				end
			end
		end
	end)
end

return DrillService
