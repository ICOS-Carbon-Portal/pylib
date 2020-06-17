#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Example 1:
    Create a digital object represenation based on a PID 
    @author: Claudio
"""


from icoscp.cpb.dobj import Dobj

pid = 'ZHgulniA9Ie7PhfnHZo2Z9Ga'
f = Dobj(pid)


if f.valid:
    data = f.get()
else:        
    raise SystemExit('no binary data available', 0)
    
# print the first few rows
print(data.head())
print('citation: ', f.citation)

