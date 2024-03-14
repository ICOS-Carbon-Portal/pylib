from typing import Any
import json
import geopandas as gpd
from geopandas import GeoDataFrame
from pprint import pprint
import pytest
from icoscp.stilt import stiltstation  # noqa: E402
# from stiltstation import __get_stations


def read_json(path: str) -> dict[Any, Any]:
    """Read dictionary from json file."""
    with open(file=path, mode='r') as json_handle:
        json_data = json.load(json_handle)
    return json_data

def pop_keys(input_dict: dict) -> None:
    """"""
    [input_dict['icos'].pop(key) for key in ['email', 'firstName', 'lastName']]

ZSF = read_json('tests/ZSF.json')
pop_keys(ZSF)
ZSF_geoinfo = ZSF['geoinfo']
ZSF_no_geoinfo = read_json('tests/ZSF_no_geoinfo.json')
HHHH = read_json('tests/HHHH.json')
MED_1 = read_json('tests/MED-1.json')
MED_1_no_geoinfo = read_json('tests/MED-1_no_geoinfo.json')


@pytest.mark.parametrize('ids, progress, expected', [
    (['ZSF'], False, ZSF),
    (['HHHH'], False, {'HHHH': HHHH}),
    (['XXX123'], False, {})
])
def test_get_stations(ids, progress, expected):
    """Test """
    res = stiltstation.__get_stations(ids, progress)
    if 'icos' in res:
        pop_keys(res)
    from pprint import pprint
    pprint(res)
    print('**************')
    pprint(expected)

    assert res == expected

@pytest.mark.parametrize('ids, progress, expected', [
    (None, False, 4),
])
def test_get_all_stations(ids, progress, expected):
    """"""
    x = stiltstation.__get_stations(ids, progress)
    res = len(x)
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
