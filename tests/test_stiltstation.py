import json
import geopandas as gpd
from geopandas import GeoDataFrame
from pprint import pprint
import pytest
from icoscp.stilt import stiltstation  # noqa: E402
# from stiltstation import __get_stations

with open(file='tests/ZSF.json', mode='r') as json_handle:
    ZSF = json.load(json_handle)
    ZSF_geoinfo = ZSF['geoinfo']
with open(file='tests/ZSF_no_geoinfo.json', mode='r') as json_handle:
    ZSF_no_geoinfo = json.load(json_handle)
with open(file='tests/HHHH.json', mode='r') as json_handle:
    HHHH = json.load(json_handle)
with open(file='tests/MED-1.json', mode='r') as json_handle:
    MED_1 = json.load(json_handle)
with open(file='tests/MED-1_no_geoinfo.json', mode='r') as json_handle:
    MED_1_no_geoinfo = json.load(json_handle)

@pytest.mark.parametrize('ids, progress, expected', [
    # (None, False, {'ZUR200': {
    #      'lat': 47.39,
    #      'lon': 8.54,
    #      'alt': 200,
    #      'locIdent': '47.39Nx008.54Ex00200',
    #      'id': 'ZUR200',
    #      'country': 'CH',
    #      'name': 'Zurich 200m',
    #      'icos': False, 'years': []
    #     }, 'ZWO200': {
    #         'lat': 52.52,
    #         'lon': 6.12,
    #         'alt': 200,
    #         'locIdent': '52.52Nx006.12Ex00200',
    #         'id': 'ZWO200',
    #         'country': 'NL',
    #         'name': 'Zwolle 200m',
    #         'icos': False,
    #         'years': []
    #     }, 'ZFS': {
    #         'lat': 47.42,
    #         'lon': 10.98,
    #         'alt': 730,
    #         'locIdent': '47.42Nx010.98Ex00730',
    #         'id': 'ZFS',
    #         'name': 'ZFS 730m',
    #         'icos': False,
    #         'years': []}}),
    # (['ZUR200'], False, {
    #     'ZUR200': {
    #         'lat': 47.39,
    #         'lon': 8.54,
    #         'alt': 200,
    #         'locIdent': '47.39Nx008.54Ex00200',
    #         'id': 'ZUR200',
    #         'country': 'CH',
    #         'name': 'Zurich 200m',
    #         'icos': False, 'years': []
    #     },
    # }),
    # (['ZUR200'], False, {
    #     'ZUR200': {
    #         'lat': 47.39,
    #         'lon': 8.54,
    #         'alt': 200,
    #         'locIdent': '47.39Nx008.54Ex00200',
    #         'id': 'ZUR200',
    #         'country': 'CH',
    #         'name': 'Zurich 200m',
    #         'icos': False, 'years': []
    #     },
    # }),
    (['ZSF'], False, {'ZSF': ZSF}),
    # (['HHHH'], False, {'HHHH': HHHH})
    (['XXX123'], False, {})
])
def test_get_stations(ids, progress, expected):
    ''' test different formats of pid. We accept PID, HANDLE/PID, URI '''
    from pprint import pprint
    res = stiltstation.__get_stations(ids, progress)
    set1 = set(res.items())
    set2 = set(expected.items())
    
    pprint(set1 ^ set2)
    # pprint(expected)
    assert res == expected


# @pytest.mark.parametrize('stn_info, expected', [
#     (ZSF_no_geoinfo, ZSF_geoinfo),
#     (HHHH, False),
#     (MED_1_no_geoinfo, MED_1)
# ])

# def test_get_geo_info(stn_info, expected):
#     res = stiltstation.get_geo_info(stn_info)
#     pprint(res)
#     print("-----------------------------------------------------")
#     pprint(expected)
#     assert res == expected
