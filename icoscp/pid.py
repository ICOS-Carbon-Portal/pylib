#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Resolve PID for ICOS and Fieldsites
    All PID's created by either the ICOS Data Portal
    or FIELDSITES are using handle.net with the ICOS Prefix.

    only one function is available .resolve(pid)
    returns the full url in form
    - https://meta.icos-cp.eu/objects/ + PID    # for ICOS
    -https://meta.fieldsites.se/objects/ + PID  # for FIELDSITES
"""

__author__ = ["Claudio Donofrio"]
__credits__ = "ICOS Carbon Portal"
__license__ = "GPL-3.0"
__version__ = "0.1.0"
__maintainer__ = "ICOS Carbon Portal, elaborated products team"
__email__ = ['info@icos-cp.eu']
__status__ = "rc1"
__date__ = "2023-01-08"

import sys
import requests as re
import  icoscp.const as CPC

def resolve(pid):
    """
       Transform the provided pid to a consistent format
       the user may provide the full url or only the pid, with or
       without the handle id.

       Return the full url in form:
        https://meta.icos-cp.eu/objects/ + PID
       OR
        https://meta.fieldsites.se/objects/ + PID

       If the full url is provided, notthing to do and return the full url
       Otherwise the handle.net API is called to resolve the PID and return
       the full URL. This is valid for ICOS CP with handle prefix 11676
       or FIELDSITES with prefix 11676.1
       If only the unique part of the PID is provided both prefixes are tested
       for validity.

    Parameters
    ----------
    pid : STR
        PID in form of
        - https://meta.icos-cp.eu/objects/Igzec8qneVWBDV1qFrlvaxJI
        - 11676/Igzec8qneVWBDV1qFrlvaxJI
        - Igzec8qneVWBDV1qFrlvaxJI

    Returns
    -------
    STR
        Full URL in form of
        https://meta.icos-cp.eu/objects/Igzec8qneVWBDV1qFrlvaxJI
        OR None, if pid not found

    """

    pid_lower = str(pid).lower()
    fullurl = ['meta.icos-cp.eu',
               'meta.fieldsites.se',
               'handle.net'
               ]

    if any(url in pid_lower for url in fullurl):
        # we have to assume that the full URL to the data object is provided
        # hence nothing to do
        return pid

    handle_kernel = kernel(pid)
    if handle_kernel['responseCode'] == 1:
        return handle_kernel['values'][0]['data']['value']

    return None


def kernel(pid):
    """
    ask handle.net for PID and return the kernel metadata

    Parameters
    ----------
    pid : STR
        PID in form of
        - https://meta.icos-cp.eu/objects/Igzec8qneVWBDV1qFrlvaxJI
        - 11676/Igzec8qneVWBDV1qFrlvaxJI
        - Igzec8qneVWBDV1qFrlvaxJI

    Returns
    -------
    kernel : DICT
        The response from handle.net API.
        if kernel['responseCode'] == 1: a valid pid entry was provided
        landing = kernel['values'][0]['data']['value']

    """

    checkpid = pid.split('/')[-1:][0]
    # get the pid and ask handle.net to resovle
    for prefix in CPC.HDL_PREFIX:
        url = f"{CPC.HANDLEURL}{prefix}/{checkpid}"
        handle_kernel = re.get(url, timeout=10).json()
        if handle_kernel['responseCode'] == 1:
            break
    return handle_kernel


if __name__ == "__main__":

    args = sys.argv[1:]
    # args is a list of the command line args

    if not args:

        MSG  = """
        You can try to run this script directly with

        python -m pid Igzec8qneVWBDV1qFrlvaxJI

        which returns the full url to the landing page

        or you can us

        import icoscp.pid
        pid = pid.resolve('Igzec8qneVWBDV1qFrlvaxJI')
        """
        print(MSG)
    else:
        print(resolve(args[0]))
