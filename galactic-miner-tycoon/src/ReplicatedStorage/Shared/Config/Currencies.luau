--!strict
-- Währungen. Konzept: spiel/10-wirtschaft-und-waehrungen.md

export type CurrencyId = "credits" | "gems"

local Currencies = {
	credits = { id = "credits", displayName = "Credits", startAmount = 100 },
	gems = { id = "gems", displayName = "Gems", startAmount = 0 },
}

return Currencies
