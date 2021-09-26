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
import icoscp.const as CPC
import xarray as xr

from icoscp.stilt import timefuncs as tf
##############################################################################

class StiltStation():

    """
    Attributes: id:              STILT station ID (e.g. 'HTM150')
                siteID:          Station ID as 3-character station code (e.g 'HTM')
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
    def get_ts(self, start_date, end_date, hours=[], columns='default'):
        
        """
        Project:         'ICOS Carbon Portal'
        Created:          Mon Oct 08 10:30:00 2018
        Last Changed:     Fri Apr 23 15:30:00 2021
        Version:          1.1.3
        Author(s):        Ute Karstens, Karolina Pantazatou

        Description:      Function that checks if there are STILT concentration time series
                          available for a given time period, and, if this is the case,
                          returns the available STILT concentration time series in a
                          pandas dataframe.

        Input: 
            columns, STR, "default", "co2", "co", "rn", "wind", "latlon", "all"
            
            default return ["isodate","co2.stilt","co2.fuel","co2.bio", "co2.background"]

        Output:           Pandas Dataframe

                          Columns:
                          1. Time (var_name: "isodate", var_type: date),
                          2. STILT CO2 (var_name: "co2.fuel", var_type: float)
                          3. Biospheric CO2 emissions (var_name: "co2.bio", var_type: float)
                          4. Background CO2 (var_name: "co2.background", var_type: float)

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

