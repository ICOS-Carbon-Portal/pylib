#!/usr/bin/env python

"""    
    create a map based on folium (wrapper for leaflet)
"""

__credits__     = "ICOS Carbon Portal"
__license__     = "GPL-3.0"
__version__     = "0.1.0"
__maintainer__  = "ICOS Carbon Portal, elaborated products team"
__email__       = ['info@icos-cp.eu', 'claudio.donofrio@nateko.lu.se']
__status__      = "rc1"
__date__        = "2021-04-16"


import folium
from folium.plugins import MarkerCluster
from typing import Any


def get(stations, fmt='map', cluster=True):
    '''
    Provide a map based on the folium module.

    Parameters
    ----------
    stations : DICT : StiltStation dictionary
    fmt: STR: ['map' | 'html'] see Returns below.
    cluster: BOOL: default True. Markers are clustered or not

    Returns
    -------
    Depending on fmt:
        By default a folium map object is returned,
        which can be displayed directly in a Jupyter Notebook
        fmt='html' returns a static html website as STR which can
        be saved to a file.
    '''
    
    if not isinstance(stations, dict):
        return 'input needs to be dictionary'
    
    zoom = 4

    #create the map
    myMap = folium.Map(zoom_start=zoom,no_wrap=True)
    
    # add tiles, to see what kind of basemap you like
    # tile layers will be displayed in the top right
    
    folium.TileLayer('openstreetmap').add_to(myMap)
    folium.TileLayer('cartodbpositron').add_to(myMap)
    folium.TileLayer('stamentoner').add_to(myMap)
    folium.TileLayer('stamenterrain').add_to(myMap)
    
    markers = []    # keep all the markers for clustering
    lats = []       # keep lat, lon vector to calculate the center of the map
    lons = []       # keep lat, lon vector to calculate the center of the map
    for k in stations:
        lat = float(stations[k]['lat'])
        lats.append(lat)
        lon = float(stations[k]['lon'])
        lons.append(lon)
        msg = _pretty_html(stations[k])
        markers.append(folium.Marker(location=[lat, lon], popup=msg))
    
    if cluster:
        mc = MarkerCluster(name='StiltStations')
        for m in markers:
            mc.add_child(m)
        myMap.add_child(mc)
    else:
        for m in markers:
            myMap.add_child(m)

    #re-centre the map
    bounds = [(min(lats), min(lons)), (max(lats), max(lons))]
    folium.FitBounds(bounds).add_to(myMap)
    #myMap.fit_bounds(sw,ne)

    folium.LayerControl().add_to(myMap)    
    return myMap

def _pretty_html(station: dict[str, Any]):
    # create a html table for the popup 
    header = """<!DOCTYPE html>
                <html>
                <link rel="stylesheet" href="https://www.w3schools.com/w3css/4/w3.css">
                <body><div class="w3-container">
                    <table width="200" class="w3-striped">
                """
    body: str = '<tr><td colspan="2">Stilt Station info: </td></tr>'
    body += '<tr><td>Stilt id: </td><td>' + station['id'] + '</td></tr>'
    if station['icos']:
        body += '<tr><td>ICOS id: </td><td><a href= "'
        body += station['icos']['uri'][0] + '">'
        body += station['icos']['stationId'] + "</a>" +'</td></tr>'
        
    body += '<tr><td>lat: </td><td>' + str(station['lat']) + '</td></tr>'
    body += '<tr><td>lon: </td><td>' + str(station['lon']) + '</td></tr>'    
    body += '<tr><td colspan="2">\
        <a href="https://stilt.icos-cp.eu/viewer/" target="_blank">\
        https://stilt.icos-cp.eu/viewer/</a></td></tr>'    
    footer = "</table></div></body></html>"
    html = header + body + footer

    return html
