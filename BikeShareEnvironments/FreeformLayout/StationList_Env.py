from Environments.BikeShare.FreeformLayout.StationList_Core import StationList_core
import gym
from gym import spaces
import numpy as np

'''
An interface for the station list representation of bikeshare environment
'''
class StationListEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self,  steps, initialDistribution, targetDistribution):
        self.name = "Station List: %s\n=>\n%s".format({str(initialDistribution), str(targetDistribution)})
        self.env = StationList_core(steps, initialDistribution, targetDistribution)
        self.action_space = spaces.Discrete(9)
        self.observation_space = spaces.Box(0.0, float(np.sum(targetDistribution)), shape=(len(initialDistribution)+2,), dtype=np.float32)

    '''
    Reset the environment
    '''
    def reset(self):
        return self.env.reset()

    '''
    Return the environment name
    '''
    def getName(self):
        return self.name

    '''
    Return the state as
    
    :return [station1, station2, ..., stationN, intendedStart, intendedDestination]
    '''
    def getState(self):
        return self.env._buildState()

    '''
    Show the environment
    '''
    def render(self, method='human'):
        self.env.render()

    '''
    Take action
    '''
    def step(self, action):
        return self.env.step(action)

    def close(self):
        self.reset()

