#!/usr/bin/env python

"""
    Extract all STILT stations from the ICOS Carbon Portal Server
    The main function is
    station.find() to search and filter STILT stations and
    station.get() to create a STILT station object with access to the data.

"""

__credits__ = "ICOS Carbon Portal"
__license__ = "GPL-3.0"
__version__ = "0.1.1"
__maintainer__ = "ICOS Carbon Portal, elaborated products team"
__email__ = ["info@icos-cp.eu", "claudio.donofrio@nateko.lu.se"]
__status__ = "rc1"
__date__ = "2021-11-04"

import re
import json
import pandas as pd
from tqdm.notebook import tqdm
from icoscp_core.icos import meta, ATMO_STATION, station_class_lookup
from icoscp_core.queries.stationlist import StationLite
from .stiltobj import StiltStation
from . import fmap
from .const import STILTINFO, STILTPATH, COUNTRIES
from pathlib import Path
from typing import Any
from . import timefuncs as tf


# --- START KEYWORD FUNCTIONS ---
def _id(kwargs, stations):
    ids = kwargs["id"]
    if isinstance(ids, str):
        ids = [ids]
    if not isinstance(ids, list):
        ids = list(ids)

    # to make the search not case sensitive we need to convert all
    # id's to CAPITAL LETTERS. The stilt on demand calculator
    # allows only captial letters.

    ids = [id.upper() for id in ids]

    # check stilt id
    flt = list(set(ids).intersection(stations))

    # check icos id
    for k in stations:
        if stations[k]['icos']:
            if stations[k]['icos']['stationId'] in ids:
                flt.append(k)

    stations = {k: stations[k] for k in flt}
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
        stations = {'empty': 'no stiltstations found'}
        return stations

    if 'outfmt' in kwargs:
        fmt = kwargs['outfmt'].lower()
    else:
        fmt = 'dict'

    # make sure we have a valid keyword, else set default dict
    valid = ['dict', 'list', 'pandas', 'map', 'avail']
    if not fmt in valid:
        fmt = 'dict'

    if fmt == 'dict':
        # default
        return stations

    if fmt == 'pandas':
        df = pd.DataFrame().from_dict(stations)
        return df.transpose()

    if fmt == 'list':
        stnlist = __get_object(stations)
        return stnlist

    if fmt == 'map':
        return fmap.get(stations)

    if fmt == 'avail':
        return _avail(stations)


def _bbox(kwargs, stations):
    """
    Find all stations within a lat/lon bounding box. Expected keyword argument
    input is bbox=[Topleft NorthWest (lat,lon),
                   BottomRight South East(lat,lon)]

    """
    bbox = kwargs['bbox']
    lat1 = float(bbox[1][0])
    lat2 = float(bbox[0][0])
    lon1 = float(bbox[0][1])
    lon2 = float(bbox[1][1])

    flt = []
    for k in stations:
        if lat1 <= float(stations[k]['lat']) <= lat2:
            if lon1 <= float(stations[k]['lon']) <= lon2:
                flt.append(k)

    stations = {k: stations[k] for k in flt}
    return stations


def _pinpoint(kwargs, stations):
    # the user MUST provide lat, lon, but only optional
    # the distance in KM to create the boundding box.
    # set default 200km bounding box..
    if len(kwargs['pinpoint']) == 2:
        kwargs['pinpoint'].append(200)
    lat = kwargs['pinpoint'][0]
    lon = kwargs['pinpoint'][1]
    deg = kwargs['pinpoint'][2] * 0.01
    lat1 = lat + deg
    lat2 = lat - deg
    lon1 = lon - deg
    lon2 = lon + deg
    box = {'bbox': [(lat1, lon1), (lat2, lon2)]}
    return _bbox(box, stations)


def _dates(kwargs, stations):
    """
    Check availability for specific dates.
    input needs to be a list. Stations are returned which have data
    for any dates in the list. Remember, only year and month is checked
    NOT single days.
    """

    # return empyt if dates is not a list
    if not isinstance(kwargs['dates'], list):
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

    stations = {k: stations[k] for k in flt}
    return stations


def __daterange(kwargs, stations):
    """
    Check availability for a date range.
    sdate AND edate is provided in the arguments. Daterange is PRIVATE
    function...and cant be called directly, but is called if
    sdate AND edate is provided in the arguments
    """

    sdate = tf.parse(kwargs['daterange'][0])
    edate = tf.parse(kwargs['daterange'][1])

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
    stations = {k: stations[k] for k in flt}
    return stations


def _sdate(kwargs, stations):
    """
    Find all stations with valid data for >= sdate (year and month only)
    """
    # Convert date-string to date obj:
    sdate = tf.parse(kwargs['sdate'])

    # return and empyt dict, if sdate is not a date object
    if not sdate:
        print("Check date format")
        return {}

    flt = []
    for st in stations:
        if tf.check_smonth(sdate, stations[st]):
            flt.append(st)

    stations = {k: stations[k] for k in flt}
    return stations


