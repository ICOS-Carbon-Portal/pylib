#!/usr/bin/env python

"""
    Created on Fri Aug  9 10:40:27 2019
    This file contains an assembly of common sparql queries.
    Each function returns a valid sparql query as string.
    Depending on query, there is an optional input parameter to 
    "limit" how many results are returned. By default it is set to 0 (zero)
    returning all results from the sparql endpoint
"""

__author__      = ["Claudio D'Onofrio"]
__credits__     = "ICOS Carbon Portal"
__license__     = "GPL-3.0"
__version__     = "0.1.3"
__maintainer__  = "ICOS Carbon Portal, elaborated products team"
__email__       = ['info@icos-cp.eu', 'claudio.donofrio@nateko.lu.se']
__status__      = "rc1"
__date__        = "2019-08-09"

from warnings import warn
# --------------------------------------------------------------------
# create internal helper functions to be used for ALL sparql queries
# --------------------------------------------------------------------

def __checklimit__(limit):
    
    """
        create a string to inject into sparql queries to limit the 
        amount of returned results
    """
    
    try:
        limit = int(limit)
        if limit > 0:
            return 'limit ' + str(limit)
        else:
            return ''
    except ValueError:
        return 'limit not an integer'



def __dobjUrl__(dobj):
    
    """
       transform the provided digital object to a consistent format
       the user may provide the full url or only the pid.
       this function will return the full url in form:
        '<https://meta.icos-cp.eu/objects/'+ dobj + '>'
    """
    
    try: 
        dobj = str(dobj)
    except:
       raise Exception('dobj not a string') 
       
       
    if 'meta.icos-cp' in dobj:
        # we assume a full ICOS URI is provided, we only need to add <>
        return '<' + dobj + '>'
    
    # this case assumes either the PID only, or possibly the handle.net
    pid = dobj.split('/')[-1]
    url = '<https://meta.icos-cp.eu/objects/%s>' % pid
    return url        

# --------------------------------------------------------------------
#   sparqls query functions
#   return a sparql query, which can be copy/pasted to the sparql
#   endpoint at https://meta.icos-cp.eu/sparqlclient/
# --------------------------------------------------------------------
def atc_co2_level2(limit=0):

    """ ICOS Atmospheric CO2 level 2 data objects """

    query = """
        prefix cpmeta: <http://meta.icos-cp.eu/ontologies/cpmeta/>
        prefix prov: <http://www.w3.org/ns/prov#>
        select ?dobj ?spec ?fileName ?size ?submTime ?timeStart ?timeEnd
        FROM <http://meta.icos-cp.eu/resources/atmprodcsv/>
        where {
                BIND(<http://meta.icos-cp.eu/resources/cpmeta/atcCo2L2DataObject> AS ?spec)
                ?dobj cpmeta:hasObjectSpec ?spec .
                FILTER NOT EXISTS {[] cpmeta:isNextVersionOf ?dobj}
                ?dobj cpmeta:hasSizeInBytes ?size .
                ?dobj cpmeta:hasName ?fileName .
                ?dobj cpmeta:wasSubmittedBy [
                prov:endedAtTime ?submTime ;
                prov:wasAssociatedWith ?submitter
                ] .
                ?dobj cpmeta:hasStartTime | (cpmeta:wasAcquiredBy / prov:startedAtTime) ?timeStart .
                ?dobj cpmeta:hasEndTime | (cpmeta:wasAcquiredBy / prov:endedAtTime) ?timeEnd .
        }
        %s
        """ % __checklimit__(limit)

    return query

# -----------------------------------------------------------------------------

def objectSpec(spec='atcCo2L2DataObject', station='', limit=0):

    """ return digital objects sorted by station and sampling height based
        on data specification  https://meta.icos-cp.eu/edit/cpmeta/ 
        -> simple object specification
        by default ATC Level2 Data for CO2 is returned
    """
        
    if station:
        station = 'FILTER(?station = "%s")' % station
    
    query = """
        prefix cpmeta: <http://meta.icos-cp.eu/ontologies/cpmeta/>
	    prefix prov: <http://www.w3.org/ns/prov#>
		select ?dobj ?station ?samplingHeight
		where {
			VALUES ?spec { <http://meta.icos-cp.eu/resources/cpmeta/%s> }
			?dobj cpmeta:hasObjectSpec ?spec .
			FILTER NOT EXISTS {[] cpmeta:isNextVersionOf ?dobj}
			?dobj cpmeta:wasSubmittedBy/prov:endedAtTime ?submEnd .
			?dobj cpmeta:wasAcquiredBy [
				prov:wasAssociatedWith ?stationIri ;
				cpmeta:hasSamplingHeight ?samplingHeight
			] .
            ?stationIri cpmeta:hasName ?station .		
			%s
		}
		order by ?station ?samplingHeight
        %s
        """ % (spec,station, __checklimit__(limit))

    return query

# -----------------------------------------------------------------------------
def atc_co_level2(limit=0):

    """ ICOS Atmospheric CO2 level 2 data objects """

    query = """
        prefix cpmeta: <http://meta.icos-cp.eu/ontologies/cpmeta/>
        prefix prov: <http://www.w3.org/ns/prov#>
        select ?dobj ?spec ?fileName ?size ?submTime ?timeStart ?timeEnd 
        FROM <http://meta.icos-cp.eu/resources/atmprodcsv/>
        where {
                BIND(<http://meta.icos-cp.eu/resources/cpmeta/atcCoL2DataObject> AS ?spec)
                ?dobj cpmeta:hasObjectSpec ?spec .
                FILTER NOT EXISTS {[] cpmeta:isNextVersionOf ?dobj}
                ?dobj cpmeta:hasSizeInBytes ?size .
                ?dobj cpmeta:hasName ?fileName .
                ?dobj cpmeta:wasSubmittedBy [
                prov:endedAtTime ?submTime ;
                prov:wasAssociatedWith ?submitter
                ] .
                
                ?dobj cpmeta:hasStartTime | (cpmeta:wasAcquiredBy / prov:startedAtTime) ?timeStart .
                ?dobj cpmeta:hasEndTime | (cpmeta:wasAcquiredBy / prov:endedAtTime) ?timeEnd .                
        }
        %s
        """ % __checklimit__(limit)

    return query

