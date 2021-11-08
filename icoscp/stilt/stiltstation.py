#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Extract all STILT stations from the ICOS Carbon Portal Server
    The main function is
    station.find() to search and filter STILT stations and
    station.get() to create a STILT station object with access to the data.

"""

__credits__     = "ICOS Carbon Portal"
__license__     = "GPL-3.0"
__version__     = "0.1.1"
__maintainer__  = "ICOS Carbon Portal, elaborated products team"
__email__       = ['info@icos-cp.eu', 'claudio.donofrio@nateko.lu.se']
__status__      = "rc1"
__date__        = "2021-11-04"

import os
import json
import numpy as np
import pandas as pd

from tqdm.notebook import tqdm

from icoscp.station import station as cpstation
from icoscp.stilt.stiltobj import StiltStation
from icoscp.stilt import geoinfo
from icoscp.stilt import fmap
import icoscp.const as CPC
import icoscp.country

from icoscp.stilt import timefuncs as tf


# --- START KEYWORD FUNCTIONS ---
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
    '''
    Parameters
    ----------
    kwargs : STR
        Define the output format. by default a 'DICT' is returned
        Possible arguments are:   
            - dict (default), with Station ID as key
            - pandas
            - list , provide a list of stilstation objects, equivalent to 
                    station.get([list of ids])
            - map (folium)
    '''
    
    if not stations:
        # no search result, return empty
        stations={'empty':'no stiltstations found'}
        return stations

    if 'outfmt' in kwargs:        
        fmt = kwargs['outfmt'].lower()
    else:
        fmt = 'dict'
    
    # make sure we have a valid keyword, else set default dict
    valid = ['dict', 'list', 'pandas', 'map']
    if not fmt in valid:
            fmt = 'dict'
    
    if fmt == 'dict':        
        #default
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
    """
    Find all stations belonging to a country based on information from
    alpha2Code', 'alpha3Code', 'name', 'nativeName', 'altSpellings', 'demonym'
    Be aware, that STILT stations can have arbitrary lat/lon which
    are in international waters and hence not associated with a country

    """
    countries = kwargs['country']
    if isinstance(countries,str):
        countries=[countries]
    if not isinstance(countries,list):
        countries=list(countries)

    idx = []
    for k in stations:
        if stations[k]['geoinfo'] is False:
            # if there is no geoinfo, skip
            continue

        for c in countries:
            # the search keys are a combination of keys from the online
            # search at restcountries.eu and the static country file
            if len(c) < 4:
                searchKeys = {'alpha2Code', 'alpha3Code', 'cca2', 'cca3','ccn3', 'cioc'}
            else:
                searchKeys = {'name', 'nativeName', 'altSpellings', 'demonym', 'demonyms'}
            
            g = stations[k]['geoinfo']

            # make sure we have only valid search keys...add two sets
            for sk in searchKeys & g.keys():
                if c.lower() in str(g[sk]).lower():
                    idx.append(k)
                    break

    flt = list(set(idx).intersection(stations))
    stations =  {k: stations[k] for k in flt}
    return stations


def _bbox(kwargs, stations):
    """
    Find all stations within a lat/lon bounding box. Expected keyword argument
    input is bbox=[Topleft NorthWest (lat,lon),
                   BottomRight South East(lat,lon)]

    """
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
    # the user MUST provide lat, lon, but only optional
    # the distance in KM to create the boundding box.
    # set default 200km bounding box..
    if len(kwargs['pinpoint']) == 2:
        kwargs['pinpoint'].append(200)
    lat = kwargs['pinpoint'][0]
    lon = kwargs['pinpoint'][1]
    deg = kwargs['pinpoint'][2]*0.01
    lat1 = lat+deg
    lat2 = lat-deg
    lon1 = lon-deg
    lon2 = lon+deg
    box = {'bbox':[(lat1, lon1),(lat2, lon2)]}
    return _bbox(box, stations)

def _dates(kwargs, stations):
    """
    Check availability for specific dates.
    input needs to be a list. Stations are returned which have data
    for any dates in the list. Remember, only year and month is checked
    NOT single days.
    """

    # return empyt if dates is not a list
    if not isinstance(kwargs['dates'],list):
        print('Dates must be a list')
        return {}

    # parse all dates to a clean list
    dates = [tf.parse(d) for d in kwargs['dates']]
    # remove Nones
    dates = [d for d in dates if d]
    if not dates:
        return {}

    flt = []
    for st in stations:
        # check each station for all dates...
        # use daterange with sdate and edate set to the same.
        for d in dates:
            if tf.check_daterange(d, d, stations[st]):
                flt.append(st)

    stations =  {k: stations[k] for k in flt}
    return stations

def __daterange(kwargs, stations):
    """
    Check availability for a date range.
    sdate AND edate is provided in the arguments. Daterange is PRIVATE
    function...and cant be called directly, but is called if
    sdate AND edate is provided in the arguments
    """

    sdate = tf.parse(kwargs['daterange'][0])
    edate =  tf.parse(kwargs['daterange'][1])

    # return an empyt dict, if date is not a date object
    if not sdate or not edate:
        return {}

    if edate < sdate:
        print('Start-date is set to a later date than end-date... ')
        return {}

    flt = []
    for st in stations:
        if tf.check_daterange(sdate, edate, stations[st]):
            flt.append(st)
    stations =  {k: stations[k] for k in flt}
    return stations



def _sdate(kwargs, stations):
    """
    Find all stations with valid data for >= sdate (year and month only)
    """
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
    """
    Find all stations with valid data for <= edate (year and month only)
    """
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


def __get_object(stations):

    return [StiltStation().get_info(stations[st]) for st in stations.keys()]


def __get_stations(ids=[], progress=True):
    """ get all stilt stations available on the server
        return dictionary with meta data, keys are stilt station id's
    """

    # invert the progress parameter, tqdm interpretation is
    # DEFAULT disable = False -> progressbar is visible
    progress = not progress
    
    # use directory listing from siltweb data
    allStations = os.listdir(CPC.STILTPATH)
    
    # if ids are provided, select only valid ids from allstations
    if ids:
        # make sure they are all upper case
        ids = [i.upper() for i in ids]
        #select only valid id from allstations
        allStations = list(set(ids).intersection(allStations))

        
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
	 # implement progress True/False
    for ist in tqdm(sorted(allStations), disable=progress):
        if not ist in df['STILT id'].values:
            continue

        stations[ist] = {}
        # get filename of link (original stiltweb directory structure) and
        # extract location information

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
            stations[k]['geoinfo'] = geo[k]['geoinfo']
        else:
            stations[k]['geoinfo'] = __country([stations[k]['lat'],stations[k]['lon']])

    return stations


def __country(latlon):
    # be aware, that by providing latlon
    # triggers an external reverse geocoder.
    return icoscp.country.get(latlon=latlon)


def __stationName(idx, name, alt):
    if name=='nan':
        name = idx
    if not (name[-1]=='m' and name[-2].isdigit()):
        name = name + ' ' + str(alt) + 'm'
    return name


def find(**kwargs):
    """
    Return a list of stilt stations. Providing no keyword arguments will
    return a complete list of all stations. You can filter the result by
    by providing the following keywords:

    Parameters
    ----------

    id STR, list of STR:
        Provide station id or list of id's. You can provide
        either stilt or icos id's mixed together.
        Example:    station.find(id='HTM')
                    station.find(id=['NOR', 'GAT344'])

    search STR:
        Arbitrary string search keyword
         Example:    station.find(search='north')

    stations DICT
        all actions are performed on this dictionary, rather than
        dynamically search for all stilt station on our server.
        Can be useful for creating a map, or getting a subset of stations
        from an existing search.
        Example: myStations = station.find(search='north')
                 refined = station.find(stations=myStations, country='Finland')

    # Spatial search keywords:

    country STR, list of STR:
        Provide country code either fullname, 2 or 3 digit
        where country is e.g "SE", "SWE" or "Sweden"
        Example:    station.find(country='Sweden')

    bbox LIST of Tuples:
        spatial filter by bounding box where
        bbox=[Topleft(lat,lon), BottomRight(lat,lon)]
        The following example is approximately covering scandinavia
        Example:    station.find(bbox=[(70,5),(55,32)])

    pinpoint LIST: [lat, lon, distanceKM]
        spatial filter by pinpoint location plus distance in KM
        distance in km is use to create a bounding box
        We use a very rough estimate of 1degree ~ 100 km
        Example: stations.find(pinpoint = [40.42, -3.70, 500]
    # Temporal search keywords:
    Be aware, that the granularity for all temporal keywords is year and month
    (days are not considered in the search): input format for the dates entry
    MUST be convertible to data time object throug pandas.
    -> pandas.to_datetime(date)

    sdate Input formats:
        - datetime.date objs
        - FLOAT or INT unix timestamp
        - pandas.datetime
        - STR: "YYYY-MM-DD" , "YYYY", "YYYY/MM/DD":
        where 'sdate' (Start Date) is a single entry. If you provide ONLY
        sdate, stations with any data available for >= sdate is returned
    Example: station.find(sdate= '2018-05-01')

    edate Input format see sdata:
        - datetime.date objs
        - FLOAT or INT unix timestamp
        - pandas.datetime
        - STR: "YYYY-MM-DD" , "YYYY", "YYYY/MM/DD":
        where 'edate' (End Date) is a single entry. If you provide ONLY
        edate, stations with any data available  <= edate is returned
    Example: station.find(edate='2018-06-01')

    If you provide sdate AND edate, any station with available data
    within that date range is retured.

    dates [] is a list of dates.
        This will return a list of stations where data is available for
        for any of the provided dates. Input format, see sdate,edate.
        Remember, that only year and month is checked.
    Example: station.find(dates=['2020-01-01', '2020/05/23'])

    progress BOOL 
        By default progress is set to True, which returns a progressbar
        while searching the catalogue of STILT stations.    
    
    outfmt STR ['dict'| 'pandas' | 'list' | 'map']:
        the result is returned as
        
            dict:       dictionary with full metadata for each station
                        Stiltstation ID is the 'key' for the dict entries
            pandas:     dataframe with some key information    
            list:       list of stilt station objects
            map:        folium map, can be displayed directly in notebooks
                        or save to a static (leaflet) .html webpage
    
    Returns
    -------
    List of Stiltstation in the form of outfmt=format, see above.
    Default DICT

    """

    # convert all keywords to lower case
    if kwargs:
        kwargs =  {k.lower(): v for k, v in kwargs.items()}
    
    if 'stations' in kwargs:
        stations = kwargs['stations']
    else:
        # start with getting all stations
        # check if progressbar should be visible or not, default True, visible
        progress = True
        if 'progress' in kwargs.keys():
            progress = kwargs['progress']
    
        stations = __get_stations(progress=progress)

    # with no keyword arguments, return all stations
    # in default format (see _outfmt())
    if not kwargs:
        return _outfmt(kwargs, stations)


    # check if sdate AND edate is provided. If yes,
    # create a date_range entry and remove sdate and edate:
    if 'sdate' in kwargs.keys() and 'edate' in kwargs.keys():
        kwargs['daterange'] = [kwargs['sdate'], kwargs['edate']]
        del kwargs['sdate']
        del kwargs['edate']



    # valid key words. Make sure all are lower capital and that
    # the function has been defined above and that outfmt is the very
    # last call:
    fun = {'id': _id,
           'country': _country,
           'bbox': _bbox,
           'pinpoint': _pinpoint,
           'sdate':_sdate,
           'edate':_edate,
           'dates':_dates,
           'daterange':__daterange,
           'search':_search}

    for k in kwargs.keys():
        if k in fun.keys():
            stations = fun[k](kwargs, stations)

    return _outfmt(kwargs, stations)

def get(id=None, progress=False):
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

    progress: BOOL
            You can display a progressbar, for long running tasks. For
            example when you get a long list of id's. By default the
            progressbar is not visible. This parameter is only applicable
            while providing id's, but NOT for dictionaries.
            
    Returns
    -------
    LIST[stiltstation]

    """

    stationslist = []


    if isinstance(id,str):
        # assuming str is a station id
        st = __get_stations([id], progress)
        if not st:
            return None
        for s in st:
            stationslist.append(StiltStation(st[s]))

    if isinstance(id,dict):
        # assuming dict is coming from .find....call
        for s in id:
            stationslist.append(StiltStation(id[s]))

    if isinstance(id, list):
        if isinstance(id[0],dict):
            # assuming dict is coming from .find....call
            for s in id:
               stationslist.append(StiltStation(id[s]))

        if isinstance(id[0], str):
            # assuming we have a list of valid station id's
            st = __get_stations(id, progress)
            if not st:
                return None
            for s in st:
                stationslist.append(StiltStation(st[s]))
                

    if len(stationslist) == 1:
        return stationslist[0]
    else:
        return stationslist

