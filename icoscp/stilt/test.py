# -*- coding: utf-8 -*-
"""
Created on Wed Apr  7 10:17:05 2021

@author: Claudio
"""

    
def a(**kwargs):
    
    # valid key words:
    keywords = ['stiltid','icosid','outfmt','country','bbox','pinpoint', \
                'sdate','edate', 'hours', 'search']
    
    for k in kwargs.keys():        
        if str(k).lower() in keywords:
            print(k,kwargs[k])
            #v(k,kwargs[k])
            
a(sDate=5)