CAPACITY_MARGIN = .10

class Station:
    '''

    Closest format =
    [
        northwest,
        northeast,
        southwest,
        southeast
    ]
    '''
    def __init__(self, id, location, closest, startS, prevDept, prevArriv, capacity):
        self.stationID = id
        self.lat = location[0]
        self.lon = location[1]
        self.closest = closest

        self.capacity = capacity
        self.margin = self.capacity * CAPACITY_MARGIN
        self.supply = startS
        self.pDepartures = prevDept
        self.pArrivals = prevArriv
        self.pExpense = 0
        self.pUnserv = 0
        self.history = []

    def getPercentCapacity(self):
        return self.supply / self.capacity

    def changePrevDept(self, change):
        self.pDepartures += change

    def changePrevArriv(self, change):
        self.pArrivals += change

    def changeSupply(self, change):
        if self.stationID == 31623:
            print("\t" + str(change))
        self.supply += change
        self.history.append(self.supply)

    def getHistory(self):
        return self.history

    def getSupply(self):
        return self.supply

    def getCoords(self):
        return [self.lat, self.lon]

    def getClosest(self):
        return self.closest

    def getId(self):
        return self.stationID

    def isClose(self, sId):
        return sId in self.closest

    def nwCl(self):
        return self.closest[0]

    def neCl(self):
        return self.closest[1]

    def swCl(self):
        return self.closest[2]

    def seCl(self):
        return self.closest[3]

    '''
    TO_DO: change to V function
    '''
    def computeLoss(self):
        percentCap = self.supply / self.capacity
        return abs(percentCap - .5)* 2
        #return (percentCap - .5) * 2


    def showClosest(self):
        print("Debugging Only")
        print("\t" + str(self.closest))

    def __str__(self):
        return "ID:{id}, ({lat}, {lon})\n\tState: {supply}/{capacity}, {pArriv}, {pDept}\n\t{closest}".format(
            id=self.stationID,
            lat=self.lat,
            lon=self.lon,
            supply=self.supply,
            capacity=self.capacity,
            pArriv=self.pArrivals,
            pDept=self.pDepartures,
            closest=self.closest
        )

