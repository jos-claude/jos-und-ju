--!strict
-- Findet die fertigen 3D-Modelle (Jos/Ju, assets/asset-liste.md) und gibt eine KOPIE zurück.
-- Die Originale werden nie verändert oder verschoben.
-- Suchreihenfolge: ServerStorage.GMT_Models.<Name>, danach Workspace.<Name> (z. B. drill_iron,
-- solange er noch nicht in GMT_Models liegt). Fehlt das Modell, kommt nil zurück und der Aufrufer
-- baut die Greybox.

local ServerStorage = game:GetService("ServerStorage")

local GameModels = {}

local warned: { [string]: boolean } = {}

function GameModels.find(name: string): Model?
	local folder = ServerStorage:FindFirstChild("GMT_Models")
	local found = folder and folder:FindFirstChild(name)
	if not found then
		found = workspace:FindFirstChild(name)
	end
	if found and found:IsA("Model") then
		return found
	end
	if not warned[name] then
		warned[name] = true
		warn(`[GameModels] Modell {name} nicht gefunden (GMT_Models oder Workspace), nehme Greybox`)
	end
	return nil
end

-- Kopie des Modells, verankert, ohne Import-Attribute und ohne Skripte. Noch ohne Parent.
function GameModels.clone(name: string): Model?
	local original = GameModels.find(name)
	if not original then
		return nil
	end
	local copy = original:Clone()
	for attribute in copy:GetAttributes() do
		copy:SetAttribute(attribute, nil)
	end
	for _, d in copy:GetDescendants() do
		if d:IsA("BaseScript") then
			d:Destroy()
		elseif d:IsA("BasePart") then
			d.Anchored = true
		end
	end
	copy:SetAttribute("SourceModel", name)
	return copy
end

-- Welt-Quader eines Teils (min, max), auch wenn es gedreht ist.
function GameModels.partBounds(p: BasePart): (Vector3, Vector3)
	local s = p.Size / 2
	local min = Vector3.new(math.huge, math.huge, math.huge)
	local max = -min
	for _, x in { -1, 1 } do
		for _, y in { -1, 1 } do
			for _, z in { -1, 1 } do
				local w = p.CFrame:PointToWorldSpace(Vector3.new(x * s.X, y * s.Y, z * s.Z))
				min = min:Min(w)
				max = max:Max(w)
			end
		end
	end
	return min, max
end

-- Welt-Quader mehrerer Teile.
function GameModels.bounds(parts: { BasePart }): (Vector3, Vector3)
	local min = Vector3.new(math.huge, math.huge, math.huge)
	local max = -min
	for _, p in parts do
		local a, b = GameModels.partBounds(p)
		min = min:Min(a)
		max = max:Max(b)
	end
	return min, max
end

-- Teile, deren Name mit `suffix` endet (z. B. "_Orange") oder den Text enthält.
function GameModels.partsMatching(model: Model, pattern: string): { BasePart }
	local list = {}
	for _, d in model:GetDescendants() do
		if d:IsA("BasePart") and string.find(d.Name, pattern) then
			table.insert(list, d)
		end
	end
	return list
end

return GameModels
