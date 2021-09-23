#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""    
    this file is intended to provide a folium map object
    for a station selection. Please do not use directly, 
    but import station and change the output format.
    
    from icoscp.station import station
    station.getIdList(.......outfmt='map')
"""

__author__ = ["Zois Zogopoulos"]
__credits__ = "ICOS Carbon Portal"
__license__ = "GPL-3.0"
__version__ = "0.1.0"
__maintainer__ = "ICOS Carbon Portal, elaborated products team"
__email__ = ['info@icos-cp.eu', 'zois.zogopoulos@nateko.lu.se']
__status__ = "rc1"
__date__ = "2021-09-20"


import json

import folium
import pandas as pd
from folium.plugins import MarkerCluster
import requests


def get(queried_stations):
    """Generates a folium map of stations.

    Uses the requested stations dataframe along with the REST countries
    API to generate an interactive folium map. Each marker in the
    folium map represents a station of observations.

    Parameters
    ----------
    queried_stations : pandas.Dataframe
        `queried_stations` dataframe includes each station's landing
        page or (uri), id, name, country, lat, lon, elevation, project,
        and theme.

    Returns
    -------
    stations_map : folium.Map
        `stations_map` is an interactive map used for visualizing
        geospatial data.

    """

    # Request countries data online.
    response = request_rest_countries()
    # Edit the requested data.
    countries_data = edit_rest_countries(response)
    stations = edit_queried_stations(queried_stations, countries_data)
    stations_map = folium.Map()
    marker_cluster = MarkerCluster()
    # Add tile layers to the folium map. Default is 'openstreetmap'.
    add_tile_layers(stations_map)
    # Use the stations at the most southwest and northeast
    # locations and bind the map within these stations.
    sw_loc = stations[['lat', 'lon']].dropna(axis=0).min().values.tolist()
    ne_loc = stations[['lat', 'lon']].dropna(axis=0).max().values.tolist()
    stations_map.fit_bounds([sw_loc, ne_loc])
    stations = stations.transpose()
    for station_index in stations:
        # Collect each station's info from the sparql query.
        station_info = stations[station_index]
        # Create the html popup message for each station.
        popup = folium.Popup(generate_popup_html(station_info, response))
        if response:
            # Set the icon for each marker according to country's code.
            icon = folium.CustomIcon(icon_image=station_info.flag, icon_size=(20, 14))
        else:
            icon = folium.Icon(color='blue', icon_color='white', icon='info_sign')
        # Add a marker for each station at the station's location
        # along with the popup and the tooltip.
        station_marker = folium.Marker(location=[station_info.lat, station_info.lon],
                                       tooltip='<b>' + station_info.id + '</b>',
                                       popup=popup,
                                       icon=icon)
        # Add the station marker to the cluster.
        marker_cluster.add_child(station_marker)
    # Add the cluster and the layer control to the folium map.
    stations_map.add_child(marker_cluster)
    stations_map.add_child(folium.LayerControl())
    return stations_map


def generate_popup_html(station_info, response):
    """Generates an html popup for an interactive folium map.

    For each station being processed creates an html popup with useful
    information.

    Parameters
    ----------
    station_info : pandas.Series
        `station_info` series contains an extended version of the
        station series in the `queried_stations` collection. This
        version includes a landing page or (uri), id, lat, lon,
        elevation, project, theme, country_code, station_name, country,
        and flag.

    Returns
    -------
    folium_html : branca.Html
        `folium_html` contains all the necessary data to visualize a
        station's information as a popup within the folium map.

    """

    # Format station's html string using data extracted from the dataframe.
    if response:
        station_html = \
            """
            <table border='0'>
                <caption style='font-weight:bold;font-size:18px;padding:15px;'>
                    Station Information
                </caption>
                <tr style='background-color:#f8f4f4'>
                    <td style="padding:4px"><nobr>Station name</nobr></td>
                    <td style="padding:4px"><nobr><a title="{uri}" href="{uri}">
                        {station_name}
                    </a></nobr></td>
                </tr>
                <tr><td style="padding:4px">Station ID</td><td style="padding:4px">{id}</td></tr>
                <tr style='background-color:#f8f4f4'>
                    <td style="padding:4px">Country, Country code</td>
                    <td style="padding:4px"><nobr>{country} - {country_code}</nobr></td>
                </tr>
                <tr>
                    <td style="padding:4px"><nobr>Latitude, Longitude, Elevation</nobr></td>
                    <td style="padding:4px"><nobr>{latitude}, {longitude}, {elevation}</nobr></td>
                </tr>
                <tr style='background-color:#f8f4f4'>
                    <td style="padding:4px">Project</td>
                    <td style="padding:4px">{project}</td>
                </tr>
                <tr><td style="padding:4px">Theme</td><td style="padding:4px">{theme}</td></tr>
            </table>
            """.format(uri=station_info.uri, station_name=station_info.station_name,
                       id=station_info.id, country=station_info.country,
                       country_code=station_info.country_code, latitude=station_info.lat,
                       longitude=station_info.lon, elevation=station_info.elevation,
                       project=station_info.project, theme=station_info.theme)
    else:
        station_html = \
            """
            <table border='0'>
                <caption style='font-weight:bold;font-size:18px;padding:15px;'>
                    Station Information
                </caption>
                <tr style='background-color:#f8f4f4'>
                    <td style="padding:4px"><nobr>Station name</nobr></td>
                    <td style="padding:4px"><nobr><a title="{uri}" href="{uri}">
                        {station_name}
                    </a></nobr></td>
                </tr>
                <tr><td style="padding:4px">Station ID</td><td style="padding:4px">{id}</td></tr>
                <tr style='background-color:#f8f4f4'>
                    <td style="padding:4px">Country code</td>
                    <td style="padding:4px"><nobr>{country_code}</nobr></td>
                </tr>
                <tr>
                    <td style="padding:4px"><nobr>Latitude, Longitude, Elevation</nobr></td>
                    <td style="padding:4px"><nobr>{latitude}, {longitude}, {elevation}</nobr></td>
                </tr>
                <tr style='background-color:#f8f4f4'>
                    <td style="padding:4px">Project</td>
                    <td style="padding:4px">{project}</td>
                </tr>
                <tr><td style="padding:4px">Theme</td><td style="padding:4px">{theme}</td></tr>
            </table>
            """.format(uri=station_info.uri, station_name=station_info['name'],
                       id=station_info.id, country_code=station_info.country,
                       latitude=station_info.lat, longitude=station_info.lon,
                       elevation=station_info.elevation, project=station_info.project,
                       theme=station_info.theme)
    # Render html from string.
    folium_html = folium.Html(station_html, script=True)
    return folium_html


def add_tile_layers(folium_map):
    """Adds multiple layers to a folium map.

    Parameters
    ----------
    folium_map : folium.Map
        `folium_map` is the parent element to which all tile layers
        (children elements) will be added.

    Returns
    -------
    folium_map : folium.Map
        Returns an updated version of the `folium_map`.

    """

    # Add built-in tile layers.
    folium_map.add_child(folium.TileLayer('cartodbpositron'))
    folium_map.add_child(folium.TileLayer('cartodbdark_matter'))
    folium_map.add_child(folium.TileLayer('stamenwatercolor'))
    folium_map.add_child(folium.TileLayer('stamentoner'))
    folium_map.add_child(folium.TileLayer('stamenterrain'))
    # Add another layer with satellite images from ESRI.
    folium_map.add_child(folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer'
              '/tile/{z}/{y}/{x}',
        attr='Esri',
        name='Esri Satellite',
        overlay=False,
        opacity=1.0,
        control=True))
    return folium_map


def request_rest_countries():
    """Requests data from rest-countries API.

    This function uses first https://restcountries.com/ and then
    https://restcountries.eu/ API to request data (names,
    country-codes and flags) for countries.

    Returns
    -------
    response : dict
        Returns a dictionary with countries data obtained from
        rest-countries API. The `service` key validates the source of
        the data ('com', 'eu' or False). If both requests fail the
        `service` key has a value of False.

    Raises
    ------
    HTTPError
        An HTTPError exception is raised if the requested REST
        countries data is unavailable.
    SSLError
        An SSLError exception is raised if the requested resources have
        an untrusted SSL certificate.

    """

    response = {'service': False}
    response_eu = None
    response_com = None
    try:
        # Try to request countries data from
        # https://restcountries.com/ REST-ful API.
        response_com = requests.get(
            'https://restcountries.com/v2/all?fields=name,flags,alpha2Code')
        response_com.raise_for_status()
    except (requests.exceptions.HTTPError, requests.exceptions.SSLError) as e:
        print("Restcountries .com request error: " + str(e))
        try:
            # If the first request fails try from
            # https://restcountries.eu REST-ful API
            response_eu = requests.get(
                'https://restcountries.eu/rest/v2/all?fields=name;flag;alpha2Code')
            response_eu.raise_for_status()
        except (requests.exceptions.HTTPError, requests.exceptions.SSLError) as e:
            print("Restcountries .eu request error: " + str(e))

    if response_com:
        response = {'service': 'com', 'data': response_com}
    elif response_eu:
        response = {'service': 'eu', 'data': response_eu}
    # If both requests failed the response will contain a False service
    # value.
    return response


def edit_rest_countries(response):
    """Edits rest-countries data.

    This function uses first https://restcountries.com/ and then
    https://restcountries.eu/ API to request data (names,
    country-codes and flags) for countries.

    Returns
    -------
    response : dict
        Returns a dictionary with countries data obtained from
        rest-countries API. The `service` key validates the source of
        the data ('com', 'eu' or False). If both requests fail the
        `service` key has a value of False.

    Raises
    ------
    HTTPError
        An HTTPError exception is raised if the requested REST
        countries data is unavailable.
    SSLError
        An SSLError exception is raised if the requested resources have
        an untrusted SSL certificate.

    """

    if response['service']:
        json_countries = json.loads(response['data'].text)
        countries_data = {}
        # Use the requested data to create a dictionary of country
        # names, codes, and flags.
        for country in json_countries:
            code = country['alpha2Code']
            country_name = country['name']
            if response['service'] == 'com':
                country_flag = country['flags'][1]
            else:
                country_flag = country['flag']
            countries_data[code] = {'name': country_name, 'flag': country_flag}
        # Include the 'UK' alpha2code which is missing from
        # restcountries API.
        countries_data['UK'] = countries_data['GB']
        print(countries_data)
        return countries_data
    else:
        return False



def edit_queried_stations(queried_stations, countries_data):
    pd.set_option("display.max_rows", None, "display.max_columns", None)
    edited_stations = pd.DataFrame()
    # Transpose the requested stations dataframe and iterate each
    # station.
    queried_stations = queried_stations.transpose()
    for station_index in queried_stations:
        # Collect each station's info from the sparql query.
        station_info = queried_stations[station_index]
        # Measurements collected from instrumented Ships of
        # Opportunity don't have a fixed location and thus are
        # excluded from the folium map.
        if station_info.lat is None or station_info.lon is None:
            continue
        if countries_data:
            # Add new labels and data (using the rest-countries API) and
            # update existing labels of the dataframe to better represent
            # the station's information.
            station_info['country_code'] = station_info.pop('country')
            station_info['station_name'] = station_info.pop('name')
            station_info['country'] = countries_data[station_info.country_code]['name']
            station_info['flag'] = countries_data[station_info.country_code]['flag']
        edited_stations = edited_stations.append(other=station_info)
    return edited_stations


