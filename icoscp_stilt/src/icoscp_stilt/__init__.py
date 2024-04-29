import os
from icoscp_stilt.const import STILTPATH


__version__ = "0.1.0a0"


if not os.path.exists(STILTPATH):
    print("""
Please be aware, that the STILT module is not supported to run
locally (outside of the Virtual Environment at the ICOS Carbon
Portal). You must use one of our Jupyter Services.
Visit https://www.icos-cp.eu/data-services/tools/jupyter-notebook
for further information. Or you may use our online STILT viewer
application https://stilt.icos-cp.eu/viewer/.
          """)
