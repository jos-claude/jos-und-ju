--!strict
-- Bodenhöhe an einer Stelle: Raycast von oben nach unten gegen das Gelände von Jos.
-- Getroffen wird nur Workspace.Terrain und (solange sie sichtbar ist) die alte Baseplate,
-- nie Deko aus Workspace.Island1, Spielfiguren oder unsere eigenen Platzhalter.

local Ground = {}

local RAY_TOP = 800
local RAY_LENGTH = 1600
local FALLBACK_Y = 0 -- Oberkante der alten Baseplate / Basis-Plateau (Auftrag 001)

-- Gibt (Höhe, gefunden) zurück. gefunden = false heißt: nichts getroffen, Höhe ist der Notwert.
function Ground.heightAt(x: number, z: number): (number, boolean)
	local include: { Instance } = { workspace.Terrain }
	local baseplate = workspace:FindFirstChild("Baseplate")
	if baseplate and baseplate:IsA("BasePart") and baseplate.Transparency < 1 and baseplate.CanCollide then
		table.insert(include, baseplate)
	end

	local params = RaycastParams.new()
	params.FilterType = Enum.RaycastFilterType.Include
	params.FilterDescendantsInstances = include
	params.IgnoreWater = true

	local result = workspace:Raycast(Vector3.new(x, RAY_TOP, z), Vector3.new(0, -RAY_LENGTH, 0), params)
	if result then
		return result.Position.Y, true
	end
	return FALLBACK_Y, false
end

return Ground
