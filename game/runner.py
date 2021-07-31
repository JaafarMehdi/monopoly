import random

from utils import *
from .settings import *
from .board import Board
from .player import Player

log = Log()
# reporting settings
progressAsterix = 1 # output * every N simulations
showMap = False # only for 1 game: show final board map
showResult = True # only for 1 game: show final money score
showRemPlayers = True
writeLog= False # write log with game events (log.txt file)


# Check if there are more then 1 player left in the game
def isGameOver(players):
    alive = 0
    for player in players:
        if not player.isBankrupt:
            alive += 1
    if alive > 1:
        return False
    else:
        return True


# simulate one game
def oneGame():
    # create players
    players = []
    # names = ["pl"+str(i) for i in range(nPlayers)]
    names = ["pl" + str(i) for i in range(nPlayers - 1)] + ["exp"]
    if shufflePlayers:
        random.shuffle(names)
    for i in range(nPlayers):
        players.append(Player(names[i]))

    # create board
    gameBoard = Board(players)

    #  netWorth history first point
    if writeData == "netWorth":
        networthstring = ""
        for player in players:
            networthstring += str(player.netWorth(gameBoard))
            if player != players[-1]:
                networthstring += "\t"
        log.write(networthstring, data=True)

    # game
    for i in range(nMoves):

        if isGameOver(players):
            # to track length of the game
            if writeData == "lastTurn":
                log.write(str(i - 1), data=True)
            break

        log.write(" TURN " + str(i + 1), 1)
        for player in players:
            if player.money > 0:
                log.write(player.name + ": $" + str(player.money) + ", position:" + str(player.position), 2)

        for player in players:
            if not isGameOver(players):  # Only continue if 2 or more players
                while player.makeAMove(gameBoard):  # returns True if player has to go again
                    pass

        # track netWorth history of the game
        if writeData == "netWorth":
            networthstring = ""
            for player in players:
                networthstring += str(player.netWorth(gameBoard))
                if player != players[-1]:
                    networthstring += "\t"
            log.write(networthstring, data=True)

    # return final scores
    results = [players[i].getMoney() for i in range(nPlayers)]

    # if it is an only simulation, print map and final score
    if nSimulations == 1 and showMap:
        gameBoard.printMap()
    if nSimulations == 1 and showResult:
        print(results)
    return results