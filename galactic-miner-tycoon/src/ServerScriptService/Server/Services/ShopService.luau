--!strict
-- Kauffelder in der Welt (Schritt 5 und 6, spiel/14 "Kaufflächen"): drauflaufen = kaufen, kein Menü.
-- Über jedem Feld stehen Name und Preis mit Erz-Symbol: grün = bezahlbar, rot = zu wenig, grau = gesperrt.
-- Bezahlt wird aus den Lager-Kästen (Wallet). Der Server erkennt selbst, wer auf einem Feld steht,
-- und prüft jeden Kauf. Gekauft wird nur beim Betreten (wieder runter und drauf = nächster Kauf).
--
-- Felder:
--   drill_iron  (Start-Halle)  Eisen-Bohrer, Preis Drills.getPrice (20, dann × 1,15, math.round)
--   forge       (vor der Tür)  Raum 2 Schmiede, 50 Eisen (Rooms.luau). Öffnet die Tür.
--   pickaxe     (Schmiede)     nächste Spitzhacken-Stufe (Pickaxe.luau), bis Shop.FORGE_MAX_PICKAXE_LEVEL
--   backpack    (Schmiede)     nächste Rucksack-Stufe (Backpack.luau), bis Shop.FORGE_MAX_BACKPACK_LEVEL
-- Dazu ein Platzhalter "Lobby (später)" in der Schmiede (ohne Funktion, Schritt 6).
--
-- Remotes (ReplicatedStorage.GMT_Remotes):
--   ShopResult  Server → Client (padId, ok, reason, text)
--     reason: "bought" | "poor" | "blocked"

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Config = ReplicatedStorage:WaitForChild("Shared"):WaitForChild("Config")
local BaseLayout = require(Config:WaitForChild("BaseLayout"))
local Drills = require(Config:WaitForChild("Drills"))
local Rooms = require(Config:WaitForChild("Rooms"))
local Pickaxe = require(Config:WaitForChild("Pickaxe"))
local Backpack = require(Config:WaitForChild("Backpack"))
local Shop = require(Config:WaitForChild("Shop"))

local Modules = script.Parent.Parent:WaitForChild("Modules")
local WorldData = require(Modules:WaitForChild("WorldData"))
local GreyboxShop = require(Modules:WaitForChild("GreyboxShop"))
local Ground = require(Modules:WaitForChild("Ground"))
local GameplayFolder = require(Modules:WaitForChild("GameplayFolder"))
local PlayerState = require(Modules:WaitForChild("PlayerState"))
local Remotes = require(Modules:WaitForChild("Remotes"))
local Wallet = require(Modules:WaitForChild("Wallet"))
local DataService = require(script.Parent:WaitForChild("DataService"))
local BaseService = require(script.Parent:WaitForChild("BaseService"))
local DrillService = require(script.Parent:WaitForChild("DrillService"))

type World = WorldData.World
type MemberStats = WorldData.MemberStats
type Cost = { [string]: number }

local CHECK_SECONDS = 0.2 -- so oft wird geprüft, wer auf welchem Feld steht
local DRILL_ID: Drills.DrillId = "drill_iron"
local FORGE_ID = "forge"

-- Was ein Feld gerade anbietet (für Anzeige und Kauf).
type Offer = {
	title: string,
	cost: Cost,
	state: GreyboxShop.PadState, -- "ok" | "poor" | "blocked"
	sub: string,
	buy: ((player: Player, world: World, stats: MemberStats) -> string)?, -- gibt die Erfolgsmeldung zurück
}

type PadInfo = {
	pad: GreyboxShop.Pad,
	x: number,
	z: number,
	groundY: number,
	inForge: boolean,
	offer: (world: World, stats: MemberStats) -> Offer,
}

local ShopService = {}

local resultEvent: RemoteEvent
local activeWorld: World? = nil
local pads: { [string]: PadInfo } = {}
local padFolder: Folder? = nil
local forgeRoom: GreyboxShop.Room? = nil
local standingOn: { [Player]: string? } = {}

local function log(message: string)
	print(`[ShopService] {message}`)
end

local function entriesFor(cost: Cost): { GreyboxShop.CostEntry }
	local entries = {}
	for _, entry in Wallet.sortedEntries(cost) do
		table.insert(entries, {
			ore = entry.ore,
			amount = entry.amount,
			color = BaseLayout.oreColors[entry.ore] or Color3.new(1, 1, 1),
		})
	end
	return entries
end

-- ok/poor nach Kasten-Inhalt; poor nennt das fehlende Erz.
local function priced(world: World, title: string, cost: Cost, okSub: string, buy: any): Offer
	local missing = Wallet.missing(world, cost)
	if missing then
		return {
			title = title,
			cost = cost,
			state = "poor",
			sub = `Zu wenig {Wallet.SHORT_NAMES[missing] or missing}`,
			buy = nil,
		}
	end
	return { title = title, cost = cost, state = "ok", sub = okSub, buy = buy }
end