# -----------------------------------------------------------------------------
def atc_ch4_level2(limit=0):

    """ ICOS Atmospheric CH4 level 2 data objects """

    query = """
        prefix cpmeta: <http://meta.icos-cp.eu/ontologies/cpmeta/>
        prefix prov: <http://www.w3.org/ns/prov#>
        select ?dobj ?spec ?fileName ?size ?submTime ?timeStart ?timeEnd
        FROM <http://meta.icos-cp.eu/resources/atmprodcsv/>
        where {
                BIND(<http://meta.icos-cp.eu/resources/cpmeta/atcCh4L2DataObject> AS ?spec)
                ?dobj cpmeta:hasObjectSpec ?spec .
                FILTER NOT EXISTS {[] cpmeta:isNextVersionOf ?dobj}
                ?dobj cpmeta:hasSizeInBytes ?size .
                ?dobj cpmeta:hasName ?fileName .
                ?dobj cpmeta:wasSubmittedBy [
                prov:endedAtTime ?submTime ;
                prov:wasAssociatedWith ?submitter
                ] .
                ?dobj cpmeta:hasStartTime | (cpmeta:wasAcquiredBy / prov:startedAtTime) ?timeStart .
                ?dobj cpmeta:hasEndTime | (cpmeta:wasAcquiredBy / prov:endedAtTime) ?timeEnd .
        }
        %s
        """ % __checklimit__(limit)

    return query
# ---------------------------------------------------------------------------

# -----------------------------------------------------------------------------
def atc_nrt_level_1(limit=0):

    """ ICOS Atmospheric level 1 data objects
        -> Data Level 1 / ATC / CH4 and CO2
    """

    query = """
        prefix cpmeta: <http://meta.icos-cp.eu/ontologies/cpmeta/>
		prefix prov: <http://www.w3.org/ns/prov#>
		select ?dobj ?spec ?fileName ?size ?submTime ?timeStart ?timeEnd
		FROM <http://meta.icos-cp.eu/resources/atmprodcsv/>
		where {
		VALUES ?spec {<http://meta.icos-cp.eu/resources/cpmeta/atcMeteoGrowingNrtDataObject> <http://meta.icos-cp.eu/resources/cpmeta/atcCo2NrtGrowingDataObject> <http://meta.icos-cp.eu/resources/cpmeta/atcCh4NrtGrowingDataObject>}
		?dobj cpmeta:hasObjectSpec ?spec .
	
		FILTER NOT EXISTS {[] cpmeta:isNextVersionOf ?dobj}
		?dobj cpmeta:hasSizeInBytes ?size .
		?dobj cpmeta:hasName ?fileName .
		?dobj cpmeta:wasSubmittedBy/prov:endedAtTime ?submTime .
		?dobj cpmeta:hasStartTime | (cpmeta:wasAcquiredBy / prov:startedAtTime) ?timeStart .
		?dobj cpmeta:hasEndTime | (cpmeta:wasAcquiredBy / prov:endedAtTime) ?timeEnd .
	    }
        %s
        """ % __checklimit__(limit)

    return query
# ---------------------------------------------------------------------------

def collections(id=None):
    """
    Return Collections
    Parameters
    ----------
    id : STR, optional
        The default is None, which returns all know collections.
        You can provide a ICOS URI or DOI to filter for a specifict collection
    Returns
    -------
    query : STR
        A query, which can be run against the SPARQL endpoint.
    """
    
    if not id:
        coll = '' # create an empyt string insert into sparql query
    else:
        coll = ''.join(['FILTER(str(?collection) = "' + id+ '" || ?doi = "' + id + '") .'])
       
    query = """
            prefix cpmeta: <http://meta.icos-cp.eu/ontologies/cpmeta/>
            prefix dcterms: <http://purl.org/dc/terms/>
            select * where{
            ?collection a cpmeta:Collection .
            %s
            OPTIONAL{?collection cpmeta:hasDoi ?doi} .
            ?collection dcterms:title ?title .
            OPTIONAL{?collection dcterms:description ?description}
            FILTER NOT EXISTS {[] cpmeta:isNextVersionOf ?collection}
            }
            order by ?title
            """ % coll

    return query


# -----------------------------------------------------------------------------
def collection_items(id):
    
    """ Return all item for a collection """
    
    query = """    
            select * where{ %s <http://purl.org/dc/terms/hasPart> ?dobj}
            """ % __dobjUrl__(id)
    return query
# -----------------------------------------------------------------------------


