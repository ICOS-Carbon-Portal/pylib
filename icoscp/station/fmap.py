import json

import folium
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

    Raises
    ------
    HTTPError
        An HTTPError exception is raised if the requested REST
        countries data is unavailable.

    """

    # Use the https://restcountries.eu REST-ful API to request data
    # for each country.
    response = requests.get('https://restcountries.eu/rest/v2/all?'
                            'fields=flag;alpha2Code;name')
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        return "Restcountries request error: " + str(e)
    json_countries = json.loads(response.text)
    # Use the requested data to create a dictionary of country
    # names, codes, and flags.
    countries_data = {}
    for dict_item in json_countries:
        countries_data[dict_item['alpha2Code']] = {'name': dict_item['name'],
                                                   'flag': dict_item['flag']}
    # Include the 'UK' alpha2code which is missing from
    # restcountries API.
    countries_data['UK'] = countries_data['GB']
    stations_map = folium.Map()
    marker_cluster = MarkerCluster()
    # Add tile layers to the folium map. Default is 'openstreetmap'.
    add_tile_layers(stations_map)
    # Use the stations at the most southwest and northeast
    # locations and bind the map within these stations.
    sw_loc = queried_stations[['lat', 'lon']].dropna(axis=0).min().values.tolist()
    ne_loc = queried_stations[['lat', 'lon']].dropna(axis=0).max().values.tolist()
    # Increase the map's bounds to visually include all the map's
    # markers.
    sw_loc = [float(sw_loc[0]), float(sw_loc[1]) + 1.3]
    ne_loc = [float(ne_loc[0]) + 1.3, float(ne_loc[1])]
    stations_map.fit_bounds([sw_loc, ne_loc])
    # Transpose the requested stations dataframe and iterate each
    # station.
    queried_stations = queried_stations.transpose()
    for station_index in queried_stations:
        # Collect each station's info from the sparql query.
        station_info = queried_stations[station_index]
        # Add new labels and data (using the rest-countries API) and
        # update existing labels of the dataframe to better represent
        # the station's information.
        station_info['country_code'] = station_info.pop('country')
        station_info['station_name'] = station_info.pop('name')
        station_info['country'] = countries_data[station_info.country_code]['name']
        station_info['flag'] = countries_data[station_info.country_code]['flag']
        # Measurements collected from instrumented Ships of
        # Opportunity don't have a fixed location and thus are
        # excluded from the folium map.
        if station_info.lat is None or station_info.lon is None:
            continue
        # Create the html popup message for each station.
        popup = folium.Popup(generate_popup_html(station_info))
        # Set the icon for each marker according to country's code.
        icon = folium.CustomIcon(icon_image=station_info.flag, icon_size=(20, 14))
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


def generate_popup_html(station_info):
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
