'''
This method offers a flat incentive for all directions whenever there is a possible unservice event
This is designed to be used as baseline method

:author: Matthew Schofield
:version: 3/25/2020
'''
class FlatIncentivizer:

    '''
    environment - the environment to apply this methodology to
    incentive - amount to consisitently offer
    '''
    def __init__(self, environment, incentive):
        self.env = environment
        self.incentive = incentive

    '''
    Run the environment with this method
    games - number of games to play
    stepsPerGames - total number of steps, should be divisiable by the stepsPerEpisode parameter of the environment
    '''
    def run(self, games, stepsPerGame):
        allUnservice = []
        allExpenses = []
        allLoss = []
        for _ in range(games):
            self.env.reset()
            direction = []
            incentive = []
            for i in range(stepsPerGame):
                '''
                The algorithm begins here
                '''
                nextMove, expense, lastDir, done = self.env.step(direction, incentive)
                if done:
                    break

                state = self.env.getState()[0]
                # identify a possible unservice event
                if state[nextMove[0]].getSupply() == 0:
                    direction = [0, 1, 2, 3]
                    incentive = [self.incentive, self.incentive, self.incentive, self.incentive]
                else:
                    direction = []
                    incentive = []
                '''
                '''
            allExpenses.append(self.env.getExpenses())
            allUnservice.append(self.env.getUnserviceRatios())
            allLoss.append(self.env.getLosses())

        return allUnservice, allExpenses