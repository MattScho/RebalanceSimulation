'''
User object to represent some data about a user that appears
requesting to use a bike

Author: Matthew Schofield
Version: 4/12/2020
'''

import math

class User:
    def __int__(self, stationAt, stationLocs):
        self.stationAt = stationAt
        self.stationLocs = stationLocs

    def _euclidDist(self, s1, s2):
        if s1 == None or s2 == None:
            return 9999999 # effectively inf
        return math.sqrt((s1.getLat() - s2.egtLat())**2 + (s1.getLon() - s2.getLon())**2)

    def cost(self, stationSuggestion):
        if stationSuggestion.getId() == self.stationAt.getId():
            return 0
        elif self.stationAt.isClose(stationSuggestion.getId()):
            return self._euclidDist(self.stationAt, stationSuggestion)
        else:
            return 99999

    def offer(self, stationSuggestion, offer):
        return offer - self.cost(stationSuggestion)