#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Created on Wed April 22 2020
    Module to create a list of ICOS station objcets.
    A station object contains attributes for:
        - stationId (shortName)
        - name (longName)
        - theme (AS, ES, OS)
        - lat (latitude)
        - lon (longitude)
        - eas (elevation above sea level)
        - eag (elevation above ground, height of the tower)        
        - firstName (PI first name)
        - lastName (PI last name)
        - email (PI email)  
        
    Examples:
    - run as script
        creates variable named 'stationList' containing a list of stations
    - import 
    import station
    myList = station.getStationList()
    
    for each station in the list you can extract above listed attributes.
    for example
    station.lat -> return latitude as float
    station.getInfo() -> returns all attributes at once.
    The format returned can be controled with ('dict')(default format)
    ('json')('list')('pandas')('html')
    
"""

__author__ = "Claudio D'Onofrio"
__credits__ = ["ICOS Carbon Portal Dev Team"]
__license__ = "GPL"
__version__ = "0.0.1. jupyter"
__maintainer__ = "Claudio D'Onofrio"
__email__ = ["claudio.donofrio at nateko.lu.se", 'info@icos-cp.eu']
__status__ = "Development"


import json
import pandas as pd
from icoscp.sparql.runsparql import RunSparql
from icoscp.sparql import sparqls

# ----------------------------------------------
class Station():
    """ Create an ICOS Station object
        including common attributes like
        ID, Name, PI, Lat, Long etc.        
    """
    
    def __init__(self, attrList=None):
        """
        Initialize your Staion either with NO arguments, or
        provide a list of arguments in the following order:
        - stationId(shortName)
        - name (longName)
        - theme (AS, ES, OS)
        - latitude
        - longitude
        - eas (elevation above sea level)
        - eag (elevation above ground, height of the tower)        
        - firstName (PI first name)
        - lastName (PI last name)
        - email (PI email)            
        """

        # Be aware, that attributList is filled to the the ORDER of attributes        
        # you need to adjust the function setStation(attributeList)
        self._stationId = None        
        self._name = None
        self._theme = None
        self._lat = None
        self._lon = None
        self._eas = None
        self._eag = None
        
        #pi information
        self._firstName = None
        self._lastName = None
        self._email = None     
        
        #check if attributeList of Station is equal to provided List
        if attrList:            
            self.setStation(attrList)
            
    
    #super().__init__() # for subclasses
    #-------------------------------------
    @property
    def stationId(self):
        return self._stationId
    
    @stationId.setter
    def stationId(self, stationId):
        self._stationId = stationId
    
    #-------------------------------------
    @property
    def theme(self):
        return self._theme
    
    @theme.setter
    def theme(self, theme):
        self._theme = theme
    
    #-------------------------------------
    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, name):
        self._name = name
    
    #-------------------------------------
    @property
    def lat(self):
        return self._lat
    
    @lat.setter
    def lat(self, lat):
        self._lat = lat
    
    #-------------------------------------
    @property
    def lon(self):
        return self._lon
    
    @lon.setter
    def lon(self, lon):
        self._lon = lon
    
    #-------------------------------------
    @property
    def eas(self):
        return self._eas
    
    @eas.setter
    def eas(self, eas):
        self._eas = eas
    
    #-------------------------------------
    @property
    def eag(self):
        return self._eag
    
    @eag.setter
    def eag(self, eag):
        self._eag = eag
    
    #-------------------------------------
    @property
    def firstName(self):
        return self._firstName
    
    @firstName.setter
    def firstName(self, firstName):
        self._firstName = firstName
    
    #-------------------------------------
    @property
    def lastName(self):
        return self._lastName
    
    @lastName.setter
    def lastName(self, lastName):
        self._lastName = lastName
    #-------------------------------------
    @property
    def email(self):
        return self._email
    
    @email.setter
    def email(self, email):
        self._email = email
    #-------------------------------------
    def __str__(self):        
        return json.dumps(self.__dict__, indent=2)
        
        
    def setStation(self, attributeList):
        """
        Parameters
        ----------
        attributeList : list | array, must be iterable for a in list:

        provide a list of arguments in the following order:
        - stationId(shortName)
        - name (longName)
        - theme (AS, ES, OS)
        - latitude (convertible to float)
        - longitude (convertible to float)
        - eas (elevation above sea level) (convertible to float)
        - eag (elevation above ground, height of the tower) (convertible to float)   
        - firstName (PI first name)
        - lastName (PI last name)
        - email (PI email)                        
        
        Returns
        -------
        None
        

        """
        if len(self.__dict__) != len(attributeList):
            raise Exception('length of property list not valid')
            return
        
        # minimal sanity check, that number attributes are actually numbers
        check = ['_lat','_lon','_eag','_eas']
        for a in zip(self.__dict__, attributeList):            
            if a[0] in check and a[1]:
                try:
                    self.__setattr__(a[0], float(a[1]))
                except:
                    self.__setattr__(a[0], '')
                    print(self.stationId + ' convert ' + a[1] + ' to float failed for ' + a[0])
            else:
                self.__setattr__(a[0], a[1])
                

    def getInfo(self, fmt = 'dict'):
        """
        Parameters
        ----------
        fmt : str ['dict' | 'json' | 'list' | 'pandas' | 'html']
            You can choose a return format by providing fmt.
            The default is 'dict'.
            

        Returns
        -------
        All attributes for the Station

        """
        #create new 'keys' without the underscore
        newKeys = [k.strip('_') for k in list(self.__dict__)]
        values =  self.__dict__.values()
        dictionary = dict(zip(newKeys,values))
        
        if fmt == 'dict':
            return dictionary
        
        if fmt == 'json':
            return json.dumps(dictionary, indent=4)
                        
        if fmt == 'list':
            return (list(newKeys), list(values))
        
        if fmt == 'pandas':            
            return pd.DataFrame(dictionary, index=[0])
        
        if fmt == 'html':
            data = pd.DataFrame(dictionary, index=[0])
            return data.to_html()

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
        stationList.append(Station(s))
        
    return stationList
# ------------------------------------------------------------    
if __name__ == "__main__":
    """
    execute only if run as a script
    get a full list from the CarbonPortal SPARQLl endpoint
    and create a list of station objects    
    """
    stationList = getStationList()
# ------------------------------------------------------------