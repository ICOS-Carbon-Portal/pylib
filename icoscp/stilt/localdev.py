# -*- coding: utf-8 -*-
"""
Created on Wed Apr  7 10:17:05 2021

@author: Claudio
"""

import json
import requests
import pandas as pd
from icoscp.stilt import timefuncs as tf
from icoscp.stilt.stiltstation import StiltStation
import icoscp.stilt.fmap as fmap

    
def _id(kwargs, stations):
    ids = kwargs['id']
    if isinstance(ids,str):
        ids=[ids]
    if not isinstance(ids,list):
        ids=list(ids)

    # to make the search not case sensitive we need to convert all
    # id's to CAPITAL LETTERS. The stilt on demand calculator
    # allows only captial letters.
    
    ids = [id.upper() for id in ids]        
    
    # get all stilt id
    flt = list(set(ids).intersection(stations))
    
    #check icos id
    for k in stations:
        if stations[k]['icos']:
            if stations[k]['icos']['stationId'] in ids:
                flt.append(k)
            
    stations =  {k: stations[k] for k in flt}
    return stations

def _outfmt(kwargs, stations):
    '''
    Parameters
    ----------
    kwargs : STR
        Define the output format. by default a 'DICT' is returned
        Possible arguments are:            
            - pandas
            - list DEFAULT
            - map (folium)
    '''
    if not stations:
        # no search restult found, return empty
        stations={'empty':'no stiltstations found'}
    
    if 'outfmt' in kwargs:
        fmt = kwargs['outfmt']
    else:
        # by default return stations is a dict..
        return stations

    if fmt == 'pandas':
        df = pd.DataFrame().from_dict(stations)
        return df.transpose()

    if fmt == 'list':
        stnlist = __get_object(stations)
        return stnlist

    if fmt == 'map':
        return fmap.get(stations)
    
        
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


def __daterange(kwargs, stations):
    """
    Check availability for a date range.
    sdate AND edate is provided in the arguments
    """
    sdate = tf.parse(kwargs['daterange'][0])
    edate =  tf.parse(kwargs['daterange'][1])
    #sdate =  tf.str_to_date(kwargs['daterange'][0])
    #edate =  tf.str_to_date(kwargs['daterange'][1])
    
    # return an empyt dict, if date is not a date object
    if not sdate or not edate:
        return {}
    
    #Check that end-date is set to a later date that start-date:
    if edate < sdate:
        print('Start-date is set to a later date than end-date... ')
        stations = {}
        return stations

    flt = []
    for st in stations:
        if tf.check_daterange(sdate, edate, stations[st]):
           flt.append(st)
    stations =  {k: stations[k] for k in flt}
    return stations

def _sdate(kwargs, stations):
    #Convert date-string to date obj:
    sdate =  tf.parse(kwargs['sdate'])
    
    # return and empyt dict, if sdate is not a date object
    if not sdate:        
        print("Check date format")
        return {}

    flt = []
    for st in stations:
        if tf.check_smonth(sdate, stations[st]):
           flt.append(st)
    
    stations =  {k: stations[k] for k in flt}
    return stations


def _edate(kwargs, stations):
    
    edate =  tf.parse(kwargs['edate'])
    
    # return an empyt dict, if sdate is not a date object
    if not edate:    
        print("Check date format")
        return {}

    flt = []
    for st in stations:
        if tf.check_emonth(edate, stations[st]):
           flt.append(st)
    
    stations =  {k: stations[k] for k in flt}
    return stations


def _hours(kwargs, stations):
    print(kwargs)  
    return stations

"""
def _search(kwargs, stations):
    # search for arbitrary string in complete dict
    idx = []
    for k in stations:
        if kwargs['search'] in json.dumps(stations[k]):
            idx.append(k)
            
    flt = list(set(idx).intersection(stations))
    stations =  {k: stations[k] for k in flt}
    return stations
"""

def _search(kwargs, stations):
    """ search for arbitrary string"""
    idx = []
    for k in stations:
        txt = json.dumps(stations[k])
        if kwargs['search'].lower() in txt.lower():
            idx.append(k)

    flt = list(set(idx).intersection(stations))
    return {k: stations[k] for k in flt}  

def find(**kwargs):
    
    if 'stations' in kwargs:
        stations = kwargs['stations']
    else:
        import json
        
        with open('stations.json') as json_file:
            stations = json.load(json_file)
    
    # convert all keywords to lower case
    kwargs =  {k.lower(): v for k, v in kwargs.items()}
    
    # check if sdate AND edate is provided. If yes, 
    # create a date_range entry and remove sdata and edate:
    if 'sdate' in kwargs.keys() and 'edate' in kwargs.keys():
        kwargs['daterange'] = [kwargs['sdate'], kwargs['edate']]
        del kwargs['sdate']
        del kwargs['edate']
        
    # valid key words. Make surea all are lower capital:
    fun = {'id': _id,                      
           'country': _country, 
           'bbox': _bbox,
           'pinpoint': _pinpoint,
           'sdate':_sdate,
           'edate':_edate,
           'daterange': __daterange,
           'hours':_hours,
           'search':_search
           }
    
    for k in kwargs.keys():        
        if k in fun.keys():
            stations = fun[k](kwargs, stations)

    return _outfmt(kwargs, stations)
    
def __get_object(stations):

    return [StiltStation().get_info(stations[st]) for st in stations.keys()]
        
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


def get(id=None):
    """
    This function returns a stilt station object or a list of
    stiltstation objects. 
    A stilt station object, gives access to the underlying data
    (timeseries and footprints)
    You may provide a str or list of STILT id's or the 'result' of a .find() 
    
    Example: .get('HTM030')
            .get(['HTM030'])
                returns one stiltobject for HTM030
             
             .get(['HTM030','HTM150'])
                 returns a list of two stiltobjects
        
            .get('KIT') 
                returns a list of stiltstations based on .find(search='KIT')
                
            .get(find(country=['Sweden','Finland']))
                returns a list of stilstations found in Sweden and Finland
    Parameters
    ----------
    id :    DICT | LIST[DICT]
                The result of .find(....) where one station (DICT) is found or 
                multiple stations (LIST[DICT])
        
            STR | LIST[STR]
                A single string or a list of strings containing one or more
                stilt station ids.

    Returns
    -------
    LIST[stiltstation]

    """
    
    stationslist = []

    if isinstance(id,str):
        st = find(id=id)
        if not st:
            return None
        for s in st:
            stationslist.append(StiltStation(st[s]))
    
    if isinstance(id,dict):  
        for s in id:
            stationslist.append(StiltStation(id[s]))
            
    if isinstance(id, list):
        if isinstance(id[0],dict):
           for s in id:
               stationslist.append(StiltStation(id[s]))
    
        if isinstance(id[0], str):            
            st = find(id=id)
            if not st:
                return None
            for s in st:
                stationslist.append(StiltStation(st[s]))
                
    if len(stationslist) == 1:
        return stationslist[0]
    else:
        return stationslist

#greece = find(search='sweden')
#test = find(stations=greece, search='norunda')
#test = find(country=['nor','Sweden'])

#test = find(sdate='2019-01-01')
#test = find(edate='2005-01-01')
myStations = find(sdate= '2018-01-01', edate='2018-05-30')
#myStations = find(sdate= '2018-05-01', edate='2018-08-01')
#print(find(id='HTm030'))

#g = get('KITTY')

#g1 = get('HTM030')
#print(g1)
"""
g2 = get(['HTM030','HTM150'])
for g in g2:
    print(g)
g3 = get(find(id='KIT030'))
print(g3)
g4 = get(find(search='KIT'))
for g in g4:
    print(g)
"""