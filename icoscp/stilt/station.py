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
import icoscp.stilt.geoinfo as geoinfo
from icoscp.station import station as cpstation

import operator
import xarray as xr
import datetime as dt

from icoscp.stilt import stationfilter
from icoscp.stilt import timefuncs as tf
from icoscp.stilt import checks
#################################################################################

# --- STILT Station Class --- #
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
    def __init__(self):
        
        #Object attributes:
        self._path_fp = CPC.STILTFP    # Path to location where STILT footprints are stored
        self._path_ts = CPC.STILTPATH  # Path to location where STILT time series are stored
        self._url = CPC.STILTINFO      # URL to STILT information 
        self.id = ''                   # STILT ID for station (e.g. 'HTM150')
        self.lat = ''
        self.lon = ''
        self.alt = ''
        self.locIdent = ''
        self.name = ''
        self.icos = False
        self.years = []
        self.geoinfo = {}
        
    #----------------------------------------------------------------------------------------------------------   
    
    #Function that allows the addition of new obj attributes at runtime:
    def newAttr(self, attr):
        
        setattr(self, attr, attr)
    #----------------------------------------------------------------------------------------------------------
    
    def get_info(self, st_dict):
        
        #Check if input is a dictionary:
        if (isinstance(st_dict, dict)):
            
            #Check if ob attributes are included as keys in the input dict:
            if(all(item in st_dict.keys() for item in ['id', 'lat', 'lon', 'alt', 'locIdent', 'name', 'icos', 'years', 'geoinfo'])):
                
                #Update obj attributes:
                self.id = st_dict['id']                  
                self.lat = st_dict['lat'] 
                self.lon = st_dict['lon'] 
                self.alt = st_dict['alt'] 
                self.locIdent = st_dict['locIdent'] 
                self.name = st_dict['name'] 
                self.icos = st_dict['icos'] 
                self.years = sorted(st_dict['years']) 
                self.geoinfo = st_dict['geoinfo'] 
                
                
            else:
                print('Error! Dictionary keys do not match STILT station obj attributes...')
            
        else:
            print('Error! Expected a dictionary with STILT station info as input...')
            
        return self
    #----------------------------------------------------------------------------------------------------------
    
    def _getLocIdent(self):
        
        #Check if locIdent folder exists:
        if(os.path.split(os.readlink(self._path_ts+self.id))[-1]):
            loc_ident = os.path.split(os.readlink(self._path_ts+self.id))[-1]
        
        else:
            loc_ident = None

        #Return value:
        return loc_ident
    #----------------------------------------------------------------------------------------------------------
    
    def _getReceptorHeight(self):
        
        #Check if locIdent folder exists:
        if(os.path.split(os.readlink(self._path_ts+self.id))[-1]):
            loc_ident = os.path.split(os.readlink(self._path_ts+self.id))[-1]
            receptor_height = np.int(loc_ident[-5:])
        
        else:
            receptor_height = None

        #Return value:
        return receptor_height
    #----------------------------------------------------------------------------------------------------------   
    
    def _getLatitude(self):
        
        #Check if locIdent folder exists:
        if(os.path.split(os.readlink(self._path_ts+self.id))[-1]):
            
            #Get location identification string ('56.10Nx013.42Ex00030')
            loc_ident = os.path.split(os.readlink(self._path_ts+self.id))[-1]
            
            #Extract latitude string ('56.10N'):
            lat_str = loc_ident[-20:-14]
            
            #Check if latitude is expressed in South degrees:
            if lat_str[-1:] == 'S':
                latitude = - np.float(lat_str[:-1])
            
            #If latitude is expressed in North degrees
            else:
                latitude = np.float(lat_str[:-1])
            
        else:
            latitude = None

        #Return value:
        return latitude
    #----------------------------------------------------------------------------------------------------------
    
    def _getLongitude(self):
        
        #Check if locIdent folder exists:
        if(os.path.split(os.readlink(self._path_ts+self.id))[-1]):
            
            #Get location identification string ('56.10Nx013.42Ex00030')
            loc_ident = os.path.split(os.readlink(self._path_ts+self.id))[-1]
            
            #Extract longitude string ('56.10N'):
            lon_str = loc_ident[-13:-6]
            
            #Check if longitude is expressed in degrees West:
            if lon_str[-1:] == 'W':
                longitude = - np.float(lon_str[:-1])
            
            #If longitude is expressed in degrees East:
            else:
                longitude = np.float(lon_str[:-1])
            
        else:
            longitude = None

        #Return value:
        return longitude
    #----------------------------------------------------------------------------------------------------------
    
    def _getName(self):
        
        #Read csv to pandas dataframe:
        try:
            df = pd.read_csv(self._url)

        except:
            df = pd.DataFrame()
    
        
        #Check if locIdent folder exists:
        if(df.empty==False):
            
            #Extract long name of STILT station:
            st_name = df['STILT name'].loc[df['STILT id']==self.id].values[0]
            
            
        else:
            st_name = None

        #Return value:
        return st_name    
    #----------------------------------------------------------------------------------------------------------
    
    #Function that checks if STILT station is also an ICOS station
    #and, if so, returns station metadata information:
    def _getIcos(self):
        
        #Get a list of ICOS station IDs (atmosphere):
        icosStations = cpstation.getIdList()
        icosStations = list(icosStations['id'][icosStations.theme=='AS'])
        
        #Get station 3-character code from STILT ID:
        stn = self.id[0:3].upper()
        
        if stn in icosStations:
            icos_info = cpstation.get(stn).info()
        else:
            icos_info = False
        
        return icos_info
    #----------------------------------------------------------------------------------------------------------
    
    def _getGeoinfo(self):
        
        #Get dict with geographic info for all stations:
        geo = geoinfo.get()
        
        #Check if the current STILT ID is included in the dict:
        if self.id in geo.keys():
            g_dict = geo[self.id]
        else:
            g_dict = stationfilter.__country([self.lat,self.lon]) 
            
        return g_dict
    #----------------------------------------------------------------------------------------------------------
    
    def _getYears(self):
        
        years = sorted(os.listdir(CPC.STILTPATH+'/'+self.id))
        
        return years
    #----------------------------------------------------------------------------------------------------------
    
    def get(self, stilt_st_id):
        
        #Check input variable is a string:
        if(not isinstance(stilt_st_id, str)):
            
            raise Exception('Wrong STILT station ID!\nInput variable is not a string...')
        
        #Check if there are STILT results available for the selected station:
        elif(stilt_st_id not in os.listdir(self._path_ts)):
            
            raise Exception('No STILT results available for selected STILT station ID')
        
        #Add string with STILT station ID info to obj attr:
        else:
            self.id = stilt_st_id
            self.locIdent = self._getLocIdent()
            self.alt = self._getReceptorHeight()
            self.lat = self._getLatitude()
            self.lon = self._getLongitude()
            self.name = self._getName()
            self.icos = self._getIcos()
            self.geoinfo = self._getGeoinfo()
            self.years = self._getYears()
        
        return self

    
    #----------------------------------------------------------------------------------------------------------
    def get_ts(self, sdate, edate, hours=['00:00', '03:00', '06:00', '09:00', '12:00', '15:00', '18:00', '21:00'], columns='default'):
    
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



        Output:           Pandas Dataframe

                          Columns:
                          1. Time (var_name: "isodate", var_type: date),
                          2. STILT CO2 (var_name: "co2.fuel", var_type: float)
                          3. Biospheric CO2 emissions (var_name: "co2.bio", var_type: float)
                          4. Background CO2 (var_name: "co2.background", var_type: float)

        """
        
        #Convert date-strings to date objs:
        s_date = tf.str_to_date(sdate)
        e_date = tf.str_to_date(edate)
        
        #Create an empty dataframe to store the timeseries:
        df=pd.DataFrame({'A' : []})
        
        #Check date input parameters:
        if (tf.check_dates(s_date, e_date) & checks.check_stilt_hours(hours) & (len(checks.check_columns(columns))>0)):

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
                #Obs! Check if cols is empty - if so prompt error msg and break, else continue
                columns = (checks.check_columns(columns))

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
                    df = df.loc[df.index.strftime('%H:%M').isin(hours)]

                else:
                    
                    #Print message:
                    print("\033[0;31;1m Error...\nToo big STILT dataset!\nSelect data for a shorter time period.\n\n")

        #Return dataframe:    
        return df
    #----------------------------------------------------------------------------------------------------------
    
    
    def get_fp(self, start_date, end_date, hours=['00:00', '03:00', '06:00', '09:00', '12:00', '15:00', '18:00', '21:00']): 
        
        #Convert date-strings to date objs:
        s_date = tf.str_to_date(start_date)
        e_date = tf.str_to_date(end_date)
        
        #Define & initialize footprint variable:
        fp = xr.DataArray()
        
        #Check date input parameters:
        if (tf.check_dates(s_date, e_date) & checks.check_stilt_hours(hours)):
        
            #Create a pandas dataframe containing one column of datetime objects with 3-hour intervals:
            date_range = pd.date_range(start_date, end_date, freq='3H')
            
            #Filter date_range by timeslots:
            date_range = [t for t in date_range if t.strftime('%H:%M') in hours]

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
    
# ----------------------------------- End of STILT Station Class ------------------------------------- #        

