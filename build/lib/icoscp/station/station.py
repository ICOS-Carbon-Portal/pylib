#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""    
    The Station module is used to explore ICOS stations and the corresponding
    data products. Since you need to know the "station id" to create a station
    object, convenience functions are provided:
    
    Example usage:
        
    from icoscp.station import station    
    station.getIdList() # returns a pandas data frame with all station Id's'
    myStation = station.get('StationId') # create a single statino object
    myList = station.getList('AS') #  returns a list of Atmospheric stations
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
        stationId, Name, PI, Lat, Lon,  etc.
        Examples:
        import station
        myList = station.getList(['AS']) 
        myStation = station.get('HTM')
        
        station.info()
        
        # extract single attribute
        station.lat -> returns latitude as float
    """
    
    def __init__(self):
        """
        Initialize your Station either with NO arguments, or
        provide a list of arguments in the exact order how the
        attributes are listed 
        [ stationID | stationName | theme | class | type | lat |
         lon | eas | eag | firstname | lastname | email | country ]
      
        """

        # Be aware, that attrList needs to be in the same ORDER as attributes                
        # info
        self._stationId = None      # shortName like HTM or SE-NOR   
        self._valid = False         # if stationId is set and valid, return True            
        self._name = None           # longName
        self._theme = None          # AS | ES | OS
        self._icosclass = None      # 1 | 2 
        self._siteType = None       # description of site
        
        #locations
        self._lat = None            # latitude
        self._lon = None            # longitude
        self._eas = None            # elevation above sea level
        self._eag = None            # elevation above ground, height of tower
        
        #pi information
        self._firstName = None      # Station PI first name
        self._lastName = None       # Station PI last name
        self._email = None          # Station PI email
        
        # other information
        self._country = None
        self._project = None        # list, project affiliation, 
        self._uri = None            # list, links to ressources, landing pages
        
            
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
    def valid(self):
        return self._valid
    
    @valid.setter
    def valid(self, valid):
        self._valid = valid
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
    @property
    def project(self):
        return self._project
    
    @project.setter
    def project(self, project):
        self._project = project
    #-------------------------------------
    @property
    def uri(self):
        return self._uri
    
    @uri.setter
    def uri(self, uri):
        self._uri = uri
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
    
    
    def setStation(self, attrib=None):
        """
        You can set attributes for the station by providing a dictionary        
        Parameters.      
        project & uri must be a list
        lat, lon, eas, eag, must be convertible to float
        everything else is a string.
        
        ----------
        attributeList : dictionary containing attributes
        
        - stationId (shortName)
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
        
        if not isinstance(attrib, dict):            
            return
        
        # minimal sanity check
        checkFloat = ['lat','lon','eag','eas']
        checkList = ['project', 'uri']
                                
        #create 'keys' without the underscore
        keys = [k.strip('_') for k in list(self.__dict__)]        
        for a in attrib:
            a = a.strip('_')
            if a in keys and a in checkFloat:
                try:
                    self.__setattr__('_'+a, float(attrib[a]))
                except:
                    continue
            elif a in keys and a in checkList:
                try:
                    self.__setattr__('_'+a, list(attrib[a]))
                except:
                    continue
            else:
                self.__setattr__('_' + a, attrib[a])
                


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
            
        if 'valid' in dictionary:
            del dictionary['valid']
        
        if fmt == 'dict':
            return dictionary
        
        if fmt == 'json':
            return json.dumps(dictionary, indent=4)
                        
        if fmt == 'list':
            return (list(dictionary.keys()), list(dictionary.values()))
        
        if fmt == 'pandas':            
            return pd.DataFrame(dictionary, index=[0])
        
        if fmt == 'html':
	    
	    #Create and initialize variable to store station info in html table:            
            html_table = '<style>td{padding: 3px;}</style><table>'

            #Loop through all keys of station dictionary:
            for k in dictionary.keys():

                #Check if current dict key holds the the long name of the station and
                #if the key to the URL of the station landing page is included:
                if((k=='name') & ('uri' in dictionary.keys())):
                    
                    #Create table row and add link with URL to station landing page:
                    html_table = html_table+'<tr><td>'+k+'</td><td><b><a href="'+str(dictionary['uri'][0])+'"target="_blank">'+str(dictionary[k])+'</a></b></td></tr>'           
                
                #Skip creating table row for 'url' key:
                elif(k=='uri'):
                    continue
                
                #Add table row with station info for current key:
                else:
                    html_table = html_table+'<tr><td>'+k+'</td><td><b>'+str(dictionary[k])+'</b></td></tr>'
            
            #Add html closing tag for table:
            html_table = html_table +'</table>'
            
            #Return station info as html table:
            return html_table
        
    def _setData(self):
        
        """
        Query the sparql endpoint for data products submitted by this station
        adjust latitude and longitude and store a list of data specifications
        and data objects (PID's)
        """
        
        if not self.stationId:
            return
        """      
        # get the ressource url and adjust lat and lon from data portal
        query = sparqls.stationResource(self.stationId)
        key, val = RunSparql(query, 'array').run()
        if val:            
            self.url = val[0][0]
            self.lat = float(val[0][2])
            self.lon = float(val[0][3])
        """            
        
        # it is possible, that a station id has multiple URI
        # ask for all URI
        query = sparqls.stationData(self.uri,'all')
        data = RunSparql(query, 'pandas').run()
        
        if not data.empty:
            self._data = data            
        else:
             self._data = 'no data available'            
         
         # check if data is available and extract the 'unique' data products        
        if isinstance(self._data, pd.DataFrame):
             p = self._data['specLabel'].unique()            
             self._products = pd.DataFrame(p)
             
             # replace samplingheight=None with empty string
             self._data.samplingheight.replace(to_replace=[None], value="", inplace=True)
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
        a list of unique values for sampling heights for the specified data product
        in case of no sampling hights or the product is not found for this
        station, an empty list is returned.
        A short-cut function is defined .sh() which calls this function.
        
        Parameters
        ----------
        product : str,  digital object specification        

        Returns
        -------
        list, empty if sampling height for product is not found.
        
        """
        # default return empty list
        sh = ['']
        
        # check if product is availabe for station
        if not product in self._data.values:
            return sh
        
        # if product is available but no sampling height is defined, return
        # count returns zero, if no sampling heights found
        if not self._data['samplingheight'][self._data.specLabel.str.match(product)].count():
            return sh
        
        # finally get all sampling heights and create a unique list        
        sh = self._data.samplingheight[self._data.specLabel == product].unique()        
        sh = list(filter(None, sh))
        if not sh:
            return['']
        
        # at this point we have to assume we have an unsorted list of
        # samplingheights as strings. cast to float and sort.
        sh = [float(s) for s in sh]
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
    
    # create the station instance
    myStn = Station()  
    
    query = sparqls.getStations(stationId)    
    stn = RunSparql(query,'pandas').run()
    
    if stn.empty:
        myStn.stationId = stationId
        myStn.valid = False        
        return myStn
    else:
        stn['project'] = stn.apply(lambda x : __project(x['uri']), axis=1)

    # we have found a valid id
    myStn.stationId = stn.id.values[0]
    myStn.valid = True
    
    # it is possible that more than one station has the same id
    # we will give precedence to the icos project
    # but provide a list of URI and projects affiliations
    
    # get lat, lon, eas from icos entry
    if not stn[stn.project.str.upper() == "ICOS"].empty:
        if stn.lat.any():
            myStn.lat = float(stn.lat[stn.project.str.upper() == 'ICOS'])
        if stn.lat.any():
            myStn.lon = float(stn.lon[stn.project.str.upper() == 'ICOS'])
        if stn.elevation.any():
            myStn.eas = float(stn.elevation[stn.project.str.upper() == 'ICOS'])
    else: 
        if stn.lat.any():
            myStn.lat = float(stn.lat.values[0])
        if stn.lon.any():
            myStn.lon = float(stn.lon.values[0])
        if stn.elevation.any():
            myStn.eas = float(stn.elevation.values[0])
        
    
    myStn.name = stn.name.iloc[0]
    myStn.country = stn.country.iloc[0]
    myStn.project = stn.project.tolist()
    myStn.uri = stn.uri.tolist()
        
    
    # if the station belongs to ICOS
    # add information from the labeling app.
    # this is an interim step and should be removed after the full meta data
    # flow from the thematic centres is achieved.        
    
    if 'ICOS' in myStn.project:            
        query = sparqls.stations_with_pi(stationId)
        lstn = RunSparql(query,'pandas').run()
        if not lstn.empty:
            myStn.theme = lstn['stationTheme'].values[0]
            myStn.icosclass = lstn['class'].values[0]
            myStn.icosclass = lstn['class'].values[0]
            myStn.firstName = lstn['firstName'].values[0]
            myStn.lastName = lstn['lastName'].values[0]
            myStn.email = lstn['email'].values[0]
            myStn.siteType = lstn['siteType'].values[0]
            myStn.eag = lstn['eag'].values[0]

    myStn._setData()        
    return myStn

    
def getIdList(project='ICOS', sort='name'):
    """
    Returns a list with all station id's. By default only only ICOS stations
    will be returned. If filter is set to 'all',  all known station id's are retured.
    Please be aware, that the usage of data associated with non-ICOS station
    might be different then the CCBY 4.0 Licence at ICOS.

    Parameters
    ----------
    project : str, optional. The default is 'ICOS'. If you provide the
                set project to "all" for all known stations
                or provide a project name (see getIdList.project)                
                             
    sort : str, optional. The default is 'name'.
    
    Returns
    -------
    Pandas data frame with station id's, name and country.
    """    
    
    project = project.upper()
    
    query = sparqls.getStations()    
    stn = RunSparql(query,'pandas').run()
    stn['project'] = stn.apply(lambda x : __project(x['uri']), axis=1)
    stn['theme'] = stn.apply(lambda x: x['uri'].split('/')[-1].split('_')[0], axis=1)
    
    if not project == 'ALL':
        stn = stn[stn.project == project.upper()]
    
    stn.sort_values(by='name', inplace=True)
    
    return stn
    
def __project(uri):
    """
    internal use, do not call directly. Lambda function
    to apply on dataframe to get a column for 'project'

    Parameters
    ----------
    uri : Carbon Portal resource descriptor
    
    Returns 
    -------
    project : str, from predefined dict

    """
    uri = uri.lower().split('/')[-1].split('_')[0]
    project = {
        'as' : "ICOS",
        'es' : "ICOS",
        'os' : "ICOS", 
        'neon' : 'NEON', 
        'ingos' : 'INGOS' ,   
        'fluxnet' : 'FLUXNET'
        }
    
    if uri in project:
        return project.get(uri)
    else:
        return 'other'
    
def getList(theme=['AS','ES','OS'], ids=None):
    """
    Query the SPARQL endpoint for stations, create an object for each Station
    and return the list of stations.
    By default all (Ocean, Ecosystem, Atmosphere) ICOS stations are returned
    which have been certified (Class 1 & 2). 
    NOTE: if you provide a station list, all other parameters are ignored.
    
    Example:
    # get all ICOS stations 
    getStationList()
    
    # get a list of station objects for ICOS Atmospheric stations
    getStationList('As')

    # get a list for Atmosphere and Ocean stations
    getStationList(['As','OS']) 
    
    # get list of stations with Id's (id's are case sensitive..)
    getStationList(ids=['HTM', 'LMP', SAC])
    
    Parameters
    ----------
    theme : str | [iterable object of strings]) valid entries AS, ES, OS
    
    stationIds : str | [iterable object of strings]) 
    
    Returns
    -------
    stationList : list of station objects
    
    """
    
    stationList = []
    
    # if a list of id's is provided, ignore theme and class.    
    if ids:
        for s in tqdm(ids):
            stationList.append(get(s))
            
        return stationList
    
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
    
    # get station list, by default returns all icos stations
    stations = getIdList()
    # filter by theme
    stations = stations[stations.theme.isin(theme)]
    
    stationList = []
    for s in tqdm(stations.id):
        stationList.append(get(s))
            
    return stationList
# ------------------------------------------------------------    
if __name__ == "__main__":
    """
    execute only if run as a script
    get a full list from the CarbonPortal SPARQL endpoint
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
    
    # return a list of station objects for all Ocean ICOS stations.
    stationList = station.getList(['OS']) 
    """
    print(msg)
    

# ------------------------------------------------------------