def station_query(filter: dict = None, return_filter: bool = False) -> str or (str, str):
    """
    Define SPARQL query to return a list of all known stations
    at the Carbon Portal. This can include NON-ICOS stations.
    Note: excluding WDGCC stations ( https://gaw.kishou.go.jp/ ),
    which are visible in the data portal for historic reasons.

    Parameters
    ----------
    filter: dictionary
        DESCRIPTION. The filter may contain selections we want to filter out on
        the sparql side, instead of doing all filtering on the python side.
        sparql will return rows satisfying all keys of the filter.
        Combining keys will return the intersection of the data sets.
        PLEASE NOTE: Some key-values are case-sensitive.
        Possible keys of the filter dictionary are
            'station': str or list of str, optional, case-sensitive
                The empty string, '', will return ALL stations.
                If you provide a station id, know that:
                - That it needs to be exactly as provided from the Triple Store.
                - The station name might not be unique.
            'theme': str or list of str, optional, case-sensitive
                The empty string, '', which returns ALL themes.
                If you provide a theme, be aware, that it needs to be
                exactly as provided from the Triple Store.
            'country': str or list of str
                Where 'country' expect country codes using alpha-2 ISO 3166.
            'project': str = 'ICOS'| 'ALL'
                The choice 'ICOS', which is default from internal icoscp-calls,
                will query for
                    (1) stations of theme 'AS', 'ES' or 'OS'
                for which
                    (2) icosClass is '1', '2' or 'associated'.
                If used to gether with the 'theme'-filter, the resulting query
                will only look for themes of the 'theme'-filter that are 'AS,
                'ES' or 'OS'.
                The choice 'ALL', then all will return all known stations.
    return_filter : bool
        DESCRIPTION. By default, `return_filter` is False. If `return_filter`
        is True then the return-value will be a tuple: (query, filter), where
        the filter might be modified.

    Returns
    -------
    query : str
        Provided the parameter `return_filter` is False.
        The `query` is a valid sparql query to run against the Carbon Portal SPARQL endpoint.
    (query, filter) : (str, str)
        Provided the parameter `return_filter` is True.
        The `query` is a valid sparql query to run against the Carbon Portal SPARQL endpoint.
        The `filter` might be modified filter.

    Example
    -------
    # The default call, will return all known stations
    >>> station_query()
    '...prefix cpmeta: <http://meta.icos-cp.eu/ontologies/cpmeta/>...'

    # For ICOS stations use:
    >>> station_query({'project': 'ICOS'})
    '...'

    # To fetch all atmospheric and ecosystem stations of ICOS, use
    # station_query({ 'theme': ['AS','ES'], 'project': 'ICOS'})

    # To fetch the atmospheric ICOS stations: 'BIR', 'HTM' and 'KIT', use
    # station_query({ 'station': ['BIR', 'HTM', 'KIT'], 'project': 'ICOS'})

    # To fetch all atmospheric ICOS stations in Norway and Sweden, use
    # station_query({ 'theme': 'AS', 'country': ['NO','SE'], 'project': 'ICOS'})

    # To fetch all ICOS and non-ICOS stations in Germany use
    # station_query({ 'country': ['DE'], 'project': 'all'})

    # To reuse a filter we can use the return_filter option
    # station_query(some_filter, return_filter = True)
    """

    # Depending on the filter we will change the
    # following default query filters:
    station_filter = ''
    theme_filter = ''
    country_filter = 'OPTIONAL {?uri cpmeta:countryCode ?country }'
    icos_filter = 'OPTIONAL {?uri cpmeta:hasStationClass ?icosClass}'

    if isinstance(filter, dict):
        # Remove redundant keys
        provided_keys = list(filter.keys())
        for any_key in provided_keys:
            if filter[any_key] in ['', [''], None]:
                filter.pop(any_key)

        # Setting some parameters upper case
        icos_themes = ['AS', 'ES', 'OS']
        upper_cond = (lambda z, w: z if w and z.upper() not in w else z.upper())
        if 'theme' in filter.keys():
            if isinstance(filter['theme'], str):
                filter['theme'] = upper_cond(filter['theme'], icos_themes)
            elif isinstance(filter['theme'], list):
                filter['theme'] = [upper_cond(x, icos_themes)
                                   for x in filter['theme']]
        if 'country' in filter.keys():
            if isinstance(filter['country'], str):
                filter['country'] = filter['country'].upper()
            elif isinstance(filter['country'], list):
                filter['country'] = [x.upper() for x in filter['country']]

        # sparql string syntax
        xsd = '^^xsd:string '

        if 'project' in filter.keys():
            filter['project'] = str(filter['project']).upper()
            if filter['project'] == 'ICOS':
                icos_filter = '''VALUES ?icosClass {"1"^^xsd:string  "2"^^xsd:string  "Associated"^^xsd:string }
                    {?uri cpmeta:hasStationClass ?icosClass}'''
                if 'theme' not in filter.keys():
                    filter['theme'] = icos_themes
                else:
                    filter['theme'] = [x for x in icos_themes if x in filter['theme']]
            elif filter['project'] == 'ALL':
                # Just filter using the other keys
                pass
            else:
                # In case wrong value is given,
                # and the filter is to be returned
                filter.pop('project')

        if 'station' in filter.keys():
            if isinstance(filter['station'], str):
                station = f'"{filter["station"]}"{xsd}'
                station_filter = f'BIND ( {station} as ?id)'
            elif isinstance(filter['station'], list):
                station = str(filter['station'])[1:-1]
                station = station.replace(',', xsd ) + xsd
                station_filter = f"VALUES ?id {{{station}}}"
            else:
                # In case wrong value is given,
                # and the filter is to be returned
                filter.pop('station')
                station_filter = ''

        if 'theme' in filter.keys():
            if isinstance(filter['theme'], str):
                theme_filter = f'BIND (cpmeta:{filter["theme"]} as ?stationTheme)'
            elif isinstance(filter['theme'], list):
                theme = ' '.join(filter['theme'])
                theme = 'cpmeta:' + theme.replace(' ', ' cpmeta:')
                theme_filter = f"VALUES ?stationTheme {{{theme}}}"
            else:
                # In case wrong value is given,
                # and the filter is to be returned
                filter.pop('theme')
                theme_filter = ''

        if 'country' in filter.keys():
            if isinstance(filter['country'], str):
                country = f"'{filter['country']}'{xsd}"
            elif isinstance(filter['country'], list):
                country = str(filter['country'])[1:-1]
                country = country.replace(',', xsd) + xsd
            else:
                # In case wrong value is given,
                # and the filter is to be returned
                filter.pop('country')
                country = ''
            country_filter = f"""VALUES ?country {{{country}}}
            {{?uri cpmeta:countryCode ?country}} """

    ## Note: sparql use {} to group variables, when using the
    #        python f-string formatting rule:
    #        - use single curly braces around variables {py_var}
    #        - use double curly braces {{}} around sparql-code {{?uri cpmeta:hasName ?name }}
    #        provided sparql expect curly braces {?uri cpmeta:hasName ?name }
    #        - use triple curly braces {{{py_var}}} provided sparql expect {eval(py_var)}

    query = f"""
        prefix xsd: <http://www.w3.org/2001/XMLSchema#>
        prefix cpmeta: <http://meta.icos-cp.eu/ontologies/cpmeta/>
        prefix cpst: <http://meta.icos-cp.eu/ontologies/stationentry/>
        select distinct ?uri ?id ?name ?icosClass ?country ?lat ?lon ?elevation ?stationTheme ?firstName ?lastName ?email ?siteType
        from <http://meta.icos-cp.eu/resources/icos/>
        from <http://meta.icos-cp.eu/resources/extrastations/>
        from <http://meta.icos-cp.eu/resources/cpmeta/>
        from <http://meta.icos-cp.eu/resources/stationentry/>
        where {{
            {{
                select ?uri ?id ?stationTheme (sample(?pers) as ?piOpt)  where
                {{
                    {station_filter}
                    ?uri cpmeta:hasStationId ?id .
                    {theme_filter}
                    ?uri a ?stationTheme .
                    OPTIONAL{{
                        ?memb cpmeta:atOrganization ?uri ; cpmeta:hasRole <http://meta.icos-cp.eu/resources/roles/PI> .
                        optional {{?memb cpmeta:hasEndTime ?membEnd}}
                        filter(!bound(?membEnd) || ?membEnd > now())
                        ?pers cpmeta:hasMembership ?memb
                    }}
                }}
                group by ?uri ?id ?stationTheme
            }}
            bind(coalesce(?piOpt, <http://dummy>) as ?pi)
            OPTIONAL{{
                ?pi cpmeta:hasFirstName ?firstName .
                ?pi cpmeta:hasLastName ?lastName
            }}
            OPTIONAL{{?pi cpmeta:hasEmail ?email}}
            OPTIONAL {{
                    {{
                        ?provSt cpst:hasProductionCounterpart ?prodUriLit .
                        bind((?uri = iri(?prodUriLit)) as ?areEqual)
                        filter(?areEqual)
                    }}
                ?provSt cpst:hasSiteType ?siteType .
            }}
            {icos_filter}
            OPTIONAL {{?uri cpmeta:hasName ?name  }}
            {country_filter}
            OPTIONAL {{?uri cpmeta:hasLatitude ?lat }}
            OPTIONAL {{?uri cpmeta:hasLongitude ?lon }}
            OPTIONAL {{?uri cpmeta:hasElevation ?elevation }}
        }}
        order by ?stationTheme ?id
        """

    if not return_filter:
        return query
    else:
        return query, filter


