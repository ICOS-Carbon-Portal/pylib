import pytest
from icoscp.stilt.stiltstation import __get_stations

STILTPATH = "tests/stiltweb/stations/"
STILTINFO = "tests/stiltweb/station_info.csv"


@pytest.mark.parametrize('ids, progress, stilt_path, stilt_info, expected', [
    (None, False, STILTPATH, STILTINFO,
     {'ZUR200': {
         'lat': 47.39,
         'lon': 8.54,
         'alt': 200,
         'locIdent': '47.39Nx008.54Ex00200',
         'id': 'ZUR200',
         'country': 'CH',
         'name': 'Zurich 200m',
         'icos': False, 'years': []
        }, 'ZWO200': {
            'lat': 52.52,
            'lon': 6.12,
            'alt': 200,
            'locIdent': '52.52Nx006.12Ex00200',
            'id': 'ZWO200',
            'country': 'NL',
            'name': 'Zwolle 200m',
            'icos': False,
            'years': []
        }, 'ZFS': {
            'lat': 47.42,
            'lon': 10.98,
            'alt': 730,
            'locIdent': '47.42Nx010.98Ex00730',
            'id': 'ZFS',
            'name': 'ZFS 730m',
            'icos': False,
            'years': []}}),
    (['ZUR200'], False, STILTPATH, STILTINFO, {
        'ZUR200': {
            'lat': 47.39,
            'lon': 8.54,
            'alt': 200,
            'locIdent': '47.39Nx008.54Ex00200',
            'id': 'ZUR200',
            'country': 'CH',
            'name': 'Zurich 200m',
            'icos': False, 'years': []
        },
    }),
    (['ZUR200'], False, STILTPATH, STILTINFO, {
        'ZUR200': {
            'lat': 47.39,
            'lon': 8.54,
            'alt': 200,
            'locIdent': '47.39Nx008.54Ex00200',
            'id': 'ZUR200',
            'country': 'CH',
            'name': 'Zurich 200m',
            'icos': False, 'years': []
        },
    }),
    (['ZSF'], False, STILTPATH, STILTINFO, {
    'ZSF': {
        'lat': 10.98,
        'lon': 47.42,
        'alt': 730,
        'locIdent': '47.42Nx010.98Ex00730',
        'id': 'ZSF',
        'country': 'DE',
        'name': 'Zugspitze 00730m',
        },
    }),
    (['XXX123'], False, STILTPATH, STILTINFO, {})
])
def test_get_stations(ids, progress, stilt_path, stilt_info, expected):
    ''' test different formats of pid. We accept PID, HANDLE/PID, URI '''
    from pprint import pprint
    res = __get_stations(ids, progress, stilt_path, stilt_info)
    pprint(res)
    pprint(expected)
    assert res == expected
