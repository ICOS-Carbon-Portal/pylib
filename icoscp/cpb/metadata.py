# -*- coding: utf-8 -*-
"""
Created on Tue May 24 11:56:23 2022
@author: Claudio
"""
from warnings import warn
import pandas as pd
import requests as re
import icoscp.pid

__author__      = ["Claudio D'Onofrio"]
__credits__     = "ICOS Carbon Portal"
__license__     = "GPL-3.0"
__version__     = "0.1.7"
__maintainer__  = "ICOS Carbon Portal, elaborated products team"
__email__       = ['info@icos-cp.eu', 'claudio.donofrio@nateko.lu.se']
__status__      = "stable"
__date__        = "2022-05-24"
__update__      = "2023-01-08"

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
    pid = icoscp.pid.resolve(pid)

    urlfmt = {'dict':'/meta.json',
              'json':'/meta.json',
              'ttl':'/meta.ttl',
              'xml':'/meta.xml',
              'iso19115':'/meta.iso.xml'}


    if fmt.lower() not in urlfmt:
        # define default value
        warn('format not valid, revert to default dictionary')
        fmt = 'dict'

    url = pid+urlfmt[fmt]

    meta = re.get(url, timeout=10)

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

    var_df = pd.DataFrame()

    # extract all variables (columns)
    var = meta['specificInfo']['columns']

    # fill the dataframe
    var_df['name'] = [v['label'] for v in var]

    # because unit is not guaranteed, we need to loop
    unit = [None] * len(var)
    for index, _val in enumerate(unit):
        # underscore in front of val removes the pylint warning
        # (_val is never used)
        if 'unit' in var[index]['valueType'].keys():
            unit[index] = var[index]['valueType']['unit']

    var_df['unit'] = unit
    var_df['type']= [v['valueType']['self']['label'] for v in var]
    var_df['format'] = [v['valueFormat'] for v in var]

    return var_df


if __name__ == "__main__":

    MSG  = """
    You should not run this script directly.
    Please import and run the .get function.
    Documentaiton is available at
    https://icos-carbon-portal.github.io/pylib/modules/#dobj

    or with help(metadata)

    Example:
    from icoscp.cpb import metadata as meta
    meta.get('https://meta.icos-cp.eu/objects/Igzec8qneVWBDV1qFrlvaxJI')
    """
    print(MSG)

    a = get('https://meta.icos-cp.eu/objects/Igzec8qneVWBDV1qFrlvaxJI')
    b = variables(a)
