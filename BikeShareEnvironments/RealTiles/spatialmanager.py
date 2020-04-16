import pickle as pkl
import pandas as pd
from BikeShareEnvironments.RealTiles.station import Station
import math
import time

class SpatialManager:
    def __init__(self):
        self.relevantStations = pkl.load(open("D:/MajorProjects/RebalanceSim/data/serialized/stationMapping.pkl", 'rb'))[0]
        self.stationToPublicFrame = pd.read_csv("D:/MajorProjects/RebalanceSim/data/serialized/DC_StationID_to_publicID_to_name")
        self.pubToCapacityMap = pkl.load(open("D:/MajorProjects/RebalanceSim/data/serialized/PubToCapacityMap.pkl", 'rb'))
        publicID = self.stationToPublicFrame["publicID"].values
        stationID = self.stationToPublicFrame["StationID"].values
        stationToPubMap = {}
        for i in range(len(stationID)):
            stationToPubMap[publicID[i]] = stationID[i]

        self.spatialLocations = pd.read_csv("D:/MajorProjects/RebalanceSim/data/serialized/RegionsWithCenter.csv")
        self.spatialLocations = self.spatialLocations.set_index("Station")

        self.tripData = pd.read_csv("D:/MajorProjects/RebalanceSim/data/RawData/Trip/201910-capitalbikeshare-tripdata.csv")

        pattern = "%Y-%m-%d %H:%M:%S"
        self.tripData["StartE"] = self.tripData["Start date"].apply(lambda x : int(time.mktime(time.strptime(x, pattern))))
        self.tripData["EndE"] = self.tripData["End date"].apply(lambda x : int(time.mktime(time.strptime(x, pattern))))
        self.tripData = self.tripData.drop(columns=["Start date","End date","Bike number","Member type"])

        experimentActionStart = 1569902400 + 1800
        self.loaderTripDataStart = self.tripData[self.tripData["StartE"] < experimentActionStart]
        self.loaderTripDataEnd = self.tripData[self.tripData["EndE"] < experimentActionStart]


        locationMap = self._buildLocationMap(self.relevantStations, self.spatialLocations)
        self.stations = {}
        for id in locationMap.keys():
            print(id)
            closest = self._findClosest(locationMap, id)
            availFrame = pd.read_csv("D:/MajorProjects/RebalanceSim/data/Availability/" + str(stationToPubMap[id]) + "_test.csv")
            availFrame = availFrame.set_index("Day")
            supply = availFrame.at[1569888000,"14400"]
            prevDept = len(self.loaderTripDataStart[self.loaderTripDataStart["Start station number"] == id])
            prevArriv = len(self.loaderTripDataEnd[self.loaderTripDataEnd["End station number"] == id])
            if id in self.pubToCapacityMap.keys():
                self.stations[id] = Station(id, locationMap[id], closest, supply, prevDept, prevArriv, self.pubToCapacityMap[id])
        for id in self.stations.keys():
            print(self.stations[id])
        self.activititySeries = self.tripData[["Start station number","End station number"]].values



    def genCost(self, s1, s2):
        s1Coords = s1.getCoords()
        s2Coords = s2.getCoords()
        meters = self.latLonsToMeterDistance(s1Coords[0], s1Coords[1], s2Coords[0], s2Coords[1])
        return meters / 100

    def latLonsToMeterDistance(self, lat1, lon1, lat2, lon2):
        R = 6370.433
        lat1Rad = lat1 * (math.pi / 180)
        lat2Rad = lat2 * (math.pi / 180)

        delLatRad = abs(lat2 - lat1) * math.pi / 180
        delLonRad = abs(lon2 - lon1) * math.pi / 180

        a = math.sin(delLatRad / 2) * math.sin(delLatRad) + \
            math.cos(lat1Rad) * math.cos(lat2Rad) * \
            math.sin(delLonRad) * math.sin(delLonRad)

        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        out = R * c * 1000
        return out

    def getActivitySeries(self):
        return self.activititySeries

    def getStations(self):
        return self.stations

    def _buildLocationMap(self, IDs, spatialFrame):
        outMap = {}
        for id in IDs:
            if not id in [31202,31119]:
                lat = spatialFrame.at[id, "Latitude"]
                lon = spatialFrame.at[id, "Longitude"]
                outMap[id] = [lat, lon]
        return outMap

    def _euclidDist(self, p1, p2):
        if p1 == None or p2 == None:
            return 9999999 # effectively inf
        return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

    def _findClosest(self, locationMap, id):
        nwStation = None
        neStation = None
        swStation = None
        seStation = None
        for nId in locationMap.keys():
            if nId != id:
                spatialLoc = self._spatialRelation(locationMap[id], locationMap[nId])
                if spatialLoc == "NW":
                    if self._euclidDist(locationMap[id], locationMap[nId]) < self._euclidDist(locationMap[id], locationMap.get(nwStation,None)):
                        nwStation = nId
                elif spatialLoc == "NE":
                    if self._euclidDist(locationMap[id], locationMap[nId]) < self._euclidDist(locationMap[id], locationMap.get(neStation,None)):
                        neStation = nId
                elif spatialLoc == "SW":
                    if self._euclidDist(locationMap[id], locationMap[nId]) < self._euclidDist(locationMap[id], locationMap.get(swStation,None)):
                        swStation = nId
                elif spatialLoc == "SE":
                    if self._euclidDist(locationMap[id], locationMap[nId]) < self._euclidDist(locationMap[id], locationMap.get(seStation,None)):
                        seStation = nId
        return [nwStation, neStation, swStation, seStation]

    '''
    p2 is to the ____ of p1
    '''
    def _spatialRelation(self, p1, p2):
        out = ""
        if p2[0] > p1[0]:
            out += "N"
        else:
            out += "S"
        if p2[1] > p1[1]:
            out += "E"
        else:
            out += "W"
        return out

SpatialManager()