class TemporalTripHandler:

    '''
    timeLeft | Destination
    '''
    def __init__(self, locations=5):
        self.tripTable = {}
        for loc in range(locations+1):
            self.tripTable[loc] = []
        self.locations = locations

    def addTrip(self, time, destination):

        # incase of a loop we will assume this takes 1 time step
        if time == 0:
            time += 1

        self.tripTable[time].append(destination)


    def timeStep(self):
        # Set up arrival dict
        arrivals = {}
        for loc in range(self.locations):
            arrivals[loc] = 0

        # Shift trips
        for k in range(1, self.locations):
            self.tripTable[k-1] = self.tripTable[k].copy()

        for dest in self.tripTable[0]:
            arrivals[dest] += 1
        self.tripTable[0] = []
        return arrivals

    def getTimeTable(self):
        return self.tripTable
