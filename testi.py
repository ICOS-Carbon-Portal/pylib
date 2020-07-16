# -*- coding: utf-8 -*-
"""
Created on Mon Jun 22 11:31:28 2020

@author: Claudio
"""

import sys
sys.path.insert(0,'C:\\Users\\Claudio\\Documents\\GitHub\\ICOS-CP\\jupyter\\pytools')
import matplotlib.pyplot as plt
from icoscp.cpb.dobj import Dobj

dobj = Dobj('https://meta.icos-cp.eu/objects/lNJPHqvsMuTAh-3DOvJejgYc')
data = dobj.get()

# extract information from the dobj meta data
# look at dobj.info() for a full list 
unit = dobj.info[1].unit[dobj.info[1]['colName'] =='ch4'].values[0]
title = dobj.info[0].specLabel[0]
title = dobj.info[2].stationName[0] + ' (' + dobj.info[2].stationId[0] + ')'
title = title + '\n'  + dobj.info[0].specLabel[0]

plot = data.plot(x='TIMESTAMP', y='ch4', grid=True, title=title)
plot.set(ylabel=unit)

plt.show()


