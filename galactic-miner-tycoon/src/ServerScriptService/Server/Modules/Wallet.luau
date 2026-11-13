--!strict
-- Bezahlen mit Erzen aus den Lager-Kästen (Entscheidungen 006 und 010: die Kästen sind das Inventar).
-- Nur der Server benutzt das. Fehlt der Kasten eines Erzes, kann man damit nicht bezahlen.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Config = ReplicatedStorage:WaitForChild("Shared"):WaitForChild("Config")
local Bins = require(Config:WaitForChild("Bins"))
local Ores = require(Config:WaitForChild("Ores"))

local WorldData = require(script.Parent:WaitForChild("WorldData"))

type World = WorldData.World
type Cost = { [string]: number }

local Wallet = {}

-- Kurze Namen für Preisschilder (Erz-IDs aus daten/ressourcen.md).
Wallet.SHORT_NAMES = {
	iron_ore = "Eisen",
	copper_ore = "Kupfer",
	coal = "Kohle",
	crystal = "Kristall",
	titanium_ore = "Titan",
}

function Wallet.amountOf(world: World, oreId: string): number
	local binId = (Bins.byOre :: any)[oreId]
	local state = binId and world.progress.bins[binId]
	return if state then state.amount else 0
end

-- Erze in fester Reihenfolge (Eisen zuerst), damit Preisschilder immer gleich aussehen.
function Wallet.sortedEntries(cost: Cost): { { ore: string, amount: number } }
	local entries = {}
	for _, oreId in Ores.order do
		local amount = cost[oreId]
		if amount and amount > 0 then
			table.insert(entries, { ore = oreId :: string, amount = amount })
		end
	end
	return entries
end

-- Erstes Erz, das fehlt (oder nil, wenn alles reicht).
function Wallet.missing(world: World, cost: Cost): string?
	for _, entry in Wallet.sortedEntries(cost) do
		if Wallet.amountOf(world, entry.ore) < entry.amount then
			return entry.ore
		end
	end
	return nil
end

function Wallet.canAfford(world: World, cost: Cost): boolean
	return Wallet.missing(world, cost) == nil
end

-- Zieht die Kosten ab. Prüft vorher alles; reicht es nicht, wird nichts abgezogen.
function Wallet.pay(world: World, cost: Cost): boolean
	if not Wallet.canAfford(world, cost) then
		return false
	end
	for _, entry in Wallet.sortedEntries(cost) do
		local state = world.progress.bins[(Bins.byOre :: any)[entry.ore]]
		state.amount -= entry.amount
	end
	return true
end

-- "20 Eisen" bzw. "100 Eisen + 15 Kupfer"
function Wallet.describe(cost: Cost): string
	local parts = {}
	for _, entry in Wallet.sortedEntries(cost) do
		table.insert(parts, `{entry.amount} {Wallet.SHORT_NAMES[entry.ore] or entry.ore}`)
	end
	return if #parts == 0 then "gratis" else table.concat(parts, " + ")
end

return Wallet
