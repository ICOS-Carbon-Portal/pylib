# -*- coding: utf-8 -*-
"""
Created on Tue May 24 11:56:23 2022
@author: Claudio
"""
from warnings import warn
import pandas as pd
import requests as re
from icoscp import const as CPC

d = 'https://meta.icos-cp.eu/objects/Igzec8qneVWBDV1qFrlvaxJI'

def get(pid, fmt='dict'):
    
    """
    Return meta data for ICOS data object.

    Parameters
    ----------
    pid : STR
        full pid url for a data object from ICOS.
        like 'https://meta.icos-cp.eu/objects/Igzec8qneVWBDV1qFrlvaxJI'
    fmt : STR, optional
        Define the format of the meta data. By default it is 'json', which 
        returns a python dictionary, with custom keys/values from ICOS.
        Valid entries are:
            dict     = ICOS standard meta data (pytyhon dictionary)
            json     = ICOS standard meta data (string)
            ttl      = Turtle file of ICOS standard meta data
            xml      = XML notation for ICOS standard meta data 
            iso19115 = XML format (ISO 19115-3:2016)

    Returns
    -------
    STRING formated to one of the output format described above. If 
    fmt is missing or not valid, by default ICOS json meta data is returned.
    as dictionary.

    """
    # ensure consistent format of pid
    pid = __pid(pid)
    
    # define valid output formats and check
    valid = ['dict','json', 'ttl', 'xml', 'iso19115']
        
    if not fmt.lower() in valid:        
        # define default value
        warn('format not valid, revert to default dictionary')
        fmt = 'dict'
             
    urlfmt = {'dict':'/meta.json',
              'json':'/meta.json',
              'ttl':'/meta.ttl',
              'xml':'/meta.xml',              
              'iso19115':'/meta.iso.xml'}
    url = pid+urlfmt[fmt]
    
    meta = re.get(url)
    
    # if the ressource (pid) is not found, return None
    if meta.status_code == 404:        
        return None
    
    if fmt == 'dict':
        # default, return the metadata as dictionary
        meta = meta.json()
    else:
        meta = meta.text        
        
    return meta

def variables(meta):
    """
    extract all variables from a metadata object
    and return a pandas data frame. Please remember that
    this list contains variables which are 'previewable' at
    https://data.icoscp.eu . These variables are considered the 
    most useful for a quick glance. BUT if you download the 
    data to your computer, you may have many more variables.

    Parameters
    ----------
    meta : DICT
        Expected the dictionary which is returned from .get(PID)

    Returns
    -------
    Pandas Dataframe.        
    """
    
    variables = pd.DataFrame()
    
    # extract all variables (columns)
    var = meta['specificInfo']['columns']
    
    # fill the dataframe
    variables['name'] = [v['label'] for v in var]
    
    # because unit is not guaranteed, we need to loop
    unit = [None] * len(var)    
    for index, val in enumerate(unit):
        if 'unit' in var[index]['valueType'].keys():
            unit[index] = var[index]['valueType']['unit']
    
    variables['unit'] = unit
    variables['type']= [v['valueType']['self']['label'] for v in var]
    variables['format'] = [v['valueFormat'] for v in var]
    
    return variables


def __pid(pid):
       
    """
       Transform the provided pid to a consistent format
       the user may provide the full url or only the pid, with or
       without the handle id.
       
       Return the full url in form:
        https://meta.icos-cp.eu/objects/ + PID
       OR
        https://meta.fieldsites.se/objects/ + PID
        
       If the full url is provided, notthing to do and return the full url
       Otherwise the handle.net API is called to resolve the PID and return
       the full URL. This is valid for ICOS CP with handle prefix 11676
       or FIELDSITES with prefix 11676.1
       If only the unique part of the PID is provided both prefixes are tested
       for validity.
    """
    
    pid_lower = str(pid).lower()
    fullurl = ['meta.icos-cp.eu', 
               'meta.fieldsites.se',
               'hdl.handle.net'
               ]
    if any([e in pid_lower for e in fullurl]):
        # we have to assume that the full URL to the data object is provided
        # hence nothing to do
        return pid
    
    checkpid = pid.split('/')
    
    if len(checkpid) == 2:
        # we assume we got a pid in form of prefix/pid
        url = f"{CPC.HANDLEURL}{pid}"
        kernel = re.get(url).json()
        if kernel['responseCode']:
            return kernel['values'][0]['data']['value']
        else:
            return None
       
    if len(checkpid) == 1:        
        # only the pid itself is provided, we need to check all prefixes
        for prefix in CPC.HDL_PREFIX:
            url = f"{CPC.HANDLEURL}{prefix}/{pid}"
            kernel = re.get(url).json()
            if kernel['responseCode'] == 1:
                return kernel['values'][0]['data']['value']
        
    # It looks like we could not find the PID
    return None        
    
    
if __name__ == "__main__":
    """
    Return meta data for an ICOS digital data object
    """
    msg  = """
    You should not run this script directly.
    Please import and run the .get function. 
    Documentaiton is available at
    https://icos-carbon-portal.github.io/pylib/modules/#dobj 
    
    or with help(metadata)
    
    Example:
    from icoscp.cpb import metadata as meta
    meta.get('https://meta.icos-cp.eu/objects/Igzec8qneVWBDV1qFrlvaxJI')
    """
    #print(msg)
    
    a = get('https://meta.icos-cp.eu/objects/Igzec8qneVWBDV1qFrlvaxJI')
    b = variables(a)