def stationData(uri, level='2'):
    """
    Define SPARQL query to get a list of data objects for a specific station.
    Since a station ID might belong to more than one, a list of URI is expected
    and all dataproducts are provided.
    Parameters
    ----------
    uri : list , station URI, 
    level : str , optional,  ['1','2','3','all'] 
            find data products for icos level. The default is 2.
    Returns
    -------
    query : str , valid sparql query.
    """
    accepted_levels = [1,2,3]
    try:
        if not isinstance(level,str):
            return
        if level.lower() == 'all':
            level = '>0'                    
        elif not int(level) in accepted_levels:
            level=' >1'
        else:
            level = ' = ' + level
    except:
        return 'input parameters not valid'

    uristr = '<' + '> <'.join(uri) + '>'

    query = """prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    prefix xsd: <http://www.w3.org/2001/XMLSchema#>
    prefix cpmeta: <http://meta.icos-cp.eu/ontologies/cpmeta/>
    prefix prov: <http://www.w3.org/ns/prov#>
    select *
    where {
	    {
            ?spec cpmeta:hasDataLevel ?datalevel .
            FILTER (?datalevel  %s)
            FILTER NOT EXISTS {?spec cpmeta:hasAssociatedProject/cpmeta:hasHideFromSearchPolicy "true"^^xsd:boolean}
            ?spec rdfs:label ?specLabel .
    	}	
	VALUES ?station {%s}
	?dobj cpmeta:hasObjectSpec ?spec .	
	FILTER NOT EXISTS {[] cpmeta:isNextVersionOf ?dobj}				
	?dobj cpmeta:wasAcquiredBy [
		prov:startedAtTime ?timeStart ;
   		prov:endedAtTime ?timeEnd ;
	 	prov:wasAssociatedWith ?station 
	] .
	?dobj cpmeta:hasSizeInBytes ?bytes .
	OPTIONAL {?dobj cpmeta:wasAcquiredBy/cpmeta:hasSamplingHeight ?samplingheight} .
    }""" % (level, uristr)

    return query


def stations_with_pi(station='', limit=0):
    """
        Definition of an old SPARQL query that was used to fetch provisional
        meta-data, namely a list of ICOS stations with principal
        investigators and e-mails.
    """
    deprecation_message = """
    This function will be deprecated in the next pylib major release.
    In its current version the function fetches a query that will return all stations or a number of stations
    given the `limit` argument.
    In order to filter only stations with a principal investigator one can run:
        from icoscp.sparql import sparqls
        from icoscp.sparql.runsparql import RunSparql
        query = sparqls.stations_with_pi()
        df = RunSparql(sparql_query=query, output_format='pandas').run()
        df_stations_with_pi = df[(df.firstName.notnull()) & (df.lastName.notnull())]
    """
    warn(deprecation_message, DeprecationWarning, stacklevel=2)
    return getStations(station=station) + __checklimit__(limit)


def getStations(station='', theme=''):
    """
    Define SPARQL query to return a list of all known stations
    at the Carbon Portal. This can include NON-ICOS stations.
    Note: excluding WDGCC stations ( https://gaw.kishou.go.jp/ ),
    which are visible in the data portal for historic reasons.
    Parameters
    ----------
    station : str, optional, case sensitive
        DESCRIPTION. The default is '', and empty string which returns ALL
        stations. If you provide a station id, be aware, that it needs to be
        exactly as provided from the Triple Store....case sensitive.
    theme : str, optional, case sensitive
        DESCRIPTION. The default is '', and empty string which returns ALL
        themes. If you provide a theme, be aware, that it needs to be
        exactly as provided from the Triple Store....case sensitive.
    Returns
    -------
    query : str, valid sparql query to run against the Carbon Portal SPARQL endpoint.
    """

    filter = dict()

    if station:
        filter['station'] = station

    if theme:
        filter['theme'] = theme

    return station_query(filter=filter)


def dobjStation(dobj):
    """
        Define SPARQL query to get information about a station
        where the digitial object was sampled.        
        :param dobj pid
    """
    query = """
            prefix cpmeta: <http://meta.icos-cp.eu/ontologies/cpmeta/>
            prefix prov: <http://www.w3.org/ns/prov#>
            select distinct ?dobj ?stationName ?stationId ?samplingHeight ?longitude ?latitude ?elevation ?theme
            where{
            		{	select ?dobj (min(?station0) as ?stationName)
            			(sample(?stationId0) as ?stationId) 
            			(sample(?stationLongitude) as ?longitude)
            			(sample(?stationLatitude) as ?latitude)
            			(sample(?stationElevation) as ?elevation)
            			(sample(?samplingHeight0) as ?samplingHeight)
            			where{
            				VALUES ?dobj { %s }
            				OPTIONAL{
            						?dobj cpmeta:wasAcquiredBy ?acq.
            						?acq prov:wasAssociatedWith ?stationUri .
            						OPTIONAL{ ?stationUri cpmeta:hasName ?station0 }
            						OPTIONAL{ ?stationUri cpmeta:hasStationId ?stationId0 }
            						OPTIONAL{ ?stationUri cpmeta:hasLongitude ?stationLongitude }
            						OPTIONAL{ ?stationUri cpmeta:hasLatitude ?stationLatitude }
            						OPTIONAL{ ?stationUri cpmeta:hasElevation ?stationElevation }
            						OPTIONAL{ ?acq cpmeta:hasSamplingHeight ?samplingHeight0 }
            				}
            			}
            			group by ?dobj
            		}
            		?dobj cpmeta:hasObjectSpec ?specUri .
            		OPTIONAL{ ?specUri cpmeta:hasDataTheme [rdfs:label ?theme ;]}
            		OPTIONAL{?dobj cpmeta:hasActualColumnNames ?columnNames }
            }
            """ %__dobjUrl__(dobj)
    return query
