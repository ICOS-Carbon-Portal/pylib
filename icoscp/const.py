#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""    
    Define global (to icoscp) constants
    mainly path variables and Url's used throughout the package
    Usage:
    >>> import icoscp.const as CPC
    >>> CPC.CP_META
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

# Metadata-schema concepts from Carbon Portal's ontologies.
CP_META = 'http://meta.icos-cp.eu/ontologies/cpmeta/'
