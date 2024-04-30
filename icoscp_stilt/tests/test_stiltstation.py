from typing import Any
import json
import pytest
from src.icoscp_stilt import stiltstation


def read_json(path: str) -> dict[Any, Any]:
    """Read dictionary from json file."""
    with open(file=path, mode='r') as json_handle:
        json_data = json.load(json_handle)
    return json_data


def replace_values(input_dict: dict) -> None:
    """
    The email, firstName, and lastName keys returned from getIdList()
    are random, therefore they are excluded from testing.
    """
    everything_equals = type('omnieq', (), {"__eq__": lambda x, y: True})()

    if 'icos' in input_dict:
        input_dict['icos']['email'] = everything_equals
        input_dict['icos']['firstName'] = everything_equals
        input_dict['icos']['lastName'] = everything_equals


def exclude_geo_info(d: dict) -> dict:
    return {k: d[k] for k in set(list(d.keys())) - set('geoinfo')}


ZSF = read_json('tests/stiltstation-mock-data/station-metadata/ZSF.json')
HHHH = read_json('tests/stiltstation-mock-data/station-metadata/HHHH.json')
MED_1 = read_json('tests/stiltstation-mock-data/station-metadata/MED-1.json')

replace_values(ZSF['ZSF'])

test_data = {
    'ZSF': {
        'full_json': ZSF,
        'geo_info': ZSF['ZSF']['geoinfo'],
        'no_geo_info': exclude_geo_info(ZSF)
    },
    'HHHH': {
        'full_json': HHHH,
        'geo_info': HHHH['HHHH']['geoinfo'],
        'no_geo_info': exclude_geo_info(HHHH)
    },
    'MED-1': {
        'full_json': MED_1,
        'geo_info': MED_1['MED-1']['geoinfo'],
        'no_geo_info': exclude_geo_info(MED_1)
    },
}


@pytest.mark.parametrize('ids, progress, expected', [
    (['ZSF'], False, test_data['ZSF']['full_json']),
    (['HHHH'], False, test_data['HHHH']['full_json']),
    (['XXX123'], False, {})
])
def test_get_stations(ids: list | None, progress: bool,
                      expected: dict[Any, Any]):
    res = stiltstation.__get_stations(ids, progress)
    assert res == expected


@pytest.mark.parametrize('ids, progress, expected', [
    (None, False, 4),
])
def test_get_all_stations(ids: list | None, progress: bool,
                          expected: dict[Any, Any]):
    """Test if all existing mock stations are returned."""
    res = len(stiltstation.__get_stations(ids, progress))
    assert res == expected


@pytest.mark.parametrize('stn_info, expected', [
    (test_data['ZSF']['no_geo_info']['ZSF'], test_data['ZSF']['geo_info']),
    (HHHH['HHHH'], False),
    (test_data['MED-1']['no_geo_info']['MED-1'], test_data['MED-1']['geo_info'])
])
def test_get_geo_info(stn_info: dict[Any, Any],
                      expected: dict[Any, Any] | bool):
    res = stiltstation.get_geo_info(stn_info)
    assert res == expected


@pytest.mark.parametrize('station_id, name, alt, expected', [
    ('ZSF', 'Zugspitze', 730, 'Zugspitze 730m'),
    ('MED-1', 'nan', 200, 'MED-1 200m'),
])
def test_station_name(station_id: str, name: str, alt: int, expected: str):
    res = stiltstation.__station_name(station_id, name, alt)
    assert res == expected
