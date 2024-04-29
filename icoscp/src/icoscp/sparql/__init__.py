"""
    The "sparql" module is a simple interface to query the ICOS CP sparql Endpoint
    (https://meta.icos-cp.eu/sparqlclient/?type=CSV)
    
    Any sparql query which runs in the online version, runs in this module
    as well. Create an instance of "RunSparql", set the query as string and 
    define the output format. In addition to conventional csv/json output
    you can choose a more python friendly conversion to array or pandas.
    
"""