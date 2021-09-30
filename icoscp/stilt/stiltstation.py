#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Description:      Class that creates objects to set and get the attributes
                      of a station for which STILT model output is available for.
"""

__credits__     = "ICOS Carbon Portal"
__license__     = "GPL-3.0"
__version__     = "0.1.0"
__maintainer__  = "ICOS Carbon Portal, elaborated products team"
__email__       = ['info@icos-cp.eu']
__status__      = "rc1"
__date__        = "2021-04-23"
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
               'alt [m]:': self.alt,
               'country': self.geoinfo['name']
               }
        return json.dumps(out)

    #----------------------------------------------------------------------------------------------------------
    def get_ts(self, start_date, end_date, hours=[], columns=''):
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
            Valid entries are "default", "co2", "co", "rn", "wind", "latlon", "all"            
            default (or empty) will return
            ["isodate","co2.stilt","co2.fuel","co2.bio", "co2.background"]
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

                #Convert numpy array with STILT results to a pandas dataframe:
                df = pd.DataFrame(output[:,:], columns=eval(columns))

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

        #Return dataframe:
        return df
    #----------------------------------------------------------------------------------------------------------

    def get_fp(self, start_date, end_date, hours=[]):
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
        fp = xr.open_mfdataset(fp_files, concat_dim="time",
                               data_vars='minimal', coords='minimal',
                               compat='override', parallel=True)

        #Format time attributes:
        fp.time.attrs["standard_name"] = "time"
        fp.time.attrs["axis"] = "T"

        #Format latitude attributes:
        fp.lat.attrs["axis"] = "Y"
        fp.lat.attrs["standard_name"] = "latitude"

        #Format longitude attributes:
        fp.lon.attrs["axis"] = "X"
        fp.lon.attrs["standard_name"] = "longitude"

        #Return footprint array:
        return fp

    #Function that checks the selection of columns that are to be
    #returned with the STILT timeseries model output:
    def __columns(self, cols):

        # check for a valid entry. If not...return default
        valid = ["default", "co2", "co", "rn", "wind", "latlon", "all"]
        if cols not in valid:
            cols = 'default'

        #Check columns-input:
        if cols=='default':
            columns = ('["isodate","co2.stilt","co2.fuel","co2.bio", "co2.background"]')

        elif cols=='co2':
            columns = ('["isodate","co2.stilt","co2.fuel","co2.bio","co2.fuel.coal",'+
                    '"co2.fuel.oil","co2.fuel.gas","co2.fuel.bio","co2.energy",'+
                    '"co2.transport", "co2.industry","co2.others", "co2.cement",'+
                    '"co2.background"]')

        elif cols=='co':
            columns = ('["isodate", "co.stilt","co.fuel","co.bio","co.fuel.coal",'+
                    '"co.fuel.oil", "co.fuel.gas","co.fuel.bio","co.energy",'+
                    '"co.transport","co.industry", "co.others", "co.cement",'+
                    '"co.background"]')

        elif cols=='rn':
            columns = ('["isodate", "rn", "rn.era", "rn.noah"]')

        elif cols=='wind':
            columns = ('["isodate", "wind.dir", "wind.u", "wind.v"]')

        elif cols=='latlon':
            columns = ('["isodate", "latstart", "lonstart"]')

        elif cols=='all':
            columns = ('["isodate","co2.stilt","co2.fuel","co2.bio","co2.fuel.coal",'+
                    '"co2.fuel.oil","co2.fuel.gas","co2.fuel.bio","co2.energy",'+
                    '"co2.transport", "co2.industry","co2.others", "co2.cement",'+
                    '"co2.background", "co.stilt","co.fuel","co.bio","co.fuel.coal",'+
                    '"co.fuel.oil","co.fuel.gas","co.fuel.bio","co.energy",'+
                    '"co.transport","co.industry","co.others", "co.cement",'+
                    '"co.background","rn", "rn.era","rn.noah","wind.dir",'+
                    '"wind.u","wind.v","latstart","lonstart"]')


        #Return variable:
        return columns

# ----------------------------------- End of STILT Station Class ------------------------------------- #
