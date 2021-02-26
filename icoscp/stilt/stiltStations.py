# -*- coding: utf-8 -*-
"""
Created on Tue Dec  8 09:07:38 2020
@author: Claudio
"""

import os
import numpy as np
import pandas as pd
from icoscp.station import station as cpstation

STILTPATH = '/data/stiltweb/stations/'

def getStilt():
    # store all STILT station information in a dictionary 
    # get all ICOS station IDs by listing subdirectories in stiltweb
    # extract location from filename of link
    
    #-----  assemble information
    # use directory listing from siltweb data
    allStations = os.listdir(STILTPATH)

    
    # add information on station name (and new STILT station id) from stations.csv file used in stiltweb     
    url="https://stilt.icos-cp.eu/viewer/stationinfo"
    df = pd.read_csv(url)
    
    
    # add ICOS flag to the station
    icosStations = cpstation.getIdList()
    icosStations = list(icosStations['id'][icosStations.theme=='AS'])
    
    #----  dictionary to return
    stations = {}

    # fill dictionary with ICOS station id, latitude, longitude and altitude
    for ist in sorted(allStations):
  
        if not ist in df['STILT id'].values:
            continue
        
        stations[ist] = {}
        # get filename of link (original stiltweb directory structure) and extract location information
       
        loc_ident = os.readlink(STILTPATH+ist)
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
        if stations[ist]['id'][0:3].upper() in icosStations:
            stations[ist]['icos'] = True
        else:
            stations[ist]['icos'] = False
        
        
        # set years and month of available data
        years = os.listdir(STILTPATH+'/'+ist)
        stations[ist]['years'] = years
        for yy in sorted(stations[ist]['years']):
            stations[ist][yy] = {}
            months = os.listdir(STILTPATH+'/'+ist+'/'+yy)
            stations[ist][yy]['months'] = months
            stations[ist][yy]['nmonths'] = len(stations[ist][yy]['months'])
            
    return stations
            

def __stationName(idx, name, alt):    
    if name=='nan':
        name = idx
    if not (name[-1]=='m' and name[-2].isdigit()):           
        name = name + ' ' + str(alt) + 'm'    
    return name
    
