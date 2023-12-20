#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Define global (to icoscp) common tool to search for
    country information based on a static local file
    country.json  -> credit to https://github.com/mledoze/countries
    and for reverse geocoding -> credit to
    https://nominatim.openstreetmap.org
"""

import importlib.resources as pkgres
import json
import sys
import warnings

from fiona.errors import DriverError
import icoscp
import geopandas as gpd
from shapely.geometry import Point
import icoscp.const as CPC


try:
    WORLD = gpd.read_file(CPC.COUNTRY_SHAPE)
except DriverError as e:
    WORLD = None
    off_server_countries_warning = (
        "Please be aware, that the reverse geocoding functionality of the "
        "\"countries\" module is not available locally (outside of the Virtual "
        "Environment at the ICOS Carbon Portal). You must use one of our "
        "Jupyter Services. Visit "
        "https://www.icos-cp.eu/data-services/tools/jupyter-notebook for "
        "further information."
    )
    warnings.warn(off_server_countries_warning, category=Warning)
    sys.stderr.flush()

def get(**kwargs):
    """
    Search country information.
    Please note: in case you provide more than one parameter, the order
    of keywords is not respected. The execution order is always like
    the function signature and as soon as a result is found, it will be
    returned and the search is stopped.

    Accepted keywords: code='', name='', latlon=[], search=''

    Example:
        .get()                      list of dict: all countries
        .get(code='CH')             dict: Switzerland
        .get(name='greece')         dict: Greece
        .get(latlon=[48.85, 2.35])  dict:
        .get(search='europe')

    Parameters
    ----------
    code : STR
        Search by ISO 3166-1 2-letter or 3-letter country codes

    name : STR
        search by country name, including alternativ spellings.
        It can be the native name or a partial name.

    latlon : List[]
        List with two integer or floating point numbers representing
        latitude and longitude. BE AWARE: using an external service
        from openstreetmap for reverse geocoding

    search : STR
        arbitrary text search, not case sensitiv, search in all fields

    Returns
    -------
    DICT: if a single country is found
    LIST[DICT]: list of dicts if more than one countre
    BOOL (False) if no result

    """

    # create a ressource file and read
    countries = pkgres.read_text(icoscp.countries, 'countries.json')
    countries  = json.loads(countries)

    if not kwargs:
        return countries

    if 'code' in kwargs.keys():
        return _c_code(kwargs['code'], countries)


    if 'name' in kwargs.keys():
        return _c_name(kwargs['name'], countries)

    if 'search' in kwargs.keys():
        return _c_search(kwargs['search'], countries)

    if 'latlon' in kwargs.keys():
        latlon = kwargs['latlon']
        if isinstance(latlon, list) and len(latlon) == 2:
            country = _c_reverse(lat=latlon[0], lon=latlon[1])
        if country:
            return _c_code(country, countries)

    return False

def _c_search(search, countries):
    country = []
    for ctn in countries:
        if search.lower() in str(ctn).lower():
            country.append(ctn)

    if not country:
        return False

    if len(country) ==1 :
        #return the dictionary rather than the list
        return country[0]

    return country


def _c_code(code, countries):
    country = []
    for ctn in countries:
        if code.lower() == str(ctn['cca2']).lower() or \
            code.lower() == str(ctn['cca3']).lower():

            country.append(ctn)
    if not country:
        return False

    if len(country) ==1 :
        #return the dictionary rather than the list
        return country[0]

    return country

def _c_name(name, countries):
    country = []
    for ctn in countries:
        if name.lower() in str(ctn['name']).lower() \
             or name.lower() in str(ctn['altSpellings']).lower():

            country.append(ctn)


    if not country:
        return False

    if len(country) ==1 :
        #return the dictionary rather than the list
        return country[0]

    return country


def _c_reverse(lat: float, lon: float):
    """
    Reverse geocoder using geopandas and shapely.

    Shapefiles are directly accessed from the /data directory of
    the ICOS Carbon Portal; currently, this functionality is limited
    to on-server use.
    """
    country = False
    if WORLD.empty:
        for index, row in WORLD.iterrows():
            if row.geometry.contains(Point(lon, lat)):
                country = row.SOV_A3.lower()
    return country


if __name__ == "__main__":

    MSG = """

    # find country information from a static file with the icoscp library.
    # you can import this file with:

    from icoscp.countries import country

    # arbitrary text search
    a = get(search='Europe')

    # search by country code (alpha2 & alpha3)
    b = get(code='SE')      # returns Sweden
    c = get(code='CHE')     # returns Switzerland

    # search by name, includes alternative spellings
    d = get(name = 'greece') # returns Greece
    e = get(name = 'helle' ) # returns Greece and Seychelles

    # reverse search using latitude, longitude
    f = get(latlon=[42.5,13.8]) # returns Italy
    """
    print(MSG)
