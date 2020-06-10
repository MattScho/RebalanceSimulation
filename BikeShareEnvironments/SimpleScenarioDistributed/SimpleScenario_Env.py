import gym
from gym import spaces
import numpy as np
from Environments.BikeShare.SimpleScenario.TemporalTripHandler import TemporalTripHandler
import random
from numpy.random import choice
'''
An interface for the station list representation of bikeshare environment
'''
class SimpleScenarioEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self, systemSize=10, numInitBikes=10, budget=0, tripsPerHour=30, dayLen=24, daysToSim=1, eventsPerStep=10, alwaysIncentive=False):
        # Set up
        self.alpha = 1
        self.name = "Simple Scenario {systemSize}".format(systemSize=systemSize)
        self.numEventsPerStep = eventsPerStep
        self.curStep = 0
        self.dayLen = dayLen
        self.daysToSim = daysToSim
        self.timeSpace = list(range(dayLen))
        self.numStations = systemSize
        self.initNumBikes = numInitBikes
        self.tripsPerHour = tripsPerHour
        self.budget = budget
        # TODO: Function that generates an initial distribution by spreading out bikes

        self.action_space = spaces.Box(0,5, shape=(self.numStations,), dtype=np.float32)
        self.observation_space = spaces.Box(0.0, self.numStations*self.initNumBikes,
                                            shape=(self.numStations+1,), dtype=np.float32)

        # Simulation
        self.alwaysIncentive = alwaysIncentive
        self.goalState = [self.initNumBikes for _ in range(self.numStations)]
        self.stations = self.goalState.copy()
        self.bikes = self._bikeDistributionsFromStations(self.stations)
        self.tripHandler = TemporalTripHandler()

    '''
    Reset the environment
    '''
    def reset(self):
        self.__init__(len(self.stations))
        return self.getState()

    '''
    Return the environment name
    '''
    def getName(self):
        return self.name

    '''
    Return the state as

    :return [station1, station2, ..., stationN, budget]
    '''
    def getState(self):
        state = np.array(self.stations)
        state = np.append(state, self.budget)
        return state

    '''
    Show the environment
    '''
    def render(self, method='human'):
        outputStr = "Stations State: {stations}\n" \
                    "Remaining Budget: {budget}"\
            .format(stations=self.stations, budget=self.budget)
        for bike in self.bikes:
            print("%.3f | " % bike)
        print(outputStr)
        # Separately add new line for clarity
        print()

    '''
    Take action
    '''

    def step(self, incentives):
        satisfiedReq = 0

        if (self.curStep % self.dayLen) < 12:
            distrib = 0
        else:
            distrib = 1
        trips = self.createTripSeries(distrib)
        for trip in trips:
            start = trip[0]
            startInd = int(trip[0])
            action = []
            if startInd != 0:
                action.append(incentives[startInd-1])
            else:
                action.append(0)

            if startInd != self.numStations-1:
                action.append(incentives[startInd+1])
            else:
                action.append(0)



            if self.stations[int(trip[0])] == 0:
                left, right = self._findClosestBikes(start)

                if left != -1:
                    leftCost = self.alpha * (start - self.bikes[left])
                else:
                    leftCost = 999

                if right != -1:
                    rightCost = self.alpha * abs(start - self.bikes[right])
                else:
                    rightCost = 999

                incentiveL = action[0]
                incentiveR = action[1]

                if incentiveL > leftCost and incentiveL <= self.budget:
                    trip[0] = self.bikes[left]
                    self.budget -= incentiveL
                    satisfiedReq += 1
                    self.stations[int(trip[0])] -= 1
                    self.bikes.pop(left)
                    self.tripHandler.addTrip(abs(int(trip[1]) - int(trip[0]))+1, trip[1])
                elif incentiveR > rightCost and incentiveR <= self.budget:
                    trip[0] = self.bikes[right]
                    self.budget -= incentiveR
                    satisfiedReq += 1
                    self.stations[int(trip[0])] -= 1
                    self.bikes.pop(right)
                    self.tripHandler.addTrip(abs(int(trip[1]) - int(trip[0]))+1, trip[1])
            else:
                left, right = self._findClosestBikes(start)
                if left == -1:
                    trip[0] = self.bikes[right]
                elif right == -1:
                    trip[0] = self.bikes[left]
                if start - self.bikes[left] < abs(start - self.bikes[right]):
                    trip[0] = self.bikes[left]
                    self.bikes.pop(left)
                else:
                    trip[0] = self.bikes[right]
                    self.bikes.pop(right)
                satisfiedReq += 1
                self.stations[int(trip[0])] -= 1
                self.tripHandler.addTrip(abs(int(trip[1]) - int(trip[0]))+1, trip[1])

        arrivals = self.tripHandler.timeStep()
        for arr in arrivals:
            self.bikes.append(arr)
            self.stations[int(arr)] += 1


        # Can be made more complex in the future
        reward = satisfiedReq # number of trips

        # Check if simulation is done
        self.curStep += 1
        done = False
        if self.curStep == self.dayLen * self.daysToSim:
            done = True
        return self.getState(), reward, done, {}

    def createTripSeries(self, distribution):
        if distribution == 0:
            possibleTrips, tripProbabilities = self._genMorningDistribution(self.numStations)
        elif distribution == 1:
            possibleTrips, tripProbabilities = self._genAfternoonDistribution(self.numStations)

        pTrips = []
        for poss in possibleTrips:
            pTrips.append(str(poss))
        trips = choice(pTrips, 20, p=tripProbabilities)
        trips = [eval(t) for t in trips]

        return trips

    def close(self):
        self.reset()

    '''
    Calculates the error between the current and goal state
    '''
    def _calculateError(self):
        # Create a vector of the absolute error between the current and goal state
        diffVector = abs(self.goalState - np.array(self.stations))
        # Find the average error
        return diffVector.mean(axis=None)

    '''
    Creates Bike distributions throughout regions
    '''
    def _bikeDistributionsFromStations(self, stations):
        bikes = []
        for station in range(len(stations)):
            for bike in range(stations[station]):
                bikes.append(self._randomizeLocaleInRegion(station))
        return  bikes

    def _randomizeLocaleInRegion(self, region):
        # (Possibly redundant) min is to catch if random.random() => 1
        return min(region + random.random(), region + .9999)

    def _findClosestBikes(self, start):
        left = self.numStations
        leftB = -1
        right = self.numStations
        rightB = -1
        for i, bike in enumerate(self.bikes):

            dist = start - bike
            if bike < start:
                if dist < left:
                    leftB = i
                    left = dist
            else:
                dist = abs(dist)
                if dist < right:
                    rightB = i
                    right = dist

        return leftB, rightB

    '''
    Normalize probability vector
    '''
    def normalize(self, vec):
        normalizeFactor = sum(vec)
        return [e/normalizeFactor for e in vec]

    '''
    mdpt  ^
         / \
    0   /   \
    
    0 <= value <= mdpt*2
    '''
    def inverseAbsoluteDistrib(self, mdpt, value, exponent):
        return abs(mdpt - value) ** exponent

    '''
    mdpt \   /
          \ /
    0      v
    
    0 <= value <= mdpt*2
    '''
    def absoluteDistrib(self, mdpt, value, exponent):
        return abs(abs(mdpt - value) - mdpt) ** exponent

    def _genAfternoonDistribution(self, numberOfStations):
        possibleTrips = []
        probabilities = []
        for i in range(numberOfStations):
            for j in range(numberOfStations):
                possibleTrips.append([i,j])

                mdpnt = int(numberOfStations/2)

                destinationIncent = self.inverseAbsoluteDistrib(mdpnt, j, 2)
                startIncent = self.absoluteDistrib(mdpnt, i, 2)
                tripIncent = destinationIncent + startIncent

                probabilities.append(tripIncent)
        probabilities = self.normalize(probabilities)
        return possibleTrips, probabilities


    def _genMorningDistribution(self, numberOfStations):
        possibleTrips = []
        probabilities = []
        for i in range(numberOfStations):
            for j in range(numberOfStations):
                possibleTrips.append([i,j])

                mdpnt = int(numberOfStations / 2)

                destinationIncent = self.absoluteDistrib(mdpnt, j, 1)
                startIncent = self.inverseAbsoluteDistrib(mdpnt, i, 1)
                tripIncent = destinationIncent + startIncent

                probabilities.append(tripIncent)
        probabilities = self.normalize(probabilities)

        return possibleTrips, probabilities

