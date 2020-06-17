#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
    
    if len(dobj.split('/')) > 1:
        # we assume the full url / handle is provided as string
        url = '<' + dobj + '>'        
    else:
        # we assume only the PID is provided
        url = '<https://meta.icos-cp.eu/objects/'+ dobj + '>'
        
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
				prov:wasAssociatedWith/cpmeta:hasName ?station ;
				cpmeta:hasSamplingHeight ?samplingHeight
			] .			
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

def collections(limit=0):
    """ Return all known collections """

    query = """
            prefix cpmeta: <http://meta.icos-cp.eu/ontologies/cpmeta/>
            prefix dcterms: <http://purl.org/dc/terms/>
            select * where{
            ?coll a cpmeta:Collection .
            OPTIONAL{?coll cpmeta:hasDoi ?doi}
            ?coll dcterms:title ?title .
            }
            %s
            """ % __checklimit__(limit)

    return query

# -----------------------------------------------------------------------------
def stationResource(stationId):
    """
    returns query to ask for the station ressource url and 
    latitute and longitude from the dataportal (NOT labelling app)
    
    Param: str, stationID like HTM or SE-NOR

    Returns str

    """
    query = """
			prefix cpmeta: <http://meta.icos-cp.eu/ontologies/cpmeta/>
			SELECT *
			FROM <http://meta.icos-cp.eu/resources/icos/>
			WHERE {
			  ?s cpmeta:hasStationId ?id .
              FILTER (?id = "%s")
			  ?s cpmeta:hasLatitude ?lat .
			  ?s cpmeta:hasLongitude ?lon .
			}
            """ % stationId
    return query

# -----------------------------------------------------------------------------

def stationData(station, level='2'):
    """
    Define SPARQL query to get a list of data objects for a specific station.

    Parameters
    ----------
    station : str , Station ID.
    level : str , optional,  ['1','2','3','all'] 
            find data products for icos level. The default is 2.

    Returns
    -------
    query : str , valid sparql query.
    """
    accepted_levels = [1,2,3]
    try:
        if not (isinstance(station, str) or isinstance(level,str)):
            return
        if level.lower() == 'all':
            level = '>0'
        elif not int(level) in accepted_levels:
            level=' = 2'
        else:
            level = ' = ' + level
    except:
        return 'input parameters not valid'

    query = """
			prefix cpmeta: <http://meta.icos-cp.eu/ontologies/cpmeta/>
			prefix prov: <http://www.w3.org/ns/prov#>
#			select ?datalevel ?dobj ?spec ?station ?timeStart ?timeEnd
			select *
			where {
				VALUES ?station {<%s>}                                 
				?dobj cpmeta:hasObjectSpec ?spec .	
				FILTER NOT EXISTS {?spec cpmeta:hasAssociatedProject/cpmeta:hasHideFromSearchPolicy "true"^^xsd:boolean}
				FILTER NOT EXISTS {[] cpmeta:isNextVersionOf ?dobj}				
				?dobj cpmeta:wasAcquiredBy / prov:startedAtTime ?timeStart .
				?dobj cpmeta:wasAcquiredBy / prov:endedAtTime ?timeEnd .
				?dobj cpmeta:wasAcquiredBy/prov:wasAssociatedWith ?station .                                                
                ?spec rdfs:label ?specLabel .                
                #OPTIONAL (?dobj cpmeta:hasSamplingHeight ?samplingHeight ) 
                ?dobj cpmeta:wasAcquiredBy/cpmeta:hasSamplingHeight ?samplingheight.
                
                
				?spec cpmeta:hasDataLevel ?datalevel .
				FILTER (?datalevel  %s)				
            }          """ % (station, level)

    return query

