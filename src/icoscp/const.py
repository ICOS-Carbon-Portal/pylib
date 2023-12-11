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
# No authentication required. This way of accessing data will be
# disabled in future releases.
ANONYMOUS_DATA = 'https://data.icos-cp.eu/portal/tabular'
# Authentication required.
SECURED_DATA = 'https://data.icos-cp.eu/cpb'
# Carbon portal authentication end-point.
CP_AUTH = 'https://cpauth.icos-cp.eu/'


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

# World's country shape file from natural earth.
COUNTRY_SHAPE = "/data/project/cartopy/shapefiles/natural_earth/cultural/10m_admin_0_countries.shp"

# Documentation
DOC_PYLIB = 'https://icos-carbon-portal.github.io/pylib/'
DOC_M_AUTH = 'https://icos-carbon-portal.github.io/pylib/modules/#authentication'
DOC_FAQ = 'https://icos-carbon-portal.github.io/pylib/faq/'
DOC_FAQ_WARNINGS = 'https://icos-carbon-portal.github.io/pylib/faq/#how-do-i-suppress-warnings'
# Metadata-schema concepts from Carbon Portal's ontologies.
CP_META = 'http://meta.icos-cp.eu/ontologies/cpmeta/'