local function blocked(title: string, cost: Cost, sub: string): Offer
	return { title = title, cost = cost, state = "blocked", sub = sub, buy = nil }
end

-- Angebote ------------------------------------------------------------------------------------------

local function drillOffer(world: World, _stats: MemberStats): Offer
	local def = Drills.byId[DRILL_ID]
	local cost = Drills.getPrice(DRILL_ID, world.progress.drillsBought[DRILL_ID] or 0)
	local unplaced = DrillService.CountUnplaced(world, DRILL_ID)
	if Shop.DRILL_NEEDS_FREE_NODE and DrillService.FreeNodeCount(world, def.ore) - unplaced <= 0 then
		local sub = if unplaced > 0 then "Stell erst deinen Bohrer auf" else "Kein freies Vorkommen"
		return blocked(def.displayName, cost, sub)
	end
	local okSub = if unplaced > 0 then `{unplaced} wartet aufs Aufstellen` else "Drauflaufen = kaufen"
	return priced(world, def.displayName, cost, okSub, function(_player: Player, w: World, _s: MemberStats): string
		w.progress.drillsBought[DRILL_ID] = (w.progress.drillsBought[DRILL_ID] or 0) + 1
		DrillService.Refresh(w)
		return `{def.displayName} gekauft! Stell ihn auf ein Vorkommen`
	end)
end

local function forgeOffer(world: World, _stats: MemberStats): Offer
	local def = Rooms.byId.forge
	local title = `Raum {def.number}: {def.displayName}`
	if world.progress.rooms[FORGE_ID] then
		return blocked(title, {}, "Gekauft")
	end
	return priced(world, title, def.cost, "Drauflaufen = kaufen", function(_player: Player, w: World, _s: MemberStats): string
		w.progress.rooms[FORGE_ID] = true
		if forgeRoom then
			GreyboxShop.openDoor(forgeRoom, false)
		end
		return `{def.displayName} gekauft! Die Tür ist offen`
	end)
end

local function forgeLocked(world: World): boolean
	return not world.progress.rooms[FORGE_ID]
end

local function pickaxeOffer(world: World, stats: MemberStats): Offer
	local nextLevel = stats.pickaxeLevel + 1
	local def = Pickaxe.levels[nextLevel]
	if not def then
		return blocked("Spitzhacke", {}, "Höchste Stufe")
	end
	local title = `{def.displayName} (Stufe {def.level})`
	if forgeLocked(world) then
		return blocked(title, def.cost, "Schmiede gesperrt")
	end
	if nextLevel > Shop.FORGE_MAX_PICKAXE_LEVEL then
		return blocked(title, def.cost, "später")
	end
	local okSub = `{def.orePerHit} Erz pro Schlag`
	return priced(world, title, def.cost, okSub, function(player: Player, _w: World, s: MemberStats): string
		s.pickaxeLevel = nextLevel
		PlayerState.refreshCarry(player, s)
		return `{def.displayName}! {def.orePerHit} Erz pro Schlag`
	end)
end

local function backpackOffer(world: World, stats: MemberStats): Offer
	local nextLevel = stats.backpackLevel + 1
	local def = Backpack.levels[nextLevel]
	if not def then
		return blocked("Rucksack", {}, "Höchste Stufe")
	end
	local title = `{def.displayName} (Stufe {def.level})`
	if forgeLocked(world) then
		return blocked(title, def.cost, "Schmiede gesperrt")
	end
	if nextLevel > Shop.FORGE_MAX_BACKPACK_LEVEL then
		return blocked(title, def.cost, "später")
	end
	local okSub = `Tragen {def.carryCapacity}`
	return priced(world, title, def.cost, okSub, function(player: Player, _w: World, s: MemberStats): string
		s.backpackLevel = nextLevel
		PlayerState.refreshCarry(player, s)
		return `{def.displayName}! Du trägst jetzt {def.carryCapacity}`
	end)
end

-- Aufbau ---------------------------------------------------------------------------------------------

local function addPad(id: string, pos: { x: number, z: number }, groundY: number, inForge: boolean, offer: any)
	local parent = padFolder :: Folder
	local pad = GreyboxShop.buildPad(parent, id, pos.x, pos.z, groundY, BaseLayout.pads.size)
	pads[id] = { pad = pad, x = pos.x, z = pos.z, groundY = groundY, inForge = inForge, offer = offer }
end

