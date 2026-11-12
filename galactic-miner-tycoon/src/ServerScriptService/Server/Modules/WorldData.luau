--!strict
-- Aufbau eines Spielstands ("Welt") und der Spieler-Übersicht. Nur Daten, kein Speichern.
-- Gespeichert wird PRO WELT, nicht pro Spieler (Entscheidung 014).
-- Rucksack, Spitzhacke usw. gehören zur Welt, je Mitglied (014, Punkt 5).
-- Neue Felder: hier im Standardwert ergänzen, `reconcile` füllt sie bei alten Spielständen auf.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Config = ReplicatedStorage:WaitForChild("Shared"):WaitForChild("Config")
local Bins = require(Config:WaitForChild("Bins"))
local Rooms = require(Config:WaitForChild("Rooms"))
local Pickaxe = require(Config:WaitForChild("Pickaxe"))
local Backpack = require(Config:WaitForChild("Backpack"))

export type BinState = {
	level: number, -- Kapazitäts-Stufe (Bins.luau)
	amount: number, -- Erz im Kasten
}

export type DrillState = {
	drillId: string, -- z. B. "drill_iron"
	nodeId: string, -- Vorkommen, auf dem er steht
	level: number,
	buffer: number, -- Erz im Puffer
}

export type NodeState = {
	nodeId: string,
	ore: string,
	x: number, -- Position auf der Insel (Studs, Mitte = Basis)
	z: number,
}

export type Progress = {
	rooms: { [string]: boolean }, -- RoomId → gekauft
	bins: { [string]: BinState }, -- BinId → Zustand (nur gekaufte Kästen)
	drillsBought: { [string]: number }, -- DrillId → Anzahl gekauft (für den Preis × 1,15^n)
	drills: { DrillState },
	nodes: { NodeState },
	rocketBuilt: boolean,
}

export type MemberStats = {
	pickaxeLevel: number,
	backpackLevel: number,
	carried: { [string]: number }, -- OreId → Erz, das man gerade trägt
}

export type World = {
	dataVersion: number,
	worldId: string,
	ownerUserId: number,
	memberUserIds: { number }, -- Besitzer steht auch drin
	createdAt: number, -- os.time()
	lastSavedAt: number, -- os.time(), für Offline-Ertrag (Entscheidung 011)
	island: number, -- 1 = Heimatplanet
	mapSeed: number, -- eigene Karte pro Welt, einmal zufällig (Entscheidung 011)
	playTimeSeconds: number, -- für "+1 Vorkommen alle 5 Minuten Spielzeit"
	progress: Progress,
	-- Schlüssel ist die UserId als Text (DataStores mögen keine Zahlen-Schlüssel mit Lücken).
	memberStats: { [string]: MemberStats },
}

export type PlayerIndex = {
	dataVersion: number,
	userId: number,
	worldIds: { string }, -- eigene Welten (höchstens MAX_WORLDS_PER_PLAYER)
	lastWorldId: string?,
}

local WorldData = {}

WorldData.DATA_VERSION = 1
WorldData.MAX_WORLDS_PER_PLAYER = 2 -- Entscheidung 014, Punkt 2
WorldData.MAX_PLAYERS_PER_WORLD = 4 -- Entscheidung 014, Punkt 3

function WorldData.newMemberStats(): MemberStats
	return {
		pickaxeLevel = Pickaxe.START_LEVEL,
		backpackLevel = Backpack.START_LEVEL,
		carried = {},
	}
end

local function newProgress(): Progress
	local rooms: { [string]: boolean } = {}
	for _, roomId in Rooms.order do
		if Rooms.byId[roomId].ownedAtStart then
			rooms[roomId] = true
		end
	end

	local bins: { [string]: BinState } = {}
	for _, binId in Bins.order do
		if Bins.byId[binId].ownedAtStart then
			bins[binId] = { level = 1, amount = 0 }
		end
	end

	return {
		rooms = rooms,
		bins = bins,
		drillsBought = {},
		drills = {},
		nodes = {},
		rocketBuilt = false,
	}
end

-- Neue Standard-Welt: Start-Halle und Eisen-Kasten, sonst nichts (Spieler startet ohne Bohrer, 016).
function WorldData.newWorld(worldId: string, ownerUserId: number, now: number, mapSeed: number): World
	local stats: { [string]: MemberStats } = {}
	stats[tostring(ownerUserId)] = WorldData.newMemberStats()
	return {
		dataVersion = WorldData.DATA_VERSION,
		worldId = worldId,
		ownerUserId = ownerUserId,
		memberUserIds = { ownerUserId },
		createdAt = now,
		lastSavedAt = now,
		island = 1,
		mapSeed = mapSeed,
		playTimeSeconds = 0,
		progress = newProgress(),
		memberStats = stats,
	}
end

function WorldData.newPlayerIndex(userId: number): PlayerIndex
	return {
		dataVersion = WorldData.DATA_VERSION,
		userId = userId,
		worldIds = {},
		lastWorldId = nil,
	}
end

-- Fehlende Felder aus `template` ergänzen (rekursiv), vorhandene Werte bleiben.
-- Listen (z. B. drills) werden nicht gemischt: fehlt die Liste, kommt die Vorlage.
function WorldData.reconcile(data: { [any]: any }, template: { [any]: any })
	for key, defaultValue in template do
		local current = data[key]
		if current == nil then
			if type(defaultValue) == "table" then
				data[key] = table.clone(defaultValue)
			else
				data[key] = defaultValue
			end
		elseif type(current) == "table" and type(defaultValue) == "table" and #defaultValue == 0 then
			WorldData.reconcile(current, defaultValue)
		end
	end
end

return WorldData
