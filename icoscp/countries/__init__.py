"""
    The countries module gives you access to a dictionry with 
    country information by
    import icoscp.countries
    
    and then you can call countries.get(.......
    
    Search country information.
    Please note: in case you provide more than one parameter, the order
    of keywords is not respected. The execution order is always like
    the function signature and as soon as a result is found, it will be
    returned and the search is stopped.

    Accepted keywords: code='', name='', latlon=[], search=''

    Example:
        .get()                      list of dict: all countries
        .get(code='CH')             dict: Switzerland
        .get(name='greece')         dict: Greece
        .get(latlon=[48.85, 2.35])  dict:
        .get(search='anything')     

    Parameters
    ----------
    code : STR
        Search by ISO 3166-1 2-letter or 3-letter country codes

    name : STR
        search by country name, including alternativ spellings.
        It can be the native name or a partial name.

    latlon : List[]
        List with two integer or floating point numbers representing
        latitude and longitude.
        BE AWARE: the reverse lookup service is only available on the
        ICOS CarbonPortal Jupyter Services

    search : STR
        arbitrary text search, not case sensitiv, search in all fields

    Returns
    -------
    DICT: if a single country is found
    LIST[DICT]: list of dicts if more than one country is found
    BOOL (False) if no result

"""
