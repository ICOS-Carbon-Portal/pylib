import pandas as pd
from stiltstation import __get_stations

# station_info = pd.read_csv("https://stilt.icos-cp.eu/viewer/stationinfo")

# station_info.to_csv("station_info.csv")

STILTPATH = "tests/stiltweb/stations/"
STILTINFO = "tests/stiltweb/station_info.csv"

res = __get_stations(ids=None, progress=False, stilt_path=STILTPATH, stilt_info=STILTINFO)
print("-----------------------------", res)
