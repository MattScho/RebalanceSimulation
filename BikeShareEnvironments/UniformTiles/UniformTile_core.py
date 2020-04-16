import numpy as np

'''
This simulates an environment of a bike share system as an n x m x 3 grid
The n and m are the length and width of the grid representing the system
and then each cell has three values, [supply, previous arrivals, previous deptartures] 
A uniform distribution is used to determine the start and end locations for transactions
'''
class UniformTile_core:

    def __init__(self, length, width, actionsPerEpisode):
        self.length = length
        self.width = width

        # The state matrix/tensor representing the environment  
        self.state = self._initState(length, width)
        self.nextInterest = self._generateNextInterest()

        # Initializes values for handling episode timing
        self.actionsPerEpisode = actionsPerEpisode
        self.remainingActions = actionsPerEpisode

        # The matrix to readjust the state upon completion of an episode
        self.stateChange = np.zeros((length, width,3))

        # Initialization of metrics
        self.unservice = 0
        self.expense = 0

        # Records metrics for evaluation
        self.unserviceRatios = []
        self.expenses = []

        # The cost matrix for moving from one station to the next
        self.costMatrix = self._generateCostMatrix()

    '''
    Resets the environment
    '''
    def reset(self):
        self.__init__(self.length, self.width, self.actionsPerEpisode)

    '''
    Initializes the state matrix
    [
        [ [Supply1, prevArrivals1, prevDepartures1] ... ]
        .
        .
        .
    ]
    '''
    def _initState(self, length, width):
        stateMatrix = np.zeros((length, width,3))
        for l in range(length):
            for w in range(width):
                stateMatrix[l][w][0] = 10
        return stateMatrix

    '''
    nextMove encoded as [start station L, start station W, end station L, end station W]
    '''
    def _generateNextInterest(self):
        # randint uniform distribution
        startLInd = np.random.randint(self.length)
        startWInd = np.random.randint(self.width)
        targetLInd = np.random.randint(self.length)
        targetWInd = np.random.randint(self.width)
        self.nextInterest = [startLInd, startWInd, targetLInd, targetWInd]
        return self.nextInterest

    '''
    Builds cost matrix for moving from one station to another
    '''
    def _generateCostMatrix(self):
        outMatrix = np.zeros((4,self.length, self.width))
        for d in [0,1,2,3]:
            for l in range(self.length):
                for w in range(self.width):
                    outMatrix[d][l][w] = np.random.randint(5)
        return outMatrix

    '''
    Returns the state and next next interest
    
    [stateMatrix, nextInterest]
    '''
    def getState(self):
        return [self.state, self.nextInterest]

    '''
    Get state of specific station
    '''
    def getSubState(self, lInd, wInd):
        return self.state[lInd][wInd]

    '''
    Return state of a station and it surrounding stations
    '''
    def getSubRegion(self, lInd, wInd):
        out = []
        out.append(self.state[lInd][wInd])
        if lInd > 0:
            out.append(self.state[lInd-1])
        if lInd < self.length-1:
            out.append(self.state[lInd+1])
        if wInd > 0:
            out.append(self.state[wInd-1])
        if wInd < self.width-1:
            out.append(self.state[wInd+1])
        return out

    '''
    Print to screen the current state
    '''
    def render(self):
        out = ""
        for l in range(self.length):
            for w in range(self.width):
                out += str(self.state[l][w]) + '\t'
            out += "\n"
        print(out)

    '''
    Return a lsit of unservice ratios
    '''
    def getUnserviceRatios(self):
        return self.unserviceRatios

    '''
    Return a list of expenses
    '''
    def getExpenses(self):
        return self.expenses

    '''
    dir 
    0 down
    1 up
    2 right
    3 left
    '''
    def step(self, dir, incentive):
        # Prepare for movement
        startStationL = self.nextInterest[0]
        startStationW = self.nextInterest[1]
        endStationL = self.nextInterest[2]
        endStationW = self.nextInterest[3]

        stepExpense = 0

        '''
        Determine if any of the given incentives is enough to change starting location
        '''
        bestOffer = 0
        bestDir = None

        for d in range(len(dir)):
            offer = incentive[d] - self.costMatrix[dir[d]][startStationL][startStationW]
            if bestOffer < offer and self.valid(startStationL, startStationW, dir[d]):
                bestOffer = offer
                bestDir = dir[d]
                stepExpense = self.costMatrix[dir[d]][startStationL][startStationW]
        if bestDir != None:
            if bestDir == 0:
                startStationL += 1
            elif bestDir == 1:
                startStationL -= 1
            elif bestDir == 2:
                startStationW += 1
            elif bestDir == 3:
                startStationW -= 1
        '''
        '''

        if self.possible(startStationL, startStationW):
            # immediately depart
            self.state[startStationL][startStationW][0] -= 1

            # wait to report changes and arrive
            self.stateChange[startStationL][startStationW][2] += 1
            self.stateChange[endStationL][endStationW][0] += 1
            self.stateChange[endStationL][endStationW][1] += 1
        else:
            # Request failed
            self.unservice += 1

        # Create next interest
        self._generateNextInterest()

        # Check if the episode is complete
        self.remainingActions -= 1
        if self.remainingActions == 0:
            self.resetEpisode()
        self.expense += stepExpense
        return self.nextInterest, stepExpense, bestDir

    '''
    Check that a station has a bike to give up
    '''
    def possible(self, startL, startW):
        return self.state[startL][startW][0] > 0

    '''
    Reset for the next episode
    '''
    def resetEpisode(self):
        # Reset counter
        self.remainingActions = self.actionsPerEpisode
        # Reallocate the previous acitivity elements of the matrix
        for l in range(self.length):
            for w in range(self.width):
                self.state[l][w][1] = 0
                self.state[l][w][2] = 0
        self.state = np.add(self.state, self.stateChange)
        self.stateChange = np.zeros((self.length, self.width, 3))

        # Save metrics
        self.unserviceRatios.append(self.unservice/self.actionsPerEpisode)
        self.expenses.append(self.expense)

        # reset unservice ratio, but not expense
        self.unservice = 0

    '''
    Check if moving in a direction is valid from a given station
    '''
    def valid(self, stationL, stationW, dir):
        ret = True
        if dir == 0 and stationL == self.length-1:
            ret = False
        elif dir == 1 and stationL == 0:
            ret = False
        elif dir == 2 and stationW == self.width-1:
            ret = False
        elif dir == 3 and stationW == 0:
            ret = False
        return ret

    '''
    Redefine the next move as a vector, useful for neural networks
    '''
    def getNextMoveAsVector(self):
        lInd = self.nextInterest[0]
        wInd = self.nextInterest[1]
        out = []
        out.append(self.state[lInd][wInd][0])
        if lInd > 0:
            out.append(self.state[lInd-1][wInd][0])
        else:
            out.append(-1.0)
        if lInd < self.length-1:
            out.append(self.state[lInd+1][wInd][0])
        else:
            out.append(-1.0)
        if wInd > 0:
            out.append(self.state[lInd][wInd-1][0])
        else:
            out.append(-1.0)
        if wInd < self.width-1:
            out.append(self.state[lInd][wInd+1][0])
        else:
            out.append(-1.0)
        out = np.array([out])
        return out