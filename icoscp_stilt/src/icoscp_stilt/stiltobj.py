#!/usr/bin/env python

"""
    Description:      Class that creates objects to set and get the attributes
                      of a station for which STILT model output is available for.
"""
# Standard library imports.
from pathlib import Path
from typing import Any, List, Optional
import json
import os

# Related third party imports.
from icoscp_core.icos import meta
from icoscp_core.queries.dataobjlist import SamplingHeightFilter
import numpy as np
import pandas as pd
import requests
import xarray as xr

# Local application/library specific imports.
from . import __version__ as release_version
from . import const as c
from . import timefuncs as tf


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

    # Import modules:

    # Function that initializes the attributes of an object:
    def __init__(self, st_dict: dict[str, Any]):

        # Object attributes:
        self._path_fp = c.STILTFP  # Path to location where STILT footprints are stored
        self._path_ts = c.STILTPATH  # Path to location where STILT time series are stored
        self._url = c.STILTTS  # URL to STILT information
        self.info = st_dict  # store the initial dict
        self.valid = False  # if input is dictionary, this will be True
        self.id = None  # STILT ID for station (e.g. 'HTM150')
        self.lat = None
        self.lon = None
        self.alt = None
        self.locIdent = None
        self.name = None
        self.icos: dict[str, Any] | None = None
        self.years = None
        self.geoinfo = None
        self.dobjs_list = None  # Store a list of associated dobjs
        self.dobjs_valid = False  # If True, dobjs sparql query already executed

        self._set(st_dict)

    # ------------------------------------------------------------------------

    def _set(self, st_dict: dict[str, Any]):
        #
        if all(item in st_dict.keys() for item in
               ['id', 'lat', 'lon', 'alt', 'locIdent', 'name', 'icos', 'years',
                'geoinfo']):
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
        # By default, called when an 'object' is printed

        out = {'id:': self.id,
               'name:': self.name,
               'lat:': self.lat,
               'lon:': self.lon,
               'alt [m]:': self.alt
               }
        return json.dumps(out)

    def get_ts(self, start_date, end_date, hours=None,
               columns: Optional[str] = None):
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
            If hours argument is empty or None, ALL Timeslots are
            returned: [0, 3, 6, 9, 12 ,15, 18, 21]
        columns : Optional[str]
            Valid entries are: 'default', 'co2', 'ch4', 'co', 'rn',
            'wind', 'latlon', 'all'.
            Using 'default', empty, or None will return:
            ['isodate', 'co2.stilt', 'co2.bio', 'co2.fuel',
            'co2.cement', 'co2.background']
            A full description of the 'columns' can be found at
            https://icos-carbon-portal.github.io/pylib/icoscp_stilt/modules/#get_tsstart_date-end_date-hoursnone-columns


        Valid results are returned as a result with LOWER-BOUND values.
        For backwards compatibility, input for str format hh:mm is
        accepted.

        Examples
        --------
        hours = ['02:00', 3, 4] will return Timeslots for 0, 3
        hours = [2, 3, 4, 5, 6] will return Timeslots for 0, 3 and 6
        hours = [] return ALL
        hours = ['10', '10:00', 10] returns timeslot 9

        Returns
        -------
        Pandas Dataframe
        """

        # Convert date-strings to date objs:
        s_date = tf.parse(start_date)
        e_date = tf.parse(end_date)
        hours = tf.get_hours(hours)
        # Check input parameters:
        if e_date < s_date:
            return False
        if not hours:
            return False
        # Create an empty dataframe to store the timeseries:
        df = pd.DataFrame({'A': []})
        # Create an empty list, to store the new time range with
        # available STILT model results:
        new_range = []
        # Create a pandas dataframe containing one column of datetime
        # objects with 3-hour intervals:
        date_range = pd.date_range(s_date, e_date, freq='3H')
        # Loop through every Datetime object in the dataframe and
        # generate a list of Datetime objects for the STILT results
        # that exist.
        for zDate in date_range:
            # Path may look like this:
            # /data/stiltweb/slots/51.41Nx006.88Ex00200/2021/01/2021x01x01x00
            if Path(
                    self._path_fp + self.locIdent,
                    str(zDate.year),
                    str(zDate.month).zfill(2),
                    str(zDate.year) + 'x' + str(zDate.month).zfill(2) + 'x' +
                    str(zDate.day).zfill(2) + 'x' + str(zDate.hour).zfill(2)
            ).exists():
                new_range.append(zDate)
        if len(new_range) > 0:
            date_range = new_range
            from_date = date_range[0].strftime('%Y-%m-%d')
            to_date = date_range[-1].strftime('%Y-%m-%d')
            columns = self.__columns(columns)
            http_resp = requests.post(
                url=self._url,
                json={
                    'stationId': self.id,
                    'fromDate': from_date,
                    'toDate': to_date,
                    'columns': columns
                },
                timeout=c.HTTP_TIMEOUT_SEC
            )
            if http_resp.status_code == 200:
                output = np.asarray(http_resp.json())
                # Convert numpy array with STILT results to a pandas dataframe
                df = pd.DataFrame(output[:, :], columns=columns)
                df = df.replace('null', np.NaN)
                df = df.astype(float)
                # Convert 'date' column to a Datetime Object type.
                df['date'] = pd.to_datetime(df['isodate'], unit='s')
                # Set 'date'-column as index:
                df.set_index(['date'], inplace=True)
                # Filter dataframe values by timeslots:
                hours = [str(h).zfill(2) for h in hours]
                df = df.loc[df.index.strftime('%H').isin(hours)]
            else:
                msg = (f'\033[0;31;1m'
                       f'There was an error during the http request. To '
                       f'reproduce it, run:\n'
                       f'import requests\n\n'
                       f'http_resp = requests.post(\n'
                       f"\turl='{self._url}',\n"
                       f'\tjson={{\n'
                       f"\t\t'stationId': '{self.id}',\n"
                       f"\t\t'fromDate': '{from_date}',\n"
                       f"\t\t'toDate': '{to_date}',\n"
                       f"\t\t'columns': {columns}\n"
                       f'\t}},\n'
                       f'\ttimeout={c.HTTP_TIMEOUT_SEC}\n'
                       f')\n'
                       f'print(http_resp.content)')
                print(msg)
        # Track data usage
        self.__portalUse('timeseries')
        return df

    def get_fp(self, start_date, end_date, hours=None):
        """
        STILT footprints for a given time period,
        with optional selection of specific hours.
        Returns the footprints as xarray (http://xarray.pydata.org/en/stable/).
        with latitude, longitude, time, ppm per (micromol m-2 s-1).
        For more information about the STILT model at ICSO Carbon Portal
        please visit https://icos-carbon-portal.github.io/pylib/icoscp_stilt/

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

        # Convert date-strings to date objs:
        s_date = tf.parse(start_date)
        e_date = tf.parse(end_date)
        hours = tf.get_hours(hours)

        # Check input parameters:
        if e_date < s_date:
            return False

        if not hours:
            return False

        # Create a pandas dataframe containing one column of datetime objects with 3-hour intervals:
        date_range = pd.date_range(start_date, end_date, freq='3H')

        # Filter date_range by timeslots:
        date_range = [t for t in date_range if int(t.strftime('%H')) in hours]

        # Loop over all dates and store the corresponding fp filenames in a list:
        fp_files = [(self._path_fp + self.locIdent +'/'+
                     str(dd.year)+'/'+str(dd.month).zfill(2)+'/'+
                     str(dd.year)+'x'+str(dd.month).zfill(2)+'x'+
                     str(dd.day).zfill(2)+'x'+str(dd.hour).zfill(2)+'/foot')
                    for dd in date_range
                    if os.path.isfile(self._path_fp + self.locIdent +'/'+
                                      str(dd.year)+'/'+str(dd.month).zfill(2)+'/'+
                                      str(dd.year)+'x'+str(dd.month).zfill(2)+'x'+
                                      str(dd.day).zfill(2)+'x'+str(dd.hour).zfill(2)+'/foot')]

        # Concatenate xarrays on time axis:
        fp = xr.open_mfdataset(fp_files, combine='by_coords',
                               data_vars='minimal', coords='minimal',
                               compat='override', parallel=True,
                               decode_cf=False)

        # now check for CF compatibility
        fp = xr.decode_cf(fp)

        # Format time attributes:
        fp.time.attrs["standard_name"] = "time"
        fp.time.attrs["axis"] = "T"

        # Format latitude attributes:
        fp.lat.attrs["axis"] = "Y"
        fp.lat.attrs["standard_name"] = "latitude"

        # Format longitude attributes:
        fp.lon.attrs["axis"] = "X"
        fp.lon.attrs["standard_name"] = "longitude"

        # track data usage
        self.__portalUse('footprint')
        # Return footprint array:
        return fp

    def get_raw(self, start_date, end_date, cols):
        """
        Please do use this function with caution. Only very experienced
        user should load raw data.

        Parameters
        ----------
        start_date : STR
            Start date in form yy-mm-dd
        end_date : STR
            End date in form yy-mm-dd.
        cols : LIST[STR]
            A list of valid column names. You can retrieve the full list
            with _raw_column_names.

        Returns
        -------
        columns : Pandas DataFrame
            returns the raw results in form of a pandas data frame
        """
        # Convert date-strings to date objs:
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

        headers = {'Content-Type': 'application/json',
                   'Accept-Charset': 'UTF-8'}
        data = '{"columns": ' + str(
            columns) + ',"fromDate": "' + s_date + '", "toDate": "' + e_date + '", "stationId": "' + self.id + '"}'
        response = requests.post(c.STILTRAW, headers=headers, data=data)

        if response.status_code != 500:
            # Get response in json-format and read it in to a numpy array:
            output = np.asarray(response.json())

            # Convert numpy array with STILT results to a pandas dataframe
            cols = columns[1:-1].replace('"', '').replace(' ', '')
            cols = list(cols.split(','))
            df = pd.DataFrame(output[:, :], columns=cols)

            # Replace 'null'-values with numpy NaN-values:
            df = df.replace('null', np.NaN)

            # Set dataframe data type to float:
            df = df.astype(float)

            # Convert the data type of the 'date'-column to Datetime Object:
            if 'isodate' in df.columns:
                df['isodate'] = pd.to_datetime(df['isodate'], unit='s')

                # Set 'date'-column as index:
                df.set_index(['date'], inplace=True)

        # track data usage
        self.__portalUse('timeseries')
        # Return dataframe:
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
            [dobj,spec,fileName,size,submTime,timeStart,timeEnd]

        """

        if not self.valid:
            return

        if not self.dobjs_valid and self.icos:
            # add corresponding data object with observations
            self.dobjs_list = [{
                'dobj': dobj.uri,
                'spec': dobj.datatype_uri,
                'fileName': dobj.filename,
                'size': dobj.size_bytes,
                'submTime': dobj.submission_time,
                'timeStart': dobj.time_start,
                'timeEnd': dobj.time_end
            } for dobj in meta.list_data_objects(
                datatype=[c.CP_OBSPACK_CO2_SPEC, c.CP_OBSPACK_CH4_SPEC],
                station=c.ICOS_STATION_PREFIX + self.icos['stationId'],
                filters=[SamplingHeightFilter("=", float(self.icos['SamplingHeight']))]
            )]
            self.dobjs_valid = True
        return self.dobjs_list

    def __columns(self, columns: Optional[str] = None) -> Optional[List]:
        # Function that checks the selection of columns that are to be
        # returned with the STILT timeseries model output:
        columns = columns.lower() if columns else None
        valid = ['default', 'co2', 'ch4', 'co', 'rn', 'wind', 'latlon', 'all']
        columns = 'default' if columns not in valid else columns

        # Check columns-input:
        if columns == 'default':
            columns = ['isodate', 'co2.stilt', 'co2.bio', 'co2.fuel',
                       'co2.cement', 'co2.non_fuel', 'co2.background']

        elif columns == 'co2':
            columns = ['isodate', 'co2.stilt', 'co2.bio', 'co2.fuel',
                       'co2.cement', 'co2.non_fuel', 'co2.bio.gee',
                       'co2.bio.resp', 'co2.fuel.coal', 'co2.fuel.oil',
                       'co2.fuel.gas', 'co2.fuel.bio', 'co2.fuel.waste',
                       'co2.energy', 'co2.transport', 'co2.industry',
                       'co2.residential', 'co2.other_categories',
                       'co2.background']

        elif columns == 'co':
            columns = ['isodate', 'co.stilt', 'co.fuel', 'co.cement',
                       'co.non_fuel', 'co.fuel.coal', 'co.fuel.oil',
                       'co.fuel.gas', 'co.fuel.bio', 'co.fuel.waste',
                       'co.energy', 'co.transport', 'co.industry',
                       'co.residential', 'co.other_categories',
                       'co.background']

        elif columns == 'ch4':
            columns = ['isodate', 'ch4.stilt', 'ch4.anthropogenic',
                       'ch4.natural', 'ch4.agriculture', 'ch4.waste',
                       'ch4.energy', 'ch4.other_categories', 'ch4.wetlands',
                       'ch4.soil_uptake', 'ch4.wildfire', 'ch4.other_natural',
                       'ch4.background']

        elif columns == 'rn':
            columns = ['isodate', 'rn', 'rn.era', 'rn.noah']

        elif columns == 'wind':
            columns = ['isodate', 'wind.dir', 'wind.u', 'wind.v']

        elif columns == 'latlon':
            columns = ['isodate', 'latstart', 'lonstart']

        elif columns == 'all':
            columns = ['isodate', 'co2.stilt', 'co2.bio', 'co2.fuel',
                       'co2.cement', 'co2.non_fuel', 'co2.bio.gee',
                       'co2.bio.resp', 'co2.fuel.coal', 'co2.fuel.oil',
                       'co2.fuel.gas', 'co2.fuel.bio', 'co2.fuel.waste',
                       'co2.energy', 'co2.transport', 'co2.industry',
                       'co2.residential', 'co2.other_categories',
                       'co2.background', 'co.stilt', 'co.fuel', 'co.cement',
                       'co.non_fuel', 'isodate', 'ch4.stilt',
                       'ch4.anthropogenic', 'ch4.natural', 'ch4.agriculture',
                       'ch4.waste', 'ch4.energy', 'ch4.other_categories',
                       'ch4.wetlands', 'ch4.soil_uptake', 'ch4.wildfire',
                       'ch4.other_natural', 'ch4.background', 'co.fuel.coal',
                       'co.fuel.oil', 'co.fuel.gas', 'co.fuel.bio',
                       'co.fuel.waste', 'co.energy', 'co.transport',
                       'co.industry', 'co.residential', 'co.other_categories',
                       'co.background', 'rn', 'rn.era', 'rn.noah', 'wind.dir',
                       'wind.u', 'wind.v', 'latstart', 'lonstart']
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
                'co2.2befg+3.othersini',
                'co2.2c.othersini',
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
                'co.2befg+3.othersini',
                'co.2c.othersini',
                'co.4f.bio_solidini',
                'co.7a.coal_hardini',
                'coini',
                'ch4.1a3a+1c1.oil_lightini',
                'ch4.1a3d+1c2.oil_heavyini',
                'ch4.4a.othersini',
                'ch4.4b.othersini',
                'ch4.4c.othersini',
                'ch4.6b.othersini',
                'ch4.7a.coal_hardini',
                'ch4.1a1a.coal_brownini',
                'ch4.1a1a.coal_hardini',
                'ch4.1a1a.coal_peatini',
                'ch4.1a1a.bio_gasini',
                'ch4.1a1a.gas_derini',
                'ch4.1a1a.gas_natini',
                'ch4.1a1a.bio_liquidini',
                'ch4.1a1a.oil_heavyini',
                'ch4.1a1a.oil_lightini',
                'ch4.1a1a.bio_solidini',
                'ch4.1a1a.solid_wasteini',
                'ch4.1a1bcr.coal_brownini',
                'ch4.1a1bcr.coal_hardini',
                'ch4.1a1bcr.coal_peatini',
                'ch4.1a1bcr.bio_gasini',
                'ch4.1a1bcr.gas_derini',
                'ch4.1a1bcr.gas_natini',
                'ch4.1a1bcr.oil_heavyini',
                'ch4.1a1bcr.oil_lightini',
                'ch4.1a1bcr.bio_solidini',
                'ch4.1a1bcr.solid_wasteini',
                'ch4.1a2+6cd.coal_brownini',
                'ch4.1a2+6cd.coal_hardini',
                'ch4.1a2+6cd.coal_peatini',
                'ch4.1a2+6cd.bio_gasini',
                'ch4.1a2+6cd.gas_derini',
                'ch4.1a2+6cd.gas_natini',
                'ch4.1a2+6cd.bio_liquidini',
                'ch4.1a2+6cd.oil_heavyini',
                'ch4.1a2+6cd.oil_lightini',
                'ch4.1a2+6cd.bio_solidini',
                'ch4.1a2+6cd.solid_wasteini',
                'ch4.1a3b.gas_natini',
                'ch4.1a3b.oil_heavyini',
                'ch4.1a3b.oil_lightini',
                'ch4.1a3ce.oil_heavyini',
                'ch4.1a4.bio_gasini',
                'ch4.1a4.bio_liquidini',
                'ch4.1a4.bio_solidini',
                'ch4.1a4.coal_brownini',
                'ch4.1a4.coal_hardini',
                'ch4.1a4.coal_peatini',
                'ch4.1a4.solid_wasteini',
                'ch4.1a4.gas_derini',
                'ch4.1a4.gas_natini',
                'ch4.1a4.oil_heavyini',
                'ch4.1a4.oil_lightini',
                'ch4.1b1.coal_brownini',
                'ch4.1b1.coal_hardini',
                'ch4.1b1.coal_peatini',
                'ch4.1b2ac.oil_heavyini',
                'ch4.1b2ac.oil_lightini',
                'ch4.1b2ac.gas_natini',
                'ch4.1b2b.gas_natini',
                'ch4.2befg+3.othersini',
                'ch4.2c.othersini',
                'ch4.4f.bio_solidini',
                'ch4.6a.othersini',
                'ch4ini',
                'rnini',
                'rn_noahini',
                'rn_eraini',
                'rn_era5mini',
                'rn_noah2mini',
                'ch4wetini',
                'ch4soilini',
                'ch4uptakeini',
                'ch4peatini',
                'ch4geoini',
                'ch4fireini',
                'ch4oceanini',
                'ch4lakesini',
                'coinio',
                'sdcoinio',
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
                'co2.2befg+3.others',
                'co2.2c.others',
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
                'co.2befg+3.others',
                'co.2c.others',
                'co.4f.bio_solid',
                'co.7a.coal_hard',
                'co',
                'ch4.1a3a+1c1.oil_light',
                'ch4.1a3d+1c2.oil_heavy',
                'ch4.4a.others',
                'ch4.4b.others',
                'ch4.4c.others',
                'ch4.6b.others',
                'ch4.7a.coal_hard',
                'ch4.1a1a.coal_brown',
                'ch4.1a1a.coal_hard',
                'ch4.1a1a.coal_peat',
                'ch4.1a1a.bio_gas',
                'ch4.1a1a.gas_der',
                'ch4.1a1a.gas_nat',
                'ch4.1a1a.bio_liquid',
                'ch4.1a1a.oil_heavy',
                'ch4.1a1a.oil_light',
                'ch4.1a1a.bio_solid',
                'ch4.1a1a.solid_waste',
                'ch4.1a1bcr.coal_brown',
                'ch4.1a1bcr.coal_hard',
                'ch4.1a1bcr.coal_peat',
                'ch4.1a1bcr.bio_gas',
                'ch4.1a1bcr.gas_der',
                'ch4.1a1bcr.gas_nat',
                'ch4.1a1bcr.oil_heavy',
                'ch4.1a1bcr.oil_light',
                'ch4.1a1bcr.bio_solid',
                'ch4.1a1bcr.solid_waste',
                'ch4.1a2+6cd.coal_brown',
                'ch4.1a2+6cd.coal_hard',
                'ch4.1a2+6cd.coal_peat',
                'ch4.1a2+6cd.bio_gas',
                'ch4.1a2+6cd.gas_der',
                'ch4.1a2+6cd.gas_nat',
                'ch4.1a2+6cd.bio_liquid',
                'ch4.1a2+6cd.oil_heavy',
                'ch4.1a2+6cd.oil_light',
                'ch4.1a2+6cd.bio_solid',
                'ch4.1a2+6cd.solid_waste',
                'ch4.1a3b.gas_nat',
                'ch4.1a3b.oil_heavy',
                'ch4.1a3b.oil_light',
                'ch4.1a3ce.oil_heavy',
                'ch4.1a4.bio_gas',
                'ch4.1a4.bio_liquid',
                'ch4.1a4.bio_solid',
                'ch4.1a4.coal_brown',
                'ch4.1a4.coal_hard',
                'ch4.1a4.coal_peat',
                'ch4.1a4.solid_waste',
                'ch4.1a4.gas_der',
                'ch4.1a4.gas_nat',
                'ch4.1a4.oil_heavy',
                'ch4.1a4.oil_light',
                'ch4.1b1.coal_brown',
                'ch4.1b1.coal_hard',
                'ch4.1b1.coal_peat',
                'ch4.1b2ac.oil_heavy',
                'ch4.1b2ac.oil_light',
                'ch4.1b2ac.gas_nat',
                'ch4.1b2b.gas_nat',
                'ch4.2befg+3.others',
                'ch4.2c.others',
                'ch4.4f.bio_solid',
                'ch4.6a.others',
                'ch4',
                'rn',
                'rn_noah',
                'rn_era',
                'rn_era5m',
                'rn_noah2m',
                'ch4wet',
                'ch4soil',
                'ch4uptake',
                'ch4peat',
                'ch4geo',
                'ch4fire',
                'ch4ocean',
                'ch4lakes',
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
                'sdco2.2befg+3.others',
                'sdco2.2c.others',
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
                'sdco.2befg+3.others',
                'sdco.2c.others',
                'sdco.4f.bio_solid',
                'sdco.7a.coal_hard',
                'sdco',
                'sdch4.1a3a+1c1.oil_light',
                'sdch4.1a3d+1c2.oil_heavy',
                'sdch4.4a.others',
                'sdch4.4b.others',
                'sdch4.4c.others',
                'sdch4.6b.others',
                'sdch4.7a.coal_hard',
                'sdch4.1a1a.coal_brown',
                'sdch4.1a1a.coal_hard',
                'sdch4.1a1a.coal_peat',
                'sdch4.1a1a.bio_gas',
                'sdch4.1a1a.gas_der',
                'sdch4.1a1a.gas_nat',
                'sdch4.1a1a.bio_liquid',
                'sdch4.1a1a.oil_heavy',
                'sdch4.1a1a.oil_light',
                'sdch4.1a1a.bio_solid',
                'sdch4.1a1a.solid_waste',
                'sdch4.1a1bcr.coal_brown',
                'sdch4.1a1bcr.coal_hard',
                'sdch4.1a1bcr.coal_peat',
                'sdch4.1a1bcr.bio_gas',
                'sdch4.1a1bcr.gas_der',
                'sdch4.1a1bcr.gas_nat',
                'sdch4.1a1bcr.oil_heavy',
                'sdch4.1a1bcr.oil_light',
                'sdch4.1a1bcr.bio_solid',
                'sdch4.1a1bcr.solid_waste',
                'sdch4.1a2+6cd.coal_brown',
                'sdch4.1a2+6cd.coal_hard',
                'sdch4.1a2+6cd.coal_peat',
                'sdch4.1a2+6cd.bio_gas',
                'sdch4.1a2+6cd.gas_der',
                'sdch4.1a2+6cd.gas_nat',
                'sdch4.1a2+6cd.bio_liquid',
                'sdch4.1a2+6cd.oil_heavy',
                'sdch4.1a2+6cd.oil_light',
                'sdch4.1a2+6cd.bio_solid',
                'sdch4.1a2+6cd.solid_waste',
                'sdch4.1a3b.gas_nat',
                'sdch4.1a3b.oil_heavy',
                'sdch4.1a3b.oil_light',
                'sdch4.1a3ce.oil_heavy',
                'sdch4.1a4.bio_gas',
                'sdch4.1a4.bio_liquid',
                'sdch4.1a4.bio_solid',
                'sdch4.1a4.coal_brown',
                'sdch4.1a4.coal_hard',
                'sdch4.1a4.coal_peat',
                'sdch4.1a4.solid_waste',
                'sdch4.1a4.gas_der',
                'sdch4.1a4.gas_nat',
                'sdch4.1a4.oil_heavy',
                'sdch4.1a4.oil_light',
                'sdch4.1b1.coal_brown',
                'sdch4.1b1.coal_hard',
                'sdch4.1b1.coal_peat',
                'sdch4.1b2ac.oil_heavy',
                'sdch4.1b2ac.oil_light',
                'sdch4.1b2ac.gas_nat',
                'sdch4.1b2b.gas_nat',
                'sdch4.2befg+3.others',
                'sdch4.2c.others',
                'sdch4.4f.bio_solid',
                'sdch4.6a.others',
                'sdch4',
                'sdrn',
                'sdrn_noah',
                'sdrn_era',
                'sdrn_era5m',
                'sdrn_noah2m',
                'sdch4wet',
                'sdch4soil',
                'sdch4uptake',
                'sdch4peat',
                'sdch4geo',
                'sdch4fire',
                'sdch4ocean',
                'sdch4lakes',
                'ubar',
                'vbar',
                'wbar',
                'wind.dir']
        return cols
# ----------------------------------- End of STILT Station Class ------------------------------------- #
