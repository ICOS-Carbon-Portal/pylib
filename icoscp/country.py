#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Define global (to icoscp) common tool to search for
    country information based on
    https://restcountries.eu/
    https://nominatim.openstreetmap.org (for reverse geocoding).
"""

import requests


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

    if 'code' in kwargs.keys():
        country = _c_code(kwargs['code'])
        if country:
            return country

    if 'name' in kwargs.keys():
        country = _c_name(kwargs['name'])
        if country:
            return country

    if 'latlon' in kwargs.keys():
        latlon = kwargs['latlon']
        if isinstance(latlon, list) and len(latlon) == 2:
            country = _c_reverse(latlon)
        if country:
            country = _c_code(country)
        if country:
            return country

    return False


def _c_code(code):
    # API to reterive country information using country code.
    url = 'https://restcountries.eu/rest/v2/alpha/' + code
    response = requests.get(url=url)
    c_info = response.json()
    if len(c_info) > 2:
        return c_info
    return False


def _c_name(name):
    # API to reterive country information using country code.
    url = 'https://restcountries.eu/rest/v2/name/' + name
    response = requests.get(url=url)
    c_info = response.json()
    if isinstance(c_info, list):
        return c_info
    return False


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
    g = get(latlon=[42,0])
    a = get(code='se')
    c = get(name='chruesimuesy')
    d = get(name='lithuania')
    e = get(code='lithuania')
    f = get(latlon=[42,0],name='schweiz')
    h = get(code='fr', latlon=[56.6,2.9])
