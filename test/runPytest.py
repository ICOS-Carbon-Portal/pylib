# -*- coding: utf-8 -*-
"""
Created on Tue Jun  7 15:05:43 2022

@author: Claudio
"""

import pytest
import os 

absolut = os.path.dirname(os.path.realpath(__file__))
f = os.path.join(absolut, './')

modules = pytest.main(["-xv", f])

'''
x = stop testing after failure
v = verbose output
'''