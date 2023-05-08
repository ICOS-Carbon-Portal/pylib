# -*- coding: utf-8 -*-
"""
Created on Tue Jan 25 22:14:49 2022
@author: Claudio
"""


import pytest
from icoscp.cpb.dobj import Dobj
import pandas


pid = 'https://meta.icos-cp.eu/objects/9GVNGXhqvmn7UUsxSWp-zLyR'
dobj = Dobj(pid)


@pytest.mark.parametrize('test_input,expected', [
    ('',False),
    (123, False),
    ('gibberish', False),
    ('9GVNGXhqvmn7UUsxSWp-zLyR', True),
    ('11676/9GVNGXhqvmn7UUsxSWp-zLyR', True),
    ('https://meta.icos-cp.eu/objects/9GVNGXhqvmn7UUsxSWp-zLyR', True)
    ])
def test_dobj(test_input, expected):
    ''' test different formats of pid. We accept PID, HANDLE/PID, URI '''
    do = Dobj(test_input)
    assert do.valid == expected

def test_lat_lon_alt():
    
    assert dobj.lat == 45.7719
    assert dobj.lon == 2.9658
    assert dobj.alt == 1465.0
    assert dobj.elevation == 1465.0

def test_colNames():
    col = ['TIMESTAMP', 'Flag', 'NbPoints', 'ch4', 'Stdev']
    assert dobj.colNames == col

def test_data():
    assert len(dobj.data) == 8806
    
    
def test_return_values():
    assert isinstance(dobj.dobj, str) 
    assert isinstance(dobj.id, str)
    assert isinstance(dobj.previous, str)
    assert isinstance(dobj.next, str)
    assert isinstance(dobj.valid, bool)
    assert isinstance(dobj.dateTimeConvert, bool)
    assert isinstance(dobj.colNames, list)
    assert isinstance(dobj.lat, float)
    assert isinstance(dobj.lon, float)
    assert isinstance(dobj.alt, float)
    assert isinstance(dobj.elevation, float)
    assert isinstance(dobj.station, dict)
    assert isinstance(dobj.data, pandas.DataFrame)
    assert isinstance(dobj.meta, dict)
    assert isinstance(dobj.variables, pandas.DataFrame)
    assert isinstance(dobj.licence, dict)
    assert isinstance(dobj.citation, str)
    assert isinstance(dobj.get(), pandas.DataFrame)
    assert isinstance(dobj.size(), tuple)
    
def test_citation():
    assert isinstance(dobj.get_citation(), str)
    assert isinstance(dobj.get_citation('plain'), str)
    assert isinstance(dobj.get_citation('bibtex'), str)
    assert isinstance(dobj.get_citation('ris'), str)
    assert dobj.citation == dobj.__str__()
    assert dobj.citation == dobj.get_citation()


    
def test_properties():
    assert dobj.previous == 'https://meta.icos-cp.eu/objects/Jn7Cl2eN09XGyxizaeFIe9IQ'
    assert dobj.next == 'https://meta.icos-cp.eu/objects/rHXuyoW3I-JVLZzuNYA6zhQ6'
    assert dobj.id == pid
    
    keys = ['accessUrl', 'coverageGeo', 'fileName', 'hash', \
            'nextVersion', 'parentCollections', 'pid', \
                'previousVersion', 'references', 'size', \
                    'specificInfo', 'specification', 'submission']
    assert list(dobj.meta.keys()) == keys
    assert len(dobj.variables) == 5  
    