#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Description:      Class that creates objects to set and get the attributes
                      of a station for which STILT model output is available for.
"""

__credits__     = "ICOS Carbon Portal"
__license__     = "GPL-3.0"
__version__     = "0.1.4"
__maintainer__  = "ICOS Carbon Portal, elaborated products team"
__email__       = ['info@icos-cp.eu']
__status__      = "release"
__date__        = "2023-01-18"
__lastchange__  = ["Zois Zogopoulos"]
#################################################################################

#Import modules
import os
import numpy as np
import pandas as pd
import requests
import json
import xarray as xr
import icoscp.const as CPC
from icoscp.stilt import timefuncs as tf
from icoscp.sparql import sparqls, runsparql
from icoscp import __version__ as release_version
##############################################################################

class StiltStation():

    """
    Attributes: id:              STILT station ID (e.g. 'HTM150')
                locIdent:        String with latitude-longitude-altitude
                                 of STILT station (e.g. '35.34Nx025.67Ex00150')
                alt:             Station altitude (in meters above ground level)
                lat:             Station latitude
                lon:             Station longitude
                name:            STILT station long name
                icos:            Variable signifying if STILT station is an ICOS station
                years:           List of years for which STILT results are available for
                geoinfo:         Dictionary with nested dictionaries of geographical info

    """

    #Import modules:

    #Function that initializes the attributes of an object:
    def __init__(self, st_dict):

        #Object attributes:
        self._path_fp = CPC.STILTFP     # Path to location where STILT footprints are stored
        self._path_ts = CPC.STILTPATH   # Path to location where STILT time series are stored
        self._url = CPC.STILTTS         # URL to STILT information
        self.info = st_dict             # store the initial dict
        self.valid = False              # if input is dictionary, this will be True
        self.id = None                  # STILT ID for station (e.g. 'HTM150')
        self.lat = None
        self.lon = None
        self.alt = None
        self.locIdent = None
        self.name = None
        self.icos = None
        self.years = None
        self.geoinfo = None
        self.dobjs_list = None               # Store a list of associated dobjs
        self.dobjs_valid = False        # If True, dobjs sparql query already executed        

        self._set(st_dict)

    #------------------------------------------------------------------------

    def _set(self, st_dict):
        #
        if all(item in st_dict.keys() for item in ['id', 'lat', 'lon', 'alt', 'locIdent', 'name', 'icos', 'years', 'geoinfo']):
            self.id = st_dict['id']
            self.lat = st_dict['lat']
            self.lon = st_dict['lon']
            self.alt = st_dict['alt']
            self.locIdent = st_dict['locIdent']
            self.name = st_dict['name']
            self.icos = st_dict['icos']
            self.years = sorted(st_dict['years'])
            self.geoinfo = st_dict['geoinfo']
            self.valid = True


    def __str__(self):
        # by default called when a an 'object' is printed

        out = {'id:': self.id,
               'name:': self.name,
               'lat:': self.lat,
               'lon:': self.lon,
               'alt [m]:': self.alt
               }
        return json.dumps(out)

    #----------------------------------------------------------------------------------------------------------
    def get_ts(self, start_date, end_date, hours=None, columns=None):
        """
        STILT concentration time series for a given time period,
        with optional selection of specific hours and columns.
        Returns time series in a pandas dataframe.

        Parameters
        ----------
        start_date : STR, FLOAT/INT (Unix timestamp), datetime object
            Example: start_date = '2018-01-01'
        end_date : STR, FLOAT/INT (Unix timestamp), datetime object
            Example: end_date = '2018-01-31'
        hours : STR | INT, optional
            If hours is empty or None, ALL Timeslots are returned.
            [0,3,6,9,12,15,18,21]

            Valid results are returned as result with LOWER BOUND values.
            For backwards compatibility, input for str format hh:mm is accepted
            Example:    hours = ["02:00",3,4] will return Timeslots for 0, 3
                        hours = [2,3,4,5,6] will return Timeslots for 0,3 and 6
                        hours = [] return ALL
                        hours = ["10", "10:00", 10] returns timeslot 9

        columns : TYPE, optional
            Valid entries are "default", "co2", "co", "rn", "wind", "latlon", "all".
            'default', empty, or None will return:
            ["isodate","co2.stilt","co2.bio","co2.fuel","co2.cement","co2.background"]
            A full description of the 'columns' can be found at
            https://icos-carbon-portal.github.io/pylib/modules/#stilt

        Returns
        -------
        Pandas Dataframe
        """


        #Convert date-strings to date objs:
        s_date = tf.parse(start_date)
        e_date = tf.parse(end_date)
        hours = tf.get_hours(hours)

        # Check input parameters:
        if e_date < s_date:
            return False

        if not hours:
            return False

        #Create an empty dataframe to store the timeseries:
        df=pd.DataFrame({'A' : []})

        #Add headers:
        headers = {'Content-Type': 'application/json', 'Accept-Charset': 'UTF-8'}

        #Create an empty list, to store the new time range with available STILT model results:
        new_range=[]

        #Create a pandas dataframe containing one column of datetime objects with 3-hour intervals:
        #date_range = pd.date_range(start_date, end_date+dt.timedelta(hours=24), freq='3H')
        date_range = pd.date_range(s_date, e_date, freq='3H')

        #Loop through every Datetime object in the dataframe:
        for zDate in date_range:

            #Check if STILT results exist:
            if os.path.exists(self._path_fp + self.locIdent + '/' +
                              str(zDate.year)+'/'+str(zDate.month).zfill(2)+'/'+
                              str(zDate.year)+'x'+str(zDate.month).zfill(2)+'x'+str(zDate.day).zfill(2)+'x'+
                              str(zDate.hour).zfill(2)+'/'):

                #If STILT-results exist for the current Datetime object, append current Datetime object to list:
                new_range.append(zDate)

        #If the list is not empty:
        if len(new_range) > 0:

            #Assign the new time range to date_range:
            date_range = new_range

            #Get new starting date:
            fromDate = date_range[0].strftime('%Y-%m-%d')

            #Get new ending date:
            toDate = date_range[-1].strftime('%Y-%m-%d')

            #Store the STILT result column names to a variable:
            columns  = self.__columns(columns)

            #Store the STILT result data column names to a variable:
            data = '{"columns": '+columns+', "fromDate": "'+fromDate+'", "toDate": "'+toDate+'", "stationId": "'+self.id+'"}'

            #Send request to get STILT results:
            response = requests.post(self._url, headers=headers, data=data)

            #Check if response is successful:
            if response.status_code != 500:

                #Get response in json-format and read it in to a numpy array:
                output=np.asarray(response.json())

                #Convert numpy array with STILT results to a pandas dataframe
                cols = columns[1:-1].replace('"','').replace(' ','')
                cols = list(cols.split(','))
                df = pd.DataFrame(output[:,:], columns=cols)

                #Replace 'null'-values with numpy NaN-values:
                df = df.replace('null',np.NaN)

                #Set dataframe data type to float:
                df = df.astype(float)

                #Convert the data type of the 'date'-column to Datetime Object:
                df['date'] = pd.to_datetime(df['isodate'], unit='s')

                #Set 'date'-column as index:
                df.set_index(['date'],inplace=True)

                #Filter dataframe values by timeslots:
                hours = [str(h).zfill(2) for h in hours]
                df = df.loc[df.index.strftime('%H').isin(hours)]

            else:

                #Print message:
                print("\033[0;31;1m Error...\nToo big STILT dataset!\nSelect data for a shorter time period.\n\n")

        # track data usage
        self.__portalUse('timeseries')
        #Return dataframe:
        return df
    #----------------------------------------------------------------------------------------------------------

    def get_fp(self, start_date, end_date, hours=None):
        """
        STILT footprints for a given time period,
        with optional selection of specific hours.
        Returns the footprints as xarray (http://xarray.pydata.org/en/stable/).
        with latitude, longitude, time, ppm per (micromol m-2 s-1).
        For more information about the STILT model at ICSO Carbon Portal
        please visit https://icos-carbon-portal.github.io/pylib/modules/#stilt

        Parameters
        ----------
        start_date : STR, FLOAT/INT (Unix timestamp), datetime object
            Example: start_date = '2018-01-01'
        end_date : STR, FLOAT/INT (Unix timestamp), datetime object
            Example: end_date = '2018-01-31'
        hours : STR | INT, optional
            If hours is empty or None, ALL Timeslots are returned.
            [0,3,6,9,12,15,18,21]

            Valid results are returned as result with LOWER BOUND values.
            For backwards compatibility, input for str format hh:mm is accepted
            Example:    hours = ["02:00",3,4] will return Timeslots for 0, 3
                        hours = [2,3,4,5,6] will return Timeslots for 0,3 and 6
                        hours = [] return ALL
                        hours = ["10", "10:00", 10] returns timeslot 9

        Returns
        -------
        Pandas Dataframe
        """

        #Convert date-strings to date objs:
        s_date = tf.parse(start_date)
        e_date = tf.parse(end_date)
        hours = tf.get_hours(hours)

        # Check input parameters:
        if e_date < s_date:
            return False

        if not hours:
            return False

        #Define & initialize footprint variable:
        fp = xr.DataArray()

        #Create a pandas dataframe containing one column of datetime objects with 3-hour intervals:
        date_range = pd.date_range(start_date, end_date, freq='3H')

        #Filter date_range by timeslots:
        date_range = [t for t in date_range if int(t.strftime('%H')) in hours]

        #Loop over all dates and store the corresponding fp filenames in a list:
        fp_files = [(self._path_fp + self.locIdent +'/'+
                     str(dd.year)+'/'+str(dd.month).zfill(2)+'/'+
                     str(dd.year)+'x'+str(dd.month).zfill(2)+'x'+
                     str(dd.day).zfill(2)+'x'+str(dd.hour).zfill(2)+'/foot')
                    for dd in date_range
                    if os.path.isfile(self._path_fp + self.locIdent +'/'+
                                      str(dd.year)+'/'+str(dd.month).zfill(2)+'/'+
                                      str(dd.year)+'x'+str(dd.month).zfill(2)+'x'+
                                      str(dd.day).zfill(2)+'x'+str(dd.hour).zfill(2)+'/foot')]

        #Concatenate xarrays on time axis:
        fp = xr.open_mfdataset(fp_files, combine='by_coords',
                               data_vars='minimal', coords='minimal',
                               compat='override', parallel=True,
                               decode_cf=False)

        # now check for CF compatibility
        fp = xr.decode_cf(fp)

        #Format time attributes:
        fp.time.attrs["standard_name"] = "time"
        fp.time.attrs["axis"] = "T"

        #Format latitude attributes:
        fp.lat.attrs["axis"] = "Y"
        fp.lat.attrs["standard_name"] = "latitude"

        #Format longitude attributes:
        fp.lon.attrs["axis"] = "X"
        fp.lon.attrs["standard_name"] = "longitude"

        # track data usage
        self.__portalUse('footprint')
        #Return footprint array:
        return fp

    def get_raw(self, start_date, end_date, cols):
        """
        Please do use this function with caution. Only very expirienced user
        should load raw data.

        Parameters
        ----------
        start_date : STR
            Start date in form yy-mm-dd
        end_date : STR
            End date in form yy-mm-dd.
        cols : LIST[STR]
            A list of valid column names. You can retrieve the full list
            with _raw_clumn_names.

        Returns
        -------
        columns : Pandas DataFrame
            returns the raw results in form of a pandas data frame
        """
        #Convert date-strings to date objs:
        s_date = tf.parse(start_date).strftime('%Y-%m-%d')
        e_date = tf.parse(end_date).strftime('%Y-%m-%d')

        # validate column names:

        # make sure isodate is in the request
        if 'isodate' not in cols:
            cols.append('isodate')
        columns = list(set(cols).intersection(self._raw_column_names()))
        if len(columns) <= 1:
            return False
        # provide double quotes in the list
        columns = json.dumps(columns)

        # Check input parameters:
        if e_date < s_date:
            return False

        # create http header and payload:

        headers = {'Content-Type': 'application/json', 'Accept-Charset': 'UTF-8'}
        data = '{"columns": '+ str(columns) + ',"fromDate": "'+s_date+'", "toDate": "'+e_date+'", "stationId": "'+self.id+'"}'
        response = requests.post(CPC.STILTRAW, headers=headers, data=data)

        if response.status_code != 500:

            #Get response in json-format and read it in to a numpy array:
            output=np.asarray(response.json())

            #Convert numpy array with STILT results to a pandas dataframe
            cols = columns[1:-1].replace('"','').replace(' ','')
            cols = list(cols.split(','))
            df = pd.DataFrame(output[:,:], columns=cols)

            #Replace 'null'-values with numpy NaN-values:
            df = df.replace('null',np.NaN)

            #Set dataframe data type to float:
            df = df.astype(float)

            #Convert the data type of the 'date'-column to Datetime Object:
            df['date'] = pd.to_datetime(df['isodate'], unit='s')

            #Set 'date'-column as index:
            df.set_index(['date'],inplace=True)


        # track data usage
        self.__portalUse('timeseries')
        #Return dataframe:
        return df

    def get_dobj_list(self):
        """
        If the stiltstation has a corresponding ICOS station
        this function will return a dictionary filled with corresponding
        dataobjects PID's. A sparql query is executed with ICOS Station id
        and the sampling height.

        Returns
        -------
        DICT
            A dictionary with the following keys:
            [dobj,hasNextVersion,spec,fileName,size,submTime,timeStart,timeEnd]

        """
        
        if not self.valid:
            return
        
        if not self.dobjs_valid and self.icos:
            # add corresponding data object with observations
            query = sparqls.dobj_for_samplingheight(\
                            self.icos['stationId'], \
                            self.icos['SamplingHeight'])
            df = runsparql.RunSparql(query, 'pandas').run()
            
            self.dobjs_list = df.to_dict('records')
            self.dobjs_valid = True        
        
        return self.dobjs_list
        
        
    def __columns(self, cols):
        #Function that checks the selection of columns that are to be
        #returned with the STILT timeseries model output:
        if cols:
            # Convert user-specified columns to lower case.
            cols = cols.lower()

        # check for a valid entry. If not...return default
        valid = ["default", "co2", "co", "rn", "wind", "latlon", "all"]
        if cols not in valid:
            cols = 'default'

        #Check columns-input:
        if cols=='default':
            columns = ('["isodate","co2.stilt","co2.bio","co2.fuel","co2.cement",'+
                       '"co2.background"]')

        elif cols=='co2':
            columns = ('["isodate","co2.stilt","co2.bio","co2.fuel","co2.cement",'+
                       '"co2.bio.gee","co2.bio.resp",' +
                       '"co2.fuel.coal","co2.fuel.oil","co2.fuel.gas",'+
                       '"co2.fuel.bio","co2.fuel.waste",'+
                       '"co2.energy","co2.transport","co2.industry",'+
                       '"co2.residential","co2.other_categories",'+
                       '"co2.background"]')

        elif cols=='co':
            columns = ('["isodate", "co.stilt","co.fuel","co.cement",'+
                       '"co.fuel.coal","co.fuel.oil", "co.fuel.gas",'+
                       '"co.fuel.bio","co.fuel.waste",'+
                       '"co.energy","co.transport","co.industry",'+
                       '"co.residential","co.other_categories",'+
                       '"co.background"]')

        elif cols=='rn':
            columns = ('["isodate", "rn", "rn.era", "rn.noah"]')

        elif cols=='wind':
            columns = ('["isodate", "wind.dir", "wind.u", "wind.v"]')

        elif cols=='latlon':
            columns = ('["isodate", "latstart", "lonstart"]')

        elif cols=='all':
            columns = ('["isodate","co2.stilt","co2.bio","co2.fuel","co2.cement",'+
                       '"co2.bio.gee", "co2.bio.resp",' +
                       '"co2.fuel.coal","co2.fuel.oil","co2.fuel.gas",'+
                       '"co2.fuel.bio","co2.fuel.waste",'+
                       '"co2.energy","co2.transport", "co2.industry",'+
                       '"co2.residential","co2.other_categories",'+
                       '"co2.background",'+
                       '"co.stilt","co.fuel","co.cement",'+
                       '"co.fuel.coal","co.fuel.oil","co.fuel.gas",'+
                       '"co.fuel.bio","co.fuel.waste",'+
                       '"co.energy","co.transport","co.industry",'+
                       '"co.residential","co.other_categories",'+
                       '"co.background",'+
                       '"rn", "rn.era","rn.noah",'+
                       '"wind.dir","wind.u","wind.v",'+
                       '"latstart","lonstart"]')

        #Return variable:
        return columns

    def __portalUse(self, dtype):
        """Assembles and posts stilt data usage."""

        if not self.geoinfo:
            country = 'unknown'
        else:
            country = self.geoinfo['name']['common']

        counter = {'StiltDataAccess': {
            'params': {
                'station_id': self.id,
                'station_coordinates': {'latitude': self.lat,
                                        'longitude': self.lon,
                                        'altitude': self.alt},
                'station_country': country,
                'library': __name__,
                'data_type': dtype,
                'version': release_version,  # Grabbed from '__init__.py'.
                'internal': True}}}
        server = 'https://cpauth.icos-cp.eu/logs/portaluse'
        requests.post(server, json=counter)

    def _raw_column_names(self):
        '''
        The STILT model calculates many different variables. We provide
        sensible groups for users, see the documentationfor .get_ts()
        This function returns an exhaustive list for all columns, approximately
        600, which can be used in conjunction get_raw()


        Returns
        -------
        cols : LIST
            All available column names from the raw data timeseries.

        '''
        cols = ['isodate',
                'ident',
                'latstart',
                'lonstart',
                'aglstart',
                'btime',
                'late',
                'lone',
                'agle',
                'zi',
                'grdht',
                'nendinarea',
                'co2.1a4.coal_brownini',
                'co2.1a4.coal_hardini',
                'co2.1a4.coal_peatini',
                'co2.1a4.gas_derini',
                'co2.1a4.gas_natini',
                'co2.1a4.oil_heavyini',
                'co2.1a4.oil_lightini',
                'co2.1a4.solid_wasteini',
                'co2.1a1a.coal_brownini',
                'co2.1a1a.coal_hardini',
                'co2.1a1a.coal_peatini',
                'co2.1a1a.gas_derini',
                'co2.1a1a.gas_natini',
                'co2.1a1a.oil_heavyini',
                'co2.1a1a.oil_lightini',
                'co2.1a1a.solid_wasteini',
                'co2.1a1bcr.coal_brownini',
                'co2.1a1bcr.coal_hardini',
                'co2.1a1bcr.coal_peatini',
                'co2.1a1bcr.gas_derini',
                'co2.1a1bcr.gas_natini',
                'co2.1a1bcr.oil_heavyini',
                'co2.1a1bcr.oil_lightini',
                'co2.1a1bcr.solid_wasteini',
                'co2.1a2+6cd.coal_brownini',
                'co2.1a2+6cd.coal_hardini',
                'co2.1a2+6cd.coal_peatini',
                'co2.1a2+6cd.gas_derini',
                'co2.1a2+6cd.gas_natini',
                'co2.1a2+6cd.oil_heavyini',
                'co2.1a2+6cd.oil_lightini',
                'co2.1a2+6cd.solid_wasteini',
                'co2.1a3b.oil_heavyini',
                'co2.1a3b.oil_lightini',
                'co2.1b2abc.oil_heavyini',
                'co2.1b2abc.oil_lght+hvy+gas_vafini',
                'co2.1b2abc.oil_lightini',
                'co2.1a3ce.oil_heavyini',
                'co2.1a3a+1c1.oil_lightini',
                'co2.1a3d+1c2.oil_heavyini',
                'co2.2a.cementini',
                'co2.2befg+3.cementini',
                'co2.2c.cementini',
                'co2.7a.coal_hardini',
                'co2.1a1a.bio_gasini',
                'co2.1a1a.bio_liquidini',
                'co2.1a1a.bio_solidini',
                'co2.1a1bcr.bio_gasini',
                'co2.1a1bcr.bio_solidini',
                'co2.1a2+6cd.bio_gasini',
                'co2.1a2+6cd.bio_liquidini',
                'co2.1a2+6cd.bio_solidini',
                'co2.1a4.bio_gasini',
                'co2.1a4.bio_liquidini',
                'co2.1a4.bio_solidini',
                'co2.4f.bio_solidini',
                'co2ini',
                'co.1a1a.coal_brownini',
                'co.1a1a.coal_hardini',
                'co.1a1a.coal_peatini',
                'co.1a1a.bio_gasini',
                'co.1a1a.gas_derini',
                'co.1a1a.gas_natini',
                'co.1a1a.bio_liquidini',
                'co.1a1a.oil_heavyini',
                'co.1a1a.oil_lightini',
                'co.1a1a.bio_solidini',
                'co.1a1a.solid_wasteini',
                'co.1a1bcr.coal_brownini',
                'co.1a1bcr.coal_hardini',
                'co.1a1bcr.coal_peatini',
                'co.1a1bcr.bio_gasini',
                'co.1a1bcr.gas_derini',
                'co.1a1bcr.gas_natini',
                'co.1a1bcr.oil_heavyini',
                'co.1a1bcr.oil_lightini',
                'co.1a1bcr.solid_wasteini',
                'co.1a2+6cd.coal_brownini',
                'co.1a2+6cd.coal_hardini',
                'co.1a2+6cd.coal_peatini',
                'co.1a2+6cd.bio_gasini',
                'co.1a2+6cd.gas_derini',
                'co.1a2+6cd.gas_natini',
                'co.1a2+6cd.bio_liquidini',
                'co.1a2+6cd.oil_heavyini',
                'co.1a2+6cd.oil_lightini',
                'co.1a2+6cd.bio_solidini',
                'co.1a2+6cd.solid_wasteini',
                'co.1a3a+1c1.oil_lightini',
                'co.1a3b.oil_heavyini',
                'co.1a3b.oil_lightini',
                'co.1a3ce.oil_heavyini',
                'co.1a3d+1c2.oil_heavyini',
                'co.1a4.bio_gasini',
                'co.1a4.bio_liquidini',
                'co.1a4.bio_solidini',
                'co.1a4.coal_brownini',
                'co.1a4.coal_hardini',
                'co.1a4.coal_peatini',
                'co.1a4.gas_derini',
                'co.1a4.gas_natini',
                'co.1a4.oil_heavyini',
                'co.1a4.oil_lightini',
                'co.1a4.solid_wasteini',
                'co.1b2ac.oil_lightini',
                'co.2a.cementini',
                'co.2befg+3.cementini',
                'co.2c.cementini',
                'co.4f.bio_solidini',
                'co.7a.coal_hardini',
                'coini',
                'rnini',
                'rn_noahini',
                'rn_eraini',
                'coinio',
                'sdco2.1a4.coal_brownini',
                'sdco2.1a4.coal_hardini',
                'sdco2.1a4.coal_peatini',
                'sdco2.1a4.gas_derini',
                'sdco2.1a4.gas_natini',
                'sdco2.1a4.oil_heavyini',
                'sdco2.1a4.oil_lightini',
                'sdco2.1a4.solid_wasteini',
                'sdco2.1a1a.coal_brownini',
                'sdco2.1a1a.coal_hardini',
                'sdco2.1a1a.coal_peatini',
                'sdco2.1a1a.gas_derini',
                'sdco2.1a1a.gas_natini',
                'sdco2.1a1a.oil_heavyini',
                'sdco2.1a1a.oil_lightini',
                'sdco2.1a1a.solid_wasteini',
                'sdco2.1a1bcr.coal_brownini',
                'sdco2.1a1bcr.coal_hardini',
                'sdco2.1a1bcr.coal_peatini',
                'sdco2.1a1bcr.gas_derini',
                'sdco2.1a1bcr.gas_natini',
                'sdco2.1a1bcr.oil_heavyini',
                'sdco2.1a1bcr.oil_lightini',
                'sdco2.1a1bcr.solid_wasteini',
                'sdco2.1a2+6cd.coal_brownini',
                'sdco2.1a2+6cd.coal_hardini',
                'sdco2.1a2+6cd.coal_peatini',
                'sdco2.1a2+6cd.gas_derini',
                'sdco2.1a2+6cd.gas_natini',
                'sdco2.1a2+6cd.oil_heavyini',
                'sdco2.1a2+6cd.oil_lightini',
                'sdco2.1a2+6cd.solid_wasteini',
                'sdco2.1a3b.oil_heavyini',
                'sdco2.1a3b.oil_lightini',
                'sdco2.1b2abc.oil_heavyini',
                'sdco2.1b2abc.oil_lght+hvy+gas_vafini',
                'sdco2.1b2abc.oil_lightini',
                'sdco2.1a3ce.oil_heavyini',
                'sdco2.1a3a+1c1.oil_lightini',
                'sdco2.1a3d+1c2.oil_heavyini',
                'sdco2.2a.cementini',
                'sdco2.2befg+3.cementini',
                'sdco2.2c.cementini',
                'sdco2.7a.coal_hardini',
                'sdco2.1a1a.bio_gasini',
                'sdco2.1a1a.bio_liquidini',
                'sdco2.1a1a.bio_solidini',
                'sdco2.1a1bcr.bio_gasini',
                'sdco2.1a1bcr.bio_solidini',
                'sdco2.1a2+6cd.bio_gasini',
                'sdco2.1a2+6cd.bio_liquidini',
                'sdco2.1a2+6cd.bio_solidini',
                'sdco2.1a4.bio_gasini',
                'sdco2.1a4.bio_liquidini',
                'sdco2.1a4.bio_solidini',
                'sdco2.4f.bio_solidini',
                'sdco2ini',
                'sdco.1a1a.coal_brownini',
                'sdco.1a1a.coal_hardini',
                'sdco.1a1a.coal_peatini',
                'sdco.1a1a.bio_gasini',
                'sdco.1a1a.gas_derini',
                'sdco.1a1a.gas_natini',
                'sdco.1a1a.bio_liquidini',
                'sdco.1a1a.oil_heavyini',
                'sdco.1a1a.oil_lightini',
                'sdco.1a1a.bio_solidini',
                'sdco.1a1a.solid_wasteini',
                'sdco.1a1bcr.coal_brownini',
                'sdco.1a1bcr.coal_hardini',
                'sdco.1a1bcr.coal_peatini',
                'sdco.1a1bcr.bio_gasini',
                'sdco.1a1bcr.gas_derini',
                'sdco.1a1bcr.gas_natini',
                'sdco.1a1bcr.oil_heavyini',
                'sdco.1a1bcr.oil_lightini',
                'sdco.1a1bcr.solid_wasteini',
                'sdco.1a2+6cd.coal_brownini',
                'sdco.1a2+6cd.coal_hardini',
                'sdco.1a2+6cd.coal_peatini',
                'sdco.1a2+6cd.bio_gasini',
                'sdco.1a2+6cd.gas_derini',
                'sdco.1a2+6cd.gas_natini',
                'sdco.1a2+6cd.bio_liquidini',
                'sdco.1a2+6cd.oil_heavyini',
                'sdco.1a2+6cd.oil_lightini',
                'sdco.1a2+6cd.bio_solidini',
                'sdco.1a2+6cd.solid_wasteini',
                'sdco.1a3a+1c1.oil_lightini',
                'sdco.1a3b.oil_heavyini',
                'sdco.1a3b.oil_lightini',
                'sdco.1a3ce.oil_heavyini',
                'sdco.1a3d+1c2.oil_heavyini',
                'sdco.1a4.bio_gasini',
                'sdco.1a4.bio_liquidini',
                'sdco.1a4.bio_solidini',
                'sdco.1a4.coal_brownini',
                'sdco.1a4.coal_hardini',
                'sdco.1a4.coal_peatini',
                'sdco.1a4.gas_derini',
                'sdco.1a4.gas_natini',
                'sdco.1a4.oil_heavyini',
                'sdco.1a4.oil_lightini',
                'sdco.1a4.solid_wasteini',
                'sdco.1b2ac.oil_lightini',
                'sdco.2a.cementini',
                'sdco.2befg+3.cementini',
                'sdco.2c.cementini',
                'sdco.4f.bio_solidini',
                'sdco.7a.coal_hardini',
                'sdcoini',
                'sdrnini',
                'sdrn_noahini',
                'sdrn_eraini',
                'sdcoinio',
                'co2.1a4.coal_brownffm',
                'co2.1a4.coal_hardffm',
                'co2.1a4.coal_peatffm',
                'co2.1a4.gas_derffm',
                'co2.1a4.gas_natffm',
                'co2.1a4.oil_heavyffm',
                'co2.1a4.oil_lightffm',
                'co2.1a4.solid_wasteffm',
                'co2.1a1a.coal_brownffm',
                'co2.1a1a.coal_hardffm',
                'co2.1a1a.coal_peatffm',
                'co2.1a1a.gas_derffm',
                'co2.1a1a.gas_natffm',
                'co2.1a1a.oil_heavyffm',
                'co2.1a1a.oil_lightffm',
                'co2.1a1a.solid_wasteffm',
                'co2.1a1bcr.coal_brownffm',
                'co2.1a1bcr.coal_hardffm',
                'co2.1a1bcr.coal_peatffm',
                'co2.1a1bcr.gas_derffm',
                'co2.1a1bcr.gas_natffm',
                'co2.1a1bcr.oil_heavyffm',
                'co2.1a1bcr.oil_lightffm',
                'co2.1a1bcr.solid_wasteffm',
                'co2.1a2+6cd.coal_brownffm',
                'co2.1a2+6cd.coal_hardffm',
                'co2.1a2+6cd.coal_peatffm',
                'co2.1a2+6cd.gas_derffm',
                'co2.1a2+6cd.gas_natffm',
                'co2.1a2+6cd.oil_heavyffm',
                'co2.1a2+6cd.oil_lightffm',
                'co2.1a2+6cd.solid_wasteffm',
                'co2.1a3b.oil_heavyffm',
                'co2.1a3b.oil_lightffm',
                'co2.1b2abc.oil_heavyffm',
                'co2.1b2abc.oil_lght+hvy+gas_vafffm',
                'co2.1b2abc.oil_lightffm',
                'co2.1a3ce.oil_heavyffm',
                'co2.1a3a+1c1.oil_lightffm',
                'co2.1a3d+1c2.oil_heavyffm',
                'co2.2a.cementffm',
                'co2.2befg+3.cementffm',
                'co2.2c.cementffm',
                'co2.7a.coal_hardffm',
                'co2.1a1a.bio_gasffm',
                'co2.1a1a.bio_liquidffm',
                'co2.1a1a.bio_solidffm',
                'co2.1a1bcr.bio_gasffm',
                'co2.1a1bcr.bio_solidffm',
                'co2.1a2+6cd.bio_gasffm',
                'co2.1a2+6cd.bio_liquidffm',
                'co2.1a2+6cd.bio_solidffm',
                'co2.1a4.bio_gasffm',
                'co2.1a4.bio_liquidffm',
                'co2.1a4.bio_solidffm',
                'co2.4f.bio_solidffm',
                'co2ffm',
                'co.1a1a.coal_brownffm',
                'co.1a1a.coal_hardffm',
                'co.1a1a.coal_peatffm',
                'co.1a1a.bio_gasffm',
                'co.1a1a.gas_derffm',
                'co.1a1a.gas_natffm',
                'co.1a1a.bio_liquidffm',
                'co.1a1a.oil_heavyffm',
                'co.1a1a.oil_lightffm',
                'co.1a1a.bio_solidffm',
                'co.1a1a.solid_wasteffm',
                'co.1a1bcr.coal_brownffm',
                'co.1a1bcr.coal_hardffm',
                'co.1a1bcr.coal_peatffm',
                'co.1a1bcr.bio_gasffm',
                'co.1a1bcr.gas_derffm',
                'co.1a1bcr.gas_natffm',
                'co.1a1bcr.oil_heavyffm',
                'co.1a1bcr.oil_lightffm',
                'co.1a1bcr.solid_wasteffm',
                'co.1a2+6cd.coal_brownffm',
                'co.1a2+6cd.coal_hardffm',
                'co.1a2+6cd.coal_peatffm',
                'co.1a2+6cd.bio_gasffm',
                'co.1a2+6cd.gas_derffm',
                'co.1a2+6cd.gas_natffm',
                'co.1a2+6cd.bio_liquidffm',
                'co.1a2+6cd.oil_heavyffm',
                'co.1a2+6cd.oil_lightffm',
                'co.1a2+6cd.bio_solidffm',
                'co.1a2+6cd.solid_wasteffm',
                'co.1a3a+1c1.oil_lightffm',
                'co.1a3b.oil_heavyffm',
                'co.1a3b.oil_lightffm',
                'co.1a3ce.oil_heavyffm',
                'co.1a3d+1c2.oil_heavyffm',
                'co.1a4.bio_gasffm',
                'co.1a4.bio_liquidffm',
                'co.1a4.bio_solidffm',
                'co.1a4.coal_brownffm',
                'co.1a4.coal_hardffm',
                'co.1a4.coal_peatffm',
                'co.1a4.gas_derffm',
                'co.1a4.gas_natffm',
                'co.1a4.oil_heavyffm',
                'co.1a4.oil_lightffm',
                'co.1a4.solid_wasteffm',
                'co.1b2ac.oil_lightffm',
                'co.2a.cementffm',
                'co.2befg+3.cementffm',
                'co.2c.cementffm',
                'co.4f.bio_solidffm',
                'co.7a.coal_hardffm',
                'coffm',
                'rnffm',
                'rn_noahffm',
                'rn_eraffm',
                'inflevergreen',
                'geeevergreen',
                'respevergreen',
                'infldecid',
                'geedecid',
                'respdecid',
                'inflmixfrst',
                'geemixfrst',
                'respmixfrst',
                'inflshrb',
                'geeshrb',
                'respshrb',
                'inflsavan',
                'geesavan',
                'respsavan',
                'inflcrop',
                'geecrop',
                'respcrop',
                'inflgrass',
                'geegrass',
                'respgrass',
                'inflothers',
                'geeothers',
                'respothers',
                'co2.1a4.coal_brown',
                'co2.1a4.coal_hard',
                'co2.1a4.coal_peat',
                'co2.1a4.gas_der',
                'co2.1a4.gas_nat',
                'co2.1a4.oil_heavy',
                'co2.1a4.oil_light',
                'co2.1a4.solid_waste',
                'co2.1a1a.coal_brown',
                'co2.1a1a.coal_hard',
                'co2.1a1a.coal_peat',
                'co2.1a1a.gas_der',
                'co2.1a1a.gas_nat',
                'co2.1a1a.oil_heavy',
                'co2.1a1a.oil_light',
                'co2.1a1a.solid_waste',
                'co2.1a1bcr.coal_brown',
                'co2.1a1bcr.coal_hard',
                'co2.1a1bcr.coal_peat',
                'co2.1a1bcr.gas_der',
                'co2.1a1bcr.gas_nat',
                'co2.1a1bcr.oil_heavy',
                'co2.1a1bcr.oil_light',
                'co2.1a1bcr.solid_waste',
                'co2.1a2+6cd.coal_brown',
                'co2.1a2+6cd.coal_hard',
                'co2.1a2+6cd.coal_peat',
                'co2.1a2+6cd.gas_der',
                'co2.1a2+6cd.gas_nat',
                'co2.1a2+6cd.oil_heavy',
                'co2.1a2+6cd.oil_light',
                'co2.1a2+6cd.solid_waste',
                'co2.1a3b.oil_heavy',
                'co2.1a3b.oil_light',
                'co2.1b2abc.oil_heavy',
                'co2.1b2abc.oil_lght+hvy+gas_vaf',
                'co2.1b2abc.oil_light',
                'co2.1a3ce.oil_heavy',
                'co2.1a3a+1c1.oil_light',
                'co2.1a3d+1c2.oil_heavy',
                'co2.2a.cement',
                'co2.2befg+3.cement',
                'co2.2c.cement',
                'co2.7a.coal_hard',
                'co2.1a1a.bio_gas',
                'co2.1a1a.bio_liquid',
                'co2.1a1a.bio_solid',
                'co2.1a1bcr.bio_gas',
                'co2.1a1bcr.bio_solid',
                'co2.1a2+6cd.bio_gas',
                'co2.1a2+6cd.bio_liquid',
                'co2.1a2+6cd.bio_solid',
                'co2.1a4.bio_gas',
                'co2.1a4.bio_liquid',
                'co2.1a4.bio_solid',
                'co2.4f.bio_solid',
                'co2',
                'co.1a1a.coal_brown',
                'co.1a1a.coal_hard',
                'co.1a1a.coal_peat',
                'co.1a1a.bio_gas',
                'co.1a1a.gas_der',
                'co.1a1a.gas_nat',
                'co.1a1a.bio_liquid',
                'co.1a1a.oil_heavy',
                'co.1a1a.oil_light',
                'co.1a1a.bio_solid',
                'co.1a1a.solid_waste',
                'co.1a1bcr.coal_brown',
                'co.1a1bcr.coal_hard',
                'co.1a1bcr.coal_peat',
                'co.1a1bcr.bio_gas',
                'co.1a1bcr.gas_der',
                'co.1a1bcr.gas_nat',
                'co.1a1bcr.oil_heavy',
                'co.1a1bcr.oil_light',
                'co.1a1bcr.solid_waste',
                'co.1a2+6cd.coal_brown',
                'co.1a2+6cd.coal_hard',
                'co.1a2+6cd.coal_peat',
                'co.1a2+6cd.bio_gas',
                'co.1a2+6cd.gas_der',
                'co.1a2+6cd.gas_nat',
                'co.1a2+6cd.bio_liquid',
                'co.1a2+6cd.oil_heavy',
                'co.1a2+6cd.oil_light',
                'co.1a2+6cd.bio_solid',
                'co.1a2+6cd.solid_waste',
                'co.1a3a+1c1.oil_light',
                'co.1a3b.oil_heavy',
                'co.1a3b.oil_light',
                'co.1a3ce.oil_heavy',
                'co.1a3d+1c2.oil_heavy',
                'co.1a4.bio_gas',
                'co.1a4.bio_liquid',
                'co.1a4.bio_solid',
                'co.1a4.coal_brown',
                'co.1a4.coal_hard',
                'co.1a4.coal_peat',
                'co.1a4.gas_der',
                'co.1a4.gas_nat',
                'co.1a4.oil_heavy',
                'co.1a4.oil_light',
                'co.1a4.solid_waste',
                'co.1b2ac.oil_light',
                'co.2a.cement',
                'co.2befg+3.cement',
                'co.2c.cement',
                'co.4f.bio_solid',
                'co.7a.coal_hard',
                'co',
                'rn',
                'rn_noah',
                'rn_era',
                'sdco2.1a4.coal_brown',
                'sdco2.1a4.coal_hard',
                'sdco2.1a4.coal_peat',
                'sdco2.1a4.gas_der',
                'sdco2.1a4.gas_nat',
                'sdco2.1a4.oil_heavy',
                'sdco2.1a4.oil_light',
                'sdco2.1a4.solid_waste',
                'sdco2.1a1a.coal_brown',
                'sdco2.1a1a.coal_hard',
                'sdco2.1a1a.coal_peat',
                'sdco2.1a1a.gas_der',
                'sdco2.1a1a.gas_nat',
                'sdco2.1a1a.oil_heavy',
                'sdco2.1a1a.oil_light',
                'sdco2.1a1a.solid_waste',
                'sdco2.1a1bcr.coal_brown',
                'sdco2.1a1bcr.coal_hard',
                'sdco2.1a1bcr.coal_peat',
                'sdco2.1a1bcr.gas_der',
                'sdco2.1a1bcr.gas_nat',
                'sdco2.1a1bcr.oil_heavy',
                'sdco2.1a1bcr.oil_light',
                'sdco2.1a1bcr.solid_waste',
                'sdco2.1a2+6cd.coal_brown',
                'sdco2.1a2+6cd.coal_hard',
                'sdco2.1a2+6cd.coal_peat',
                'sdco2.1a2+6cd.gas_der',
                'sdco2.1a2+6cd.gas_nat',
                'sdco2.1a2+6cd.oil_heavy',
                'sdco2.1a2+6cd.oil_light',
                'sdco2.1a2+6cd.solid_waste',
                'sdco2.1a3b.oil_heavy',
                'sdco2.1a3b.oil_light',
                'sdco2.1b2abc.oil_heavy',
                'sdco2.1b2abc.oil_lght+hvy+gas_vaf',
                'sdco2.1b2abc.oil_light',
                'sdco2.1a3ce.oil_heavy',
                'sdco2.1a3a+1c1.oil_light',
                'sdco2.1a3d+1c2.oil_heavy',
                'sdco2.2a.cement',
                'sdco2.2befg+3.cement',
                'sdco2.2c.cement',
                'sdco2.7a.coal_hard',
                'sdco2.1a1a.bio_gas',
                'sdco2.1a1a.bio_liquid',
                'sdco2.1a1a.bio_solid',
                'sdco2.1a1bcr.bio_gas',
                'sdco2.1a1bcr.bio_solid',
                'sdco2.1a2+6cd.bio_gas',
                'sdco2.1a2+6cd.bio_liquid',
                'sdco2.1a2+6cd.bio_solid',
                'sdco2.1a4.bio_gas',
                'sdco2.1a4.bio_liquid',
                'sdco2.1a4.bio_solid',
                'sdco2.4f.bio_solid',
                'sdco2',
                'sdco.1a1a.coal_brown',
                'sdco.1a1a.coal_hard',
                'sdco.1a1a.coal_peat',
                'sdco.1a1a.bio_gas',
                'sdco.1a1a.gas_der',
                'sdco.1a1a.gas_nat',
                'sdco.1a1a.bio_liquid',
                'sdco.1a1a.oil_heavy',
                'sdco.1a1a.oil_light',
                'sdco.1a1a.bio_solid',
                'sdco.1a1a.solid_waste',
                'sdco.1a1bcr.coal_brown',
                'sdco.1a1bcr.coal_hard',
                'sdco.1a1bcr.coal_peat',
                'sdco.1a1bcr.bio_gas',
                'sdco.1a1bcr.gas_der',
                'sdco.1a1bcr.gas_nat',
                'sdco.1a1bcr.oil_heavy',
                'sdco.1a1bcr.oil_light',
                'sdco.1a1bcr.solid_waste',
                'sdco.1a2+6cd.coal_brown',
                'sdco.1a2+6cd.coal_hard',
                'sdco.1a2+6cd.coal_peat',
                'sdco.1a2+6cd.bio_gas',
                'sdco.1a2+6cd.gas_der',
                'sdco.1a2+6cd.gas_nat',
                'sdco.1a2+6cd.bio_liquid',
                'sdco.1a2+6cd.oil_heavy',
                'sdco.1a2+6cd.oil_light',
                'sdco.1a2+6cd.bio_solid',
                'sdco.1a2+6cd.solid_waste',
                'sdco.1a3a+1c1.oil_light',
                'sdco.1a3b.oil_heavy',
                'sdco.1a3b.oil_light',
                'sdco.1a3ce.oil_heavy',
                'sdco.1a3d+1c2.oil_heavy',
                'sdco.1a4.bio_gas',
                'sdco.1a4.bio_liquid',
                'sdco.1a4.bio_solid',
                'sdco.1a4.coal_brown',
                'sdco.1a4.coal_hard',
                'sdco.1a4.coal_peat',
                'sdco.1a4.gas_der',
                'sdco.1a4.gas_nat',
                'sdco.1a4.oil_heavy',
                'sdco.1a4.oil_light',
                'sdco.1a4.solid_waste',
                'sdco.1b2ac.oil_light',
                'sdco.2a.cement',
                'sdco.2befg+3.cement',
                'sdco.2c.cement',
                'sdco.4f.bio_solid',
                'sdco.7a.coal_hard',
                'sdco',
                'sdrn',
                'sdrn_noah',
                'sdrn_era',
                'ubar',
                'vbar',
                'wbar',
                'wind.dir']
        return cols
# ----------------------------------- End of STILT Station Class ------------------------------------- #
