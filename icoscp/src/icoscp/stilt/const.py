import os

_in_production: bool = (os.getenv('MODE', 'production') == 'production')

HTTP_TIMEOUT_SEC = 10

# Path to location where STILT footprints are stored
STILTFP = '/data/stiltweb/slots/'

STILT_VIEWER = 'https://stilt.icos-cp.eu/viewer/'
# online results
STILTTS = STILT_VIEWER + 'stiltresult'

# stiltresults all columns, raw
STILTRAW = STILT_VIEWER + 'stiltrawresult'

STILTINFO = (STILT_VIEWER + 'stationinfo') if _in_production \
    else 'tests/stiltstation-mock-data/stiltweb/station_info.csv'

STILTPATH = '/data/stiltweb/stations/' if _in_production \
    else 'tests/stiltstation-mock-data/stiltweb/stations/'

CP_OBSPACK_CO2_SPEC = 'http://meta.icos-cp.eu/resources/cpmeta/ObspackTimeSerieResult'
CP_OBSPACK_CH4_SPEC = 'http://meta.icos-cp.eu/resources/cpmeta/ObspackCH4TimeSeriesResult'
ICOS_STATION_PREFIX = 'http://meta.icos-cp.eu/resources/stations/AS_'

COUNTRIES = {
    "AL": "Albania",
    "AD": "Andorra",
    "AT": "Austria",
    "BY": "Belarus",
    "BE": "Belgium",
    "BA": "Bosnia and Herzegovina",
    "BG": "Bulgaria",
    "HR": "Croatia",
    "CY": "Cyprus",
    "CZ": "Czech Republic",
    "DK": "Denmark",
    "EE": "Estonia",
    "FI": "Finland",
    "FR": "France",
    "DE": "Germany",
    "GR": "Greece",
    "HU": "Hungary",
    "IS": "Iceland",
    "IE": "Ireland",
    "IT": "Italy",
    "LV": "Latvia",
    "LI": "Liechtenstein",
    "LT": "Lithuania",
    "LU": "Luxembourg",
    "MK": "North Macedonia",
    "MT": "Malta",
    "MD": "Moldova",
    "MC": "Monaco",
    "ME": "Montenegro",
    "NL": "Netherlands",
    "NO": "Norway",
    "PL": "Poland",
    "PT": "Portugal",
    "RO": "Romania",
    "RU": "Russia",
    "SM": "San Marino",
    "RS": "Serbia",
    "SK": "Slovakia",
    "SI": "Slovenia",
    "ES": "Spain",
    "SE": "Sweden",
    "CH": "Switzerland",
    "TR": "Turkey",
    "UA": "Ukraine",
    "GB": "United Kingdom",
    "VA": "Vatican City",
    "XZ": "international waters"
}
