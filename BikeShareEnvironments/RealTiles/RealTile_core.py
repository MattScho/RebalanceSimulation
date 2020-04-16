import numpy as np
from BikeShareEnvironments.RealTiles.spatialmanager import SpatialManager

class RealTile_core:

    def __init__(self, actionsPerEpisode):
        self.spatialManager = SpatialManager()
        self.stations = self.spatialManager.getStations()
        self.activitySeries = self.spatialManager.getActivitySeries()

        self.actionCounter = 0
        self._generateNextInterest()
        self.resolutionQueue = []

        self.actionsPerEpisode = actionsPerEpisode
        self.remainingActions = actionsPerEpisode

        self.unservice = 0
        self.expense = 0
        self.unserviceRatios = []
        self.expenses = []
        self.loss = []

    def reset(self):
        self.__init__(self.actionsPerEpisode)

    def getActivitySeries(self):
        return self.activitySeries

    '''
    nextMove encoded as [start station L, start station W, end station L, end station W]
    '''
    def _generateNextInterest(self):
        if self.actionCounter == len(self.activitySeries):
            self.nextInterest = []
            return []
        nextAction = self.activitySeries[self.actionCounter]
        self.actionCounter += 1
        self.nextInterest = nextAction
        if not self.nextInterest[0] in self.stations.keys() or not self.nextInterest[1] in self.stations.keys():
            self._generateNextInterest()

    def getState(self):
        return [self.stations, self.nextInterest]

    def getSubState(self, id):
        station = self.stations[id]
        return [station, station.getClosest()]

    def render(self):
        print(self.nextInterest)
        for k in self.stations.keys():
            print(self.stations[k])
        print()


    def getUnserviceRatios(self):
        return self.unserviceRatios

    def getExpenses(self):
        return self.expenses

    def getLosses(self):
        return self.loss

    '''
    dir 
    0 down
    1 up
    2 right
    3 left
    or as
    0 1
    3 2
    '''
    def step(self, dir, incentive):
        startStation = self.stations[self.nextInterest[0]]
        endStation = self.stations[self.nextInterest[1]]

        '''
        '''
        stepExpense = 0
        bestOffer = 0
        bestDir = None

        for d in range(len(dir)):
            if not startStation.getClosest()[dir[d]] == None:
                offer = incentive[d] - self.spatialManager.genCost(startStation, self.stations[startStation.getClosest()[dir[d]]])
                if bestOffer < offer:
                    bestOffer = offer
                    bestDir = dir[d]
                    stepExpense = incentive[d]
        if bestDir != None:
            startStation = self.stations[startStation.getClosest()[bestDir]]
        '''
        '''

        if self.possible(startStation):
            # immediately depart
            startStation.changeSupply(-1)

            # wait to report changes and arrive
            self.resolutionQueue.append([startStation.getId(), endStation.getId()])
        else:
            self.unservice += 1

        self._generateNextInterest()
        self.remainingActions -= 1
        if self.remainingActions == 0:
            self.resetEpisode()
        self.expense += stepExpense
        done = False
        if self.nextInterest == []:
            done = True
        return self.nextInterest, stepExpense, bestDir, done

    def possible(self, station):
        return station.getSupply() > 0

    def resetEpisode(self):
        print("\tResolving")
        print(len(self.resolutionQueue))
        self.remainingActions = self.actionsPerEpisode

        for obj in self.resolutionQueue:
            self.stations[obj[0]].changePrevDept(1)
            self.stations[obj[1]].changeSupply(1)
            self.stations[obj[1]].changePrevArriv(1)
        self.resolutionQueue = []

        self.loss.append(self.genSystemLoss())
        self.unserviceRatios.append(self.unservice/self.actionsPerEpisode)
        self.expenses.append(self.expense)
        self.unservice = 0


    def genSystemLoss(self):
        losses = []
        for station in self.stations.keys():
            losses.append(self.stations[station].computeLoss())
        return sum(losses)/len(losses)
    '''
    def getNextMoveAsState(self):
        dept = self.nextInterest[0]
        arriv = self.nextInterest[1]
        out = np.array([out])
        return out  
    '''