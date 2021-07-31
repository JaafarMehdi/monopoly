import random
import math
import time
import matplotlib.pyplot as plt
import numpy as np

from game import *
from utils import *

from game.runner import oneGame

# simulation settings
nPlayers = 4
nMoves = 1000
nSimulations = 1000
seed = "" # "" for none
shufflePlayers = True

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



# run multiple game somulations
def runSimulation():
    results = []
    for i in range(nSimulations):
        
        log.write("="*10+" GAME "+str(i+1)+" "+"="*10+"\n")

        # remaining players - add to the results list
        results.append(oneGame())

        # write remaining players in a data log
        if writeData=="remainingPlayers":
            remPlayers = sum([1 for r in results[-1] if r>0])
            log.write(str(remPlayers), data=True)

            
        if (i+1)%progressAsterix == 0:
            pass
            print ("*", end = "")
    print ()

    return results


# Analize results 
def analyzeResults(results):
    
    remainingPlayers = [0,]*nPlayers
    for result in results:
        alive = 0
        for score in result:
            if score>=0:
                alive +=1
        remainingPlayers[alive-1] += 1
        
    if showRemPlayers:
        print ("Remaining:", remainingPlayers)

def analyzeData():
    
    if writeData == "losersNames" or writeData == "experiment" or writeData=="remainingPlayers":
        groups = {}
        with open("data.txt", "r") as fs:
            for line in fs:
                item = line.strip()
                if item in groups:
                    groups[item] += 1
                else:
                    groups[item] = 1
        experiment = 0
        control = 0
        for item in sorted(groups.keys()):
            count = groups[item]/nSimulations

            if writeData == "losersNames":
                count = 1-count
            if item=="exp":
                experiment = count
            else:
                control += count
                
            margin = 1.96 * math.sqrt(count*(1-count)/nSimulations)
            print ("{}: {:.1%} +- {:.1%}".format(item, count, margin) )

        if experiment!=0:
            print ("Exp result: {:.1%}".format(experiment-control/(nPlayers-1)) )

    if writeData == "netWorth":
        print ("graph here")
        npdata = np.transpose( np.loadtxt("data.txt", dtype=int, delimiter="\t") )
        x = np.arange(0, max( [len(d) for d in npdata] ) )
        
        plt.ioff()
        fig, ax = plt.subplots() 
        for i in range(nPlayers):
            ax.plot(x, npdata[i], label='1')
        plt.savefig("fig"+str(time.time())+".png")


if __name__ == "__main__":

        print ("="*40)

        t = time.time()
        log = Log()
        if seed != "":
            random.seed(seed)
        else:
            random.seed()
        print ("Players:", nPlayers, " Turns:", nMoves, " Games:", nSimulations, " Seed:", seed)
        results = runSimulation()
        analyzeResults(results)
        log.close()
        analyzeData()
        print ("Done in {:.2f}s".format(time.time()-t))
    
