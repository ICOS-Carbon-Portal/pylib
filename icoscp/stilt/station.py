#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""    
    Extract all STILT stations from the ICOS Carbon Portal Server
    The main function is station.get() to filter and search. See
    Description of keyword arguments. 
"""

__credits__     = "ICOS Carbon Portal"
__license__     = "GPL-3.0"
__version__     = "0.1.0"
__maintainer__  = "ICOS Carbon Portal, elaborated products team"
__email__       = ['info@icos-cp.eu', 'claudio.donofrio@nateko.lu.se']
__status__      = "rc1"
__date__        = "2021-04-12"

import os
import numpy as np
import pandas as pd
import requests
import json
from tqdm.notebook import tqdm
from icoscp.station import station as cpstation
import icoscp.stilt.geoinfo as geoinfo
import icoscp.stilt.fmap as fmap
import icoscp.const as CPC

# --- START KEYWORD FUNCTIONS ---

def _id(kwargs, stations):
    ids = kwargs['id']
    if isinstance(ids,str):
        ids=[ids]
    if not isinstance(ids,list):
        ids=list(ids)
    
    # check stilt id
    flt = list(set(ids).intersection(stations))
    
    #check icos id
    for k in stations:
        if stations[k]['icos']:
            if stations[k]['icos']['stationId'] in ids:
                flt.append(k)
            
    stations =  {k: stations[k] for k in flt}
    return stations

def _outfmt(kwargs, stations):

    if 'outfmt' in kwargs: 
        fmt = kwargs['outfmt']
    else:
        fmt = 'dict'
        
    if fmt == 'pandas':
        df = pd.DataFrame().from_dict(stations)        
        return df.transpose()
        
    if fmt == 'list':
        print('fn convert dict to stilt objects needs to be implemented')
        #stnlist = __get_object(stations)
        return stations

    if fmt == 'map':              
        return fmap.get(stations)
    
    if fmt == 'map_html':         
        return fmap.get(stations, 'html')
    
    # by default return stations is a dict..
    return stations 

def _country(kwargs, stations):
    countries = kwargs['country']
    if isinstance(countries,str):
        countries=[countries]
    if not isinstance(countries,list):
        countries=list(countries)
       
    idx = []
    for k in stations:
        for c in countries:
            g = stations[k]['geoinfo']
            check = []  
            # sometime country is not available....
            # location in a ocean for example..hence try:
            try:
                check.append(g['alpha2Code'].lower())
                check.append(g['alpha3Code'].lower())
                check.append(g['countryName'].lower())
                check.append(g['name'].lower())
                check.append(g['nativeName'].lower())
                check.append(g['altSpellings'])
            except:
                pass
            
            if c.lower() in check:
                idx.append(k)
    
    flt = list(set(idx).intersection(stations))
    stations =  {k: stations[k] for k in flt}
    return stations
            

def _bbox(kwargs, stations):
    bbox=kwargs['bbox']
    lat1 = float(bbox[1][0])
    lat2 = float(bbox[0][0])
    lon1 = float(bbox[0][1])
    lon2 = float(bbox[1][1])
            
    flt = []
    for k in stations:
        if lat1 <= float(stations[k]['lat']) <= lat2:
            if lon1 <= float(stations[k]['lon']) <= lon2:
                flt.append(k)                
        
    stations =  {k: stations[k] for k in flt}
    return stations

def _pinpoint(kwargs, stations):
    lat = kwargs['pinpoint'][0]
    lon = kwargs['pinpoint'][1]
    deg = kwargs['pinpoint'][2]*0.01
    lat1 = lat+deg
    lat2 = lat-deg
    lon1 = lon-deg
    lon2 = lon+deg
    box = {'bbox':[(lat1, lon1),(lat2, lon2)]}
    return _bbox(box, stations)

def _sdate(kwargs, stations):
    print(kwargs)  
    return stations

def _edate(kwargs, stations):
    print(kwargs)  
    return stations

def _hours(kwargs, stations):
    print(kwargs)  
    return stations

def _search(kwargs, stations):
    """ search for arbitrary string"""
    idx = []
    for k in stations:
        txt = json.dumps(stations[k])                         
        if kwargs['search'].lower() in txt.lower():
            idx.append(k)
            
    flt = list(set(idx).intersection(stations))    
    return {k: stations[k] for k in flt}

# --- END KEYWORD FUNCTIONS ---



def __get_all():
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
    
    # merge geoinfo
    geo = geoinfo.get()
    
    for k in stations:  
        if k in geo.keys():
            stations[k]['geoinfo'] = geo[k]
    else:
        stations[k]['geoinfo'] = __country([stations[k]['lat'],stations[k]['lon']]) 
    
    return stations
 

def __country(latlon):
        """ return country information based on lat lon wgs84"""  
        url='https://api.bigdatacloud.net/data/reverse-geocode-client?'\
            'latitude=' + str(latlon[0]) + '&longitude=' + str(latlon[1])
        resp = requests.get(url=url)        
        a = resp.json()
        
        # API to reterive country name using country code. 
        url='https://restcountries.eu/rest/v2/alpha/' + a['countryCode']
        resp = requests.get(url=url)
        b = resp.json()
        
        return {**a, **b}
        
    
def __stationName(idx, name, alt):    
    if name=='nan':
        name = idx
    if not (name[-1]=='m' and name[-2].isdigit()):           
        name = name + ' ' + str(alt) + 'm'    
    return name


def get(**kwargs):
    """
    Return a list of stilt stations. Providing no keyword arguments will
    return a complete list of all stations. You can filter the result by 
    by providing the following keywords:
    

    Parameters
    ----------    
                                    
    id STR, list of STR:
        Provide station id or list of id's. You can provide
        either stilt or icos id's mixed together.
        Example:    station.get(id='HTM')
                    station.get(id=['NOR', 'GAT344'])


    outfmt STR ['pandas' | 'dict' | 'list' | 'map' | 'map_html']:
        the result is returned as
            pandas,  dataframe with some key information
            dict:       dictionary with full metadata for each station
            list:       list of stilt station objects
            map:        folium map, can be displayed directly in notebooks
            map_html:   STR, a static html representation. save this string
                        as file to get a static html map
    stations DICT
        all actions are performed on this dictionary, rather than
        dynamically search for all stilt station on our server.
        Can be useful for creating a map, or getting a subset of stations
        from an existing search.
        
    #Spatial search keywords:

    country STR, list of STR:
        Provide country code either fullname, 2 or 3 digit 
        where country is e.g "SE", "SWE" or "Sweden" 
        Example:    station.get(country='Sweden')
        
    bbox LIST of Tuples:
        spatial filter by bounding box where bbox=[Topleft(lat,lon), BR(lat,lon)]
        The following example is approximately covering scandinavia
        Example:    station.get(bbox=[(70,5),(55,32)])

    pinpoint LIST: [lat, lon, distanceKM]
        spatial filter by pinpoint location plus distance in KM
        distance in km is use to create a bounding box
        We use a very rough estimate of 1degree = 100 km
    
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
    
    if 'stations' in kwargs:        
        stations = kwargs['stations']
    else:        
        # start with getting all stations
        stations = __get_all()
    
    # with no keyword arguments, return all stations
    # in default format (see _outfmt())
    if not kwargs:
        return _outfmt(kwargs, stations)

   # convert all keywords to lower case
    kwargs =  {k.lower(): v for k, v in kwargs.items()}
    
    # valid key words. Make surea all are lower capital and that
    # the function has been defined above and that outfmt is the very 
    # last call:
    fun = {'id': _id,
           'country': _country, 
           'bbox': _bbox,
           'pinpoint': _pinpoint,
           'sdate':_sdate,
           'edate':_edate,
           'hours':_hours,
           'search':_search           
           }
    
    for k in kwargs.keys():        
        if k in fun.keys():
            stations = fun[k](kwargs, stations)

    return _outfmt(kwargs, stations)