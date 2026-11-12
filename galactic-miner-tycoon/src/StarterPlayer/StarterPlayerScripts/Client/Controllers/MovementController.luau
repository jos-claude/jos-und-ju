--!strict
-- Planeten-Gefühl beim Steuern des eigenen Charakters:
-- 1. Trägheit: sanftes Anlaufen und kurzes Nachrutschen auf dem Boden.
-- 2. Schwung in der Luft: Die Richtung ändert sich nur langsam, Loslassen bremst nicht sofort.
-- 3. Staubwolke bei der Landung, in der Farbe des Bodens.
-- Schwerkraft, Sprunghöhe und Laufgeschwindigkeit setzt der MovementService auf dem Server.
-- Konzept: spiel/17-bewegung-und-physik.md · Zahlen: Shared/Config/Movement.luau

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local Movement = require(ReplicatedStorage:WaitForChild("Shared"):WaitForChild("Config"):WaitForChild("Movement"))

type MoveFunction = (Player, Vector3, boolean) -> ()

-- Nach der eingestellten Zeit fehlen noch ca. 5 % (e^-3).
local SETTLE_FACTOR = 3
-- Längster Zeitschritt fürs Glätten, damit ein Ruckler keinen Sprung macht.
local MAX_STEP = 0.1
-- Kommt so lange keine Eingabe, ist die Steuerung aus (z. B. Cutscene): dann sofort anhalten.
local IDLE_RESET_TIME = 0.2
local DUST_TEXTURE = "rbxasset://textures/particles/smoke_main.dds"
local DUST_RAY_LENGTH = 12

local player = Players.LocalPlayer

local MovementController = {}

local humanoid: Humanoid? = nil
local rootPart: BasePart? = nil
local dustAttachment: Attachment? = nil
local dustEmitter: ParticleEmitter? = nil

local originalMove: MoveFunction? = nil
local smoothedMove = Vector3.zero
local lastMoveCall = 0
local fallSpeed = 0

-- Wandelt die Eingabe (relativ zur Kamera) in eine Richtung in der Welt um.
local function toWorld(moveVector: Vector3, cameraRelative: boolean): Vector3
	local camera = workspace.CurrentCamera
	if not cameraRelative or not camera then
		return moveVector
	end
	local look = camera.CFrame.LookVector
	local forward = Vector3.new(look.X, 0, look.Z)
	if forward.Magnitude < 0.001 then
		-- Kamera schaut senkrecht nach unten: Bildschirm-oben zählt als vorne.
		local up = camera.CFrame.UpVector
		forward = Vector3.new(up.X, 0, up.Z)
	end
	if forward.Magnitude < 0.001 then
		return moveVector
	end
	forward = forward.Unit
	local right = Vector3.new(-forward.Z, 0, forward.X)
	return right * moveVector.X - forward * moveVector.Z
end

local function isAirborne(h: Humanoid): boolean
	local state = h:GetState()
	return state == Enum.HumanoidStateType.Freefall or state == Enum.HumanoidStateType.Jumping
end

-- Ersetzt die Bewegungsfunktion des Roblox-Steuermoduls. Wird jedes Bild mit der Eingabe aufgerufen.
local function smoothMove(plr: Player, moveVector: Vector3, cameraRelative: boolean)
	local move = originalMove :: MoveFunction
	local now = os.clock()
	local dt = math.clamp(now - lastMoveCall, 0, MAX_STEP)
	lastMoveCall = now

	local h = humanoid
	if not h or h.Sit then
		-- Im Sitz (z. B. später im Rover) nichts glätten.
		smoothedMove = Vector3.zero
		move(plr, moveVector, cameraRelative)
		return
	end

	local target = toWorld(moveVector, cameraRelative)
	local settleTime: number
	if isAirborne(h) then
		settleTime = Movement.airControlTime
	elseif target.Magnitude >= smoothedMove.Magnitude then
		settleTime = Movement.groundAccelTime
	else
		settleTime = Movement.groundDecelTime
	end

	if settleTime <= 0 then
		smoothedMove = target
	else
		local alpha = 1 - math.exp(-SETTLE_FACTOR / settleTime * dt)
		smoothedMove = smoothedMove:Lerp(target, alpha)
		if (smoothedMove - target).Magnitude < 0.01 then
			smoothedMove = target
		end
	end

	move(plr, smoothedMove, false)
end

local function hookControls()
	local playerScripts = player:WaitForChild("PlayerScripts")
	local playerModuleScript = playerScripts:WaitForChild("PlayerModule", 10)
	if not playerModuleScript then
		warn("[MovementController] PlayerModule fehlt – Trägheit ist aus.")
		return
	end
	local ok, playerModule = pcall(require, playerModuleScript)
	local controls = if ok and type(playerModule) == "table" then playerModule:GetControls() else nil
	if type(controls) ~= "table" or type(controls.moveFunction) ~= "function" then
		warn("[MovementController] Roblox-Steuermodul hat sich geändert – Trägheit ist aus.")
		return
	end
	originalMove = controls.moveFunction
	controls.moveFunction = smoothMove
