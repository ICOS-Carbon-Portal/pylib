#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Example 1:
    Create a digital object represenation based on a PID 
    @author: Claudio
"""

from icoscp.cpb.dobj import Dobj

pid = 'https://meta.icos-cp.eu/objects/lNJPHqvsMuTAh-3DOvJejgYc'
f = Dobj(pid)
    
# print the first few rows
print(f.data.head())
# print citation
print('citation: ', f.citation)

f.data.plot(x='TIMESTAMP', y='ch4', grid=True)