def _edate(kwargs, stations):
    """
    Find all stations with valid data for <= edate (year and month only)
    """
    edate = tf.parse(kwargs['edate'])

    # return an empyt dict, if sdate is not a date object
    if not edate:
        print("Check date format")
        return {}

    flt = []
    for st in stations:
        if tf.check_emonth(edate, stations[st]):
            flt.append(st)

    stations = {k: stations[k] for k in flt}
    return stations


def _project(kwargs: dict[str, str], stations: dict[str, Any]) -> dict[str, Any]:
    proj = kwargs['project'].lower()

    return {
        id: s
        for id, s in stations.items()
        if s['icos'] and s['icos']['uri'][0] in station_class_lookup()
    } if proj == 'icos' else {}

def _country(kwargs, stations):
    ccode = kwargs['country']
    return {
        id: station
        for id, station in stations.items()
        if station['country'] == ccode
    }

def _avail(stations):
    years_set = set()
    availability = {}

    for stn in stations:
        avail_per_stn = {}
        if stations[stn]['icos']:
            avail_per_stn['ICOS id'] = stations[stn]['icos']['stationId']
            avail_per_stn['ICOS alt'] = stations[stn]['icos']['SamplingHeight']
        else:
            avail_per_stn['ICOS id'] = ''
        if stations[stn]['alt'] != None:
            avail_per_stn['Alt'] = stations[stn]['alt']
        else:
            avail_per_stn['Alt'] = 0
        if stations[stn]['years'] != None:
            years_set = years_set.union(stations[stn]['years'])
            for y in stations[stn]['years']:
                avail_per_stn[int(y)] = int(stations[stn][y]['nmonths'])
        availability[stn] = avail_per_stn

    year_list = list(range(min({int(x) for x in years_set}),
                           max({int(x) for x in years_set}) + 1))
    columns_list = ['Alt'] + year_list + ['ICOS id'] + ['ICOS alt']

    df = pd.DataFrame(data=list(availability[x] for x in availability.keys()),
                      index=list(availability.keys()),
                      columns=columns_list)
    # Fill in the gaps.
    df[year_list] = df[year_list].fillna(0)
    df[['Alt'] + year_list] = df[['Alt'] + year_list].applymap(int)

    # convert alt to string, so that we can remove nan values
    df['ICOS alt'] = df['ICOS alt'].astype(str)
    df['ICOS alt'] = df['ICOS alt'].str.replace('nan', '')

    # sort by StiltStation id
    df.sort_index(inplace=True)
    return df


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
    return [StiltStation(stations[st]) for st in stations.keys()]


def __get_stations(ids: list | None = None,
                   progress: bool = True,
                   ) -> dict[Any, Any]:
    """
    Get all stilt stations available on the server and return a
    dictionary with metadata. Keys for the dictionary are stilt station
    id's.
    """

    all_stations = {}
    # Use directory listing from STILTPATH. STILT jobs that are not
    # finished yet do not have a directory.
    for p in Path(STILTPATH).iterdir():
        # A symbolic link might exist but not have a target.
        if p.is_symlink() and p.exists():
            all_stations[p.name] = p

    all_station_ids = list(all_stations.keys())
    # If no station ids are provided then all stations are returned.
    requested_stations = list(
        set([i.upper() for i in ids]).intersection(all_station_ids)
    ) if ids else all_station_ids

    df = pd.read_csv(STILTINFO)
    icos_stations = {s.id: s for s in meta.list_stations(ATMO_STATION)}

    stations = {}
    for station_id in tqdm(requested_stations, disable=not progress):
        # This is what a loc looks like -> 47.42Nx010.98Ex00730
        loc = all_stations[station_id].readlink().name
        stiltinfo_row = pd.DataFrame()
        # Extract matching row from STILTINFO.
        if station_id in list(df['STILT id'].values):
            stiltinfo_row = df.loc[df['STILT id'] == station_id]

        stn_info = get_stn_info(loc, station_id, stiltinfo_row, icos_stations)
        stn_info['geoinfo'] = get_geo_info(stn_info)
        stations[station_id] = stn_info

    return stations


def parse_location(loc: str) -> dict[str, Any]:
    """Pares a stilt location name such as 47.42Nx010.98Ex00730

    >>> parse_location("47.42Nx010.98Ex00730")
    {'lat': 47.42, 'lon': 10.98, 'alt': 730, 'locIdent': '47.42Nx010.98Ex00730'}
    """
    # This is what a loc looks like -> 
    lat, lon, alt = loc.split('x')
    return {
        'lat': -float(lat[:-1]) if lat[-1] == 'S' else float(lat[:-1]),
        'lon': -float(lon[:-1]) if lon[-1] == 'W' else float(lon[:-1]),
        'alt': int(alt),
        'locIdent': loc,
    }