# -----------------------------------------------------------------------------
# originals from Karolina
# stripped to return sparql queries only
# -----------------------------------------------------------------------------

def get_coords_icos_stations_atc():
    
    """
    Input parameters: No input parameter/s
    Output:           pandas dataframe
                      columns: 
                            1. URL to station landing page (var_name: 'station', var_type: String)
                            2. Name of station PI (var_name: 'PI_names', var_type: String)
                            3. Station name (var_name: 'stationName', var_type: String)
                            4. 3-character Station ID (var_name: 'stationId', var_type: String)
                            5. 2-character Country code (var_name: 'Country', var_type: String)
                            6. Station Latitude (var_name: 'lat', var_type: String)
                            7. Station Longitude (var_name: 'lon', var_type: String)
    """
    
    #Define SPARQL query:
    query = """
        prefix cpmeta: <http://meta.icos-cp.eu/ontologies/cpmeta/>
        select *
        from <http://meta.icos-cp.eu/resources/icos/>
        where{
        {
        select ?station (GROUP_CONCAT(?piLname; separator=";") AS ?PI_names)
        where{
          ?station a cpmeta:AS .
          ?piMemb cpmeta:atOrganization ?station  .
          ?piMemb cpmeta:hasRole <http://meta.icos-cp.eu/resources/roles/PI> .
          filter not exists {?piMemb cpmeta:hasEndTime []}
          ?pi cpmeta:hasMembership ?piMemb .
          ?pi cpmeta:hasLastName ?piLname .
        }
        group by ?station
        }
        ?station cpmeta:hasName ?stationName ;
           cpmeta:hasStationId ?stationId ;
           cpmeta:countryCode ?Country ;
           cpmeta:hasLatitude ?lat ;
           cpmeta:hasLongitude ?lon .
        }
        order by ?Short_name
    """
    
    #Return string with SPARQL query:
    return query

# -----------------------------------------------------------------------------

def get_icos_stations_atc_L1():
    
    """
    Description:      Download ICOS station names for all L1 gases from ICOS CP with a SPARQL-query.
    Input parameters: No input parameter/s
    Output:           Pandas Dataframe
                      columns: 
                            1. URL to ICOS RI Data Object Landing Page (var_name: 'dobj', var_type: String)
                            2. Filename for Data Object (var_name: 'filename', var_type: String)
                            3. Name of gas (var_name: 'variable', var_type: String)
                            4. Station name (var_name: 'stationName', var_type: String)
                            5. Sampling height a.g.l. (var_name: 'height', var_type: String)
                            6. Sampling Start Time (var_name: 'timeStart', var_type: String)
                            7. Sampling End Time (var_naem: 'timeEnd', var_type: String)
    """
    
    #Define SPARQL query:
    query = """
        prefix cpres: <http://meta.icos-cp.eu/resources/cpmeta/>
        prefix cpmeta: <http://meta.icos-cp.eu/ontologies/cpmeta/>
        prefix prov: <http://www.w3.org/ns/prov#>
        select ?dobj ?fileName ?variable ?stationName ?height ?timeStart ?timeEnd #?stationId
        where{
           values ?vtype { cpres:co2MixingRatio cpres:coMixingRatioPpb cpres:ch4MixingRatioPpb}
           #values ?spec {cpres:atcCo2NrtGrowingDataObject cpres:atcCoNrtGrowingDataObject cpres:atcCh4NrtGrowingDataObject}
           ?vtype rdfs:label ?variable .
           ?col cpmeta:hasValueType ?vtype .
           ?dset cpmeta:hasColumn ?col .
           ?spec cpmeta:containsDataset ?dset .
           ?spec cpmeta:hasAssociatedProject <http://meta.icos-cp.eu/resources/projects/icos> .
           ?spec cpmeta:hasDataLevel "1"^^xsd:integer .
           ?dobj cpmeta:hasObjectSpec ?spec .
           ?dobj cpmeta:hasName ?fileName .
           ?dobj cpmeta:hasSizeInBytes ?fileSize .
           filter not exists {[] cpmeta:isNextVersionOf ?dobj}
           ?dobj cpmeta:wasAcquiredBy [
              #prov:wasAssociatedWith/cpmeta:hasStationId ?stationId ;
              prov:startedAtTime ?timeStart ;
              prov:endedAtTime ?timeEnd ;
              prov:wasAssociatedWith ?stationIri 
            ] .
            ?stationIri cpmeta:hasName ?stationName .
            ?dobj cpmeta:wasAcquiredBy/cpmeta:hasSamplingHeight ?height .
        }
        order by ?variable ?stationName ?height
    """
    
    #Return string with SPARQL query:
    return query

# -----------------------------------------------------------------------------

