from BikeShareEnvironments.GaussianTiles.GaussianTile_core import GaussianTile_core
'''
An interface for the gaussian bikeshare environment
'''
class GaussianTile_Wrapper:
    def __init__(self, length, width, actionsPerEpisode):
        self.name = "Gaussian_Tile_%sx%s".format({length, width})
        self.env = GaussianTile_core(length, width, actionsPerEpisode)

    '''
    Reset the environment
    '''
    def reset(self):
        self.env.reset()

    '''
    Return dimensions of the environment
    '''
    def getLW(self):
        return self.env.length, self.env.width

    '''
    Return the environment name
    '''
    def getName(self):
        return self.name

    '''
    Return the state as
    [stateMatrix, nextInterest]
    '''
    def getState(self):
        return self.env.getState()

    '''
    Show the environment
    '''
    def render(self):
        self.env.render()

    '''
       have the environment step
       dir is a list of [0,1,2,3] where:
           0 down
           1 up
           2 right
           3 left
       and incentive is the incentive offered for that direction

       Example:
       dir: [1,2]
       incentive: [3,5]

       would mean that there is an offer of
       3 currency (say dollars) for a user to move up/north
       and
       5 currency for a user to move right/east
       '''
    def step(self, dir, incentive):
        return self.env.step(dir, incentive)

    '''
    A list of the unservice ratios
    '''
    def getUnserviceRatios(self):
        return self.env.getUnserviceRatios()

    '''
    A list of expenses
    '''
    def getExpenses(self):
        return self.env.getExpenses()

    '''
    Returns the intended next move as a vector for use in a neural network
    '''
    def getNextMoveAsState(self):
        return self.env.getNextMoveAsState()
