#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    
    Description:      Python functions that perform controls over input
                      parameters to STILT-module functions.
                      
    
"""

__author__      = ["Karolina Pantazatou"]
__credits__     = "ICOS Carbon Portal"
__license__     = "GPL-3.0"
__version__     = "0.0.1"
__maintainer__  = "ICOS Carbon Portal, elaborated products team"
__email__       = ['info@icos-cp.eu', 'karolina.pantazatou@nateko.lu.se']
__date__        = "2021-04-26"

###############################################################################

#Import modules:
from icoscp.stilt import timefuncs as tf


def check_stilt_hours(ls):
    
    #Create & initialize control-variable:
    check = False
    
    #Valid STILT timeslots:
    stilt_hours=['00:00', '03:00', '06:00', '09:00', '12:00', '15:00', '18:00', '21:00']
    
    #Check if input parameter with timeslot-info is valid:
    if (tf.check_hours(ls)):
        
        if(False not in [h in stilt_hours for h in ls]):
            check = True
        else:
            print("Error! STILT model outputs are available in 3-hour interavals (e.g. '00:00', '03:00', '06:00', '09:00', '12:00', '15:00', '18:00', '21:00')")
            
    return check
###############################################################################


#Function that checks the selection of columns that are to be 
#returned with the STILT timeseries model output:
def check_columns(cols):
    
    #Check columns-input:
    if cols=='default':
        columns = ('["isodate","co2.stilt","co2.fuel","co2.bio", "co2.background"]')
            
    elif cols=='co2':
        columns = ('["isodate","co2.stilt","co2.fuel","co2.bio","co2.fuel.coal",'+
                '"co2.fuel.oil","co2.fuel.gas","co2.fuel.bio","co2.energy",'+
                '"co2.transport", "co2.industry","co2.others", "co2.cement",'+
                '"co2.background"]')
            
    elif cols=='co':
        columns = ('["isodate", "co.stilt","co.fuel","co.bio","co.fuel.coal",'+
                '"co.fuel.oil", "co.fuel.gas","co.fuel.bio","co.energy",'+
                '"co.transport","co.industry", "co.others", "co.cement",'+
                '"co.background"]')
            
    elif cols=='rn':
        columns = ('["isodate", "rn", "rn.era", "rn.noah"]')
            
    elif cols=='wind':
        columns = ('["isodate", "wind.dir", "wind.u", "wind.v"]')
        
    elif cols=='latlon':
        columns = ('["isodate", "latstart", "lonstart"]')
            
    elif cols=='all':
        columns = ('["isodate","co2.stilt","co2.fuel","co2.bio","co2.fuel.coal",'+
                '"co2.fuel.oil","co2.fuel.gas","co2.fuel.bio","co2.energy",'+
                '"co2.transport", "co2.industry","co2.others", "co2.cement",'+
                '"co2.background", "co.stilt","co.fuel","co.bio","co.fuel.coal",'+
                '"co.fuel.oil","co.fuel.gas","co.fuel.bio","co.energy",'+
                '"co.transport","co.industry","co.others", "co.cement",'+
                '"co.background","rn", "rn.era","rn.noah","wind.dir",'+
                '"wind.u","wind.v","latstart","lonstart"]')
    else:
        print('Invalid STILT timeseries column keyword!\nPlease select one of the valid keywords: "default", "co2", "co", "rn", "wind", "latlon", "all"')
        columns = []
    
    #Return variable:
    return columns
###############################################################################

