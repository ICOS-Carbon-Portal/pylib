"""
The Station Module is used to give easy access to
STILT results. Find STILT stations, and get access
to timeseries and spatial footprints.
"""

import os


try:
    os.stat('/data/')
except FileNotFoundError as error:
    print('Error! The Stilt module can only be used on ICOS servers and not '
          'locally.\nExiting...')
    exit(0)
