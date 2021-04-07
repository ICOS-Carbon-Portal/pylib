# -*- coding: utf-8 -*-
"""
Created on Tue Dec  8 09:07:38 2020
@author: Claudio
"""

import os
import numpy as np
import pandas as pd
import requests
from icoscp.station import station as cpstation
import icoscp.const as CPC

def get(**kwargs):
    """
    Return a list of stilt stations. Providing no keyword arguments will
    return a complete list of all stations. You can filter the result by 
    by providing the following keywords:
    

    Parameters
    ----------    
                                    
    stiltID STR, list of STR:
        Provide the stilt station id         

    icosID STR, list of STR:
        Provide ICOS station id

    outfmt STR ['pandas' | 'dict' | 'list']:
        the result is returned as
            pandas,  dataframe with some key information
            dict, dictionary with full metadata for each station
            list of stilt station objects

    #Spatial search keywords:

    country STR, list of STR:
        Provide country code either fullname, 2 or 3 digit 
        where country is e.g "SE", "SWE" or "Sweden" (ISO standard)

    bbox LIST of Tuples:
        spatial filter by bounding box where bbox=[Topleft(lat,lon), BR(lat,lon)]

    pinpoint LIST: [lat, lon, distanceKM]
        spatial filter by pinpoint location plus distance in KM
        distance in km is use to create a bounding box.
    
    #Temporal keywords:
    sdate Input formats:
           - datetime.date objs
           - unix timestamp
           - pandas.datetime
           - STR: "YYYY-MM-DD":
        where 'sdate' is a list of dates.
        single list-item refers to start date (if edate is also provided) of a period or a single date
        single list-item refers (if edate is not provided) 
        multiple items for list of single dates option

    edate Input format see sdata:
        where 'sdate' is a single date

    hours LIST of (see Input format sdate):
        where 'hours' is a list of hours (strings, int or datetime objs).
        
        Default ['00:00', '03:00', ..., '21:00'] --- > all the timeslots with data (no filter)

    search STR:
        Arbitrary string search keyword

    
    

    Returns
    -------
    List of Stiltstation in the form of outfmt=format, see format above.

    """
    
    # start with getting all stations
    stations = __get_all()
    
    if not kwargs:
        return stations

    # valid key words:
    keywords = ['stiltid','icosid','outfmt','country','bbox','pinpoint', \
                'sdate','edate', 'hours', 'search']
    
    for k in kwargs.keys():
        if str(k).lower() in keywords:
            print(k,kwargs[k])
            #v(k,kwargs[k])
    

def __get_all():
    """
    

    Returns
    -------
    stations : TYPE
        DESCRIPTION.

    """
    
    # store all STILT station information in a dictionary 
    # get all ICOS station IDs by listing subdirectories in stiltweb
    # extract location from filename of link
    
    #-----  assemble information
    # use directory listing from siltweb data
    allStations = os.listdir(CPC.STILTPATH)

    
    # add information on station name (and new STILT station id) from stations.csv file used in stiltweb. this is available from the backend through a url...see constants
    df = pd.read_csv(CPC.STILTINFO)
    
    
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
        if stations[ist]['id'][0:3].upper() in icosStations:
            stations[ist]['icos'] = True
        else:
            stations[ist]['icos'] = False
        
        
        # set years and month of available data
        years = os.listdir(CPC.STILTPATH+'/'+ist)
        stations[ist]['years'] = years
        for yy in sorted(stations[ist]['years']):
            stations[ist][yy] = {}
            months = os.listdir(CPC.STILTPATH+'/'+ist+'/'+yy)
            stations[ist][yy]['months'] = months
            stations[ist][yy]['nmonths'] = len(stations[ist][yy]['months'])
            
    return stations
            
def __country(countrycode='', latlon=[]):
    '''
    returns the country name and json object with full information about the 
    country from https://restcountries.eu.
    Please provided either the country code like 'se' or 'swe'
    OR latlon.
        If both parameters are provided, contrycode only is used.
        If no parameter is provided, False is returned

    Example:    c = __country('SE')
                c = __country('SWE')
                c = __country(latlon=[65.2,13.5])
    '''
    if countrycode:
        # API to reterive country name using country code. 
        url = 'https://restcountries.eu/rest/v2/alpha/' + countrycode
        resp = requests.get(url=url)
        country_information=resp.json()
        return country_information['name'], country_information

    if len(latlon)==2:           
        url='https://api.bigdatacloud.net/data/reverse-geocode-client?latitude=' + \
            str(latlon[0]) + '&longitude=' + str(latlon[1]) + '12&localityLanguage=en'
        resp = requests.get(url=url)
        country_information=resp.json()
        return country_information['countryName'], country_information

    
def __stationName(idx, name, alt):    
    if name=='nan':
        name = idx
    if not (name[-1]=='m' and name[-2].isdigit()):           
        name = name + ' ' + str(alt) + 'm'    
    return name
    