def get_icos_stations_atc_L2():
    """    
    Description:      Download ICOS station names for all L2 gases from ICOS CP with a SPARQL-query.
    Input parameters: No input parameter/s
    Output:           pandas dataframe
                      columns: 
                            1. URL to ICOS RI Data Object Landing Page (var_name: 'dobj', var_type: String)
                            2. Filename for Data Object (var_name: 'filename', var_type: String)
                            3. Name of gas (var_name: 'variable', var_type: String)
                            4. Station name (var_name: 'stationName', var_type: String)
                            5. Sampling height a.g.l. (var_name: 'height', var_type: String)
                            6. Sampling Start Time (var_name: "timeStart", var_type: Datetime Object)
                            7. Sampling End Time (var_name: "timeEnd", var_type: Datetime Object)
    """
    
    #Define SPARQL query:
    query = """
        prefix cpres: <http://meta.icos-cp.eu/resources/cpmeta/>
        prefix cpmeta: <http://meta.icos-cp.eu/ontologies/cpmeta/>
        prefix prov: <http://www.w3.org/ns/prov#>
        select ?dobj ?fileName ?variable ?stationName ?height ?timeStart ?timeEnd #?stationId
        where{
           values ?vtype {cpres:coMixingRatioPpb cpres:ch4MixingRatioPpb cpres:co2MixingRatio }
           #values ?spec {cpres:atcCo2L2DataObject cpres:atcCoL2DataObject cpres:atcCh4L2DataObject}
           ?vtype rdfs:label ?variable .
           ?col cpmeta:hasValueType ?vtype .
           ?dset cpmeta:hasColumn ?col .
           ?spec cpmeta:containsDataset ?dset .
           ?spec cpmeta:hasAssociatedProject <http://meta.icos-cp.eu/resources/projects/icos> .
           ?spec cpmeta:hasDataLevel "2"^^xsd:integer .
           ?dobj cpmeta:hasObjectSpec ?spec .
           ?dobj cpmeta:hasName ?fileName .
           filter not exists {[] cpmeta:isNextVersionOf ?dobj}
           ?dobj cpmeta:wasAcquiredBy [
              #prov:wasAssociatedWith/cpmeta:hasStationId ?stationId ;
              prov:startedAtTime ?timeStart ;
              prov:endedAtTime ?timeEnd ;
              prov:wasAssociatedWith/cpmeta:hasName ?stationName
            ] .
            ?dobj cpmeta:wasAcquiredBy/cpmeta:hasSamplingHeight ?height .
        }
        order by ?variable ?stationName ?height
    """
    
    #Return string with SPARQL query:
    return query

# -----------------------------------------------------------------------------
# originals from Ute
# stripped to return sparql queries only
# -----------------------------------------------------------------------------


def get_station_class():
    # Query the ICOS SPARQL endpoint for a station list
    # query stationId, class, lng name and country

    query = """
    prefix st: <http://meta.icos-cp.eu/ontologies/stationentry/>
    select distinct ?stationId ?stationClass ?country ?longName
    from <http://meta.icos-cp.eu/resources/stationentry/>
    where{
      ?s a st:AS .
      ?s st:hasShortName ?stationId .
      ?s st:hasStationClass ?stationClass .
      ?s st:hasCountry ?country .
      ?s st:hasLongName ?longName .
      filter (?stationClass = "1" || ?stationClass = "2")
    }
    ORDER BY ?stationClass ?stationId 
    """

    return query

# -----------------------------------------------------------------------------
def atc_query(tracer,level=2):
    """
        Return SPARQL query to get a list of
        ICOS Atmospheric CO2, CO or MTO, level 2 or level 1 (=NRT) data objects
       :return: SPARQL query to get all ATC Level <level> products for tracer <tracer>
       :rtype: string 
    """
    tracer = tracer.lower().title()
    dataobject = ["NrtGrowingDataObject","L2DataObject"]
    
    query = """
        prefix cpmeta: <http://meta.icos-cp.eu/ontologies/cpmeta/>
        prefix prov: <http://www.w3.org/ns/prov#>
        select ?dobj ?spec ?fileName ?size ?submTime ?timeStart ?timeEnd
        FROM <http://meta.icos-cp.eu/resources/atmprodcsv/>
        where {
                BIND(<http://meta.icos-cp.eu/resources/cpmeta/atc"""+tracer+dataobject[level-1]+"""> AS ?spec)
                ?dobj cpmeta:hasObjectSpec ?spec .
	
                FILTER NOT EXISTS {[] cpmeta:isNextVersionOf ?dobj}
                ?dobj cpmeta:hasSizeInBytes ?size .
                ?dobj cpmeta:hasName ?fileName .
                ?dobj cpmeta:wasSubmittedBy [
                prov:endedAtTime ?submTime ;
                prov:wasAssociatedWith ?submitter
                ] .
                ?dobj cpmeta:hasStartTime | (cpmeta:wasAcquiredBy / prov:startedAtTime) ?timeStart .
                ?dobj cpmeta:hasEndTime | (cpmeta:wasAcquiredBy / prov:endedAtTime) ?timeEnd .
        }
        """
    return query
#------------------------------------------------------------------------------
    
def atc_stationlist(station,tracer='co2',level=2):
    """
        Return SPARQL query to get a list of
        ICOS Atmospheric CO2, CO or MTO, level 2 or level 1 (=NRT) data objects
        for all stations in list
       :return: SPARQL query to get all ATC products for specific stations, tracer and ICOS-level
       :rtype: string 
    """
    tracer = tracer.lower().title()
    dataobject = ["NrtGrowingDataObject","L2DataObject"]
    
    if type(station) == str:
        station = [station]
    strUrl=" "
    for ist in station:
        strUrl = strUrl + " " + """<http://meta.icos-cp.eu/resources/stations/AS_"""+ist+""">"""

    query = """
    prefix cpmeta: <http://meta.icos-cp.eu/ontologies/cpmeta/>
    prefix prov: <http://www.w3.org/ns/prov#>
    select ?dobj ?spec ?fileName ?size ?submTime ?timeStart ?timeEnd
    FROM <http://meta.icos-cp.eu/resources/atmprodcsv/>
    where {
        BIND(<http://meta.icos-cp.eu/resources/cpmeta/atc"""+tracer+dataobject[level-1]+"""> AS ?spec)
        ?dobj cpmeta:hasObjectSpec ?spec .
        VALUES ?station {"""+strUrl+"""} ?dobj cpmeta:wasAcquiredBy/prov:wasAssociatedWith ?station .
        FILTER NOT EXISTS {[] cpmeta:isNextVersionOf ?dobj}
        ?dobj cpmeta:hasSizeInBytes ?size .
        ?dobj cpmeta:hasName ?fileName .
        ?dobj cpmeta:wasSubmittedBy [
            prov:endedAtTime ?submTime ;
            prov:wasAssociatedWith ?submitter
        ] .
        ?dobj cpmeta:hasStartTime | (cpmeta:wasAcquiredBy / prov:startedAtTime) ?timeStart .
        ?dobj cpmeta:hasEndTime | (cpmeta:wasAcquiredBy / prov:endedAtTime) ?timeEnd .
        }
        """
    return query

#------------------------------------------------------------------------------


