--!strict
-- Server-Start: lädt alle Services in Services/ und ruft Init() und danach Start() auf.
-- Neuer Service = neue ModuleScript-Datei in Services/, sonst nichts.
-- Architektur: technik/architektur.md

local servicesFolder = script:WaitForChild("Services")

local loaded: { [string]: any } = {}

for _, child in servicesFolder:GetChildren() do
	if child:IsA("ModuleScript") then
		local ok, result = pcall(require, child)
		if ok then
			loaded[child.Name] = result
		else
			warn(`[Server] Service {child.Name} konnte nicht geladen werden: {result}`)
		end
	end
end

for name, service in loaded do
	if type(service) == "table" and type(service.Init) == "function" then
		service.Init()
	end
end

for name, service in loaded do
	if type(service) == "table" and type(service.Start) == "function" then
		task.spawn(service.Start)
	end
end

print("Server started")
