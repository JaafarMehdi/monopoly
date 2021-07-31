import random

from utils import *
from .settings import *
from .cell import *

log = Log()

class Player:

    def __init__(self, name):
        self.name = name
        self.position = 0
        self.money = settingStartingMoney
        self.consequentDoubles = 0
        self.inJail = False

        self.daysInJail = 0
        self.hasJailCardChance = False
        self.hasJailCardCommunity = False
        self.isBankrupt = False
        self.hasMortgages = []
        self.plotsWanted = []
        self.plotsOffered = []
        self.plotsToBuild = []
        self.cashLimit = expUnspendableCash if name == "exp" else behaveUnspendableCash

    def __str__(self):
        return "Player: " + self.name + \
               ". Position: " + str(self.position) + \
               ". Money: $" + str(self.money)

    # some getters and setters

    def getMoney(self):
        return self.money

    def getName(self):
        return self.name

    # add money (salary, receive rent etc)
    def addMoney(self, amount):
        self.money += amount

    # subtract money (pay reny, buy property etc)
    def takeMoney(self, amount):
        self.money -= amount

    # subtract money (pay reny, buy property etc)
    def moveTo(self, position):
        self.position = position
        log.write(self.name + " moves to cell " + str(position), 3)

    # make a move procedure
    def makeAMove(self, board):

        goAgain = False

        # Only proceed if player is alive (not bankrupt)
        if self.isBankrupt:
            return

        # to track the popular cells to land
        if writeData == "popularCells":
            log.write(str(self.position), data=True)

        log.write("Player " + self.name + " goes:", 2)

        # non-board actions: Trade, unmortgage, build
        # repay mortgage if you have X times more cashe than mortgage cost
        while self.repayMortgage():
            board.recalculateAfterPropertyChange()

        # build houses while you have pare cash
        while board.improveProperty(self, self.money - self.cashLimit):
            pass

        # Calculate property player wants to get and ready to give away
        if expRefuseTrade and self.name == "exp":
            pass  # Experiement: do not trade
        elif behaveDoTrade:
            #  Make a trade
            if not self.twoWayTrade(board) and nPlayers >= 3 and behaveDoThreeWayTrade:
                self.threeWayTrade(board)

        # roll dice
        dice1 = random.randint(1, 6)
        dice2 = random.randint(1, 6)
        log.write(self.name + " rolls " + str(dice1) + " and " + str(dice2) + " = " + str(dice1 + dice2), 3)

        # doubles
        if dice1 == dice2 and not self.inJail:
            goAgain = True  # go again if doubles
            self.consequentDoubles += 1
            log.write("it's a number " + str(self.consequentDoubles) + " double in a row", 3)
            if self.consequentDoubles == 3:  # but go to jail if 3 times in a row
                self.inJail = True
                log.write(self.name + " goes to jail on consequtive doubles", 3)
                self.moveTo(10)
                self.consequentDoubles = 0
                return False
        else:
            self.consequentDoubles = 0  # reset doubles counter

        # Jail situation:
        # Stay unless you roll doubles
        if self.inJail:
            if self.hasJailCardChance:
                self.hasJailCardChance = False
                board.chanceCards.append(1)  # return the card
                log.write(self.name + " uses the Chance GOOJF card to get out of jail", 3)
            elif self.hasJailCardCommunity:
                self.hasJailCardCommunity = False
                board.communityCards.append(6)  # return the card
                log.write(self.name + " uses the Community GOOJF card to get out of jail", 3)
            elif dice1 != dice2:
                self.daysInJail += 1
                if self.daysInJail < 3:
                    log.write(self.name + " spends this turn in jail", 3)
                    return False  # skip turn in jail
                else:
                    self.takeMoney(settingJailFine)  # get out on fine
                    self.daysInJail = 0
                    log.write(self.name + " pays fine and gets out of jail", 3)
            else:  # get out of jail on doubles
                log.write(self.name + " rolls double and gets out of jail", 3)
                self.daysInJail = 0
                goAgain = False
        self.inJail = False

        # move the piece
        self.position += dice1 + dice2

        # correction of the position if landed on GO or overshoot GO
        if self.position >= 40:
            # calculate correct cell
            self.position = self.position - 40
            # get salary for passing GO
            self.addMoney(settingsSalary)
            log.write(self.name + " gets salary: $" + str(settingsSalary), 3)

        log.write(self.name + " moves to cell " + str(self.position) + ": " + board.b[self.position].name + \
                  (" (" + board.b[self.position].owner.name + ")" if type(board.b[self.position]) == Property and
                                                                     board.b[self.position].owner != "" else ""), 3)

        # perform action of the cell player ended on
        board.action(self, self.position)

        # check if bankrupt after the action
        self.checkBankrupcy(board)

        if goAgain:
            log.write(self.name + " will go again now", 3)
            return True  # make a move again
        return False  # no extra move

    # get the cheapest mortgage property (name, price)
    def cheapestMotgage(self):
        cheapest = False
        for mortgage in self.hasMortgages:
            if not cheapest or mortgage[1] < cheapest[1]:
                cheapest = mortgage
        return cheapest

    # Chance card make general repairs: 25/house 100/hotel
    def makeRepairs(self, board, repairtype):
        repairCost = 0
        if repairtype == "chance":
            perHouse, perHotel = 25, 100
        else:
            perHouse, perHotel = 40, 115
        log.write("Repair cost: $" + str(perHouse) + " per house, $" + str(perHotel) + " per hotel", 3)

        for plot in board.b:
            if type(plot) == Property and plot.owner == self:
                if plot.hasHouses == 5:
                    repairCost += perHotel
                else:
                    repairCost += plot.hasHouses * perHouse
        self.takeMoney(repairCost)
        log.write(self.name + " pays total repair costs $" + str(repairCost), 3)

    # check if player has negative money
    # if so, start selling stuff and mortgage plots
    # if that's not enough, player bankrupt
    def checkBankrupcy(self, board):
        if self.money < 0:
            log.write(self.name + " doesn't have enough cash", 3)
            while self.money < 0:
                worstAsset = board.choosePropertyToMortgageDowngrade(self)
                if worstAsset == False:
                    self.isBankrupt = True
                    board.sellAll(self)
                    board.recalculateAfterPropertyChange()
                    log.write(self.name + " is now bankrupt. Their property is back on board.", 3)

                    # to track players who lost
                    if writeData == "losersNames":
                        log.write(self.name, data=True)

                    # to track cells to land one last time
                    if writeData == "popularCells":
                        log.write(str(self.position), data=True)

                    return
                else:
                    board.b[worstAsset].mortgage(self, board)
                    board.recalculateAfterPropertyChange()

    # Calculate net worth of a player (for property tax)
    def netWorth(self, board):
        worth = self.money
        for plot in board.b:
            if type(plot) == Property and plot.owner == self:
                if plot.isMortgaged:
                    worth += plot.cost_base // 2
                else:
                    worth += plot.cost_base
                    worth += plot.cost_house * plot.hasHouses
        return worth

        ## Behaviours

    # if there is a mortgage with pay less then current money // behaveUnmortgageCoeff
    # repay the mortgage
    def repayMortgage(self):
        cheapest = self.cheapestMotgage()
        if cheapest and self.money > cheapest[1] * behaveUnmortgageCoeff:
            cheapest[0].unmortgage(self)
            return True
        return False

    # does player want to buy a property
    def wantsToBuy(self, cost, group):

        if self.name == "exp" and group == expRefuseProperty:
            log.write(self.name + " refuses to buy " + expRefuseProperty + " property", 3)
            return False
        if self.money > cost + self.cashLimit:  # leave some money just in case
            return True
        else:
            return False

    # Look for and perform a two-way trade
    def twoWayTrade(self, board):
        tradeHappened = False
        for IWant in self.plotsWanted[::-1]:
            ownerOfWanted = board.b[IWant].owner
            if ownerOfWanted == "":
                continue
            # Find a match betwee what I want / they want / I have / they have
            for TheyWant in ownerOfWanted.plotsWanted[::-1]:
                if TheyWant in self.plotsOffered \
                        and board.b[IWant].group != board.b[TheyWant].group:  # prevent exchanging in groups of 2
                    log.write("Trade match: " + self.name + " wants " + board.b[IWant].name + \
                              ", and " + ownerOfWanted.name + " wants " + board.b[TheyWant].name, 3)

                    # Compensate that one plot is cheaper than another one
                    if board.b[IWant].cost_base < board.b[TheyWant].cost_base:
                        cheaperOne, expensiveOne = IWant, TheyWant
                    else:
                        cheaperOne, expensiveOne = TheyWant, IWant
                    priceDiff = board.b[expensiveOne].cost_base - board.b[cheaperOne].cost_base
                    log.write("Price difference is $" + str(priceDiff), 3)

                    # make sure they they can pay the money
                    if board.b[cheaperOne].owner.money - priceDiff >= board.b[cheaperOne].owner.cashLimit:
                        log.write("We have a deal. Money and property changed hands", 3)
                        # Money and property change hands
                        board.b[cheaperOne].owner.takeMoney(priceDiff)
                        board.b[expensiveOne].owner.addMoney(priceDiff)
                        board.b[cheaperOne].owner, board.b[expensiveOne].owner = \
                            board.b[expensiveOne].owner, board.b[cheaperOne].owner
                        tradeHappened = True

                        # recalculated wanted and offered plots
                        board.recalculateAfterPropertyChange()
        return tradeHappened

    # Look for and perform a three-way trade
    def threeWayTrade(self, board):
        tradeHappened = False
        for wanted1 in self.plotsWanted[::-1]:
            ownerOfWanted1 = board.b[wanted1].owner
            if ownerOfWanted1 == "":
                continue
            for wanted2 in ownerOfWanted1.plotsWanted[::-1]:
                ownerOfWanted2 = board.b[wanted2].owner
                if ownerOfWanted2 == "":
                    continue
                for wanted3 in ownerOfWanted2.plotsWanted[::-1]:
                    if wanted3 in self.plotsOffered:

                        # check we have property from 3 groups
                        # otherwise someone can give and take brown or indigo at the same time
                        checkDiffGroup = set()
                        checkDiffGroup.add(board.b[wanted1].group)
                        checkDiffGroup.add(board.b[wanted2].group)
                        checkDiffGroup.add(board.b[wanted3].group)
                        if len(checkDiffGroup) < 3:
                            continue

                        topay1 = board.b[wanted1].cost_base - board.b[wanted3].cost_base
                        topay2 = board.b[wanted2].cost_base - board.b[wanted1].cost_base
                        topay3 = board.b[wanted3].cost_base - board.b[wanted2].cost_base
                        if self.money - topay1 > self.cashLimit and \
                                ownerOfWanted1.money - topay2 > ownerOfWanted1.cashLimit and \
                                ownerOfWanted2.money - topay3 > ownerOfWanted2.cashLimit:
                            log.write("Tree way trade: ", 3)
                            log.write(self.name + " gives " + board.b[wanted3].name + " and $" + str(topay1) + " for " +
                                      board.b[wanted1].name, 4)
                            log.write(ownerOfWanted1.name + " gives " + board.b[wanted1].name + " and $" + str(
                                topay2) + " for " + board.b[wanted2].name, 4)
                            log.write(ownerOfWanted2.name + " gives " + board.b[wanted2].name + " and $" + str(
                                topay3) + " for " + board.b[wanted3].name, 4)
                            # Money and property change hands
                            board.b[wanted1].owner = self
                            board.b[wanted2].owner = ownerOfWanted1
                            board.b[wanted3].owner = ownerOfWanted2
                            self.takeMoney(topay1)
                            ownerOfWanted1.takeMoney(topay2)
                            ownerOfWanted2.takeMoney(topay3)
                            tradeHappened = True
                            # recalculated wanted and offered plots
                            board.recalculateAfterPropertyChange()
