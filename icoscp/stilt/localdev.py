# -*- coding: utf-8 -*-
"""
Created on Wed Apr  7 10:17:05 2021

@author: Claudio
"""

import json
import requests
import pandas as pd
from icoscp.stilt import timefuncs as tf
    
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
    if not stations:
        # no search restult found, return empty
        return None
    
    if 'outfmt' in kwargs: 
        fmt = kwargs['outfmt']
    else:
        #default return format
        return stations
    
    
    if fmt == 'pandas':
        df = pd.DataFrame().from_dict(stations)
        df = df.transpose()
        return df
        
    if fmt == 'list':
        print('fn convert dict to stilt objects needs to be implemented')
        #stnlist = __get_object(stations)
        return stations

        
def _country(kwargs, stations):
    countries = kwargs['country']
    if isinstance(countries,str):
        countries=[countries]
    if not isinstance(countries,list):
        countries=list(countries)
    
    idx = []
    for k in stations:
        if stations[k]['geoinfo'] == False:
            # if there is no geoinfo, skip
            continue
        
        for c in countries:
            g = stations[k]['geoinfo']            
            searchKeys = {'alpha2Code', 'alpha3Code', 'name', 'nativeName', 'altSpellings', 'demonym'}
            
            # make sure we have only valid search keys...add two sets
            for sk in (searchKeys & g.keys()):
                if c.lower() in str(g[sk]).lower():                    
                    idx.append(k)
                    break
    
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
    
    # Check if both start-date and end-date have been provided:
    if(('sdate' in kwargs.keys()) & ('edate' in kwargs.keys())):
        #Check that end-date is set to a later date that start-date:
        if not(tf.check_dates(tf.str_to_date(kwargs['sdate']), tf.str_to_date(kwargs['edate']))):
            # print('Error! Start-date is set to a later date than end-date... ')
            stations = {}
            return stations

    #Convert date-string to date obj:
    sdate =  tf.str_to_date(kwargs['sdate'])

    #Check if date-string could be converted to date obj:
    if sdate is not None:

        #Filter stations by sdate:
        stations = {st:stations[st] for st in stations
                    if ((tf.check_dates(sdate, tf.get_st_dates(stations[st])[1]))&
                        ((tf.check_smonth(sdate, stations[st])) or
                         (True in [sdate.year < y
                                   for y in list(map(int, stations[st]['years']))])))}
    #If input is in wrong format:
    else:
        #Prompt error message:
        print("Wrong date format! Expected 'sdate' expressed as YYYY-MM-DD")

        stations = {}

    return stations


def _edate(kwargs, stations):
    # Check if both start-date and end-date have been provided:
    if(('sdate' in kwargs.keys()) & ('edate' in kwargs.keys())):
        #Check that end-date is set to a later date that start-date:
        if not(tf.check_dates(tf.str_to_date(kwargs['sdate']), tf.str_to_date(kwargs['edate']))):
            # print('Error! Start-date is set to a later date than end-date... ')
            stations = {}
            return stations

    #Convert date-string to date obj:
    edate =  tf.str_to_date(kwargs['edate'])

    #Check if date-string could be converted to date obj:
    if edate is not None:

        #Filter stations by sdate:
        stations = {st:stations[st] for st in stations
                    if ((tf.check_dates(tf.get_st_dates(stations[st])[0], edate))&
                        ((tf.check_emonth(edate, stations[st])) or
                         (True in [edate.year > y
                                   for y in list(map(int, stations[st]['years']))])))}

    #If input is in wrong format:
    else:
        #Prompt error message:
        print("Wrong date format! Expected 'edate' expressed as YYYY-MM-DD")
        stations = {}

    return stations


def _hours(kwargs, stations):
    print(kwargs)  
    return stations

def _search(kwargs, stations):
    """ search for arbitrary string in complete dict"""
    idx = []
    for k in stations:
        if kwargs['search'] in json.dumps(stations[k]):
            idx.append(k)
            
    flt = list(set(idx).intersection(stations))
    stations =  {k: stations[k] for k in flt}
    return stations
    

def find(**kwargs):
    import json
    
    with open('stations.json') as json_file:
        stations = json.load(json_file)
    
    # convert all keywords to lower case
    kwargs =  {k.lower(): v for k, v in kwargs.items()}
    
    # valid key words. Make surea all are lower capital:
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
    
        
def __country(latlon,id):
    """ return country information based on lat lon wgs84"""  
    url='https://api.bigdatacloud.net/data/reverse-geocode-client?'\
        'latitude=' + str(latlon[0]) + '&longitude=' + str(latlon[1])
    resp = requests.get(url=url)        
    a = resp.json()
    
    #API to reterive country name using country code. 
    url='https://restcountries.eu/rest/v2/alpha/' + a['countryCode']
    resp = requests.get(url=url)
    b = resp.json()
    country = {**a, **b}
    return country


def get(stations=None, id=None):
    """
    This function returns a list of stiltstation objects. 
    A valid object, gives access to the underlying timeseries and footprints
    You may provide a str or list of STILT id's or the 'result' of a search 
    
    Example: .get('HTM030')
             .get(['HTM030'])
             .get(['HTM030','HTM150'])
    Parameters
    ----------
    stations : DICT | LIST[DICT]
        The result of .find(....) where one station (DICT) is found or 
        multiple stations (LIST[DICT])
        
    id : STR | LIST[STR]
        A single string or a list of strings containing one or more stilt
        station ids.

    Returns
    -------
    LIST[stiltstation]

    """
    from icoscp.stilt.stiltstation import StiltStation
    obj = []

    if isinstance(id,str) or isinstance(id,list):
        st = find(id=id)
        for s in st:
            obj.append(StiltStation(st[s]))
    
    if isinstance(stations,dict):
        for s in stations:
            obj.append(StiltStation(stations[s]))
    
    return obj  

test = find(country='greece')
#test = find(pinpoint=[55.7,13.1,300])
test = find(country=['nor','Sweden'])

#htm = find(id='HTM030')

#test1 = get(stations=htm)
#test2 = get(id=['HTM030','HTM150'])