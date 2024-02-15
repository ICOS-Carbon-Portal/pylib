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
    (['ZUR200'], True, STILTPATH, STILTINFO, {
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
    (['XXX123'], False, STILTPATH, STILTINFO, {})
])
def test_get_stations(ids, progress, stilt_path, stilt_info, expected):
    ''' test different formats of pid. We accept PID, HANDLE/PID, URI '''
    res = __get_stations(ids, progress, stilt_path, stilt_info)
    assert res == expected
