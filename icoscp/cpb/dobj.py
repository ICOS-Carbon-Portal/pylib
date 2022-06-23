#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Created on Fri Aug  9 10:40:27 2019
    Use an ICOS digital object id (persistent identification url)
    to load a binary representation of the data object.
"""

__author__      = ["Claudio D'Onofrio"]
__credits__     = "ICOS Carbon Portal"
__license__     = "GPL-3.0"
__version__     = "0.1.7"
__maintainer__  = "ICOS Carbon Portal, elaborated products team"
__email__       = ['info@icos-cp.eu', 'claudio.donofrio@nateko.lu.se']
__status__      = "stable"
__date__        = "2022-05-24"

import os
from warnings import warn
import requests
import struct
import pandas as pd

from icoscp import __version__ as release_version
from icoscp.cpb import dtype
from icoscp.cpb import metadata
import icoscp.const as CPC


class Dobj():
    """ Use an ICOS digital object id to query the sparql endpoint
        for infos, and create the "payload" to retrieve the binary data
        the method .getColumns() will return the actual data
    """

    def __init__(self, digitalObject = None):

        self._dobj = None           # contains the pid
        self._colSelected = None    # 'none' -> ALL columns are returned
        self._endian = 'big'        # default "big endian conversion
        self._dtconvert = True      # convert Unixtimstamp to datetime object
        self._meta = None           # contains metadata about dobj
        self._variables = None      # contains a list of variables, former info2
        self._colSchema = None      # format of columns (read struct bin data)
        self._struct = None         # format of columns (read struct bin data)
        self._json = None           # holds the "payload" for requests
        self._islocal = None        # status if file is read from local store
                                    # if localpath + dobj is valid
        
        self._dobjValid = False     # -> see __set_meta()        
        self._data = pd.DataFrame() # This holds the data pandas dataframe
                                    # persistent in the object.
        self._datapersistent = True # If True (default), data is kept persistent
                                    # in self._data. If False, force to reload
                                    
        # this needs to be the last call within init. If dobj is provided
        # meta data is retrieved and .valid is True
        self.dobj = digitalObject   


    #-----------
    @property
    def dobj(self):        
        return self._dobj

    @dobj.setter
    def dobj(self, digitalObject = None):
        
        if not digitalObject:
            self._dobjValid = False
            return
        else:
            self._dobj = digitalObject
            # set_meta will return false or true
            self._dobjValid = self.__set_meta()
    #-----------    
    @property
    def id(self):
        return self._dobj

    @id.setter
    def id(self, id=None):
        self.__init__(id)       
    #-----------            
    @property
    def previous(self):
        prev = None
        if self.valid and 'previousVersion' in self.meta.keys():
            prev = self.meta['previousVersion']
        return prev
    #-----------
    @property
    def next(self):
        nextversion = None
        if self.valid and 'nextVersion' in self.meta.keys():
            nextversion = self.meta['nextVersion']
        return nextversion
    #-----------
    @property
    def valid(self):
        return self._dobjValid
    #-----------
    @property
    def dateTimeConvert(self):
        return self._dtconvert
    #-----------
    @dateTimeConvert.setter
    def dateTimeConvert(self, convert=True):
        self._dtconvert = convert
    #-----------
    @property
    def colNames(self):
        if self._dobjValid:
            cols = self.variables['name'].tolist()
            return cols
        return None
    #-----------
    @property
    def station(self):
        if self.valid:
            return self.meta['specificInfo']['acquisition']['station']
        
    #-----------
    @property
    def lat(self):
        if self.valid:
            return float(self.meta['specificInfo']['acquisition']['station']['location']['lat'])
    #-----------
    @property
    def lon(self):
        if self.valid:
            return float(self.meta['specificInfo']['acquisition']['station']['location']['lon'])
    #-----------
    @property
    def elevation(self):
        if self.valid:
            return float(self.meta['specificInfo']['acquisition']['station']['location']['alt'])
    @property
    def alt(self):
        if self.valid:
            return self.elevation
    #-----------
    @property
    def data(self):
        return self.get()
    #-----------
    @property
    def info(self):
        if self._dobjValid:
            msg = """
            ICOSCP release >= 0.1.15has changed 
            the format of .info and will return a dictionary containing
            all the metadata. The meta data should now be accessed through
            .meta
            
            This warning will be removed in future icoscp releases. Please
            update your code base accordingly. Documentation is available at
            https://icos-carbon-portal.github.io/pylib/modules/#dobj
            """
            warn(msg, FutureWarning)
            return self.meta
        return None
    #-----------
    @property
    def meta(self, fmt='json'):
        if self._dobjValid:
            return self._meta
        return None
    #-----------
    @property
    def variables(self):
        if self._dobjValid:
            return self._variables
        return None
    #-----------
    @property
    def licence(self):
        """ Returns DICT, with the licencse for this dataobject """
        if self._dobjValid:
            return self._meta['references']['licence']
        return None
    #-----------
    @property
    def citation(self):
        return self.get_citation('plain')
# -------------------------------------------------

    def __str__(self):
        
        if not self.valid:
            return ''
        
        return self.get_citation('plain')


    def get_citation(self, format='plain'):
        '''
        Returns the citation string in different formats.
        By default a plain formated string is returned.
    
        Parameters
        ----------
        format : STR, optional
            possible options are : plain (default), bibtex, ris
            

        Returns
        -------
        STR
    
        '''
        if not self._dobjValid:
            return
        
        citfmt = {
                    'bibtex':  'citationBibTex',
                    'ris':     'citationRis',
                    'plain':   'citationString'
                  }
        
        format = format.lower()        
        if not format in citfmt.keys():
            format = 'plain'
        
        return self.meta['references'][citfmt[format]]

    def getColumns(self, columns=None):
        ''' see help for .get() '''
        return self.get(columns)
    
    def get(self, columns=None):

        '''
        Access to the data. Returns all OR selected columns from the server.
        You can see valid entries with .variables['names']
        If columns are not provided, all columns will be returned
        which is the same as .data OR .get
        
        If the data has already been downloaded and stored in the object
        the existing data frame is returned.

        Parameters
        ----------
        columns : LIST[STR]
            Provide a list of strings (column names)

        Returns
        -------
        PANDAS DATAFRAME            

        '''
        
        if not self._dobjValid:
            return 
        
        #check if the data is alreday present and persistent is true.
        # return the existing dataframe in self._data
        if not self._data.empty and self._datapersistent:
            return self._data

        # if datapersistence is false or the data is missing download..
        # if columns = None, return ALL columns, otherwise,
        # try to extract only a subset of columns
       
        self.__setColumns(columns)
        self.__getPayload()

        return self.__getColumns()


# -------------------------------------------------
    def __set_meta(self):
        ''' retreive meta data for the object
        and set
            self.meta
            self.variables
        '''
        
        # get all the meta data and check..
        self._meta = metadata.get(self.dobj)
        
        if not self._meta:            
            return False
        else:
            # set conveniance excerpts from meta
            self._variables = metadata.variables(self._meta)
            return True
        
        
    def __getPayload(self):

        """ this function sends predefined sparql queries to the cp endpoint
            a single digital object is interrogated to check
            if a binary data representation is available
            if successful _dobjValid is "True"
        """

        # extract the col formats, AFTER sorting the variable names        
        # create the dataType format, neccesary to interpret the binary
        # data with python struct library or numpy
        fmt = self.variables.sort_values('name')['format'].tolist()
        self._colSchema = [dtype.map_type(f) for f in fmt]
        
        
        rows = int(self.meta['specificInfo']['nRows'])
        
        # possibly we don't need all the schema.. only the ones from
        # selected columns, which gives us the structure of the returned binary
        # data
        slicedSchema = [self._colSchema[sel] for sel in self._colSelected]
        struct = [dtype.struct(sel,rows) for sel in slicedSchema]
        
        self._struct = dtype.endian(self._endian) + ''.join(struct)

        # assemble the json object needed to return the data
        self._json = {
                    'tableId':self.dobj.split('/')[-1],
                    'schema':{'columns':self._colSchema,
                    'size':int(self.meta['specificInfo']['nRows'])},
                    'columnNumbers':self._colSelected,
                    'subFolder':self.meta['specification']['format']['uri'].split('/')[-1]
            }

        self._dobjValid = True
        return

# -------------------------------------------------
    def __getColumns(self):
        """
            check if a local path is set and valid
            otherwise try to download from the cp server
        """
        
        #assemble local file path
        folder = self.meta['specification']['format']['uri'].split('/')[-1]
        fileName = ''.join([self.dobj.split('/')[-1],'.cpb'])
        localfile = os.path.abspath(''.join([CPC.LOCALDATA,folder,'/',fileName]))

        if os.path.isfile(localfile):
            self._islocal = True
            with open(localfile, 'rb') as binData:
                content = binData.read()
            # for local files, we always return ALL columns
            self._colSelected = list(range(0,len(self.variables)))
            self.__getPayload()

        else:
            self._islocal = False
            r = requests.post(CPC.DATA, json=self._json, stream=True)
            try:
                r.raise_for_status()
                content = r.content
            except requests.exceptions.HTTPError as e:
                raise Exception(e)

        #track data usage
        self.__portalUse()
        return self.__unpackRawData(content)

    def __unpackRawData(self, rawData):
        # unpack the binary data
        data = struct.unpack_from(self._struct, rawData)

        # get them into a pandas data frame, column by column
        df = pd.DataFrame()        
        columns = self.variables['name'].tolist()
        
        # make sure the list is sorted by variable name, this is how the
        # binary fileformat is built.
        columns.sort()
        
        
        rows = int(self.meta['specificInfo']['nRows'])

        try:
            for idx,col in enumerate(self._colSelected):
                lst = list(data[idx*rows:(idx+1)*rows])
                if self._colSchema[col] == 'CHAR':
                    #convert UTF-16 , this is often used in "Flag" columns
                    lst = [chr(i) for i in lst]
                df[columns[col]] = lst
                
        except Exception as e:
            raise Exception('_unpackRawData')
            print(e)

        """
            The ICOS Carbon Portal provides a TIMESTAMP which is
            a unix timestamp in milliseconds [UTC]
            Convert the "number" to a pandas date/time object
        """
        
        if 'TIMESTAMP' in df.columns and self._dtconvert:
            df['TIMESTAMP'] = pd.to_datetime(df.loc[:,'TIMESTAMP'],unit='ms')
        
        if 'TIMESTAMP_END' in df.columns and self._dtconvert:
            df['TIMESTAMP_END'] = pd.to_datetime(df.loc[:,'TIMESTAMP_END'],unit='ms')

        # there are files with date and time where
        # date is a unixtimestamp
        # time seconds per day
        if 'date' in df.columns and self._dtconvert:
            df['date'] = pd.to_datetime(df.loc[:,'date'],unit='D')

        if 'time' in df.columns and self._dtconvert:
            # convert unix timestamp
            df['time'] = pd.to_datetime(df.loc[:,'time'],unit='s')
            # remove the data, so that only time remains
            df['time'] = pd.to_datetime(df.loc[:,'time'],format='%H:%M').dt.time

        
        # store data in object
        if self._datapersistent:
            self._data = df
        
        return df

    # -------------------------------------------------
    def __portalUse(self):

        """ private function to track data usage """

        counter = {'BinaryFileDownload':{
        'params':{
            'objId':self._dobj,
            'columns': self.colNames,
            'library':__name__,
            'version':release_version,  # from '__init__.py'.
            'internal': str(self._islocal)}
            }
        }
        server = 'https://cpauth.icos-cp.eu/logs/portaluse'
        requests.post(server, json=counter)

    # -------------------------------------------------
    def __setColumns(self, columns=None):
        '''
        this function sets the columnNumbers to extract data
        

        Parameters
        ----------
        columns : LIST[STR], optional
            List of column names to be returned. The default is None, which 
            returns ALL columns available.

        
            1. If columns=None returns all ColumnNumbers
            2. List -> columNames as strings
                Only valid uniqe entries will be returned
                if none of the values are valid, default (ALL)
                will be set.
            
            The columns are stored in self._colSelected
            
        '''
        if not columns: # the list is empty, hence set ALL
            self._colSelected = list(range(0,len(self.variables)))
            return
        
        colSelected = []

        # we deal everything in uppercase to make it case INsensitive
        # extract the list, sort, and reindex. sorting MUST be done, 
        # the binary fileformat is stored in the sorted order of column names
        
        colNames = [c for c in self.variables['name'].tolist()]
        colNames.sort()
        # Only now we can convert to case insensitive uppercase, this needs
        # to come AFTER sorting.. otherwise the order is wrong
        colNames = [c.upper() for c in colNames]
        
        
        for c in columns:
            #check if list entry is a "name"
            if (isinstance(c,str) and c.upper() in colNames):
                idx = colNames.index(c.upper())
        
            if idx not in colSelected:
                colSelected.append(idx)

        colSelected.sort()
        
        if not colSelected: # the list is empty, hence set ALL
            self._colSelected = list(range(0,len(self.variables)))                    
        else:
            self._colSelected = colSelected

        return


    # ------------------------------------------------------------
    def size(self):
        """
        return the real size of object
        https://goshippo.com/blog/measure-real-size-any-python-object/
        """
        import icoscp.cpb.get_size as s
        return s.get(self)


if __name__ == "__main__":
    """
    execute only if run as a script
    """

    msg="""
    You should use this Class within a script.
    Example to create a digital object representation

    from icoscp.cpb.dobj import Dobj

    do = Dobj('https://meta.icos-cp.eu/objects/M6XCOcBsPDTnlUv_6gGNZ2EX')
    data = do.get()
    data.head(3)
    """

    print(msg)
