import json

import folium
from folium.plugins import MarkerCluster
import requests


def get(queried_stations):
    # Use the https://restcountries.eu REST-ful API to request data
    # for each country.
    response = requests.get('https://restcountries.eu/rest/v2/all? '
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
    # Add built-in tile layers. Default is 'openstreetmap'.
    stations_map.add_child(folium.TileLayer('cartodbpositron'))
    stations_map.add_child(folium.TileLayer('cartodbdark_matter'))
    stations_map.add_child(folium.TileLayer('stamenwatercolor'))
    stations_map.add_child(folium.TileLayer('stamentoner'))
    stations_map.add_child(folium.TileLayer('stamenterrain'))
    # Add another layer with satellite images from ESRI.
    stations_map.add_child(folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer'
              '/tile/{z}/{y}/{x}',
        attr='Esri',
        name='Esri Satellite',
        overlay=False,
        opacity=1.0,
        control=True))
    # Use the stations at the most southwest and northeast
    # locations and bind the map within these stations.
    sw_loc = queried_stations[['lat', 'lon']].dropna(axis=0).min().values.tolist()
    ne_loc = queried_stations[['lat', 'lon']].dropna(axis=0).max().values.tolist()
    # Increase the map's bounds to visually include all the map's
    # markers.
    sw_loc = [float(sw_loc[0]), float(sw_loc[1]) + 1.3]
    ne_loc = [float(ne_loc[0]) + 1.3, float(ne_loc[1])]
    stations_map.fit_bounds([sw_loc, ne_loc])
    # Iterate over pandas stations. (Warning! Pandas dataframes
    # shouldn't be iterated unless absolutely necessary. This
    # implementation might change.
    for idx in queried_stations.index.values:
        code = queried_stations.iloc[idx]['country']
        queried_stations['country_name'] = countries_data[code]['name']
        queried_stations['flag'] = countries_data[code]['flag']
        # Station to be processed.
        station_info = queried_stations.iloc[idx]
        # Measurements collected from instrumented Ships of
        # Opportunity don't have a fixed location and thus are
        # excluded from the folium map.
        if station_info.lat is None or station_info.lon is None:
            continue
        # Create the html popup message for each station.
        popup = folium.Popup(generate_html(station_info))
        # Set the icon for each marker according to country's code.
        icon = folium.CustomIcon(icon_image=countries_data[station_info[3]]['flag'],
                                 icon_size=(20, 14))
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


def generate_html(station_info):
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
                    {name}
                </a></nobr></td>
            </tr>
            <tr><td style="padding:4px">Station ID</td><td style="padding:4px">{id}</td></tr>
            <tr style='background-color:#f8f4f4'>
                <td style="padding:4px">Country, Country code</td>
                <td style="padding:4px"><nobr>{country_name} - {country_code}</nobr></td>
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
        """.format(uri=station_info[0], name=station_info[2], id=station_info[1],
                   country_name=station_info[9],
                   country_code=station_info[3], latitude=station_info[4],
                   longitude=station_info[5],
                   elevation=station_info[6], project=station_info[7], theme=station_info[8])
    # Render html from string.
    folium_html = folium.Html(station_html, script=True)
    return folium_html
