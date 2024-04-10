#!/usr/bin/env python

"""
    Description:      Python functions that process time in STILT model outputs.    
"""

__author__      = ["Karolina Pantazatou", "Claudio DOnofrio"]
__credits__     = "ICOS Carbon Portal"
__license__     = "GPL-3.0"
__version__     = "0.0.3"
__maintainer__  = "ICOS Carbon Portal, elaborated products team"
__email__       = ['info@icos-cp.eu', 'karolina.pantazatou@nateko.lu.se']
__date__        = "2022-11-23"
__lastchange__  = ["Claudio DOnofrio"]
###############################################################################

#Import modules:
from datetime import date
import pandas as pd
import re
###############################################################################


#Function that returns a tuple with the start-date and
#end-date for a STILT station's available output:
def get_st_dates(st_dict):

    s_year = min(list(map(int, st_dict['years']))) #get start year
    e_year = max(list(map(int, st_dict['years']))) #get end year

    s_month = min(list(map(int, st_dict[str(s_year)]['months']))) #get start month
    e_month = max(list(map(int, st_dict[str(e_year)]['months']))) #get end month

    #Create start_date for STILT station output:
    stilt_s_date = date(s_year, s_month, 1)

    #Create end_date for STILT station output:
    stilt_e_date = date(e_year, e_month, 1)
    
    #Return tuple with STILT station start-date & end-date:
    return (stilt_s_date, stilt_e_date)
###############################################################################

def get_hours(hours):
    """
    STILT results are availabe in 3 hour times slots: 0 3 6 9 12 15 18 21
    You may choose to return only results for a specific time slot.
    Selection of hours: Input is expected to be a list or convertible to a list
    where each item can be casted to integer in the range of 0 to 23.
    
    If hours is empty or None, ALL Timeslots are returned.
    Valid results are returned as result with LOWER BOUND values.
    Example:    hours = [2,3,4] will return Timeslots for 0, 3 
                hours = [2,3,4,5,6] will return Timeslots for 0,3 and 6
                hours = [] return ALL
                hours = [10] returns timeslot 9
    """
    
    
    valid = [0,3,6,9,12,15,18,21,24]
    valid_hours = []
    
    if not hours:
        # return ALL in case no hours or only invalid hours are provided
        valid_hours = valid[0:8]
    
    else:
        for h in hours:
            # for back compatibility, we need to check input for str format
            # hh:mm -> convert to int
            if isinstance(h, str):
                if re.match('[0-9][0-9]:[0-9][0-9]', h):
                    h = h[0:2]
                    
            h = int(h)
            if h < 0 or h > 24:
                pass
            for i in range(0,8):
                if h >= valid[i] and h < valid[i+1]:
                    valid_hours.append(valid[i])
                    break                
        # make sure we have unique values
        valid_hours = list(set(valid_hours))
    
    return valid_hours
    
###############################################################################

def parse(date):
    """
    convert date from different input formats:        

    Parameters
    ----------
    date :  STR 
            FLOAT (unix timestamp) 
            Python native datetime.date object
            pandas datetime object

    Returns
    -------
    datetime.date
    """
    out = False
    try:
        if isinstance(date, str):
            date = pd.to_datetime(date).date()
            out = True
        if isinstance(date, float) or isinstance(date, int):
            date = pd.to_datetime(date, unit='s').date()
            out = True
        
        if not out:            
            date = pd.to_datetime(date).date()
        
    except:
        date = None
    
    return date
    
    
def check_smonth(sdate, st_dict):
    """
    Function that checks if STILT model output is available for >= start date
    the check is for year and month only. 
    Example sdate = '2017-03-15' will return all stations which have data 
    for March 2017 or newer.
    """
    
    # if data exists in a year after sdate.year....True
    years = [int(y) for y in st_dict['years']]
    if any(y > sdate.year for y in years):
        return True 
    
    # if sdate.year is in years..check sdate.month 
    if sdate.year in years:
        months = [int(m) for m in st_dict[str(sdate.year)]['months']]
        if any(m >= sdate.month for m in months):
            return True
    return False


def check_emonth(edate, st_dict):
    """
    Function that checks if STILT model output is available for <= end date
    the check is for year and month only. 
    Example edate = '2017-03-15' will return all stations which have data 
    before or equal to March 2017.
    """
    
    # if data exists in a year before edate.year....True
    years = [int(y) for y in st_dict['years']]    
    if any(y < edate.year for y in years):
        return True 
    
    
    # if sdate.year is in years..check sdate.month 
    if edate.year in years:
        months = [int(m) for m in st_dict[str(edate.year)]['months']]
        if any(m <= edate.month for m in months):
            return True
    return False
    

def check_daterange(sdate, edate, st_dict):
    """
    Function that checks if STILT model output is available for
    >= sdate and <= edate
    the check is for year and month only. 
    Example daterange = ['2017-03-15','2017-05-28']' 
    will return all stations which have data >= March, 2017 and <= May 2017    
    """
    
    reflist = pd.date_range(start=sdate, end=edate, freq='MS').to_list()
    checklist = []            
    for y in st_dict['years']:
        for m in st_dict[y]['months']:
            checklist.append(pd.to_datetime(y + '-' + m))
    
    if list(set(checklist) & set(reflist)):
        return True
    
