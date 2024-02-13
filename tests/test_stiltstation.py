import pytest
from icoscp.stilt.stiltstation import __get_stations

STILTPATH = "tests/stiltweb/stations/"
STILTINFO = "tests/stiltweb/station_info.csv"


@pytest.mark.parametrize('ids, progress, stilt_path, stilt_info, expected', [
    (None, False, STILTPATH, STILTINFO, {})
])
def test_get_stations(ids, progress, stilt_path, stilt_info, expected):
    ''' test different formats of pid. We accept PID, HANDLE/PID, URI '''
    res = __get_stations(ids, progress, stilt_path, stilt_info)
    print("-----------------------------", res)
    assert res == expected
