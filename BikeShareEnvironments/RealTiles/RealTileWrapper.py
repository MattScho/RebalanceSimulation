from BikeShareEnvironments.RealTiles.RealTile_core import RealTile_core
from BikeShareEnvironments.RealTiles.spatialmanager import SpatialManager


class RealTile_Wrapper:
    def __init__(self, actionsPerEpisode):
        self.name = "Real_Tile"
        self.env = RealTile_core(actionsPerEpisode)


    def reset(self):
        self.env.reset()

    def getActivitySeries(self):
        return self.env.getActivitySeries()

    def getName(self):
        return self.name

    def getState(self):
        return self.env.getState()

    def render(self):
        self.env.render()

    def step(self, dir, incentive):
        return self.env.step(dir, incentive)

    def getUnserviceRatios(self):
        return self.env.getUnserviceRatios()

    def getExpenses(self):
        return self.env.getExpenses()

    def getSubState(self, id):
        return self.env.getSubState(id)


    def getLosses(self):
        return self.env.getLosses()