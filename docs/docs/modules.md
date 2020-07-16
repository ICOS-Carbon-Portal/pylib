# Content

The following modules are available in the library to find and access data hosted at the Carbon Portal. After a succesful installation into your python environment you should be able to load the modules with:

- `from icoscp.cpb import Dobj`
- `from icoscp.station import station`
- `from icoscp.sparql.runsparql import RunSparql`
- `from icoscp.sparql import sparqls`

<hr>

## dobj

This is the basic module to load a **d**igital **obj**ect (data set) into memory. You need to know a valid persistent identifier (PID/URL) to access the data. Either you can browse the data portal (https://data.icos-cp.eu) to find PID's or you can use the 'station' package to find PID's programatically (see section [station](#station)). In essence each data object is linked to a unique and persistend identifier in the form of a URL. Hence each data object has an online landing page. If you select any data object on https://data.icos-cp.eu and then navigate to the PID link (which looks like 11676/j7-Lxlln8_ysi4DEV8qine_v ) you end up on the 'landing' page of the document. If you look at the address bar of your browser, you will see an URL similar to https://meta.icos-cp.eu/objects/j7-Lxlln8_ysi4DEV8qine_v . To access the data you need to know this URL or the last part of the URL (j7-Lxlln8_ysi4DEV8qine_v).

Load the module with:<br>
`from icoscp.cpb.dobj import Dobj`

classmethod **Dobj(digitalObject='')**<br>
You can initialise a Dobj with a PID. The following two statements yield the same result.<br>
`myDobj = Dobj('https://meta.icos-cp.eu/objects/j7-Lxlln8_ysi4DEV8qine_v')`<br>
`myDobj = Dobj('j7-Lxlln8_ysi4DEV8qine_v')`

Attributes:

### **Dobj.citation**
Citation string

- Return STR

### **Dobj.colNames**
Available column names. This information is part of the Dobj.info, which holds all the available meta data.

- Return pandas.core.series.Series

### **Dobj.dateTimeConvert = True**
Set or retrieve. Default **True**. The binary data representation provides a UTC Timestamp as Unixtimestamp. By default this is converted to a DateTimeObject (**pandas._libs.tslibs.timestamps.Timestamp**). If you prefer to have the raw Unixtimestamp (**numpy.float64**), set Dobj.dateTimeConvert = False prior to issue the .get() command.

- Return BOOL

### **Dobj.dobj = PID**
Set or retrievethe PID for the Dobj, default is empty (""). If a PID is set, an automatic chekck is performed to find the meta data for the object. If this is succesfull, the 'valid' property is set to **True**

- Return STR

### **Dobj.get()**
Retrieve the actual data for the PID.

- Retrun Pandas DataFrame

### **Dobj.valid**
True if PID is set and found at the ICOS Carbon Portal

- Return BOOL

All Dobj related meta data is available in the following properties.

### **Dobj.info**
This will return a list of three pandas data frames which contain meta data.

	info[0] -> information about the dobj like, url, specification, number of rows, related file name.
	info[1] -> information about the data like colName, value type, unit, kind
	info[2] -> information about the station, where the data was obtained. Name, id, lat, lon etc..

- Return LIST[Pandas DataFrame]

### **Dobj.lat**
Latitude for station

- Return FLOAT
	
### **Dobj.lon**
Longitute for station

- Return FLOAT
	
### **Dobj.elevation**
Elevation above sea level for station. Be aware, this is NOT the sampling height for the data points.

- Return FLOAT
	
### **Dobj.station**
Station name

- Return STR


## station
The station module provides a search facility to explore ICOS stations and find associated data objects and data products. There is a lot of information available abouthe the ICOS stations, partner countries, measured variables and much more in the [ICOS Handbook](https://www.icos-cp.eu/sites/default/files/cmis/ICOS%20Handbook%202020.pdf). 

load the module with:<br>
`from icoscp.station import station`

classmethod **station.Station()**<br>
The station object is primarily a data structure to store the associated meta data. The meta data is provided with specific and complex Sparql queries. It is possible to instantiate this class on its own, but we recommend to use the convenience functions `station.getIdList()` `station.get('StationID')` `station.getList()`  as described further below to create the station object. Once you have a created valid station object a list attributes are available:

### **Station.country**
Country code

- Return STR

### **Station.data(level=None)**
All associated data object for the station are returned. ICOS distinguishes data in terms of how processed they are.

	Data level 1: Near Real Time Data (NRT) or Internal Work data (IW).
	Data level 2: The final quality checked ICOS RI data set,
					published by the CFs, to be distributed through the Carbon Portal.
					This level is the ICOS-data product and free available for users.
	Data level 3: All kinds of elaborated products by scientific communities
					that rely on ICOS data products are called Level 3 data.
	
- Return Pandas DataFrame

### **Station.eag**
Elevation above **ground**, if available. Please note, this is a general information  about the height of the tower. This is NOT a sampling height and it is not guranteed to be accurate.

- Return FLOAT

### **Station.eas**
Elevation above **sea level** in meter.

- Return FLOAT

### **Station.icosclass**
Classification for certified ICOS stations. Please consult the [ICOS Handbook](https://www.icos-cp.eu/sites/default/files/cmis/ICOS%20Handbook%202020.pdf) for further information about the Class 1&2 certificate.

- Return STR

### **Station.firstName**
PI (Principal Investigator) First Name.

- Return STR

### **Station.lastName**
PI (Principal Investigator) last name

- Return STR

### **Station.email**
PI (Principal Investigator) email address

- Return STR

### **Station.lat**
Latitude for the station.

- Return FLOAT

### **Station.lon**
Longitude for the station.

- Return FLOAT

### **Station.name**
Returns the full name for the station.

- Return STR

### **Station.project**
ICOS Carbon Portal is a data portal from and for the ICOS community. However, the data portal does host more than ICOS data. The station association is listed here (if available)

- Return LIST

### **Station.stationId**
Set or retrieve the StationId 

- Return STR

### **Station.theme**
For ICOS stations a 'theme' is provided. Please note that, a station may belong to more than one theme, but with different themes. For example the stationId "NOR" (Norunda, Sweden), will give you access to the atmospheric data products, whereas the stationId
 "SE-Nor" will return the Ecosystem data products.
 
	AS for Atmospheric Stations
	ES for Ecosystem Stations
	OS for Ocean Stations
	
- Return STR

### **Station.uri**
Link to the landing page for the station. Because a station ID may be associated with more than one 'project' this returns a list of URI's

- Return LIST

### **Station.valid**
True if stationId is found.

- Return BOOL

### **Convenience functions**
The following three functions are recommend to get information about the available stations at the Carbon Portal and how to get a valid station object (or list of):

`station.getIdList(project='ICOS', sort='name')`

This returns a DataFrame with columns:
	
	['uri', 'id', 'name', 'country', 'lat', 'lon', 'elevation', 'project', 'theme']

By default ICOS certified stations are returned. If project is set to 'all', all known  stations (to the Carbon Portal) are returned. By default the DataFrame is sorted by name. You can provide any column name as sorting parameter. The 'id' of the record, can be used to instantiate  a station. Hence it is easy to adjust and filter these records and use the column 'id' as input for station.get()

- Return Pandas DataFrame

`station.get('StationID')`
Provide a valid station id (see getIdList()) to create a Station object. NOTE: stationId is CaseSensitive.

- Return Station Object

`station.getList(theme=['AS','ES','OS'], ids=None)`

This is the easiest way to get a list of ICOS stations. By default a full list of all certified ICOS stations is returned. You can filter the output by provided a list of themes OR you can provide a list of station id's. NOTE: If you provide a list of id's, the theme filter is ignored. 

	.getList(['as', 'os'])
		list with ICOS atmospheric and ocean stations
	.getList(ids=['NOR', 'HTM', 'HUN'])
		list with stations NOR (Norunda), HTM (Hyltemossa), HUN (Hegyhatsal)

- Return LIST[Station Objects]

## sparql
At the ICOS Carbon Portal we store all data and meta data as linked data in a triple store. For more information about this approach refer to [Semantic Web](https://www.w3.org/standards/semanticweb/), [Resource Description Framework (RDF)](https://www.w3.org/RDF/), and [Triple Stores](https://en.wikipedia.org/wiki/Triplestore).

This module is a simple interface to the [SPARQL endpoint](https://meta.icos-cp.eu/sparqlclient/?type=CSV) at the Carbon Portal. You can write your own queries and use the module to query the database or use some of the provided built in queries. 

Load the module with:<br>
`from icoscp.sparql.runsparql import RunSparql`

classmethod **RunSparql(sparql_query='', output_format='txt')**<br>
sparql_query needs to be a valid query. You can test a query directly at the online SPARQL endpoint at [https://meta.icos-cp.eu/sparqlclient/?type=CSV](https://meta.icos-cp.eu/sparqlclient/?type=CSV). The ouput format is by default (txt/json) but you can adjust with the following formats ['json', 'csv', 'dict', 'pandas', 'array', 'html'].

### **RunSparql.data**
If a query is set and the method .run() was executed, it returns the result from the SPARQL endpoint. If no data is available the method returns False as BOOL.

- Return BOOL | STR

### **RunSparql.query = 'query'**
Retrieve or set the query.

- Return STR

### **RunSparql.format = 'fmt'**
Retrieve or set the output format.
	
	fmt = 'json', 'csv', 'dict', 'pandas', 'array', 'html'

- Return STR

### **RunSparql.format = 'fmt'**
Retrieve or set the output format.
	
	fmt = 'json', 'csv', 'dict', 'pandas', 'array', 'html'

- Return TUPLE | FMT

### **RunSparql.run()**
This method actually executes the query and formats the result to the output format. If the sparql query is not executable because of syntax errors, for example, a TUPLE is returned (False, 'Bad Request')

- Return TUPLE | FMT




<hr>cd20200715