def icos_hist_L1_L2_sparql(station_code, icos_label):
    
    '''
    Description: Function that returns a pandas DataFrame with file info
                 for a specified station from the drought2018AtmoProduct. 
                
    Input:       1. Station code, characters (var_name: "station_code", var_type: String)
                 2. Station sampling height  (var_name: "samp_height", var_type: Int/Float)
                 3. Label specifying if the station is an ICOS station 
                    (var_name: "icos_label", var_type: Boolean)
    
    Output:      Pandas DataFrame
                
                 1. Data Object ID (var_name: "dobj", var_type: String)
                 2. Data specification (var_name: "spec", var_type: String)
                 3. Filename (var_name: "fileName", var_type: String)
                 4. Size (var_name: "size", var_type: Int)
                 5. Submission time (var_name: "submTime", var_type: String)
                 6. Observation starting time (var_name: "timeStart", var_type: String)
                 7. Observation end date (var_name: "timeEnd", var_type: String)
                 8. Station sampling height (var_name: "samplingHeight", var_type: String)
                
                
    '''    
    
    #If the station is an ICOS station:
    if(icos_label):
        station_label = 'AS_' + station_code
    
    #If the station is NOT an ICOS station:
    else:
        station_label = 'ATMO_' + station_code

       
    #Define SPARQL query:
    query = '''
        prefix cpmeta: <http://meta.icos-cp.eu/ontologies/cpmeta/>
        prefix prov: <http://www.w3.org/ns/prov#>
        select ?dobj ?spec ?fileName ?size ?submTime ?timeStart ?timeEnd ?samplingHeight
        where {
            VALUES ?spec {<http://meta.icos-cp.eu/resources/cpmeta/atcCo2NrtGrowingDataObject>
            <http://meta.icos-cp.eu/resources/cpmeta/atcCo2L2DataObject>
            <http://meta.icos-cp.eu/resources/cpmeta/drought2018AtmoProduct>}
            ?dobj cpmeta:hasObjectSpec ?spec .
            VALUES ?station {<http://meta.icos-cp.eu/resources/stations/'''+station_label+'''>}
            ?dobj cpmeta:wasAcquiredBy/prov:wasAssociatedWith ?station .
            ?dobj cpmeta:hasSizeInBytes ?size .
            ?dobj cpmeta:hasName ?fileName .
            ?dobj cpmeta:wasSubmittedBy/prov:endedAtTime ?submTime .
            ?dobj cpmeta:hasStartTime | (cpmeta:wasAcquiredBy / prov:startedAtTime) ?timeStart .
            ?dobj cpmeta:hasEndTime | (cpmeta:wasAcquiredBy / prov:endedAtTime) ?timeEnd .
            FILTER NOT EXISTS {[] cpmeta:isNextVersionOf ?dobj}
            OPTIONAL{?dobj cpmeta:wasAcquiredBy / cpmeta:hasSamplingHeight ?samplingHeight}
        }
        order by desc(?submTime)
    '''
    return query
#------------------------------------------------------------------------------


def icos_hist_sparql():
    
    '''
    Description: Function that returns a pandas DataFrame with info
                 for all stations included in the drought2018AtmoProduct. 
                
    Input:       No input parameters
    
    Output:      Pandas DataFrame
                
                 1. Station code, 3 characrers (var_name: "Short_name", var_type: String)
                 2. Country code, 2 characters (var_name: "Country", var_type: String)
                 3. Station latitude (var_name: "lat", var_type: String)
                 4. Station longitude (var_name: "lon", var_type: String)
                 5. Station name (var_name: "Long_name", var_type: String)
                 6. Sampling height (var_name: "height", var_type: String)
                
                
    '''
  
    #Define SPARQL query:    
    query = """
        prefix cpmeta: <http://meta.icos-cp.eu/ontologies/cpmeta/>
	prefix prov: <http://www.w3.org/ns/prov#>
	select
	(str(?sName) AS ?Short_name)
	?Country
	?lat ?lon
	(str(?lName) AS ?Long_name)
	?height
	where{
	{
	select distinct ?s ?height
	where {
	?dobj cpmeta:hasObjectSpec <http://meta.icos-cp.eu/resources/cpmeta/drought2018AtmoProduct> .
	?dobj cpmeta:wasAcquiredBy/prov:wasAssociatedWith ?s .
	?dobj cpmeta:hasSizeInBytes ?size .
	OPTIONAL{?dobj cpmeta:wasAcquiredBy/cpmeta:hasSamplingHeight ?height }
	FILTER NOT EXISTS {[] cpmeta:isNextVersionOf ?dobj}
	}
	}
	?s cpmeta:hasStationId ?sName .
	?s cpmeta:hasName ?lName .
	?s cpmeta:countryCode ?Country .
	?s cpmeta:hasLatitude ?lat .
	?s cpmeta:hasLongitude ?lon .
	}
    """
    
    return query
#------------------------------------------------------------------------------



def get_icos_citation(dataObject):
    
    """
    Project:         'ICOS Carbon Portal'
    Created:          Fri May 10 12:35:00 2019
    Last Changed:     Fri May 15 09:55:00 2020
    Version:          1.1.0
    Author(s):        Oleg, Karolina
    
    Description:      Function that takes a string variable representing the URL with data object ID as input and
                      returns a query-string with the citation for the corresponding data object. The data object ID is
                      a unique identifier of every separate ICOS dataset.
    
    Input parameters: Data Object ID (var_name: "dataObject", var_type: String)
    
    Output:           Citation (var_type: String)
    """
    
    #Get data object URL regardless if dobj is expressed as an URL or as an alpharithmetical code (i.e. fraction of URL)
    dobj = __dobjUrl__(dataObject)
    
    #Define SPARQL-query to get the citation for the given data object id:
    query = """
        prefix cpmeta: <http://meta.icos-cp.eu/ontologies/cpmeta/>
        select * where{
        optional{"""+dobj+""" cpmeta:hasCitationString ?cit}}
        """
    
    #Return query-string:
    return query
#------------------------------------------------------------------------------



