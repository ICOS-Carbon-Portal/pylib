#!/usr/bin/env python

"""
    Created on Tue Aug 13 11:45:36 2019
    Check the usage of dataobjects through this
    It is a completely anonymous service to record how many times
    a dataobject is accessed.    
"""

__author__      = ["Claudio D'Onofrio"]
__credits__     = "ICOS Carbon Portal"
__license__     = "GPL-3.0"
__version__     = "0.1.0"
__maintainer__  = "ICOS Carbon Portal, elaborated products team"
__email__       = ['info@icos-cp.eu', 'claudio.donofrio@nateko.lu.se']
__status__      = "rc1"
__date__        = "2019-08-13"

import requests
import json

class Logfile():
    
    def __init__(self):
        self.server = 'https://restheart.icos-cp.eu/db/portaluse/'        
        self.flt = "?filter={'BinaryFileDownload':{'$exists':'true'}}&&count=true"        
        self._log = None        
        
        self.__getLogFile()
    
    @property
    def getLog(self):        
        return self._log                
    
    def getCount(self):        
        if self._log is not None:
            return self._log['_size']
        else:
            return 0

    def __getLogFile(self):
        url = self.server + self.flt
        r = requests.get(url)        
        self._log = json.loads(r.text)
        
if __name__ == '__main__':    
    print(str(Logfile().getCount()) + ' downloads counted')