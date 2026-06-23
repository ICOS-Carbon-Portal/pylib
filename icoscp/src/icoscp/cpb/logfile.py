"""
    Check the usage of dataobjects through this
    It is a completely anonymous service to record how many times
    a dataobject is accessed.    
"""

import json

import requests


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