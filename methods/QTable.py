import numpy as np


class QTableIncentive:

    def __init__(self, environment, alpha):
        self.env = environment
        self.alpha = alpha
        self.length, self.width = self.env.getLW()
        self.QTable = self._generateCostMatrix(self.length,self.width)

    def _generateCostMatrix(self, length, width):
        outMatrix = np.zeros((4, length, width))
        for d in [0, 1, 2, 3]:
            for l in range(length):
                for w in range(width):
                    outMatrix[d][l][w] = np.random.randint(5)

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
                '''
                '''
                nextMove, expense, dir = self.env.step(direction, incentive)

                if dir == None:
                    self.QTable[0][nextL][nextW] += self.alpha
                    self.QTable[1][nextL][nextW] += self.alpha
                    self.QTable[2][nextL][nextW] += self.alpha
                    self.QTable[3][nextL][nextW] += self.alpha
                else:
                    self.QTable[dir][nextL][nextW] -=  self.alpha
                nextL = nextMove[0]
                nextW = nextMove[1]

                totalBudget += expense
                expenses.append(totalBudget)
                state = self.env.getState()[0]
                if state[nextL][nextW][0] == 0:
                    direction = [0, 1, 2, 3]
                    incentive = [self.QTable[0][nextL][nextW],
                                 self.QTable[1][nextL][nextW],
                                 self.QTable[2][nextL][nextW],
                                 self.QTable[3][nextL][nextW]]
                else:
                    direction = []
                    incentive = []
                '''
                '''
            allExpenses.append(self.env.getExpenses())
            allUnservice.append(self.env.getUnserviceRatios())

        return allUnservice, allExpenses



