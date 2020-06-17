
## Please use the following structure as "header" entries for python files:
## everything inside the -------- code block--------
## should be present. 
### __data__ is used for creatin date__
### __version__ we follow a major.minor.micro structure. The first release was unified to version 0.1.0


----------- beginning of file, no empty lines ------------
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Created on Fri Aug  9 10:40:27 2019
    Use an ICOS digital object id (persistent identification url)
    to load a binary representation of the data object.
"""

__author__      = ["Claudio D'Onofrio"]
__credits__     = "ICOS Carbon Portal"
__license__     = "GPL-3.0"
__version__     = "0.1.0"
__maintainer__  = "ICOS Carbon Portal, elaborated products team"
__email__       = ['info@icos-cp.eu', 'claudio.donofrio@nateko.lu.se']
__status__      = "rc1"
__date__        = "2019-08-09"

import os
import requests
import struct
import pandas as pd

from icoscp.sparql.runsparql import RunSparql
import icoscp.sparql.sparqls as sparqls
from icoscp.cpb import dtype_dict

------------ end of header entries -----------------------