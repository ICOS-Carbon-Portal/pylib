#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Created on Wed April 22 2020
    The Station module is used to explore ICOS stations and the corresponding
    data products. Since you need to know the "station id" to create a station
    object, convenience functions are provided:
    
    Example usage:
        
    from icoscp.station import station
    station.getIdList() -> returns a pandas data frame with all ICOS stations
    myStation = station.get('ID') -> provide an ID to create a station object
    myList = station.getList('AS', '1') ->  returns a list of class 1
                                            Atmospheric stations         
"""

__author__      = ["Claudio D'Onofrio"]
__credits__     = "ICOS Carbon Portal"
__license__     = "GPL-3.0"
__version__     = "0.1.0"
__maintainer__  = "ICOS Carbon Portal, elaborated products team"
__email__       = ['info@icos-cp.eu', 'claudio.donofrio@nateko.lu.se']
__status__      = "rc1"
__date__        = "2019-08-09"

import json
import pandas as pd
from icoscp.sparql.runsparql import RunSparql
from icoscp.sparql import sparqls
from tqdm import tqdm

# ----------------------------------------------
class Station():
    """ Create an ICOS Station object. This class intends to create 
        an instance of station, providing meta data including 
        ID, Name, PI, Lat, Long etc.
        Examples:
        import station
        myList = station.getList(['AS'], 1) 
        myStation = station.get('HTM')
        
        station.info()
        
        # extract single attribute
        station.lat -> returns latitude as float
    """
    
    def __init__(self, attrList=None):
        """
        Initialize your Staion either with NO arguments, or
        provide a full list of arguments in the exact order how the
        attributes are listed 
        [ stationID | stationName | theme | class | type | lat |
         lon | eas | eag | firstname | lastname | email | country ]
      
        """

        # Be aware, that attrList needs to be in the same ORDER as attributes                
        # info
        self._stationId = None          # shortName like HTM or SE-NOR               
        self._name = None               # longName
        self._theme = None              # AS | ES | OS
        self._icosclass = None          # 1 | 2 
        self._siteType = None           # description of site
        
        #locations
        self._lat = None                # latitude
        self._lon = None                # longitude
        self._eas = None                # elevation above sea level
        self._eag = None                # elevation above ground, height of tower
        
        #pi information
        self._firstName = None          # Station PI first name
        self._lastName = None           # Station PI last name
        self._email = None              # Station PI email
        
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
        return self.info('json')
        
    def data(self, level=None):
        """
        return a list of digital objects for the station
        parameter: level [str | int] default None
        provide filter to dataobjects
            1 = raw data
            2 = QAQC data
            3 = elaborated products
        """
        if not isinstance(self._data, pd.DataFrame):
            # _data is not a dataframe but contains a string...
            return self._data

        if level:
            # if level is provided, filter pandas data frame
            return self._data[self._data['datalevel']==str(level)]
        else:
            # return complete pandas data fram
            return self._data
    
    def products(self, fmt='pandas'):
        """
        Parameters
        ----------
        fmt : str,  optional ['pandas', 'dict']
                    Return a pandas dataframe of unique data products for
                    the station. The default is 'pandas'.

        Returns
        -------
        [pandas data frame | dict]
            uniqe list of data products.

        """
        
        if not isinstance(self._products, pd.DataFrame):
            return self._products
        
        if fmt == 'dict':
            return self._products.to_dict()
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
        # summary of information about station
        if 'data' in dictionary:
            del dictionary['data']
            
        if 'products' in dictionary:
            del dictionary['products']
        
        if fmt == 'dict':
            return dictionary
        
        if fmt == 'json':
            return json.dumps(dictionary, indent=4)
                        
        if fmt == 'list':
            return (list(dictionary.keys()), list(dictionary.values()))
        
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
        if isinstance(self._data, pd.DataFrame):
            p = self._data['specLabel'].unique()            
            self._products = pd.DataFrame(p)
        else:
            self._products = 'no data available'

            
    def sh(self, product = None):
        """        
        This function is a short cut to return the getSamplingHeight()        
        for documentation, please refer to .getSamplingHeight()
        """
        return self.getSamplingHeight(product)
    
    def getSamplingHeight(self, product = None):
        """        

        Parameters
        ----------
        product : str,  please provide a valid object specification
                        DESCRIPTION. The default is None.

        Returns
        -------
        a list of unique values for sampling for the specified data product\
        in case of no samplinghights or the product is not found for this
        station, an empty list is returned.       

        """
        # default return value is empty list
        sh = ['']
        if not product:
            return sh
        
        # check if product is availabe for station
        if not product in self._data.values:
            return sh
        
        # if product is available but no sampling height is defined, return
        if not self._data['samplingheight'][self._data.specLabel.str.contains(product)].count():
            return sh
        
        # finaly get all sampling heights and create a unique list
        # count returns zero, of no sampling heights found
        sh = self._data['samplingheight'][self._data.specLabel == product].astype(float)
        sh = sh.unique().tolist()
        sh.sort()        
        return sh
        
        
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
    msg = """
    You have chosen to run this as a standalone script.
    usually you would try to import a station in your own script
    and then you have the following basic commands [examples]:
    
    # return a list of ICOS Station ID's
    idList = station.getIdList 
    
    # return the station object for ID (example > Norunda in Sweden)
    myStation = station.get('NOR') 
    
    # return a list of station objects for all Level 1 Ocean ICOS stations.
    stationList = station.getList(['OS'], '1') 
    """
    print(msg)
    

# ------------------------------------------------------------