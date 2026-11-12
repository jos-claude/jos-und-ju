--!strict
-- Legt RemoteEvents in ReplicatedStorage.GMT_Remotes an (nur der Server). Der Client wartet darauf.
-- Namen: PascalCase, Verb zuerst (technik/namenskonventionen.md).

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local FOLDER_NAME = "GMT_Remotes"

local Remotes = {}

local function folder(): Folder
	local existing = ReplicatedStorage:FindFirstChild(FOLDER_NAME)
	if existing and existing:IsA("Folder") then
		return existing
	end
	local created = Instance.new("Folder")
	created.Name = FOLDER_NAME
	created.Parent = ReplicatedStorage
	return created
end

function Remotes.event(name: string): RemoteEvent
	local parent = folder()
	local existing = parent:FindFirstChild(name)
	if existing and existing:IsA("RemoteEvent") then
		return existing
	end
	local created = Instance.new("RemoteEvent")
	created.Name = name
	created.Parent = parent
	return created
end

return Remotes
