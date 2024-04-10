"""
Created on Wed Sep 30 09:38:18 2020
based on : return the real size of object
           https://goshippo.com/blog/measure-real-size-any-python-object/
"""

import sys

def get(obj):
    size = _get_size(obj)     
    power = 2**10
    n = 0
    power_labels = {0 : 'bytes', 1: 'KB', 2: 'MB', 3: 'GB', 4: 'TB'}
    while size > power:
        size /= power
        n += 1
    return round(size,3), power_labels[n]


def _get_size(obj, seen=None):
    """Recursively finds size of objects"""
    size = sys.getsizeof(obj)
    if seen is None:
        seen = set()
    obj_id = id(obj)
    if obj_id in seen:
        return 0
    # Important mark as seen *before* entering recursion to gracefully handle
    # self-referential objects
    seen.add(obj_id)
    if isinstance(obj, dict):
        size += sum([_get_size(v, seen) for v in obj.values()])
        size += sum([_get_size(k, seen) for k in obj.keys()])
    elif hasattr(obj, '__dict__'):
        size += _get_size(obj.__dict__, seen)
    elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
        size += sum([_get_size(i, seen) for i in obj])
    return size
    