def icos_prods_per_domain(domain='atmosphere'):
    
    """
    Project:         'ICOS Carbon Portal'
    Created:          Fri Mar 19 09:35:00 2021
    Last Changed:     Fri Mar 19 09:35:00 2021
    Version:          1.0.0
    Author(s):        Oleg, Karolina
    
    Description:      Function that creates a string for a SPARQL query.
                      The query is supposed to return all ICOS L1 & L2 
                      ICOS data product names/ spec labels (incl. pre-ICOS
                      data from InGos and Drought 2018 project data) for
                      the selected domain.
    
    Input parameters: ICOS domain e.g. "atmosphere", "ecosystem" or "ocean"
                      (var_name: "domain", var_type: String)
    
    Output:           SPARQL query (var_type: String)
    
    """
    
    #Check input value:
    if ((domain!='atmosphere') & (domain!='ecosystem') & (domain!='ocean')):
        
        #Error message for invalid input entry:
        print("Invalid input variable! Acceptable domain values are: 'atmosphere', 'ecosystem' or 'ocean'")
        query = ''
    
    #If input entry is valid:
    else:
    
        #Define SPARQL-query to get the available data product names for a given domain:
        query = """ prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        prefix cpmeta: <http://meta.icos-cp.eu/ontologies/cpmeta/>
        select ?specLabel ?spec where{
        ?spec cpmeta:hasDataTheme <http://meta.icos-cp.eu/resources/themes/"""+domain+"""> .
        ?spec cpmeta:hasDataLevel ?dataLevel .
        filter(?dataLevel > 0 && ?dataLevel < 3)
        {
            {?spec cpmeta:hasAssociatedProject <http://meta.icos-cp.eu/resources/projects/icos> }
            UNION
            {
                ?spec cpmeta:hasAssociatedProject?/cpmeta:hasKeywords ?keywords
                filter(contains(?keywords, "pre-ICOS"))
            }
        }
        filter exists{?spec cpmeta:containsDataset []}
        filter exists{[] cpmeta:hasObjectSpec ?spec}
        ?spec rdfs:label ?specLabel .
        }
        order by ?specLabel
        """
    
    #Return query-string:
    return query
#------------------------------------------------------------------------------



def prod_availability(dobj_spec_ls):
    
    """
    Project:         'ICOS Carbon Portal'
    Created:          Fri Mar 19 09:35:00 2021
    Last Changed:     Fri Mar 19 09:35:00 2021
    Version:          1.0.0
    Author(s):        Oleg, Karolina
    
    Description:      Function that creates a string for a SPARQL query.
                      The query is supposed to return a pandas dataframe
                      with metadata for all stations (within a certain domain)
                      that produce the selected data products. The metadata 
                      includes: data object id, station ID, station sampling height 
                      (if applicable), data product specification label,
                      start-date of observations and end-date of observations.
    
    Input parameters: List of ICOS data object specifications
                      (var_name: "dobj_spec_ls", var_type: List of strings)
    
    Output:           SPARQL query (var_type: String)
    
    """
    
    #Check input:
    if (isinstance(dobj_spec_ls, list) & (len(dobj_spec_ls)>0) & (len(dobj_spec_ls)<4)):
        
        #Add '<' and '>' at the begining and the end of every dobj spec label:
        dobj_spec_ls_frmt = ['<'+i+'>' for i in dobj_spec_ls if isinstance(i, str)]
        
        #Export list items to a string:
        dobj_spec_labels = ' '.join(dobj_spec_ls_frmt)
    
        #
        query = """prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        prefix cpmeta: <http://meta.icos-cp.eu/ontologies/cpmeta/>
        prefix prov: <http://www.w3.org/ns/prov#>
        select ?dobj ?samplingHeight ?specLabel ?timeStart ?timeEnd ?stationId
        where {
            {
                select * where {
                    VALUES ?spec {"""+dobj_spec_labels+"""
                    }
                    ?dobj cpmeta:hasObjectSpec ?spec .
                    ?dobj cpmeta:wasAcquiredBy [
                        prov:startedAtTime ?timeStart ;
                        prov:endedAtTime ?timeEnd ;
                        prov:wasAssociatedWith ?station
                    ] .
                    optional {?dobj cpmeta:wasAcquiredBy/cpmeta:hasSamplingHeight ?samplingHeight }
                    FILTER NOT EXISTS {[] cpmeta:isNextVersionOf ?dobj}
                }
            }
            ?station cpmeta:hasStationId ?stationId .
            ?spec rdfs:label ?specLabel
        }"""
        
    else:
        
        #Prompt error message:
        print('Invalid entry! The input has to be a list of 1 to max 3 items.')
        
        #Empty query:
        query = ''
    
    #Return query-string:
    return query

def dobj_for_samplingheight(station, height):
    """
    Return a list of dobj, based on Station Id and SamplingHeight
    used by stiltstation module

    Parameters
    ----------
    station : STR
        ICOS Atmospheric station ID.
    height : INT|FLOAT
        provide a valid sampling height for the station.
        Input must be convertible to FLOAT

    Returns
    -------
    A list of Dobj available for the station at sampling height.

    """ 
    # sanity check
    height = float(height)

    query = """prefix cpmeta: <http://meta.icos-cp.eu/ontologies/cpmeta/>
    prefix prov: <http://www.w3.org/ns/prov#>
    prefix xsd: <http://www.w3.org/2001/XMLSchema#>
    select ?dobj ?hasNextVersion ?spec ?fileName ?size ?submTime ?timeStart ?timeEnd
    where {
    	?spec cpmeta:hasDataLevel [] .
    			FILTER(STRSTARTS(str(?spec), "http://meta.icos-cp.eu/"))
    			FILTER NOT EXISTS {?spec cpmeta:hasAssociatedProject/cpmeta:hasHideFromSearchPolicy "true"^^xsd:boolean}
    	?dobj cpmeta:hasObjectSpec ?spec .
    	BIND(EXISTS{[] cpmeta:isNextVersionOf ?dobj} AS ?hasNextVersion)
    	VALUES ?station {<http://meta.icos-cp.eu/resources/stations/AS_%s>}
    			?dobj cpmeta:wasAcquiredBy/prov:wasAssociatedWith ?station .
    	?dobj cpmeta:hasSizeInBytes ?size .
    ?dobj cpmeta:hasName ?fileName .
    ?dobj cpmeta:wasSubmittedBy/prov:endedAtTime ?submTime .
    ?dobj cpmeta:hasStartTime | (cpmeta:wasAcquiredBy / prov:startedAtTime) ?timeStart .
    ?dobj cpmeta:hasEndTime | (cpmeta:wasAcquiredBy / prov:endedAtTime) ?timeEnd .
    	FILTER NOT EXISTS {[] cpmeta:isNextVersionOf ?dobj}
    ?dobj cpmeta:wasAcquiredBy / cpmeta:hasSamplingHeight ?samplingHeight .
    FILTER( ?samplingHeight = "%s"^^xsd:float )
    }
    order by desc(?submTime) """  % (station, height)

    return query
