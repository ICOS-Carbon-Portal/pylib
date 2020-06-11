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

# ----------------------------------------------
# for testing only, set path to ICOS pytools
import sys
sys.path.insert(0,'C:\\Users\\Claudio\\Documents\\GitHub\\ICOS-CP\\jupyter\\pytools')
# ----------------------------------------------

import json
import pandas as pd
from icoscp.sparql.runsparql import RunSparql
from icoscp.sparql import sparqls
from icoscp.cpb.cpbinfile import CpBinFile as binfile
from tqdm import tqdm

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

        # Be aware, that attrList needs to be in the same ORDER as attributes                
        # info
        self._stationId = None          # shortName like HTM or SE-NOR               
        self._name = None               # longName
        self._theme = None              # AS | ES | OS
        self._icosclass = None          # 1 | 2 
        self._siteType = None           # description of site
        
        #locations
        self._lat = None
        self._lon = None
        self._eas = None
        self._eag = None
        
        #pi information
        self._firstName = None
        self._lastName = None
        self._email = None
        
        # other information
        self._country = None     
        
        
        # if the object is initialized with values
        # the count of entries in the list must be equal to the number
        # of attributes and the correct order as well. Entries can be empty.
        
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
    def icosclass(self):
        return self._icosclass
    
    @icosclass.setter
    def icosclass(self, icosclass):
        self._icosclass = icosclass
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
    @property
    def country(self):
        return self._country
    
    @country.setter
    def country(self, country):
        self._country = country
    #-------------------------------------
    def __str__(self):          
        return json.dumps(self.__dict__, indent=2)
        #d =  self.__dict__
        #d.pop('_data', None)
        #return json.dumps(d, indent=2)
        
    def data(self, level=None):
        
        if not isinstance(self._data, pd.DataFrame):
            # _data is not a dataframe but contains a string...
            return self._data

        if level:
            # if level is provided, filter pandas data frame
            return self._data[self._data['datalevel']==str(level)]
        else:
            # return complete pandas data fram
            return self._data
    
    def products(self):
        
        if not isinstance(self._products, pd.DataFrame):
            return self._products
        else:            
            return self._products
    
    
    def setStation(self, attributeList):
        """
        Parameters
        ----------
        attributeList : list | array, must be iterable for a in list:

        provide a list of arguments in the following order:
        - stationId(shortName)
        - name (longName)
        - theme (AS, ES, OS)
        - Class (ICOS Station class, see ICOS Handbook)
        - siteType (description of site, if available)
        - latitude (convertible to float)
        - longitude (convertible to float)
        - eas (elevation above sea level) (convertible to float)
        - eag (elevation above ground, height of the tower) (convertible to float)   
        - firstName (PI first name)
        - lastName (PI last name)
        - email (PI email)    
        - country                    
        
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
                    #print(self.stationId + ' convert ' + a[1] + ' to float failed for ' + a[0])
            else:
                self.__setattr__(a[0], a[1])
        
        # lets try to populate the data objects
        self.__setData()

    def info(self, fmt = 'dict'):
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
        # remove data and products from the dict to get a shorter
        # summary of informatino about station
        if 'data' in dictionary:
            del dictionary['data']
            
        if 'products' in dictionary:
            del dictionary['products']
        
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
        
    def __setData(self):
        
        """
        Query the sparql endpoint for data products submitted by this station
        adjust latitude and longitude and store a list of data specifications
        and data objects (PID's)
        """
        
        if not self.stationId:
            return
        
        # get the ressource url and adjust lat and lon from data portal
        query = sparqls.stationResource(self.stationId)
        key, val = RunSparql(query, 'array').run()
        if val:            
            self.url = val[0][0]
            self.lat = float(val[0][2])
            self.lon = float(val[0][3])
            
            query = sparqls.stationData(self.url,'all')
            self._data = RunSparql(query, 'pandas').run()
            
        else:
            self._data = 'no data available'
        
        # check if data is available and extract the 'unique' data products
        # and unique sampling heights
        if isinstance(self._data, pd.DataFrame):
            p = self._data['specLabel'].unique()            
            self._products = pd.DataFrame(p)
            
            sh = self._data['samplingheight'].astype(float)
            sh = sh.unique().tolist()   
            sh.sort()
            self._samplingheight = sh
        else:
            self._products = 'no data available'
            self._samplingheight = []
     

"""
        # get all the digital data objects... without extracting the data
        
        dobjList = []
        for pid in self._data['dobj']:
            dobjList.append(binfile(pid))
        if dobjList:
            self.dobjList = dobjList
"""        
            
# --EOF Station Class-----------------------------------------            
# ------------------------------------------------------------
def get(stationId):
    """
    Parameters
    ----------
    stationId : str StationId as you can extract with getIdList. Example 'NOR'
                for Atmosphere Norunda station
    example :  get('NOR')
            
    Returns
    -------
    station : object Returns a station object (if stationId is found)

    """
    query = sparqls. stations_with_pi()
    key, stations = RunSparql(query,'array').run()
    #idx = [i for i, s in enumerate(stations) if stationId in s]
    for stn in stations:
        if stn[0].lower() == stationId.lower():
            return Station(stn)
    return 'station '+ stationId + ' not found'

    
def getIdList():
    """
    Returns a list with Station Id extracted from the Labelling app.
    """
    query = sparqls. stations_with_pi()
    return RunSparql(query,'pandas').run()
    
    
def getList(theme=['AS','ES','OS'], icosclass=['1','2']):
    """
    Query the SPARQL endpoint for stations, create
    an object for each Station and return a list of stations
    which are in the "labeliing" app. By default only stations
    which have been certified (Class 1 & 2) are return.
    Param:      theme (str | [iterable object])
                label (str | [iterable object])
    Example:    getStationList('As')
                getStationList(('As','OS'), '2')
    
    Returns
    -------
    stationList : list, default is all certified stations
    """
    
    defaulttheme=['AS','ES','OS']
    
     # make sure input is in uppercase    
    try:
        
        if isinstance(theme, str):            
            if not theme.upper() in defaulttheme:
                raise Exception('theme')
        else:
           theme = [x.upper() for x in theme]                  
           
    except:
        # looks like input is not a string and/or not an iterable str.
        # comparison failed. Revert to default values, return all certified stations.
        theme=['AS','ES','OS']           
    
    query = sparqls. stations_with_pi()    
    key, stations = RunSparql(query,'array').run()
        
    stationList = []
    for stn in tqdm(stations):
        if stn[2] in theme:
            if stn[3] in icosclass:                
                stationList.append(Station(stn))        
            elif '0' in icosclass and not stn[3] in icosclass :
                stationList.append(Station(stn))        
            
    return stationList
# ------------------------------------------------------------    
if __name__ == "__main__":
    """
    execute only if run as a script
    get a full list from the CarbonPortal SPARQLl endpoint
    and create a list of station objects    
    """
    print("You have chosen to run this as a standalone script")
    print("usually you would try to import a station in your own script")
    print("and then you have the following basic commands [examples]:")
    print("idList = station.getIdList # returns a list of ICOS Station ID's")
    print("norunda = station.get('NOR') # returns a station object for the Atmospheric station of Norunda")
    print("stationList = station.getList(['OS']) # returns a list of station objects for all Ocean ICOS stations.")
    
    myStation = get('nor')    
    
    
    #print(norunda.info())
    
    # getIdList()
    # getStationList()
# ------------------------------------------------------------