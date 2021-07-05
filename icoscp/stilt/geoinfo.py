# -*- coding: utf-8 -*-
"""
STILT stations by nature have only a geolocation [lat, lon], but no
other geographical information attached. This helper script
runs through all the available stilt stations, to
1. reverse geocode the location 
2. store all the information into a json file for offline retrieval.
(the json file will be distributed with the library for the moment)

The reason behind this, we cannot afford  the time to reverse geocode
all the stations 'live'. However the script can only run on our server
where we have access to the stilt station lat/lon information, this is
currently not available through http. ideally it will be provided through
https://stilt.icos-cp.eu/viewer/stationinfo

"""

import json
from icoscp.station import station as cpstation
import icoscp.const as CPC
import os
import pandas as pd
from tqdm import tqdm
import numpy as np
import icoscp.country as country


STN = 'stations.json'

def _save():
    ''' please DO NOT execute this function
        unless you want to re-create / update the offline station
        list, stored inside this script. If this is the case, 
		please execute this script on a CarbonPortal server, 
		with access to the stilt data file system.
		The content of the resulting stations.json file should be
		copied into this file to replace the current directory
    '''
        
    with open(STN, 'w') as f:
        json.dump(__save_all(), f)
        
def get(id=None):
    """
    Returns all offline STILT stations geographica info.

    Parameters
    ----------
    id : STR, default None -> which returns ALL stations
        Stilt station ID

    Returns
    -------
    DICT
        Geographical information locally stored for the Stilt station.
        If lat/lon is within a countryborder, the result
        from icoscp.coutntry9[lat, lon]) is returned.

    """
    
    d = os.path.abspath(__file__)
    stn = os.path.join(os.path.split(d)[0], 'stations.json')
    with open(stn, 'r') as f:
        data = json.loads(f.read())
    
    if id in data.keys():
        return data[id]
    
    return data


def __save_all():
    """ get all stilt stations available on the server 
        return dictionary with meta data, keys are stilt station id's
    """
        
    # use directory listing from siltweb data
    allStations = os.listdir(CPC.STILTPATH)

    # add information on station name (and new STILT station id)
    # from stations.csv file used in stiltweb.
    # this is available from the backend through a url
    df = pd.read_csv(CPC.STILTINFO)
    
    # add ICOS flag to the station
    icosStations = cpstation.getIdList()
    icosStations = list(icosStations['id'][icosStations.theme=='AS'])
    
    # dictionary to return
    stations = {}

    # fill dictionary with ICOS station id, latitude, longitude and altitude
    for ist in tqdm(sorted(allStations)):
  
        if not ist in df['STILT id'].values:
            continue
        
        stations[ist] = {}
        # get filename of link (original stiltweb directory structure) and extract location information
       
        loc_ident = os.readlink(CPC.STILTPATH+ist)
        clon = loc_ident[-13:-6]
        lon = np.float(clon[:-1])
        if clon[-1:] == 'W':
            lon = -lon
        clat = loc_ident[-20:-14]
        lat = np.float(clat[:-1])
        if clat[-1:] == 'S':
            lat = -lat
        alt = np.int(loc_ident[-5:])

        stations[ist]['lat']=lat
        stations[ist]['lon']=lon
        stations[ist]['alt']=alt
        stations[ist]['locIdent']=os.path.split(loc_ident)[-1]

        # set the name and id         
        stations[ist]['id'] = df.loc[df['STILT id'] == ist]['STILT id'].item()        
        stationName = str(df.loc[df['STILT id'] == ist]['STILT name'].item())        
        stations[ist]['name'] = __stationName(stations[ist]['id'], stationName, stations[ist]['alt'])        

        # set a flag if it is an ICOS station
        stn = stations[ist]['id'][0:3].upper()
        if stn in icosStations:
            stations[ist]['icos'] = cpstation.get(stn).info()
        else:
            stations[ist]['icos'] = False
        
        # set years and month of available data
        years = os.listdir(CPC.STILTPATH+'/'+ist)
        stations[ist]['years'] = years
        for yy in sorted(stations[ist]['years']):
            stations[ist][yy] = {}
            months = os.listdir(CPC.STILTPATH+'/'+ist+'/'+yy)
            # remove cache txt entry
            sub = 'cache'
            months = sorted([m for m in months if not sub.lower() in m.lower()])
            stations[ist][yy]['months'] = months
            stations[ist][yy]['nmonths'] = len(stations[ist][yy]['months'])
    
    for s in tqdm(stations):
        stations[s]['geoinfo'] = country.get(latlon=[stations[s]['lat'],stations[s]['lon']])
        
    return stations

def __stationName(idx, name, alt):    
    if name=='nan':
        name = idx
    if not (name[-1]=='m' and name[-2].isdigit()):           
        name = name + ' ' + str(alt) + 'm'    
    return name
