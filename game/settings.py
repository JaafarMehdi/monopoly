# some game rules
settingStartingMoney = 1500
settingsSalary = 200
settingsLuxuryTax = 75
settingsPropertyTax = 200
settingJailFine = 50
settingHouseLimit = 32
settingHotelLimit = 12
settingsAllowUnEqualDevelopment = False # default = False



# players behaviour settings
behaveUnspendableCash = 0 # Money I want to will have left after buying stuff
behaveUnmortgageCoeff = 3 # repay mortgage if you have times this cash
behaveDoTrade = True # willing to trade property
behaveDoThreeWayTrade = True # willing to trade property three-way
behaveBuildCheapest = False
behaveBuildRandom = False

# experimental settings
# for a player named exp:
expRefuseTrade = False # refuse to trade property
expRefuseProperty = "" # refuse to buy this group
expHouseBuildLimit = 100 # limit houses built
expUnspendableCash = 0 # unspendable money
expBuildCheapest = False
expBuildExpensive = False
expBuildThree = False


## Various raw data to output (to data.txt file)
#writeData = "none"
#writeData = "popularCells" # Cells to land
#writeData = "lastTurn" # Length of the game
writeData = "losersNames" # Who lost
#writeData = "netWorth" # history of a game
#writeData = "remainingPlayers"

# simulation settings TODO this is a duplicate should be parametrised
nPlayers = 4
nMoves = 1000
nSimulations = 1000
seed = "" # "" for none
shufflePlayers = True