end

local function getGroundHit(character: Model, root: BasePart): RaycastResult?
	local params = RaycastParams.new()
	params.FilterType = Enum.RaycastFilterType.Exclude
	params.FilterDescendantsInstances = { character }
	params.IgnoreWater = true
	return workspace:Raycast(root.Position, Vector3.new(0, -DUST_RAY_LENGTH, 0), params)
end

local function getGroundColor(hit: RaycastResult?): Color3
	if hit then
		local part = hit.Instance
		if part:IsA("Terrain") then
			return part:GetMaterialColor(hit.Material)
		elseif part:IsA("BasePart") then
			return part.Color
		end
	end
	return Movement.landingDustFallbackColor
end

local function createDust(root: BasePart)
	local attachment = Instance.new("Attachment")
	attachment.Name = "LandingDustAttachment"
	attachment.Parent = root

	local emitter = Instance.new("ParticleEmitter")
	emitter.Name = "LandingDust"
	emitter.Enabled = false
	emitter.Texture = DUST_TEXTURE
	emitter.Size = NumberSequence.new({
		NumberSequenceKeypoint.new(0, 0.6),
		NumberSequenceKeypoint.new(1, 2.4),
	})
	emitter.Transparency = NumberSequence.new({
		NumberSequenceKeypoint.new(0, 0.3),
		NumberSequenceKeypoint.new(1, 1),
	})
	emitter.Lifetime = NumberRange.new(0.6, 1.1)
	emitter.Speed = NumberRange.new(5, 9)
	emitter.SpreadAngle = Vector2.new(80, 80)
	emitter.Drag = 4
	-- Leichte Schwerkraft: Der Staub sinkt nur langsam.
	emitter.Acceleration = Vector3.new(0, -2, 0)
	emitter.Rotation = NumberRange.new(0, 360)
	emitter.RotSpeed = NumberRange.new(-60, 60)
	emitter.Parent = attachment

	dustAttachment = attachment
	dustEmitter = emitter
end

local function onLanded(character: Model)
	local speed = fallSpeed
	fallSpeed = 0
	local root = rootPart
	local attachment = dustAttachment
	local emitter = dustEmitter
	if not root or not attachment or not emitter or speed < Movement.landingDustMinSpeed then
		return
	end

	local hit = getGroundHit(character, root)
	if hit then
		attachment.WorldPosition = hit.Position + Vector3.new(0, 0.2, 0)
	else
		attachment.Position = Vector3.new(0, -3, 0)
	end
	-- Etwas heller als der Boden, damit der Staub sichtbar ist.
	local color = getGroundColor(hit):Lerp(Color3.new(1, 1, 1), 0.25)
	emitter.Color = ColorSequence.new(color)
	emitter:Emit(math.clamp(math.floor(speed / 3), 6, 18))
end

local function onHeartbeat()
	-- Steuerung wurde abgeschaltet: nicht weiterrutschen.
	if smoothedMove ~= Vector3.zero and os.clock() - lastMoveCall > IDLE_RESET_TIME then
		smoothedMove = Vector3.zero
		local move = originalMove
		if move then
			move(player, Vector3.zero, false)
		end
	end

	-- Fallgeschwindigkeit merken, damit die Landung weiß, wie hart sie war.
	local h = humanoid
	local root = rootPart
	if h and root and h:GetState() == Enum.HumanoidStateType.Freefall then
		fallSpeed = math.max(0, -root.AssemblyLinearVelocity.Y)
	end
end

local function onCharacterAdded(character: Model)
	humanoid = nil
	rootPart = nil
	dustAttachment = nil
	dustEmitter = nil
	smoothedMove = Vector3.zero
	fallSpeed = 0

	local humanoidInstance = character:WaitForChild("Humanoid", 10)
	local rootInstance = character:WaitForChild("HumanoidRootPart", 10)
	if player.Character ~= character then
		return -- In der Zwischenzeit neu gespawnt.
	end
	if not (humanoidInstance and humanoidInstance:IsA("Humanoid")) then
		return
	end
	if not (rootInstance and rootInstance:IsA("BasePart")) then
		return
	end
	local h = humanoidInstance :: Humanoid
	local root = rootInstance :: BasePart
	humanoid = h
	rootPart = root

	if Movement.landingDust then
		createDust(root)
		h.StateChanged:Connect(function(_oldState, newState)
			if newState == Enum.HumanoidStateType.Landed then
				onLanded(character)
			end
		end)
	end
end

function MovementController.Init() end

function MovementController.Start()
	player.CharacterAdded:Connect(onCharacterAdded)
	if player.Character then
		task.spawn(onCharacterAdded, player.Character)
	end
	RunService.Heartbeat:Connect(onHeartbeat)
	hookControls()
end

return MovementController
