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
import requests
import icoscp


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
    countries = pkgres.read_text(icoscp, 'countries.json')
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
            country = _c_reverse(latlon)
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


def _c_reverse(latlon):
    """Reverse geocode coordinates.

    Use latitude and longitude coordinates to reverse geocode a
    location. Locations within Europe are handled by icos nominatim
    service https://nominatim.icos-cp.eu/. Other cases of reverse
    geocoding are handled by https://nominatim.openstreetmap.org.

    Parameters
    ----------
    latlon : list
        `latlon` list includes latitude and longitude coordinates which
        will be used to reverse geocode.

    Returns
    -------
    location_info : dict
        Returns a dictionary with a human-readable address or place. If
        the request could not be geocoded a boolean `False` is returned
        instead.

    Raises
    ------
    RequestException
        A RequestException is raised if icos nominatim is unavailable,
        if icos nominatim could not geocode with `zoom=3`, or if
        OpenStreetMap nominatim is unavailable.

    """
    # Icos nominatim service is the first responder to a reverse
    # geocoding request.
    icos_base = 'https://nominatim.icos-cp.eu/reverse?format=json&'
    icos_url = icos_base + 'lat=' + str(latlon[0]) + '&lon=' + str(latlon[1]) + '&zoom=3'
    unable_to_geocode = False
    try:
        icos_response = requests.get(url=icos_url)
        if icos_response.status_code == 200:
            json_content = icos_response.json()
            # Icos nominatim geocoder successfully returned a location.
            if 'error' not in json_content.keys() and 'address' in json_content.keys():
                location_info = json_content['address']['country_code']
                return location_info
            else:
                unable_to_geocode = True
        # Raise this exception if icos nominatim is unavailable.
        else:
            raise requests.exceptions.RequestException
    except requests.exceptions.RequestException as request_exception:
        exception_message = ('Request failed with: ' + str(request_exception) + '\n'
                             'Icos reverse geocoding service is unavailable.\n'
                             'Redirecting to external https://nominatim.openstreetmap.org ...\n')
        # print(exception_message)
    # Handle errors due to incomplete nominatim database.
    # Icos nominatim might be able to reverse geocode without using
    # the zoom option.
    if unable_to_geocode:
        # Remove zoom from request.
        icos_url = icos_base + 'lat=' + str(latlon[0]) + '&lon=' + str(latlon[1])
        try:
            # print('Retrying without zoom ...')
            icos_response = requests.get(url=icos_url)
            if icos_response.status_code == 200:
                json_content = icos_response.json()
                # Icos nominatim geocoder successfully returned a
                # location.
                if 'error' not in json_content.keys() and 'address' in json_content.keys():
                    location_info = json_content['address']['country_code']
                    return location_info
                # Raise this exception in case icos nominatim is unable
                # to geocode. This should be replaced by a custom
                # exception raise.
                else:
                    raise requests.exceptions.RequestException
            # Raise this exception in case icos nominatim is
            # unavailable. This is a strong indicator that icos
            # nominatim crashed during consequential requests.
            else:
                raise requests.exceptions.RequestException
        except requests.exceptions.RequestException as request_exception:
            exception_message = (
                    'Request failed: ' + str(request_exception) + '\n'  
                    'Icos nominatim was unable to reverse geocode or less likely the service '
                    'crashed during two consequential requests.\nRedirecting to external '
                    'OpenStreetMap nominatim https://nominatim.openstreetmap.org ...\n')
            # print(exception_message)
    # If icos nominatim is unavailable try OpenStreetMap nominatim
    # service instead.
    external_base = 'https://nominatim.openstreetmap.org/reverse?format=json&'
    external_url = external_base + 'lat=' + str(latlon[0]) + '&lon=' + str(latlon[1]) + '&zoom=3'
    try:
        external_response = requests.get(url=external_url)
        if external_response.status_code == 200:
            json_content = external_response.json()
            # OpenStreetMap nominatim geocoder successfully returned a
            # location.
            if 'error' not in json_content.keys() and 'address' in json_content.keys():
                location_info = json_content['address']['country_code']
                return location_info
        # Raise this exception if external OpenStreetMap nominatim
        # is unavailable.
        else:
            raise requests.exceptions.RequestException
    except requests.exceptions.RequestException as request_exception:
        exception_message = ('Request failed: ' + str(request_exception) + '\n'
                             'External geocoding services at '
                             'https://nominatim.openstreetmap.org are unavailable.\n')
        # print(exception_message)
    return False


if __name__ == "__main__":

    MSG = """

    # find country information from a static file with the icoscp library.
    # you can import this file with:

    from icoscp import country

    # arbitrary text search
    a = get(search='Europe')

    # search by country code (alpha2 & alpha3)
    b = get(code='SE')      # returns Sweden
    c = get(code='CHE')     # returns Switzerland

    # search by name, includes alternative spellings
    d = get(name = 'greece') # returns Greece
    e = get(name = 'helle' ) # returns Greece and Seychelles

    # search by lat lon...!! BE AWARE this is using an external
    # rest API from OpenStreeMap https://nominatim.openstreetmap.org
    f = get(latlon=[42.5,13.8]) # returns Italy
    """
    print(MSG)
