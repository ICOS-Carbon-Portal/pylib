#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 13 11:45:36 2019
"""

__author__ = "Claudio D'Onofrio"
__credits__ = ["ICOS Carbon Portal Dev Team"]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Claudio D'Onofrio"
__email__ = ["claudio.donofrio at nateko.lu.se", 'info@icos-cp.eu']
__status__ = "Development"


""" check the usage of this download library """

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