def stations_with_pi(limit=0):
    """
        Define SPARQL query to get a list of ICOS stations with PI and email.
        As per writing, (April 2019, the list is pulled from the provisional
        data, labeling process)
    """

    query = """
            prefix st: <http://meta.icos-cp.eu/ontologies/stationentry/>
            select distinct ?stationId ?stationName ?stationTheme 
            ?class  ?siteType
            ?lat ?lon ?eas ?eag ?firstName ?lastName ?email ?country
            from <http://meta.icos-cp.eu/resources/stationentry/>
            where{
                optional{?s st:hasLon ?lon} .
                optional{?s st:hasLat ?lat} .
                optional{?s st:hasElevationAboveSea ?eas} .
                optional{?s st:hasElevationAboveGround ?eag} .
                ?s st:hasShortName ?stationId .
                ?s st:hasLongName ?stationName .
                ?s st:hasPi ?pi .
                ?pi st:hasFirstName ?firstName .
                ?pi st:hasLastName ?lastName .
                ?pi st:hasEmail ?email .
                ?s a ?stationClass .
                ?s st:hasStationClass ?class .
                optional{?s st:hasCountry ?country} .
                optional{?s st:hasSiteType ?siteType} .
                
                BIND (replace(str(?stationClass), "http://meta.icos-cp.eu/ontologies/stationentry/", "") AS ?stationTheme )
            }            
            %s
        """ % __checklimit__(limit)

    return query
# -----------------------------------------------------------------------------

def cpbGetInfo(dobj):
    """
        Define SPARQL query to get information about a digitial object
        aiming to assmble the underlying binary data structure schema for
        a fast access to the binary file.
        Input dobj: Persisten Identifier
        dobj may be in the form of the PID or the full handle
    """
   
    query = """
            prefix cpmeta: <http://meta.icos-cp.eu/ontologies/cpmeta/>
            select * where {
                values ?dobj { %s }
                ?dobj cpmeta:hasObjectSpec ?objSpec ;
                cpmeta:hasNumberOfRows ?nRows ;
                cpmeta:hasName ?fileName .
                ?objSpec rdfs:label ?specLabel .
                OPTIONAL{?dobj cpmeta:hasActualColumnNames ?columnNames }
            }
            
            """ %__dobjUrl__(dobj)

    return query
# -----------------------------------------------------------------------------
def cpbGetSchemaDetail(formatSpec):
    """
        Define SPARQL query to get information about a digitial object
        to assmble the underlying binary data structure schema for
        access to the binary file.
        :param formatSpec url for the specification  
    """

    query = """
            prefix cpmeta: <http://meta.icos-cp.eu/ontologies/cpmeta/>
            SELECT distinct ?objFormat ?colName ?valueType ?valFormat ?unit ?qKind ?colTip ?isRegex
            WHERE {
                <%(formSpec)s> cpmeta:containsDataset ?dset .
                <%(formSpec)s> cpmeta:hasFormat ?objFormat .
                ?dset cpmeta:hasColumn ?column .
                ?column cpmeta:hasColumnTitle ?colName ;
                    cpmeta:hasValueFormat ?valFormat ;
                    cpmeta:hasValueType ?valType .                
                ?valType rdfs:label ?valueType .
                optional{?valType rdfs:comment ?colTip }
                optional{
                    ?valType cpmeta:hasUnit ?unit .
                    ?valType cpmeta:hasQuantityKind [rdfs:label ?qKind ] .
                }
            } order by ?colName                       
            """ % {'formSpec': formatSpec}
    return query

# -----------------------------------------------------------------------------
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
          ?pi cpmeta:hasMembership ?piMemb .
          ?piMemb cpmeta:atOrganization ?station  .
           ?piMemb cpmeta:hasRole <http://meta.icos-cp.eu/resources/roles/PI> .
           filter not exists {?piMemb cpmeta:hasEndTime []}
           ?pi cpmeta:hasLastName ?piLname .
        }
        group by ?station
        }
        ?station a cpmeta:AS .
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
              prov:wasAssociatedWith/cpmeta:hasName ?stationName 
            ] .
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

