import os

_in_production: bool = (os.getenv('MODE', 'production') == 'production')

# Path to location where STILT footprints are stored
STILTFP = '/data/stiltweb/slots/'

# online results
STILTTS = 'https://stilt.icos-cp.eu/viewer/stiltresult'

# stiltresults all columns, raw
STILTRAW = 'https://stilt.icos-cp.eu/viewer/stiltrawresult'

STILTINFO = 'https://stilt.icos-cp.eu/viewer/stationinfo' if _in_production \
    else 'tests/stiltstation-mock-data/stiltweb/station_info.csv'

STILTPATH = '/data/stiltweb/stations/' if _in_production \
    else 'tests/stiltstation-mock-data/stiltweb/stations/'
