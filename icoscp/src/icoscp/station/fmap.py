#!/usr/bin/env python

"""Provide folium map object for station selection.

Please do not use directly, but import station and change the output format.

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

# Standard library imports.
import json
import os
# Related third party imports.
from folium.plugins import MarkerCluster
import folium
import pandas as pd
import requests


def get(queried_stations, project, icon):
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

    project : str
        The name of the project that the user inserted in the caller
        function in order to search for stations.

    icon: None | str, optional
        Argument passed down from `getIdList()` function.

    Returns
    -------
    stations_map : folium.Map
        `stations_map` is an interactive map used for visualizing
        geospatial data.

    """
    # Request countries data online.
    response = request_rest_countries()
    # Edit the requested data.
    edited_response = collect_rest_data(response)
    # Apply countries data on the queried stations and remove stations
    # without a fixed location.
    stations = edit_queried_stations(queried_stations, edited_response)
    stations_map = folium.Map()
    # Provide the map name within the top right menu.
    if project == 'ALL':
        cluster_name = ', '.join(['ICOS', 'NEON', 'INGOS', 'FLUXNET'])
    else:
        cluster_name = project
    marker_cluster = MarkerCluster(name=cluster_name)
    # Add tile layers to the folium map. Default is 'openstreetmap'.
    add_tile_layers(stations_map)
    # Use the stations at the most southwest and northeast locations
    # and bind the map within these stations.
    sw_loc = stations[['lat', 'lon']].dropna(axis=0).min().values.tolist()
    ne_loc = stations[['lat', 'lon']].dropna(axis=0).max().values.tolist()
    stations_map.fit_bounds([sw_loc, ne_loc])
    stations = stations.transpose()
    for station_index in stations:
        # Collect each station's info.
        station_info = stations[station_index]
        # Create the html popup message for each station.
        popup = folium.Popup(generate_popup_html(station_info, response))
        if icon == 'flag' and response['service']:
            # Set the folium icon for each marker using the country's
            # flag.
            folium_icon = folium.CustomIcon(icon_image=station_info.flag,
                                            icon_size=(20, 14))
        elif icon and os.path.isfile(icon):
            # The `folium_icon` variable needs to be initialized for
            # each marker and each marker will include a copy of the
            # custom image in the generated html map. This results in
            # maps with large size, thus one needs to use small sized
            # images. This issue is already mentioned here:
            # https://github.com/python-visualization/folium/issues/744
            folium_icon = folium.features.CustomIcon(icon, icon_size=(20, 14))
        else:
            folium_icon = folium.Icon(color='blue', icon_color='white',
                                      icon='info_sign')
        # Add a marker for each station at the station's location
        # along with the popup and the tooltip.
        station_marker = folium.Marker(
            location=[station_info.lat, station_info.lon],
            tooltip=f'<b>{station_info.id}</b>',
            popup=popup,
            icon=folium_icon)
        # Add the station marker to the cluster.
        marker_cluster.add_child(station_marker)
    # Add the cluster and the layer control to the folium map.
    stations_map.add_child(marker_cluster)
    stations_map.add_child(folium.LayerControl())
    return stations_map


def request_rest_countries():
    """Requests data from rest-countries API.

    This function uses https://restcountries.com/ API to request data
    (names ,country-codes and flags) for countries.

    Returns
    -------
    response : dict
        Returns a dictionary with countries data obtained from
        rest-countries API. The `service` key validates the source of
        the data ('com', or False). If the request fails the `service`
        key has a value of False.

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
    response_com = None
    try:
        # Try to request countries data from
        # https://restcountries.com/ REST-ful API.
        response_com = requests.get(
            'https://restcountries.com/v2/all?fields=name,flags,alpha2Code')
        response_com.raise_for_status()
    except (requests.exceptions.HTTPError, requests.exceptions.SSLError) as e:
        print('Restcountries \'.com\' request error: ' + str(e))

    if response_com:
        response = {'service': 'com', 'data': response_com}
    # If the request failed, the response will contain a False service
    # value which is then used by the caller function to generate the
    # folium map without any errors but with less information.
    return response


def collect_rest_data(response):
    """Extracts raw rest-countries data from requested resources.

    Parameters
    ----------
    response : dict
        If the requested resources were available the `response`
        dictionary will contain the raw rest-countries data.

    Returns
    -------
    response : dict
        Returns an updated version of the `response` dictionary
        obtained from `request_rest_countries()` function. If the
        request was successful, this version will include the
        rest-countries data that was extracted from the request.

    """

    # Rest-countries resources are available.
    if response['service']:
        json_countries = json.loads(response['data'].text)
        countries_data = {}
        # Use the requested data to create a dictionary of country
        # names, codes, and flags.
        for country in json_countries:
            code = country['alpha2Code']
            country_name = country['name']
            country_flag = country['flags']['svg']
            countries_data[code] = {'name': country_name, 'flag': country_flag}
        # Include the 'UK' alpha2code which is missing from
        # restcountries API.
        countries_data['UK'] = countries_data['GB']
        # Add the created dictionary to the response.
        response['countries_data'] = countries_data
    return response


def edit_queried_stations(queried_stations, edited_response):
    """Applies new data on queried stations.

    Uses the `edited_response` dictionary to add data to the queried
    stations which are then appended to a new dataframe.

    Parameters
    ----------
    queried_stations : pandas.Dataframe
        `queried_stations` dataframe includes each station's landing
        page or (uri), id, name, country, lat, lon, elevation, project,
        and theme.
    edited_response: dict
        `edited_response` is an updated version of the `response`
        dictionary obtained from `request_rest_countries()` function.
        If the request was successful, this version will include the
        rest-countries data that was extracted using the
        `collect_rest_data()` function.

    Returns
    -------
    edited_stations : pandas.Dataframe
        `edited_stations` is an updated version of the
        `queried_stations` dataframe which was obtained using a sparql
        query. Also, this edited version is stripped off stations
        without a fixed position (Instrumented ships of opportunity).

    """

    stations = list()
    folium_station = pd.DataFrame()
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
        # The requested resources are available.
        if edited_response['service']:
            countries_data = edited_response['countries_data']
            # Add new labels and data (using the rest-countries API) and
            # update existing labels of the dataframe to better represent
            # the station's information.
            station_info['country_code'] = station_info.pop('country')
            station_info['station_name'] = station_info.pop('name')
            station_info['country'] = countries_data[station_info.country_code]['name']
            station_info['flag'] = countries_data[station_info.country_code]['flag']
            stations.append(station_info)
        #
        folium_stations = pd.concat(stations, axis=1).transpose()
    return folium_stations


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
    response : dict
        An updated version of the `response` dictionary
        obtained from `request_rest_countries()` function. If any of
        HTTP requests were successful, this version will include the
        rest-countries data that was extracted from the requests.

    Returns
    -------
    folium_html : branca.Html
        `folium_html` contains all the necessary data to visualize a
        station's information as a popup within the folium map.

    """

    # Format station's html string using data extracted from the dataframe.
    if response['service']:
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






