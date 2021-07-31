from utils import *
from .settings import *

log = Log()


# Generic Cell Class, base for other classes
class Cell:

    def __init__(self, name):
        self.name = name
        self.group = ""

    def action(self, player):
        pass


# Pay Luxury Tax cell (#38)
class LuxuryTax(Cell):

    def action(self, player):
        player.takeMoney(settingsLuxuryTax)
        log.write(player.name + " pays Luxury Tax $" + str(settingsLuxuryTax), 3)


# Pay Property Tax cell (200 or 10%) (#4)
class PropertyTax(Cell):

    def action(self, player, board):
        toPay = min(settingsPropertyTax, player.netWorth(board) // 10)
        log.write(player.name + " pays Property Tax $" + str(toPay), 3)
        player.takeMoney(toPay)


# Go to Jail (#30)
class GoToJail(Cell):

    def action(self, player):
        player.moveTo(10)
        player.inJail = True
        log.write(player.name + " goes to jail from Go To Jail ", 3)


# Chance cards
class Chance(Cell):

    def action(self, player, board):

        # Get the card
        chanceCard = board.chanceCards.pop(0)

        # Actions for various cards

        # 0: Advance to St.Charle
        if chanceCard == 0:
            log.write(player.name + " gets chance card: Advance to St.Charle's", 3)
            if player.position >= 11:
                player.addMoney(settingsSalary)
                log.write(player.name + " gets salary: $" + str(settingsSalary), 3)
            player.position = 11
            log.write(player.name + " goes to " + str(board.b[11].name), 3)
            board.action(player, player.position)

        # 1: Get Out Of Jail Free
        elif chanceCard == 1:
            log.write(player.name + " gets chance card: Get Out Of Jail Free", 3)
            player.hasJailCardChance = True

        # 2: Take a ride on the Reading
        elif chanceCard == 2:
            log.write(player.name + " gets chance card: Take a ride on the Reading", 3)
            if player.position >= 5:
                player.addMoney(settingsSalary)
                log.write(player.name + " gets salary: $" + str(settingsSalary), 3)
            player.position = 5
            log.write(player.name + " goes to " + str(board.b[player.position].name), 3)
            board.action(player, player.position)

        # 3: Move to the nearest railroad and pay double
        elif chanceCard == 3:
            log.write(player.name + " gets chance card: Move to the nearest railroad and pay double", 3)
            # Don't get salary, even if you pass GO (card doesnt say to do it)
            # Dont move is already on a rail.
            # Also, I assue advance means you should go to the nearest in fron of you, not behind
            player.position = ((player.position + 4) // 10 * 10 + 5) % 40  # nearest railroad
            board.action(player, player.position, special="from_chance")  # twice for double rent, if needed

        # 4: Advance to Illinois Avenue
        elif chanceCard == 4:
            log.write(player.name + " gets chance card: Advance to Illinois Avenue", 3)
            if player.position >= 24:
                player.addMoney(settingsSalary)
                log.write(player.name + " gets salary: $" + str(settingsSalary), 3)
            player.position = 24
            log.write(player.name + " goes to " + str(board.b[player.position].name), 3)
            board.action(player, player.position)

        # 5: Make general repairs to your property
        elif chanceCard == 5:
            log.write(player.name + " gets chance card: Make general repairs to your property", 3)
            player.makeRepairs(board, "chance")

        # 6: Advance to GO
        elif chanceCard == 6:
            log.write(player.name + " gets chance card: Advance to GO", 3)
            player.addMoney(settingsSalary)
            log.write(player.name + " gets salary: $" + str(settingsSalary), 3)
            player.position = 0
            log.write(player.name + " goes to " + str(board.b[player.position].name), 3)

        # 7: Bank pays you dividend $50
        elif chanceCard == 7:
            log.write(player.name + " gets chance card: Bank pays you dividend $50", 3)
            player.addMoney(50)

        # 8: Pay poor tax $15
        elif chanceCard == 8:
            log.write(player.name + " gets chance card: Pay poor tax $15", 3)
            player.takeMoney(15)

        # 9: Advance to the nearest Utility and pay 10x dice
        elif chanceCard == 9:
            log.write(player.name + " gets chance card: Advance to the nearest Utility and pay 10x dice", 3)
            if player.position > 12 and player.position <= 28:
                player.position = 28
            else:
                player.position = 12
            board.action(player, player.position, special="from_chance")

        # 10: Go Directly to Jail
        elif chanceCard == 10:
            log.write(player.name + " gets chance card: Go Directly to Jail", 3)
            player.moveTo(10)
            player.inJail = True
            log.write(player.name + " goes to jail on Chance card", 3)

        # 11: You've been elected chairman. Pay each player $50
        elif chanceCard == 11:
            log.write(player.name + " gets chance card: You've been elected chairman. Pay each player $50", 3)
            for other_player in board.players:
                if other_player != player and not other_player.isBankrupt:
                    player.takeMoney(50)
                    other_player.addMoney(50)

        # 12: Advance to BoardWalk
        elif chanceCard == 12:
            log.write(player.name + " gets chance card: Advance to BoardWalk", 3)
            player.position = 39
            log.write(player.name + " goes to " + str(board.b[player.position].name), 3)
            board.action(player, player.position)

        # 13: Go back 3 spaces
        elif chanceCard == 13:
            log.write(player.name + " gets chance card: Go back 3 spaces", 3)
            player.position -= 3
            log.write(player.name + " goes to " + str(board.b[player.position].name), 3)
            board.action(player, player.position)

        # 14: Your building loan matures. Receive $150.
        elif chanceCard == 14:
            log.write(player.name + " gets chance card: Your building loan matures. Receive $150", 3)
            player.addMoney(150)

        # 15: You have won a crossword competition. Collect $100
        elif chanceCard == 15:
            log.write(player.name + " gets chance card: You have won a crossword competition. Collect $100", 3)
            player.addMoney(100)

        # Put the card back
        if chanceCard != 1:  # except GOOJF card
            board.chanceCards.append(chanceCard)


# Community Chest cards
class Community(Cell):

    def action(self, player, board):

        # Get the card
        communityCard = board.communityCards.pop(0)

        # Actions for various cards

        # 0: Pay school tax $150
        if communityCard == 0:
            log.write(player.name + " gets community card: Pay school tax $150", 3)
            player.takeMoney(150)

        # 1: Opera night: collect $50 from each player
        if communityCard == 1:
            log.write(player.name + " Opera night: collect $50 from each player", 3)
            for other_player in board.players:
                if other_player != player and not other_player.isBankrupt:
                    player.addMoney(50)
                    other_player.takeMoney(50)
                    other_player.checkBankrupcy(board)

        # 2: You inherit $100
        if communityCard == 2:
            log.write(player.name + " gets community card: You inherit $100", 3)
            player.addMoney(100)

        # 3: Pay hospital $100
        if communityCard == 3:
            log.write(player.name + " gets community card: Pay hospital $100", 3)
            player.takeMoney(100)

        # 4: Income tax refund $20
        if communityCard == 4:
            log.write(player.name + " gets community card: Income tax refund $20", 3)
            player.addMoney(20)

        # 5: Go Directly to Jail
        elif communityCard == 5:
            log.write(player.name + " gets community card: Go Directly to Jail", 3)
            player.moveTo(10)
            player.inJail = True
            log.write(player.name + " goes to jail on Community card", 3)

        # 6: Get Out Of Jail Free
        elif communityCard == 6:
            log.write(player.name + " gets community card: Get Out Of Jail Free", 3)
            player.hasJailCardCommunity = True

        # 7: Second prize in beauty contest $10
        if communityCard == 7:
            log.write(player.name + " gets community card: Second prize in beauty contest $10", 3)
            player.addMoney(10)

        # 8: You are assigned for street repairs
        elif communityCard == 8:
            log.write(player.name + " gets community card: You are assigned for street repairs", 3)
            player.makeRepairs(board, "community")

        # 9: Bank error in your favour: $200
        if communityCard == 9:
            log.write(player.name + " gets community card: Bank error in your favour: $200", 3)
            player.addMoney(200)

        # 10: Advance to GO
        elif communityCard == 10:
            log.write(player.name + " gets community card: Advance to GO", 3)
            player.addMoney(settingsSalary)
            log.write(player.name + " gets salary: $" + str(settingsSalary), 3)
            player.position = 0
            log.write(player.name + " goes to " + str(board.b[player.position].name), 3)

        # 11: X-Mas fund matured: $100
        if communityCard == 11:
            log.write(player.name + " gets community card: X-Mas fund matured: $100", 3)
            player.addMoney(100)

        # 12: Doctor's fee $50
        if communityCard == 12:
            log.write(player.name + " gets community card: Doctor's fee $50", 3)
            player.takeMoney(50)

        # 13: From sale of stock you get $45
        if communityCard == 13:
            log.write(player.name + " gets community card: From sale of stock you get $45", 3)
            player.addMoney(45)

        # 14: Receive for services $25
        if communityCard == 14:
            log.write(player.name + " gets community card: Receive for services $25", 3)
            player.addMoney(25)

        # 15: Life insurance matures, collect $100
        if communityCard == 15:
            log.write(player.name + " gets community card: Life insurance matures, collect $100", 3)
            player.addMoney(100)

        # Put the card back
        if communityCard != 6:  # except GOOJF card
            board.communityCards.append(communityCard)


# Property Class (for Properties, Rails, Utilities)
class Property(Cell):

    def __init__(self, name, cost_base, rent_base, cost_house, rent_house, group):
        self.name = name
        self.cost_base = cost_base
        self.rent_base = rent_base
        self.cost_house = cost_house
        self.rent_house = rent_house
        self.group = group
        self.owner = ""
        self.isMortgaged = False
        self.isMonopoly = False
        self.hasHouses = 0

    # Player ended on a property
    def action(self, player, rent, board):

        # it's their property or mortgaged - do nothing
        if self.owner == player or self.isMortgaged:
            log.write("No rent this time", 3)
            return

        # Property up for sale
        elif self.owner == "":
            if player.wantsToBuy(self.cost_base, self.group):
                log.write(player.name + " buys property " + self.name + " for $" + str(self.cost_base), 3)
                player.takeMoney(self.cost_base)
                self.owner = player
                board.recalculateAfterPropertyChange()
            else:
                pass  # auction here
                log.write(player.name + " didn't buy the property.", 3)
                # Auction here
                # Decided not to implement it...
            return

        # someone else's property - pay the rent
        else:
            player.takeMoney(rent)
            self.owner.addMoney(rent)
            log.write(player.name + " pays the rent $" + str(rent) + " to " + self.owner.name, 3)

    # mortgage the plot to the player / or sell the house
    def mortgage(self, player, board):
        # Sell hotel
        if self.hasHouses == 5:
            player.addMoney(self.cost_house * 5 // 2)
            self.hasHouses = 0
            board.nHotels -= 1
            log.write(player.name + " sells hotel on " + self.name, 3)
        # Sell one house
        elif self.hasHouses > 0:
            player.addMoney(self.cost_house // 2)
            self.hasHouses -= 1
            board.nHouses -= 1
            log.write(player.name + " sells house on " + self.name, 3)
        # Mortgage
        else:
            self.isMortgaged = True
            player.addMoney(self.cost_base // 2)
            # log name of the plot and money player need to pay to get it back
            player.hasMortgages.append((self, int((self.cost_base // 2) * 1.1)))
            log.write(player.name + " mortgages " + self.name, 3)

    # unmortgage thr plot
    def unmortgage(self, player):
        # print (player.hasMortgages)
        for mortgage in player.hasMortgages:
            if mortgage[0] == self:
                thisMortgage = mortgage
        self.isMortgaged = False
        player.takeMoney(thisMortgage[1])
        player.hasMortgages.remove(thisMortgage)
        log.write(player.name + " unmortgages " + self.name, 3)

