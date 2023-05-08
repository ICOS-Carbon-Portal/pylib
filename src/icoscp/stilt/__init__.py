"""
The Station Module is used to give easy access to
STILT results. Find STILT stations, and get access
to timeseries and spatial footprints.
"""

import os
import icoscp.const as CPC

if not os.path.exists(CPC.STILTPATH):
    print("""
Please be aware, that the STILT module is not supported to run
locally (outside of the Virtual Environment at the ICOS Carbon
Portal). You must use one of our Jupyter Services.
Visit https://www.icos-cp.eu/data-services/tools/jupyter-notebook
for further information. Or you may use our online STILT viewer
application https://stilt.icos-cp.eu/viewer/.
    """)