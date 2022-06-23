#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""    
    Define global (to icoscp) constants
    mainly path variables and Url's used throught the package
    usage: import icoscp.const as CPC
    CPC.ST_PATH
    
"""


# -------------------------------------------------------------
# Dobj
# read ICOS data through https calls
DATA        = 'https://data.icos-cp.eu/portal/tabular'
# read data from local file
LOCALDATA   = '/data/dataAppStorage/'

 # -------------------------------------------------------------
# Stilt specific
#local path to stiltstations if running on jupyter server
STILTPATH = '/data/stiltweb/stations/'

# Path to location where STILT footprints are stored
STILTFP = '/data/stiltweb/slots/'

# provide STILT station info from backend
STILTINFO = 'https://stilt.icos-cp.eu/viewer/stationinfo'

# online results
STILTTS = 'https://stilt.icos-cp.eu/viewer/stiltresult'

# stiltresults all columns, raw
STILTRAW = 'https://stilt.icos-cp.eu/viewer/stiltrawresult'