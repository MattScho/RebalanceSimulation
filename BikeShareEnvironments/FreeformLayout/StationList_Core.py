import numpy as np

'''
This simulates an environment of a bike share system as a single vector (list) of station information (capacity)

A uniform distribution is used to determine the start and end locations for transactions

author: Matthew Schofield
version: 5.21.2020
'''

class StationList_core:

    def __init__(self, steps, initialDistribution, targetDistribution):
        '''
        Handler for simulation

        :param steps: Duration of simulation
        :param initialDistribution: The starting layout of the system
        :param targetDistribution: The desired distribution of bikes to be maintained
        '''

        # Check that the initial and target distributions have the same number of stations, vectors are of the same length
        if len(initialDistribution) != len(targetDistribution):
            Exception("Initialization and goal states have differing number of stations:\n\t{initial}\n\t{target}".format(initial=len(initialDistribution), target=len(targetDistribution)))

        self.numberOfStations = len(initialDistribution)

        # Initialize step
        # Counter for the current timestep
        self.timestep = 0
        self.maxSteps = steps

        # The state represention of the environment
        self.stations = list(initialDistribution)

        # Hold the input distributions
        self.initialState = initialDistribution
        self.goalState = targetDistribution

        # Initialize for representation of first transaction
        self.nextInterest = self._generateNextInterest(self.numberOfStations)

        # Initialize variable to track the error of the previous state
        self.prevError = 0

    '''
    Create a representation of the state for usage by models
    
    :return [station1, station2, ..., stationN, intendedStart, intendedDestination]
    '''
    def _buildState(self):
        outState = np.array(self.stations)
        outState = np.append(outState, self.nextInterest[0])
        outState = np.append(outState, self.nextInterest[1])
        return outState

    '''
    nextMove encoded as [start station L, start station W, end station L, end station W]
    '''
    def _generateNextInterest(self, numberOfStations):
        # randint uniform distribution
        start = np.random.randint(numberOfStations)
        target = np.random.randint(numberOfStations)
        self.nextInterest = [start, target]
        return self.nextInterest

    '''
    Resets the environment
    '''
    def reset(self):
        # Recreates the object
        self.__init__(self.maxSteps, self.initialState, self.goalState)
        return self._buildState()

    '''
    Print to screen a representation of the current state
        
    Currently: 
    station1 Availability, ..., stationN Availability
    '''
    def render(self):
        out = ""
        for station in range(self.numberOfStations):
            out += str(self.stations[station]) + ' '
        print(out)
        print(self._calculateError())

    '''
    Calculates the error between the current and goal state
    '''
    def _calculateError(self):
        # Create a vector of the absolute error between the current and goal state
        diffVector = abs(self.goalState - np.array(self.stations))
        # Find the average error
        return diffVector.mean(axis=None)

    '''
    Calculate the reward based on the error difference
    '''
    def _resultsBasedReward(self, errorDiff):
        if errorDiff > 0:
            reward = 5
        else:
            reward = -1
        return reward

    '''    
    Action conversion  
        | S-1 | S | S+1 |
    ----|-----|---|-----|
    E-1 |  0  | 1 |  2  |
    ----|-----|---|-----|
    E   |  3  | 4 |  5  |
    ----|-----|---|-----|
    E+1 |  6  | 7 |  8  |
    ----|-----|---|-----|
    
    Algorithm
    Is - Intended Start
    Ie - Intended End
    A - Action
    Fs - Finalized Start
    Fe - Finalized End 
    
    Fs = Is + ((A % 3)-1)
    Fe = Ie + ((A / 3) - 1)
    '''
    def convertStartEnd(self, start, end, action):
        # Algorithm here is described in the method description above
        start = start + ((action % 3) - 1)
        end = end + (int(action / 3) - 1)
        return start, end


    '''
    Action conversion  
        | S-1 | S | S+1 |
    ----|-----|---|-----|
    E-1 |  0  | 1 |  2  |
    ----|-----|---|-----|
    E   |  3  | 4 |  5  |
    ----|-----|---|-----|
    E+1 |  6  | 7 |  8  |
    ----|-----|---|-----|
    
    The action can move the start and end location 
    '''
    def step(self, action):
        # Prepare for movement
        start = self.nextInterest[0]
        end = self.nextInterest[1]

        # Check that the action is possible (will not go out of bounds)
        if self.possible(action):
            # Do conversion
            start, end = self.convertStartEnd(start, end, action)

            # There is a bike to leave
            if self.stations[start] > 0:
                # Move bike
                self.stations[end] += 1
                self.stations[start] -= 1

                # Calculate error after move
                error = self._calculateError()
                errorDiff = self.prevError - error
                # Save the current error
                self.prevError = error

                # Calculate reward based on error difference
                reward = self._resultsBasedReward(errorDiff)
            # Tried to use a station that has no available bikes,
            else:
                reward = -1
        # Tried to move out of bounds
        else:
            # Move bike
            self.stations[end] += 1
            self.stations[start] -= 1
            reward = -1

        # Create next interest
        self._generateNextInterest(self.numberOfStations)

        # Not done yet, check momentarily for an overwrite
        done = False

        # Increment time
        self.timestep += 1

        # Are we done??
        if self.timestep == self.maxSteps:
            # Show how we did
            self.render()
            print("DONE")
            print()
            done = True

        outState = self._buildState()
        return outState, reward, done, {}

    '''
    Check that a station has a bike to give up
    '''
    def possible(self, action):
        start = self.nextInterest[0]
        end = self.nextInterest[1]

        # Simulate movement
        start, end = self.convertStartEnd(start, end, action)

        return start >= 0 and start < self.numberOfStations and end >= 0 and end < self.numberOfStations
