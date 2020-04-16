'''
This utility maps stations to their capacities

Author: Matthew Schofield
Version: 4/11/2020
'''
import pandas as pd
import numpy as np
import pickle as pkl

'''
pathToDataFile: a weekly record for station occupancy, this is used to as we can take the number of available docks
    + available bikes to find the capacity of the station
pathToSidToPublic: path to the file csv that maps station IDs to their 'public IDs'
'''
def capcityExtraction(pathToDataFile, pathToSidToPublic):
    # Read in weekly data file
    data = pd.read_csv(pathToDataFile, names=["lr", "si", "nba", "nda", "inst", "rntng","rtrng"])
    # Get unique station IDs
    uniqueSid = np.unique(data["si"].values)

    # Build map of station IDs to capacities
    sidCapcityMap = {}
    for sid in uniqueSid:
        record = data[data.si == sid].iloc[0]
        sidCapcityMap[sid] = record.nda + record.nba

    # Convert capacity map
    pubToSid = pd.read_csv(pathToSidToPublic)
    pubCapacitymap = {}
    for k in sidCapcityMap.keys():
        if not pubToSid[pubToSid.StationID == k].empty:
            # Get the record with the given station id
            record = pubToSid[pubToSid.StationID == k].iloc[0]
            # Map the public ID to the capacity
            pubCapacitymap[record.publicID] = sidCapcityMap[k]
    return pubCapacitymap

# Create map
pubToCapacityMap = capcityExtraction("DC_data_1580694232_to_1581304847.csv", "DC_StationID_to_publicID_to_name")

# Dump the data to a pkl file
pkl.dump(pubToCapacityMap, open("PubToCapcityMap.pkl", 'wb+'))
