--!strict
-- Rechnet Tragevorrat und Lager-Mengen aus und schreibt sie als Attribute an den Player.
-- Der Client (HUD) liest nur diese Attribute. Entscheiden tut immer der Server.
--
-- Attribute am Player:
--   CarryCapacity, CarriedTotal, Carried_<OreId>      (Tragevorrat)
--   PickaxeLevel, SwingSeconds                         (Spitzhacke)
--   Bin_<OreId>, BinCap_<OreId>                        (nur gekaufte Kästen)

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Config = ReplicatedStorage:WaitForChild("Shared"):WaitForChild("Config")
local Ores = require(Config:WaitForChild("Ores"))
local Bins = require(Config:WaitForChild("Bins"))
local Pickaxe = require(Config:WaitForChild("Pickaxe"))
local Backpack = require(Config:WaitForChild("Backpack"))

local WorldData = require(script.Parent:WaitForChild("WorldData"))

type World = WorldData.World
type MemberStats = WorldData.MemberStats
type BinState = WorldData.BinState

local PlayerState = {}

function PlayerState.carryCapacity(stats: MemberStats): number
	local level = Backpack.levels[stats.backpackLevel] or Backpack.levels[Backpack.START_LEVEL]
	return level.carryCapacity
end

function PlayerState.carriedTotal(stats: MemberStats): number
	local total = 0
	for _, amount in stats.carried do
		total += amount
	end
	return total
end

function PlayerState.pickaxeLevel(stats: MemberStats): Pickaxe.PickaxeLevel
	return Pickaxe.levels[stats.pickaxeLevel] or Pickaxe.levels[Pickaxe.START_LEVEL]
end

function PlayerState.binCapacity(binId: string, state: BinState): number
	local def = (Bins.byId :: any)[binId]
	local level = def.levels[state.level] or def.levels[1]
	return level.capacity
end

function PlayerState.refreshCarry(player: Player, stats: MemberStats)
	player:SetAttribute("CarryCapacity", PlayerState.carryCapacity(stats))
	player:SetAttribute("CarriedTotal", PlayerState.carriedTotal(stats))
	for _, oreId in Ores.order do
		player:SetAttribute(`Carried_{oreId}`, stats.carried[oreId] or 0)
	end
	local pick = PlayerState.pickaxeLevel(stats)
	player:SetAttribute("PickaxeLevel", pick.level)
	player:SetAttribute("SwingSeconds", pick.swingSeconds)
end

function PlayerState.refreshBins(player: Player, world: World)
	for _, binId in Bins.order do
		local state = world.progress.bins[binId]
		local ore = Bins.byId[binId].ore
		if state then
			player:SetAttribute(`Bin_{ore}`, state.amount)
			player:SetAttribute(`BinCap_{ore}`, PlayerState.binCapacity(binId, state))
		else
			player:SetAttribute(`Bin_{ore}`, nil)
			player:SetAttribute(`BinCap_{ore}`, nil)
		end
	end
end

return PlayerState
