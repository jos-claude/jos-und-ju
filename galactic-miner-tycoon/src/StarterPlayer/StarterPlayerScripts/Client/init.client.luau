--!strict
-- Client-Start: lädt alle Controller in Controllers/ und ruft Init() und danach Start() auf.
-- Neuer Controller = neue ModuleScript-Datei in Controllers/, sonst nichts.
-- Architektur: technik/architektur.md

local controllersFolder = script:WaitForChild("Controllers")

local loaded: { [string]: any } = {}

for _, child in controllersFolder:GetChildren() do
	if child:IsA("ModuleScript") then
		local ok, result = pcall(require, child)
		if ok then
			loaded[child.Name] = result
		else
			warn(`[Client] Controller {child.Name} konnte nicht geladen werden: {result}`)
		end
	end
end

for name, controller in loaded do
	if type(controller) == "table" and type(controller.Init) == "function" then
		controller.Init()
	end
end

for name, controller in loaded do
	if type(controller) == "table" and type(controller.Start) == "function" then
		task.spawn(controller.Start)
	end
end

print("Client started")
