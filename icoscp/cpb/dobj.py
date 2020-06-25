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
__version__     = "0.1.1"
__maintainer__  = "ICOS Carbon Portal, elaborated products team"
__email__       = ['info@icos-cp.eu', 'claudio.donofrio@nateko.lu.se']
__status__      = "rc1"
__date__        = "2019-08-09"

import os
import requests
import struct
import pandas as pd

from icoscp.sparql.runsparql import RunSparql
import icoscp.sparql.sparqls as sparqls
from icoscp.cpb import dtype_dict

class Dobj():
    """ Use an ICOS digital object id to query the sparql endpoint
        for infos, and create the "payload" to retrieve the binary data
        the method .getColumns() will return the actual data
    """
    
    def __init__(self, digitalObject = ''):          
        
        self._colSelected = None    # 'none' -> ALL columns are returned
        self._endian = 'big'        # default "big endian conversion 
        self._dtconvert = True      # convert Unixtimstamp to datetime object
        self._info1 = None          # sparql query object           
        self._info2 = None          # sparql query objcect format
        self._info3 = None          # station information for dobj
        self._colSchema = None      # format of columns (read struct bin data)        
        self._dtypeStruct = None    # format of columns (read struct bin data)        
        self._json = None           # holds the "payload" for requests        
        self._server = 'https://data.icos-cp.eu/portal/tabular'
        self._localpath = '/data/dataAppStorage/'        # read data from local file
        self._islocal = None        # status if file is read from local store
                                    # if localpath + dobj is valid                                     
        self._dobjSet = False       # -> see dobj setter
        self._dobjValid = False     # -> see __getPayload()
        
        self.citation = None        # hold the citation string for the object
        
        # this needs to be the last call within init. If dobj is provided
        # __payLoad() is exectued automatically to create json object 
        # for all columns#
        self.dobj = digitalObject   # this sets self._dobj, which is the PID        
        
        
    #-----------
    @property
    def dobj(self):
        return self._dobj
    
    @dobj.setter
    def dobj(self, digitalObject=''):
        if not digitalObject:
            self._dobjSet = False
            return
        else:
            self._dobj = digitalObject
            self._dobjSet = True
            self.__getPayload()
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
            return self._info2['colName']
        return None  
    #-----------
    @property
    def station(self):
        return self._info3.stationName[0]
    #-----------
    @property
    def lat(self):
        return float(self._info3.latitude[0])
    #-----------
    @property
    def lon(self):
        return float(self._info3.longitude[0])
    #-----------
    @property
    def elevation(self):
        return float(self._info3.elevation[0])
    #-----------
    @property
    def info(self):
        if self._dobjValid:
            return [self._info1, self._info2, self._info3]
        return None 
    #-----------

# -------------------------------------------------    
    def get(self):
        """ return data as pandas data frame"""
        return self.getColumns()
    
    def getColumns(self, columns=None):
        # if columns = None, return ALL columns, otherwise, 
        # try to extract only a subset of columns
        if (not columns) & self._dobjValid:
            # return all columns
            return self.__getColumns()
        
        if columns:
            if self.__setColumns(columns):
                # set columns and recompute payload
                self.__getPayload()
        
        if self._dobjValid:
            return self.__getColumns()
        
        return False
    
# -------------------------------------------------    
    def __getPayload(self):
        """ this function sends predefined sparql queries to the cp endpoint
            a single digital object is interrogated to check
            if a binary data representation is available
            if successful _dobjValid is "True"
        """
        if not self._dobjSet:
            return
                
        sparql = RunSparql()
        """
        get information about the digital objcect and if 
        there is a dataset with format specification
        It is possible, that "optional" columns are present.
        -   check if columnNames is empty or not. If not adjust 
            info2 accordingly
        """
        
        sparql.query = sparqls.cpbGetInfo(self.dobj)
        sparql.format = 'pandas'
        sparql.run()
        self._info1 = sparql.data()
        if not len(self._info1):
            self._dobjValid=False              
            return

        # -------------------------------------------------
        # get the information about the underlying format
        # from the previous query -> sparql.data....
        sparql.query = sparqls.cpbGetSchemaDetail(self._info1['objSpec'][0])
        sparql.run()  
        self._info2 = sparql.data()
        
        # the lenght of info2 will be equal to "all" columns...         
        if not len(self._info2):
            self._dobjValid = False
            return False
        
        # ...except if info[1][columnNames] contains a list (optional columns...)               
        if not pd.isnull(self._info1['columnNames'][0]):            
            colList = self._info1['columnNames'][0]
            # remove [] from beginning and end
            colList = colList[1:len(colList)-1]
            # remove all double quotes"
            colList = colList.replace('"', '')
            #create a list
            colList = colList.split(',')
            #remove leading and trailing whitespaces from entries
            colList = [c.strip() for c in colList]
            # remove all "columns" from info2 which are not in colList
            for i, c in enumerate(self._info2['colName']):
                if not c in colList:
                    self._info2 = self._info2.drop(i)   
                  
        # if no specific columns are selected, default to all
        if not self._colSelected:
            self._colSelected = list(range(0,len(self._info2)))

        # -------------------------------------------------
        # create the dataType format, neccesary to interpret the binary 
        # data with python struct library or numpy
        self._colSchema = []        
        for f in self._info2['valFormat']:
            try:
                self._colSchema.append(dtype_dict.mapDataTypesCP(f))  
            except:
                raise Exception('dtype_dict')
                    
        dtypeStruct = []
        for d in self._colSelected:    
            dtypeStruct.append(dtype_dict.structTypes(self._colSchema[d],int(self._info1['nRows'][0])))                    
            
        self._dtypeStruct = dtype_dict.structEndian(self._endian) + ''.join(dtypeStruct)
        
        # assemble the json object needed to return the data
        self._json = {'tableId':self._info1['dobj'].iloc[0].split('/')[-1],
                          'schema':{'columns':self._colSchema,
                                    'size':int(self._info1['nRows'].iloc[0])},
                                    'columnNumbers':self._colSelected,
                                    'subFolder':self._info2['objFormat'].iloc[0].split('/')[-1]
                     }
        
        # get the citation for this object
        sparql.query = sparqls.get_icos_citation(self.dobj)                   
        citation = sparql.run()['cit'][0] 
        if not citation:
            self.citation = 'no citation available ...'
        else:
            self.citation = citation  
        
        self._dobjValid = True
        return
        
