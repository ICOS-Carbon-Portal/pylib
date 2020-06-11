# -*- coding: utf-8 -*-
"""
Created on Thu Jun 11 20:45:00 2020

@author: Claudio
"""


# ----------------------------------------------
# for testing only, set path to ICOS pytools
import sys
sys.path.insert(0,'C:\\Users\\Claudio\\Documents\\GitHub\\ICOS-CP\\jupyter\\pytools')
# ----------------------------------------------

from icoscp.cpb.cpbinfile import CpBinFile

fId = 'ZHgulniA9Ie7PhfnHZo2Z9Ga'

f = CpBinFile(fId)
if f.valid:
    data = f.getColumns()
else:    
    raise SystemExit('no binary data available',0)
    
# print the first few rows
print(data.head())
print(f.citation)