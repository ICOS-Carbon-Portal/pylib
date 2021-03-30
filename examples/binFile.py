#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Example:
    Create a digital object represenation based on a PID 
    Full documentation for the library available @
    https://icos-carbon-portal.github.io/pylib/  
    
    for more examples, please visit our Jupyter Hub and navigate
    to pylib_examples
    https://exploredata.icos-cp.eu
"""

from icoscp.cpb.dobj import Dobj

pid = 'https://meta.icos-cp.eu/objects/lNJPHqvsMuTAh-3DOvJejgYc'
f = Dobj(pid)
    
# print the first few rows
print(f.data.head())
# print citation
print('citation: ', f.citation)

f.data.plot(x='TIMESTAMP', y='ch4', grid=True)