local function build()
	local root = GameplayFolder.get()
	local folder = Instance.new("Folder")
	folder.Name = "BuyPads"
	folder.Parent = root
	padFolder = folder

	local hall = BaseLayout.hall
	local hallY = Ground.heightAt(hall.centerX, hall.centerZ)
	local f = BaseLayout.forge
	local forgeY, hit = Ground.heightAt(f.centerX, f.centerZ)
	if not hit then
		warn(`[ShopService] Kein Gelände unter der Schmiede gefunden, nehme y = {forgeY}`)
	end
	local outsideY = Ground.heightAt(BaseLayout.pads.forgeRoom.x, BaseLayout.pads.forgeRoom.z)

	forgeRoom = GreyboxShop.buildForge(root, f, forgeY)
	GreyboxShop.closeDoor(forgeRoom :: GreyboxShop.Room, `GESPERRT\n{Wallet.describe(Rooms.byId.forge.cost)}`)

	local p = BaseLayout.pads
	addPad(DRILL_ID, p.drillIron, hallY, false, drillOffer)
	addPad(FORGE_ID, p.forgeRoom, outsideY, false, forgeOffer)
	addPad("pickaxe", p.pickaxe, forgeY, true, pickaxeOffer)
	addPad("backpack", p.backpack, forgeY, true, backpackOffer)
	GreyboxShop.buildPlaceholderPad(folder, "GMT_PH_LobbyPlaceholder", "Lobby (später)", p.lobby.x, p.lobby.z, forgeY, p.size)
	log(`Kauffelder und Schmiede gebaut (Halle y = {string.format("%.2f", hallY)}, Schmiede y = {string.format("%.2f", forgeY)})`)
end

-- Anzeige --------------------------------------------------------------------------------------------

local function displayStats(world: World): MemberStats?
	local players = DataService.GetPlayersInWorld(world.worldId)
	return if players[1] then DataService.GetStats(players[1]) else nil
end

local function refreshPads(world: World)
	local stats = displayStats(world)
	if not stats then
		return
	end
	for id, info in pads do
		local offer = info.offer(world, stats)
		GreyboxShop.setPad(info.pad, offer.title, entriesFor(offer.cost), offer.state, offer.sub)
		-- Gekaufte Schmiede: Feld vor der Tür verschwindet.
		if id == FORGE_ID then
			local model = info.pad.part.Parent
			if model then
				model.Parent = if world.progress.rooms[FORGE_ID] then nil else padFolder
			end
		end
	end
end

-- Kaufen ---------------------------------------------------------------------------------------------

local function padUnder(player: Player): string?
	local character = player.Character
	local root = character and character:FindFirstChild("HumanoidRootPart")
	if not root or not root:IsA("BasePart") then
		return nil
	end
	local half = BaseLayout.pads.size / 2 + 0.5
	for id, info in pads do
		local model = info.pad.part.Parent
		if model and model.Parent then
			local rel = root.Position - Vector3.new(info.x, info.groundY, info.z)
			if math.abs(rel.X) <= half and math.abs(rel.Z) <= half and rel.Y >= -2 and rel.Y <= BaseLayout.pads.height then
				return id
			end
		end
	end
	return nil
end

local function tryBuy(player: Player, padId: string)
	local world = DataService.GetWorld(player)
	local stats = DataService.GetStats(player)
	local info = pads[padId]
	if not world or not stats or not info or world ~= activeWorld then
		return
	end
	local offer = info.offer(world, stats)
	if offer.state == "blocked" then
		resultEvent:FireClient(player, padId, false, "blocked", offer.sub)
		return
	end
	if offer.state ~= "ok" or not offer.buy then
		resultEvent:FireClient(player, padId, false, "poor", offer.sub)
		return
	end
	if not Wallet.pay(world, offer.cost) then -- prüft noch einmal selbst
		resultEvent:FireClient(player, padId, false, "poor", offer.sub)
		return
	end
	local text = offer.buy(player, world, stats)
	BaseService.RefreshBins(world)
	refreshPads(world)
	log(`{player.Name} kauft {padId} für {Wallet.describe(offer.cost)}`)
	resultEvent:FireClient(player, padId, true, "bought", text)
end

local function onPlayerReady(_player: Player, world: World)
	if activeWorld and activeWorld.worldId ~= world.worldId then
		return -- M1: eine Welt pro Server
	end
	activeWorld = world
	if forgeRoom then
		if world.progress.rooms[FORGE_ID] then
			GreyboxShop.openDoor(forgeRoom, true)
		else
			GreyboxShop.closeDoor(forgeRoom, `GESPERRT\n{Wallet.describe(Rooms.byId.forge.cost)}`)
		end
	end
	refreshPads(world)
end

function ShopService.Init()
	resultEvent = Remotes.event("ShopResult")
end

function ShopService.Start()
	build()
	DataService.OnPlayerReady(onPlayerReady)
	Players.PlayerRemoving:Connect(function(player)
		standingOn[player] = nil
		task.defer(function()
			local world = activeWorld
			if world and #DataService.GetPlayersInWorld(world.worldId) == 0 then
				activeWorld = nil
			end
		end)
	end)

	task.spawn(function()
		while true do
			task.wait(CHECK_SECONDS)
			local world = activeWorld
			if world then
				for _, player in Players:GetPlayers() do
					local padId = padUnder(player)
					if padId and standingOn[player] ~= padId then
						standingOn[player] = padId
						tryBuy(player, padId)
					elseif not padId then
						standingOn[player] = nil
					end
				end
				refreshPads(world)
			end
		end
	end)
end

return ShopService
