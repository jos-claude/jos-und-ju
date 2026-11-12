--!strict
-- Unser eigener Ordner im Workspace für Spielobjekte (Halle, Lager, Vorkommen): Workspace.GMT_Gameplay.
-- Er gehört Ju. Jos' Welt (Terrain, Island1, GMT_Models) wird nie angefasst.
-- Der Inhalt wird beim Serverstart neu gebaut; man kann den Ordner jederzeit löschen.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local BaseLayout = require(ReplicatedStorage:WaitForChild("Shared"):WaitForChild("Config"):WaitForChild("BaseLayout"))

local GameplayFolder = {}

function GameplayFolder.get(): Folder
	local existing = workspace:FindFirstChild(BaseLayout.FOLDER_NAME)
	if existing and existing:IsA("Folder") then
		return existing
	end
	local created = Instance.new("Folder")
	created.Name = BaseLayout.FOLDER_NAME
	created.Parent = workspace
	return created
end

-- Unterordner (z. B. "OreNodes"), wird bei Bedarf angelegt.
function GameplayFolder.child(name: string): Folder
	local root = GameplayFolder.get()
	local existing = root:FindFirstChild(name)
	if existing and existing:IsA("Folder") then
		return existing
	end
	local created = Instance.new("Folder")
	created.Name = name
	created.Parent = root
	return created
end

-- Alten Inhalt (z. B. aus einem früheren Lauf) entfernen. Nur unser eigener Ordner.
function GameplayFolder.reset(): Folder
	local root = GameplayFolder.get()
	root:ClearAllChildren()
	return root
end

return GameplayFolder
