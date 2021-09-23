#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Define global (to icoscp) common tool to search for
    country information based on a static local file
    country.json credit to https://github.com/mledoze/countries
    and for reverse geocoding:
    https://nominatim.openstreetmap.org 
"""

import importlib.resources as pkgres
import icoscp
import requests
import json

def get(**kwargs):
    """
    Search country information is based on
    https://restcountries.eu/ and https://nominatim.openstreetmap.org
    (for reverse geocoding).
    Please note: in case you provide more than one parameter, the order
    of keywords is not respected. The execution order is always like
    the function signature and as soon as a result is found, it will be
    returned and the search is stopped.

    Accepted keywords: code='', name='', latlon=[]

    Example:
        country(code='se')  -> returns a dict with Sweden
        country(name='se')  -> returns a list of dict with ~10 countries
        country(latlon=[45.5,3.15])

    Parameters
    ----------
    code : STR
        Search by ISO 3166-1 2-letter or 3-letter country codes
    name : STR
        search by country name. It can be the native name or partial name
    latlon : List[]
        List containing  two integer or floating point numbers representing
        latitude and longitude. Example [48.85, 2.35]

        If a list with latitude and longitude is provided, a reverse
        geocoding is applied. If the provided point is within a country
        a code='' search is performed as explained above.


    Returns
    -------
    DICT: for positive results for searching code or latlon
    LIST[DICT]: for positive results for name search
    BOOL (False) if no result

    """

    if not kwargs:
        return False
    
    
    countries = pkgres.read_text(icoscp, 'countries.json')
    countries  = json.loads(countries)
    
        
    if 'code' in kwargs.keys():        
        return _c_code(kwargs['code'], countries)
        

    if 'name' in kwargs.keys():
        return _c_name(kwargs['name'], countries)


    if 'latlon' in kwargs.keys():
        latlon = kwargs['latlon']
        if isinstance(latlon, list) and len(latlon) == 2:
            country = _c_reverse(latlon)
        if country:
            return _c_code(kwargs['code'], countries)

    return False


def _c_code(code, countries):        
    country = []
    for c in countries:
        if code.lower() == str(c['cca2']).lower() or \
            code.lower() == str(c['cca3']).lower():
                country.append(c)
    if not country:
        return False
    
    if len(country) ==1 :
        #return the dictionary rather than the list
        return country[0]
    else:
        return country

def _c_name(name, countries):
    country = []
    for c in countries:
         if name.lower() in str(c['name']).lower() \
             or name.lower() in str(c['altSpellings']).lower():
                 country.append(c)
            
            
    if not country:
        return False
    
    if len(country) ==1 :
        #return the dictionary rather than the list
        return country[0]
    else:
        return country

def _c_reverse(latlon):
    # revers geocoding
    base = 'https://nominatim.openstreetmap.org/reverse?format=json&'
    url = base + 'lat=' + str(latlon[0]) + '&lon=' + str(latlon[1]) + '&zoom=3'
    response = requests.get(url=url)
    country = response.json()
    if 'address' in country.keys():
        return country['address']['country_code']

    return False


if __name__ == "__main__":
    # in case it is run standalone
    
    a = get()
    b = get(code='abW')
    c = get(name='republic')
    d = get(name='lithuania')
    e = get(code='lithuania')
    f = get(latlon=[42,0],name='schweiz')
    g = get(code='fr', latlon=[56.6,2.9])