def get_stn_info(loc: str,
                 station_id: str,
                 stiltinfo_row: pd.DataFrame,
                 icos_stations: dict[str, StationLite]) -> dict[str, Any]:
    """Return stilt-station metadata."""

    stn_info = parse_location(loc)
    stn_info['id'] = station_id
    station_name = station_id
    stn_info['icos'] = False

    if not stiltinfo_row.empty:
        if pd.isna(station_name := stiltinfo_row['STILT name'].item()):
            station_name = 'nan'
        if not pd.isna(country_code := stiltinfo_row['Country'].item()):
            stn_info['country'] = country_code
        if not pd.isna(icos_id := stiltinfo_row['ICOS id'].item()):
            icos_st: StationLite | None = icos_stations.get(icos_id, None)
            if icos_st is not None:
                stn_info['icos'] = {
                    'country': icos_st.country_code,
                    'eas': icos_st.elevation,
                    'lat': icos_st.lat,
                    'lon': icos_st.lon,
                    'stationId': icos_st.id,
                    'uri': [icos_st.uri],
                    'name': icos_st.name
                }

        if isinstance(stn_info['icos'], dict) and not stiltinfo_row.empty:
            stn_info['icos']['SamplingHeight'] = \
                stiltinfo_row['ICOS height'].item()

    stn_info['name'] = __station_name(station_id,
                                      station_name,
                                      stn_info['alt'])
    years = sorted(
        p.name for p in Path(f'{STILTPATH}{station_id}/').iterdir()
        if p.is_dir() and re.match(r'\d{4}', p.name)
    )

    stn_info['years'] = years
    for year in years:
        months = sorted(
            p.name for p in Path(f'{STILTPATH}{station_id}/{year}').iterdir()
            if p.is_dir() and re.match(r'\d{2}', p.name)
        )
        stn_info[year] = {
            'months': months,
            'nmonths': len(months)
        }

    return stn_info


def get_geo_info(stn_info: dict[str, Any]) -> dict[str, Any]:
    """Fetch geo-information for a station."""

    cc: str | None = stn_info.get('country')
    if not cc:
        raise ValueError(f"No 'country' value in station info {stn_info}")
    elif not cc in COUNTRIES:
        raise ValueError(f"Bad/unrecognized country code: {cc}")
    else:
        return {'name': {'common': COUNTRIES[cc]}}


def __station_name(station_id: str, name: str, alt: int) -> str:
    """Create name from station id and altitude."""

    station_name = station_id if name == 'nan' else name
    if not (name[-1] == 'm' and name[-2].isdigit()):
        station_name = f'{station_name} {str(alt)}m'
    return station_name


def find(**kwargs):
    """
    Return a list of stilt stations. Providing no keyword arguments will
    return a complete list of all stations. You can filter the result by
    providing the following keywords:

    Parameters
    ----------

    id STR, list of STR:
        Provide station id or list of id's. You can provide
        either stilt or icos id's mixed together.
        Example:    station.find(id='HTM')
                    station.find(id=['NOR', 'GAT344'])

    country STR:
        ISO 3166-1 alpha-2 country code

    search STR:
        Arbitrary string search keyword
         Example:    station.find(search='north')

    stations DICT
        all actions are performed on this dictionary, rather than
        dynamically search for all stilt station on our server.
        Can be useful for creating a map, or getting a subset of stations
        from an existing search.
        Example: myStations = station.find(search='north')
                 refined = station.find(stations=myStations, country='FI')

    # Spatial search keywords:

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

    project STR 'icos'.
        This will only return stilt stations that are ICOS stations.
    Example: station.find(project='icos')

    progress BOOL
        By default progress is set to True, which returns a progressbar
        while searching the catalogue of STILT stations.

    outfmt STR ['dict'| 'pandas' | 'list' | 'map'| 'avail']:
        the result is returned as

            dict:       dictionary with full metadata for each station
                        Stiltstation ID is the 'key' for the dict entries
            pandas:     dataframe with some key information
            list:       list of stilt station objects
            map:        folium map, can be displayed directly in notebooks
                        or save to a static (leaflet) .html webpage
            avail:      This choice will return availability of time series
                        data for all stilt stations.
                        Output format is a pandas dataframe.

    Returns
    -------
    List of Stiltstation in the form of outfmt=format, see above.
    Default DICT

    """

    # convert all keywords to lower case
    if kwargs:
        kwargs = {k.lower(): v for k, v in kwargs.items()}

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
           'sdate': _sdate,
           'edate': _edate,
           'dates': _dates,
           'daterange': __daterange,
           'search': _search,
           'project': _project}

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

            .get(find(country='SE'))
                returns a list of stilstations found in Sweden
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

    if isinstance(id, str):
        # assuming str is a station id
        st = __get_stations([id], progress)
        if not st:
            return None
        for s in st:
            stationslist.append(StiltStation(st[s]))

    if isinstance(id, dict):
        # assuming dict is coming from .find....call
        for s in id:
            stationslist.append(StiltStation(id[s]))

    if isinstance(id, list):
        if isinstance(id[0], dict):
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
