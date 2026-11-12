--!strict
-- Speicher-Schicht: entweder echter DataStore oder ein Mock im Arbeitsspeicher.
--
-- SCHUTZ FÜR ECHTE SPIELSTÄNDE:
-- 1. In Roblox Studio wird IMMER der Mock benutzt. Es gibt keinen Schalter, der das ändert.
-- 2. Der echte DataStore verweigert den Start, wenn er doch in Studio erzeugt wird.
-- 3. Der Mock vergisst alles, wenn der Play-Test endet. Er schreibt nie nach außen.
-- Weitere Regel im WorldRepository: Ist das Laden gescheitert, wird nie gespeichert.

local HttpService = game:GetService("HttpService")
local RunService = game:GetService("RunService")
local DataStoreService = game:GetService("DataStoreService")

export type StoreKind = "mock" | "datastore"

export type Store = {
	kind: StoreKind,
	name: string,
	-- Gibt (ok, wert) zurück. ok = false heißt: Lesen fehlgeschlagen (nicht: "leer").
	get: (self: Store, key: string) -> (boolean, any),
	-- Gibt (ok, fehler) zurück.
	set: (self: Store, key: string, value: any) -> (boolean, string?),
}

local MAX_ATTEMPTS = 3
local RETRY_WAIT_SECONDS = 1

local SaveStore = {}

-- Gemeinsamer Mock-Inhalt pro Store-Name (damit zwei Aufrufe mit gleichem Namen dieselben Daten sehen).
local mockData: { [string]: { [string]: string } } = {}

-- Mock: speichert als JSON-Text, damit nicht speicherbare Werte (Instanzen, Funktionen,
-- gemischte Tabellen) schon im Studio auffallen und Lesen immer eine frische Kopie liefert.
function SaveStore.newMock(name: string): Store
	local bucket = mockData[name]
	if not bucket then
		bucket = {}
		mockData[name] = bucket
	end

	local store = {
		kind = "mock" :: StoreKind,
		name = name,
	}

	function store.get(_self: Store, key: string): (boolean, any)
		local text = bucket[key]
		if text == nil then
			return true, nil
		end
		return true, HttpService:JSONDecode(text)
	end

	function store.set(_self: Store, key: string, value: any): (boolean, string?)
		local ok, result = pcall(HttpService.JSONEncode, HttpService, value)
		if not ok then
			return false, `Mock: nicht speicherbar: {result}`
		end
		bucket[key] = result
		return true, nil
	end

	return (store :: any) :: Store
end

function SaveStore.newDataStore(name: string): Store
	if RunService:IsStudio() then
		error("SaveStore: echter DataStore in Studio verboten (Schutz für echte Spielstände)")
	end

	local dataStore = DataStoreService:GetDataStore(name)

	local store = {
		kind = "datastore" :: StoreKind,
		name = name,
	}

	function store.get(_self: Store, key: string): (boolean, any)
		local lastError: any = nil
		for attempt = 1, MAX_ATTEMPTS do
			local ok, result = pcall(dataStore.GetAsync, dataStore, key)
			if ok then
				return true, result
			end
			lastError = result
			task.wait(RETRY_WAIT_SECONDS * attempt)
		end
		warn(`[SaveStore] Lesen fehlgeschlagen ({name}/{key}): {lastError}`)
		return false, nil
	end

	function store.set(_self: Store, key: string, value: any): (boolean, string?)
		local lastError: any = nil
		for attempt = 1, MAX_ATTEMPTS do
			local ok, result = pcall(dataStore.SetAsync, dataStore, key, value)
			if ok then
				return true, nil
			end
			lastError = result
			task.wait(RETRY_WAIT_SECONDS * attempt)
		end
		return false, tostring(lastError)
	end

	return (store :: any) :: Store
end

-- Wählt den richtigen Speicher: in Studio immer Mock, im echten Spiel der DataStore.
function SaveStore.open(name: string): Store
	if RunService:IsStudio() then
		return SaveStore.newMock(name)
	end
	return SaveStore.newDataStore(name)
end

return SaveStore
