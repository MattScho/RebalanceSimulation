import numpy as np


class Real_QTableIncentive:

    def __init__(self, environment, alpha):
        self.env = environment
        self.alpha = alpha
        self.QTable = self._generateCostMatrix(5)

    def bucketSubState(self, subState, buckets=5):
        bucketSize = 1 / buckets
        bucketedState = []


        for state in subState:
            found = False
            for i in reversed(range(buckets)):
                if state >= bucketSize * i:
                    bucketedState.append(bucketSize*i)
                    found = True
            if not found:
                bucketedState.append(-1 * (1/buckets))
        return bucketedState

    '''
    table is 
    [RequestStation][NW][NE][SW][SE]
    '''
    def _generateCostMatrix(self, buckets):
        bucketSize = 1 / buckets
        bucketList = list(range(buckets))
        bucketList.append(-1)
        outMatrix = {}
        for req in bucketList:
            outMatrix[req*bucketSize] = {}
            for NW in bucketList:
                outMatrix[req*bucketSize][NW*bucketSize] = {}
                for NE in bucketList:
                    outMatrix[req*bucketSize][NW*bucketSize][NE*bucketSize]  = {}
                    for SW in bucketList:
                        outMatrix[req*bucketSize][NW*bucketSize][NE*bucketSize][SW*bucketSize] = {}
                        for SE in bucketList:
                            outMatrix[req*bucketSize][NW*bucketSize][NE*bucketSize][SW*bucketSize][SE*bucketSize] =\
                                [np.random.randint(5), np.random.randint(5), np.random.randint(5), np.random.randint(5)]
        return outMatrix

    def run(self, games, stepsPerGame):
        allUnservice = []
        allExpenses = []
        for _ in range(games):
            self.env.reset()
            totalBudget = 0
            expenses = []
            direction = []
            incentive = []
            nextL = 0
            nextW = 0
            for i in range(stepsPerGame):
                print(i)
                '''
                '''
                nextInterest = self.env.getState()[1]
                vectorSubState = self.genSubState(nextInterest[0])
                beforeActionLose = self.genLossofSubState(nextInterest[0])
                buckets = self.bucketSubState(vectorSubState)
                action = self.act(buckets)
                nextMove, expense, lastDir, done = self.env.step([0, 1, 2, 3], action)
                if done:
                    break
                afterActionLose = self.genLossofSubState(nextInterest[0])
                reward = beforeActionLose - afterActionLose
                self.enactReward(buckets, reward * self.alpha)
                '''
                '''
            allExpenses.append(self.env.getExpenses())
            allUnservice.append(self.env.getUnserviceRatios())

        return allUnservice, allExpenses

    def genLossofSubState(self, sId):
        subState = self.env.getSubState(sId)

        state = self.env.getState()[0]
        out = [subState[0].computeLoss()]
        for i in range(4):
            if subState[1][i] != None:
                out.append(state[subState[1][i]].computeLoss())
        return sum(out)/len(out)


    def genSubState(self, station):
        subState = self.env.getSubState(station)
        state = self.env.getState()[0]
        out = [subState[0].getPercentCapacity()]
        for i in range(4):
            if subState[1][i] != None:
                out.append(state[subState[1][i]].getPercentCapacity())
            else:
                out.append(-1.0 * 1/5)
        return out

    def act(self, state):
        action = self.QTable[state[0]][state[1]][state[2]][state[3]][state[4]]
        print("\t" + str(action))
        return action

    def enactReward(self, state, reward):
        newAction = []
        for offer in self.QTable[state[0]][state[1]][state[2]][state[3]][state[4]]:
            newAction.append(min(max(offer - reward*self.alpha, 0),5))

        self.QTable[state[0]][state[1]][state[2]][state[3]][state[4]] = newAction