# -------------------------------------------------    
    def __getColumns(self):
        """
            check if a local path is set and valid
            otherwise try to download from the cp server
        """ 
        # get the station information for the dobj, 
        sparql = RunSparql()
        sparql.format = 'pandas'
        sparql.query = sparqls.dobjStation(self.dobj)
        sparql.run()  
        self._info3 = sparql.data()        
        
        
        #assemble local file path        
        folder = self._info2['objFormat'].iloc[0].split('/')[-1]        
        fileName = ''.join([self.dobj.split('/')[-1],'.cpb'])
        localfile = os.path.abspath(''.join([self._localpath,folder,'/',fileName]))
        
        if os.path.isfile(localfile): 
            self._islocal = True
            with open(localfile, 'rb') as binData:
                content = binData.read()
            # we need to select ALL columns
            self._colSelected = None             
            self.__getPayload()
            return self.__unpackRawData(content)  
            
        else:
            self._islocal = False
            r = requests.post(self._server, json=self._json, stream=True) 
            try:
                r.raise_for_status()
            except requests.exceptions.HTTPError as e:
                raise Exception(e)

            #track data usage
            self.__portalUse()
            
            return self.__unpackRawData(r.content)                    

    def __unpackRawData(self, rawData):
        # unpack the binary data
        data = struct.unpack_from(self._dtypeStruct, rawData)
        
        # get them into a pandas data frame, column by column
        df = pd.DataFrame()
        rows = int(self._info1['nRows'])  
        
        try:
            for idx,col in enumerate(self._colSelected):                       
                lst = list(data[idx*rows:(idx+1)*rows])
                if(self._colSchema[col] == 'CHAR'):
                    #convert UTF-16 , this is often used in "Flag" columns
                    lst = [chr(i) for i in lst]            
                df[self._info2.iloc[col]['colName']] = lst
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
                    
        return df

    # -------------------------------------------------                       
    def __portalUse(self):
        
        """ private function to track data usage """        
        counter = {'BinaryFileDownload':{
        'params':{
            'objId':self._dobj,
            'columns': self.colNames.tolist(),            
            'library':__name__, 
            'version':__version__}
            }
        }
        server = 'https://cpauth.icos-cp.eu/logs/portaluse'        
        requests.post(server, json=counter)
        
    # -------------------------------------------------                       
    def __setColumns(self, columns=None):
        """ this function sets the columnNumbers to extract data 
            :Param colums (None | List)
            
            1. If columns=None returns all ColumnNumbers
            2. List -> either a list of numbers(indices for columns), columNames
                as strings or a mixture of both.
                Only valid uniqe entries will be returned
                
            Return: Bool (True|False)
                    False if:   _dobjValid is False
                                columns is not a list
                                column could not be found in dobj
                    True if self._colSeleceted contains valid entries and hence
                    the "__getPayload" is valid, such that __getData can be exectuded.            
        """
        if not self._dobjValid:
            return False
        
        if columns is None:
            # with colSelected None, payload returns ALL available columns
            self._colSelected = None            
            return True

        if not isinstance(columns, list):
            try:
                columns = list(columns)
            except: 
                return False
        
        colSelected = []
        
        # we deal everything in uppercase to make it case INsensitive
        colNames = [c.upper() for c in self.colNames.tolist()]
        colIndexRange = range(len(colNames))
        for c in columns:
            #check if list entry is a "name"
            if (isinstance(c,str) and c.upper() in colNames):         
                idx = colNames.index(c.upper())                
            # check if an "index" is provided
            elif (isinstance(c, int) and c in colIndexRange):
                idx = c            
            if (idx not in colSelected):
                colSelected.append(idx)
        
        if not colSelected: # the list is empty..            
            return False
        else:
            self._colSelected = colSelected
            
        return True
