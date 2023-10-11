# -*- coding: utf-8 -*-
"""
Created on Tue May 24 11:56:23 2022
@author: Claudio
"""
from warnings import warn
import pandas as pd
import requests as re
from icoscp_core.metaclient import MetadataClient, _get_json_meta
from icoscp_core.envri import ICOS_CONFIG
from dataclasses import asdict

d = 'https://meta.icos-cp.eu/objects/Igzec8qneVWBDV1qFrlvaxJI'

def get(pid, fmt='dict') -> dict | str:
    """
    Returns metadata for data objects.

    Uses a persistent identifier and an envri-configuration to fetch
    metadata in a specific format.

    Parameters
    ----------
    pid : str
        The full persistent identifier for a data object, like
        'https://meta.icos-cp.eu/objects/Igzec8qneVWBDV1qFrlvaxJI'.
    fmt : str, optional
        Define the format of the metadata. By default, it is 'json',
        which returns a python dictionary, with custom keys/values from
        ICOS.
        Valid entries are:
            dict = ICOS standard metadata (python dictionary)
            json = ICOS standard metadata (string)
            ttl = Turtle file of ICOS standard metadata
            xml = XML notation for ICOS standard metadata
            iso19115 = XML format (ISO 19115-3:2016)

    Returns
    -------
    meta: dict | str
        By default, this function returns a dictionary. For the rest
        formats (ttl, xml, iso19115) it returns a string.

    Raises
    ------
    e: Exception
        A general-type exception is raised which originates from the
        icoscp_core library, or from a failed get request.

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
    dev_meta, meta = None, None
    try:
        if fmt == 'dict':
            meta_data_client = MetadataClient(envri_conf=ICOS_CONFIG)
            dev_meta = meta_data_client.get_dobj_meta(dobj=url)
        else:
            meta = re.get(url)
    except Exception as e:
        raise e
    else:
        if fmt == 'dict':
            meta = asdict(dev_meta)
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
        'https://meta.icos-cp.eu/objects/ + pid
    """
    pid = str(pid)
    if '/' in pid:
        # this is the case of providing
        # the full url or the handle/pid
        pid = pid.split('/')[-1]
    url = 'https://meta.icos-cp.eu/objects/' + pid
    return url


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

