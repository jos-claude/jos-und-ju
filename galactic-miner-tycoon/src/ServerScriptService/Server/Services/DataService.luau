--!strict
-- Vorlage für einen Service. Speichern/Laden der Spielerdaten (technik/datenspeicherung.md).
-- TODO: DataStore anbinden (Meilenstein M1).

local DataService = {}

function DataService.Init()
	-- Hier nur Vorbereitung (Tabellen anlegen). Noch nicht auf andere Services zugreifen.
end

function DataService.Start()
	-- Hier läuft die eigentliche Arbeit (Spieler laden, Auto-Save-Schleife).
end

return DataService
