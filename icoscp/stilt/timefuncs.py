#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    
    Description:      Python functions that process time in STILT model outputs.
                      
    
"""

__author__      = ["Karolina Pantazatou"]
__credits__     = "ICOS Carbon Portal"
__license__     = "GPL-3.0"
__version__     = "0.0.1"
__maintainer__  = "ICOS Carbon Portal, elaborated products team"
__email__       = ['info@icos-cp.eu', 'karolina.pantazatou@nateko.lu.se']
__date__        = "2021-04-21"

###############################################################################

#Import modules:
import re
from datetime import datetime, date
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


#Function that checks if a start-date refers to an earlier date than an end-date:
def check_dates(s_date, e_date):
    
    #Define and initialize control variable:
    check = False
    
    #Check if input parameters are valid:
    if((isinstance(s_date, date)& isinstance(e_date, date))):
        
        #Compute the difference between end_date and start_date:
        diff = e_date - s_date

        #If start_date corresponds to a later date than end_date:
        if(diff.days>=0):
            
            check = True
    
    #Return control variable:
    return check
###############################################################################


def check_hours(ls):
     
    def check_hour_str(h_str):
        
        #Create & initialize control-variables:
        check_hour = False
        check_mins = False
        
        #Check if input variable is a string:
        if(isinstance(h_str, str)):
            
            #Check if input time-string follows the format "HH:MM":
            matched = re.match("[0-9][0-9]:[0-9][0-9]", h_str)
            
            #If the input time-string follows the format "HH:MM"
            if(bool(matched)):
                
                #Check hour-values:
                if((int(h_str[0:2])>=0) & (int(h_str[0:2])<=23)):
                    check_hour = True
                    
                else:
                    print('Invalid entry! Valid hour-values range from "00" to "23"...')
                    
                #Check minute-values:
                if((int(h_str[3:5])>=0) & (int(h_str[3:5])<=59)):
                    check_mins = True
                    
                else:
                    print('Invalid entry! Valid minute-values range from "00" to "59"...')
            
            else:
                print('Invalid input parameter! Expected a string entry with the format "HH:MM"...')
                
        else:
            print('Error! Expected hour-value to be inserted as a string...')
        
        if(check_hour & check_mins):
            return True
        else:
            return False
            
    
    #Create & initialize control-variable:    
    check = False
    
    #Check if input variable is a list:
    if (isinstance(ls, list)):
        
        check_ls = [check_hour_str(hour_string) for hour_string in ls]
        
        if(False not in check_ls):
            check = True
            
    else:
        print('Invalid input parameter! Expected a list...')
    
    return check
###############################################################################


#Function that takes a date-string as input and
#checks if it follows a valid format:
def check_datestring_format(d_str):
    
    #Create control variables:
    month_check = False
    day_check = False

    #Check if date-string follows the pattern "YYYY-MM-DD":
    matched = re.match("[0-9][0-9][0-9][0-9]-[0-1][0-9]-[0-3][0-9]", d_str)

    #Check if input variable is a string:
    if(isinstance(d_str, str)):
        
        #Check the length of the date-string:
        if(len(d_str)==10):
            
            #Check month-input:
            if((int(d_str[5:7])>0) & (int(d_str[5:7])<=12)):
                month_check = True
            else:
                print('Invalid entry! Valid month-values: "01", "02", ..., "12"')
            
            #Check day-input:
            if((int(d_str[8:10])>0) & (int(d_str[8:10])<=31)):
                day_check = True
            else:
                print('Invalid entry! Valid day-values: "01", "02", ..., "31"')

        else:
            print('Invalid date entry! Expected an entry following the format YYYY-MM-DD...')
    else:
        print('Error! Expected a string as input...')
        
    #Control all check-values:
    if (bool(matched) & month_check & day_check):
        return True
    else:
        return False
###############################################################################    


#Function that takes a date-string as input
#and returns a date-datetime object:
def str_to_date(d_string):
    
    if(check_datestring_format(d_string)):
        
        #Convert string with date info to date object:
        date_obj = datetime.strptime(d_string, '%Y-%m-%d').date()
        
    else:
        date_obj = None
        
    #Return date object:
    return date_obj  
###############################################################################


#Function that checks if STILT model output is available for the months after
#the month specified in a start-date (for the same year as start-date):
def check_smonth(sdate, st_dict):
    
    #Create & initialize check variable:
    check = False
    
    #Check if the year of start-date is included
    #in the STILT-station output period:
    if(str(sdate.year) in st_dict['years']):
        
        #Check if the STILT-station output includes results for months later in the start-date year:
        if(True in [sdate.month <= m for m in list(map(int,st_dict[str(sdate.year)]['months']))]):
            check = True
    
    #Return check variable:
    return check
###############################################################################


#Function that checks if STILT model output is available for the months before
#the month specified in a end-date (for the same year as end-date):
def check_emonth(edate, st_dict):
    
    #Create & initialize check variable:
    check = False
    
    #Check if the year of end-date is included
    #in the STILT-station output period:
    if(str(edate.year) in st_dict['years']):
        
        #Check if the STILT-station output includes results for months earlier in the end-date year:
        if(True in [edate.month >= m for m in list(map(int,st_dict[str(edate.year)]['months']))]):
            check = True
    
    #Return check variable:
    return check
    