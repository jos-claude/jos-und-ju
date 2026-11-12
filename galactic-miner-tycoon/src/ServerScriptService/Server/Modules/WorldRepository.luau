--!strict
-- Laden, Anlegen und Speichern von Welten. Kennt keine Spieler-Objekte, nur UserIds,
-- damit es sich ohne Play-Test prüfen lässt (mit einem Mock-Store).
--
-- Schlüssel: "player_<UserId>" (Spieler-Übersicht) und "world_<WorldId>" (Spielstand).
-- Schutzregeln:
-- * Lesen fehlgeschlagen → Welt gilt als nicht geladen und wird NIE gespeichert
--   (sonst würde ein leerer Standard-Spielstand einen echten überschreiben).
-- * Spielstand ist neuer als dieser Code (dataVersion zu hoch) → nicht laden, nicht speichern.

local HttpService = game:GetService("HttpService")

local SaveStore = require(script.Parent.SaveStore)
local WorldData = require(script.Parent.WorldData)

type Store = SaveStore.Store
type World = WorldData.World
type PlayerIndex = WorldData.PlayerIndex

export type LoadResult = {
	ok: boolean,
	world: World?,
	created: boolean, -- true = neue Standard-Welt angelegt (erster Spielstart)
	error: string?,
}

export type WorldRepository = {
	worldStore: Store,
	playerStore: Store,
	loadOrCreateForPlayer: (self: WorldRepository, userId: number) -> LoadResult,
	saveWorld: (self: WorldRepository, world: World) -> (boolean, string?),
}

local WorldRepositoryModule = {}

local function playerKey(userId: number): string
	return `player_{userId}`
end

local function worldKey(worldId: string): string
	return `world_{worldId}`
end

local function fail(message: string): LoadResult
	return { ok = false, world = nil, created = false, error = message }
end

local function prepareLoadedWorld(world: World, userId: number)
	WorldData.reconcile(world :: any, WorldData.newWorld(world.worldId, world.ownerUserId, 0, 0) :: any)
	-- Mitglied ergänzen (für Koop später; jetzt ist es immer der Besitzer).
	local key = tostring(userId)
	if world.memberStats[key] == nil then
		world.memberStats[key] = WorldData.newMemberStats()
	else
		WorldData.reconcile(world.memberStats[key] :: any, WorldData.newMemberStats() :: any)
	end
	if not table.find(world.memberUserIds, userId) then
		table.insert(world.memberUserIds, userId)
	end
end

function WorldRepositoryModule.new(worldStore: Store, playerStore: Store): WorldRepository
	local repo = {
		worldStore = worldStore,
		playerStore = playerStore,
	}

	function repo.saveWorld(self: WorldRepository, world: World): (boolean, string?)
		world.lastSavedAt = os.time()
		return self.worldStore:set(worldKey(world.worldId), world)
	end

	local function createWorld(self: WorldRepository, userId: number, index: PlayerIndex): LoadResult
		if #index.worldIds >= WorldData.MAX_WORLDS_PER_PLAYER then
			return fail("Keine freien Spielstand-Plätze")
		end
		local worldId = HttpService:GenerateGUID(false)
		local mapSeed = Random.new():NextInteger(1, 2 ^ 31 - 1)
		local world = WorldData.newWorld(worldId, userId, os.time(), mapSeed)

		-- Zuerst die Welt speichern, dann erst die Übersicht: So zeigt die Übersicht nie
		-- auf eine Welt, die es nicht gibt.
		local okWorld, errWorld = self:saveWorld(world)
		if not okWorld then
			return fail(`Neue Welt nicht gespeichert: {errWorld}`)
		end
		table.insert(index.worldIds, worldId)
		index.lastWorldId = worldId
		local okIndex, errIndex = self.playerStore:set(playerKey(userId), index)
		if not okIndex then
			return fail(`Spieler-Übersicht nicht gespeichert: {errIndex}`)
		end
		return { ok = true, world = world, created = true, error = nil }
	end

	-- Lädt die zuletzt benutzte Welt des Spielers. Hat er noch keine, wird die
	-- Standard-Welt angelegt (Entscheidung 014: erste Welt beim ersten Spielstart).
	-- Später (Lobby, M1b) kommt die Welt-ID aus dem Spielstand-Pad bzw. TeleportData.
	function repo.loadOrCreateForPlayer(self: WorldRepository, userId: number): LoadResult
		local okIndex, rawIndex = self.playerStore:get(playerKey(userId))
		if not okIndex then
			return fail("Spieler-Übersicht konnte nicht gelesen werden")
		end

		local index: PlayerIndex
		if rawIndex == nil then
			index = WorldData.newPlayerIndex(userId)
		else
			index = rawIndex :: PlayerIndex
			if (index.dataVersion or 0) > WorldData.DATA_VERSION then
				return fail("Spieler-Übersicht stammt von einer neueren Spielversion")
			end
			WorldData.reconcile(index :: any, WorldData.newPlayerIndex(userId) :: any)
		end

		local worldId = index.lastWorldId or index.worldIds[1]
		if worldId == nil then
			return createWorld(self, userId, index)
		end

		local okWorld, rawWorld = self.worldStore:get(worldKey(worldId))
		if not okWorld then
			return fail(`Welt {worldId} konnte nicht gelesen werden`)
		end
		if rawWorld == nil then
			-- Übersicht zeigt auf eine fehlende Welt: nichts überschreiben, melden.
			return fail(`Welt {worldId} fehlt im Speicher`)
		end

		local world = rawWorld :: World
		if (world.dataVersion or 0) > WorldData.DATA_VERSION then
			return fail(`Welt {worldId} stammt von einer neueren Spielversion`)
		end
		prepareLoadedWorld(world, userId)
		return { ok = true, world = world, created = false, error = nil }
	end

	return (repo :: any) :: WorldRepository
end

return WorldRepositoryModule
