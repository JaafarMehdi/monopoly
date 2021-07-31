# reporting settings
progressAsterix = 1 # output * every N simulations
showMap = False # only for 1 game: show final board map
showResult = True # only for 1 game: show final money score
showRemPlayers = True
writeLog= False # write log with game events (log.txt file)

## Various raw data to output (to data.txt file)
#writeData = "none"
#writeData = "popularCells" # Cells to land
#writeData = "lastTurn" # Length of the game
writeData = "losersNames" # Who lost
#writeData = "netWorth" # history of a game
#writeData = "remainingPlayers"


class Log:
# TODO write alogger that dont need close and open
    def __init__(self):
        # self.datafs = open("data.txt", "w")
        # self.fs = open("log.txt", "w")
        return

    def close(self):
        # self.datafs.close()
        # self.fs.close()
        return

    def write(self, text, level=0, data=False):
        # if data and writeData:
        #     self.datafs.write(text + "\n")
        #     return
        # if writeLog:
        #     if level < 2:
        #         self.fs.write("\n" * (2 - level))
        #     self.fs.write("\t" * level + text + "\n")
        return