#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Example to create a new class based on the station class
to add some specific information. 
For this example we will add the information for the
National Network URL, which we will read from a .csv file
    
"""

__author__ = "Claudio D'Onofrio"
__credits__ = ["ICOS Carbon Portal Dev Team"]
__license__ = "GPL"
__version__ = "0.0.1. jupyter"
__maintainer__ = "Claudio D'Onofrio"
__email__ = ["claudio.donofrio at nateko.lu.se", 'info@icos-cp.eu']
__status__ = "Development"

# ----------------------------------------------
# for testing only, set path to ICOS pytools
import sys
sys.path.insert(0,'C:\\Users\\Claudio\\Documents\\GitHub\\ICOS-CP\\jupyter\\pytools')
# ----------------------------------------------


from icoscp.api.station import Station
from icoscp.sparql.runsparql import RunSparql
from icoscp.sparql import sparqls
# ----------------------------------------------
class myStation(Station):
    """ Create an ICOS Station object and extend the basic class       
        for this example, we will add a field
        for the ICOS National Network URL 
    """    
    
    def __init__(self, attrList=None):
        
        super().__init__(attrList)
        
        self._networkurl = None
        
    #-------------------------------------
    @property
    def networkurl(self):
        return self._networkurl
    
    @networkurl.setter
    def networkurl(self, networkurl):
        self._networkurl = networkurl
    
    #-------------------------------------

# ------------------------------------------------------------
def getStationList():
    """
    Query the SPARQL endpoint for stations, create
    an object for each Station and return a list of stations
    
    Returns
    -------
    stationList : list
    """
    query = sparqls. stations_with_pi()
    cpStations = RunSparql(query,'pandas').run()    
    stationList = []
    for s in cpStations.values.tolist():        
        stationList.append(myStation(s))
        
    return stationList
# ------------------------------------------------------------    


