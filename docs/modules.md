# Content

The following modules are available in the library to find and access data hosted at the Carbon 
Portal. After a successful installation into your python environment you should be able to load 
the modules with:

- `from icoscp.cpb.dobj import Dobj`
- `from icoscp.station import station`
- `from icoscp.collection import collection`
- `from icoscp.stilt import stiltstation`
- `from icoscp.sparql.runsparql import RunSparql`
- `from icoscp.sparql import sparqls`

<hr><hr>

## Dobj

This is the basic module to load a **d**igital **obj**ect (data set) into memory. You need to 
know a valid persistent identifier (PID/URL) to access the data. Either you can browse the 
[data portal](https://data.icos-cp.eu) to find PID's or you can use the 'station' package to 
find PID's programmatically (see section [station](#station)). In essence each data object is 
linked to a unique and persistent identifier in the form of a URL. Hence, each data object has 
an on-line landing page. If you select any data object on 
[https://data.icos-cp.eu](https://data.icos-cp.eu) and then navigate to the PID link (which 
looks like `11676/j7-Lxlln8_ysi4DEV8qine_v` ) you end up on the 'landing' page of the document. 
If you look at the address bar of your browser, you will see a URL similar to 
[https://meta.icos-cp.eu/objects/j7-Lxlln8_ysi4DEV8qine_v](
https://meta.icos-cp.eu/objects/j7-Lxlln8_ysi4DEV8qine_v). To access the data you need to know 
this URL or the last part of the URL (`j7-Lxlln8_ysi4DEV8qine_v`).

Load the module with:<br>
	from icoscp.cpb.dobj import Dobj

classmethod **Dobj(digitalObject='')**<br>
You can initialise a Dobj with a PID. The following two statements yield the same result.

	myDobj = Dobj('https://meta.icos-cp.eu/objects/j7-Lxlln8_ysi4DEV8qine_v')
	myDobj = Dobj('j7-Lxlln8_ysi4DEV8qine_v')

or create an 'empty' instance and the set the identifier later:

	myDobj = Dobj()
	myDobj.dobj = "j7-Lxlln8_ysi4DEV8qine_v"
<br>

<h2>Attributes:</h2>
<hr>

### **Dobj.citation**
Citation string

- Return STR

### **Dobj.licence**
Licence associated with the dataset.

- Return DICT

### **Dobj.colNames**
Available column names. This information is part of the Dobj.info, which holds all the 
available metadata.

- Return pandas.core.series.Series

### **Dobj.dateTimeConvert = True**
Set or retrieve. Default **True**. The binary data representation provides a UTC Timestamp as 
Unixtimestamp. By default, this is converted to a DateTimeObject
(**pandas._libs.tslibs.timestamps.Timestamp**). If you prefer to have the raw Unixtimestamp 
(**numpy.float64**), set Dobj.dateTimeConvert = False prior to issue the .get() command.

- Return BOOL

### **Dobj.dobj = PID**
See Dobj.id

### **Dobj.id = PID** 
Set or retrieve the PID for the Dobj, default is empty (""). If a PID is set, an automatic 
check is performed to find the metadata for the object. If this is successful, the 'valid' 
property is set to **True**

- Return STR

### **Dobj.data**
Retrieve the actual data for the PID, the same as `.get()`.

- Return Pandas DataFrame

### **Dobj.get()**
Retrieve the actual data for the PID. The same as `.data`

- Return Pandas DataFrame

### **Dobj.valid**
True if PID is set and found at the ICOS Carbon Portal

- Return BOOL

All Dobj related metadata is available in the following properties.

### **Dobj.info**
This will return a list of three pandas data frames which contain metadata.
```
info[0] -> information about the dobj like, url, specification, number of rows, related file name.
info[1] -> information about the data like colName, value type, unit, kind
info[2] -> information about the station, where the data was obtained. Name, id, lat, lon etc..
```

- Return LIST[Pandas DataFrame]

### **Dobj.lat**
Latitude for station

- Return FLOAT
	
### **Dobj.lon**
Longitude for station

- Return FLOAT
	
### **Dobj.elevation**
Elevation above sea level for station. Be aware, this is NOT the sampling height for the data 
points.

- Return FLOAT
	
### **Dobj.station**
Station name

- Return STR

### **Dobj.size()**
The real size of the dobj in [bytes, KB, MB, TB]. Since this object may contain the data, it is 
no longer just a pointer to data.

- Return TUPLE (int32, STR), where int32 represents the size and STR the unit. Example output 
  looks like: (4.353, 'MB')

<hr><hr>

## Station
The station module provides a search facility to explore ICOS stations and find associated data 
objects and data products. There is a lot of information available about the ICOS stations, 
partner countries, measured variables and much more in the 
[ICOS Handbook](https://www.icos-cp.eu/sites/default/files/cmis/ICOS%20Handbook%202020.pdf). 

load the module with:

	from icoscp.station import station

classmethod **station.Station()**<br>
The station object is primarily a data structure to store the associated metadata. The metadata 
is provided with specific and complex Sparql queries. It is possible to instantiate this 
class on its own, but we recommend using the convenience functions `station.getIdList()` 
`station.get('StationID')` `station.getList()`  as described further below to create the 
station object. Once you have a created valid station object a list attributes are available:


<h2>Attributes:</h2>
<hr>

### **Station.country**
Country code

- Return STR

### **Station.data(level=None)**
All associated data object for the station are returned. ICOS distinguishes data in terms of 
how processed they are.

	- Data level 1: Near Real Time Data (NRT) or Internal Work data (IW).
	- Data level 2: The final quality checked ICOS RI data set, published by the CFs, 
					to be distributed through the Carbon Portal. 
					This level is the ICOS-data product and free available for users.
	- Data level 3: All kinds of elaborated products by scientific communities
					that rely on ICOS data products are called Level 3 data.

- Return Pandas DataFrame

### **Station.eag**
Elevation above **ground**, if available. Please note, this is general information about the 
height of the tower. This is NOT a sampling height, and it is not guaranteed to be accurate.

- Return FLOAT

### **Station.eas**
Elevation above **sea level** in meter.

- Return FLOAT

### **Station.icosclass**
Classification for certified ICOS stations. Please consult the 
[ICOS Handbook](https://www.icos-cp.eu/sites/default/files/cmis/ICOS%20Handbook%202020.pdf) for 
further information about the Class 1&2 certificate.

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
ICOS Carbon Portal is a data portal from and for the ICOS community. However, the data portal 
does host more than ICOS data. The station association is listed here (if available)

- Return LIST

### **Station.stationId**
Set or retrieve the StationId 

- Return STR

### **Station.theme**
For ICOS stations a 'theme' is provided. Please note that, a station may belong to more than 
one theme, but with different themes. For example the stationId "NOR" (Norunda, Sweden), will 
give you access to the atmospheric data products, whereas the stationId "SE-Nor" will return 
the Ecosystem data products.
 
	AS for Atmospheric Stations
	ES for Ecosystem Stations
	OS for Ocean Stations
	
- Return STR

### **Station.uri**
Link to the landing page for the station. Because a station ID may be associated with more than 
one 'project' this returns a list of URI's

- Return LIST

### **Station.valid**
True if stationId is found.

- Return BOOL

### **Convenience functions**
The following three functions are recommended to get information about the available 
stations at the Carbon Portal and how to get a valid station object (or list of):

#### station.getIdList()
```
station.getIdList(project='ICOS', sort='name')
```

This returns a DataFrame with columns:

`['uri', 'id', 'name', 'country', 'lat', 'lon', 'elevation', 'project', 'theme']`

By default, ICOS certified stations are returned. If project is set to 'all', all known 
stations (to the Carbon Portal) are returned. By default, the DataFrame is sorted by name. You 
can provide any column name as sorting parameter. The 'id' of the record, can be used to 
instantiate  a station. Hence, it is easy to adjust and filter these records and use the column 
'id' as input for station.get()

- Return Pandas DataFrame  
```
station.getIdList(project='ALL', outfmt='map')
```
If the optional argument `outfmt='map'` is given, a folium map is created with all the queried 
stations provided by the `project` argument. Stations without a fixed location (like 
measurements collected from instrumented Ships of Opportunity) will not be included in the map. 
Each marker in the map represents a station and contains station related information.

- Return Folium Map

#### station.get()

	station.get('stationID')

Provide a valid station id (see getIdList()) to create a Station object. NOTE: stationId is 
CaseSensitive.

- Return Station Object


#### station.getList()

	 station.getList(theme=['AS','ES','OS'], ids=None)

This is the easiest way to get a list of ICOS stations. By default, a full list of all 
certified ICOS stations is returned. You can filter the output by provided a list of themes OR 
you can provide a list of station id's. NOTE: If you provide a list of id's, the theme filter 
is ignored. 

	station.getList(['as', 'os'])
list with ICOS atmospheric and ocean stations

	station.getList(ids=['NOR', 'HTM', 'HUN'])
	
list with stations NOR (Norunda), HTM (Hyltemossa), HUN (Hegyhatsal)

- Return LIST[Station Objects]

<hr><hr>

## Collection

This module supports to load a collection of digital objects. Data products 
([https://www.icos-cp.eu/data-products](https://www.icos-cp.eu/data-products)) or collections 
are an assembly for a specific theme, or project. For example the ICOS community assembled data 
to provide a base for the Drought anomaly in 2018. This dataset was then used to study the 
impact of this extreme event, which ultimately led to a series of publications available as 
'theme issue' in [The Royal Society](https://royalsocietypublishing.org/toc/rstb/2020/375/1810).
Subsequently, the data sets are now public available at the ICOS Carbon Portal 
([Drought-2018 ecosystem eddy covariance flux product for 52 stations](
https://www.icos-cp.eu/data-products/YVR0-4898) and 
[Drought-2018 atmospheric CO2 Mole Fraction product for 48 stations (96 sample heights)](
https://www.icos-cp.eu/data-products/ERE9-9D85). <br>

Load the module with:<br>
	from icoscp.collection import collection

classmethod **Collection(coll)**<br>
(where `coll` represents a `pandas` data frame, similar to the output from .getIdList()). BUT 
only similar. We do **NOT Recommend** to instantiate this class directly. Please **use** the 
function **.get(CollectionId)**. The Purpose of the class documentation is to provide you a 
list of attributes available, after the .get(CollectionId) return a collection object.

<h2>Attributes:</h2>
<hr>

### **Collection.id**
This is the ICOS URI (PID). A link to the landing page on the ICOS data portal.

- Return STR

### **Collection.doi**
If available, the official DOI in form of '10.18160/ry7n-3r04'.

- Return Str

### **Collection.citation**
For convenience the citation string provided from [https://citation.crosscite.org/] is stored 
in this attribute. If you like to have a different format, please have a look at .getCitation 
description below.

- Return STR

### **Collection.title**
- Return STR

### **Collection.description**
- Return STR

### **Collection.info()**
For convenience all the attributes above `(id, doi, citation, title, description)`. You can 
choose the output format with fmt=["dict" | "pandas" | "html"]. The default is "dict".

	info(self, fmt='dict')

- Return FMT, default DICT

### **Collection.datalink**
This returns a list of PID/URI of digital objects associated with the collection.

- Return LIST[STR]

### **Collection.data**
This returns a list of Dobj associated to the collection. Please refer to the module Digital
Object above.

- Return LIST[Dobj]

### **Collection.getCitation()**

	Collection.getCitation(format='apa', lang='en-GB')**

If the collection has a DOI, you will get a citation string from 
[https://citation.crosscite.org/](https://citation.crosscite.org/). You may provide any style & 
language parameters found on the website. Our default style is *apa* and language *en-GB*, 
which  is stored in the attribute `collection.citation`. Use the function getCitation(), if you 
need a specific format & language adaption. Example to get a Bibtex styled citation:
`.getCitation('bibtex','de-CH')`


### **Convenience functions**
The following functions are recommended to get information about the available collections as 
well  as creating an instance of a collection.

#### collection.getIdList()

	collection.getIdList()

This will return a `pandas` data frame, listing all available collections at the data portal. The 
data frame contains the following columns: 
`['collection', 'doi', 'title', 'description', 'dobj', 'count']`. We would recommend that you 
pay close attention to the `count`. We have collections with many data objects associated. If 
you just want to play around, select a collection with less than 10 objects.

- `collection` contains the PID/URI for the collection. This is the ID you need to provide for 
the .get(CollectionId) function. Please be aware that you need to provide the full URI.<br>
Example: .get('https://meta.icos-cp.eu/collections/n7cIMHIyqHJKBeF_3jjgptHP')
- `dobj` contains a list (LIST[STR]) of all PID/URI associated data objects.<br>
- `count` tells you how many data objects are associated with this collection.
<br><br>
- Returns a pandas data frame 

#### collection.get()

	collection.get(CollectionId)

Create a collection object. See the class method above for the attributes available in the 
collection object. The `CollectionId` must be either the full ICOS URI of the collection 
landing page or the DOI (if one is available). Not all collections have a DOI. Both information 
can be extracted with the function .getIdList() .The following to lines to create 
'myCollection' yield the **same result**:

	myCollection = get('https://meta.icos-cp.eu/collections/n7cIMHIyqHJKBeF_3jjgptHP')
	myCollection = get('10.18160/ry7n-3r04')


- Returns Collection

<hr>

## STILT
At the ICOS Carbon Portal we offer a service to calculate your own STILT footprints and 
visualize the results. Find out more on our website
[https://www.icos-cp.eu/data-services/tools/stilt-footprint](
https://www.icos-cp.eu/data-services/tools/stilt-footprint). The calculated footprints and time 
series results are also available through this python library. Please be aware, that the 
calculated **footprints are only available on our servers**, including our virtual 
computational environments. Please read about our public available Jupyter Hub 
[here](https://icos-carbon-portal.github.io/jupyter/). Time series can be accessed from outside 
our servers as well.

load the module with:

	from icoscp.stilt import stiltstation

Two functions are available: one to find STILT stations and one to extract the STILT station as 
an object, which gives access to the data (time series and footprints).
### stiltstation

### .find(\*\*kwargs)
This is the main function to find STILT stations. By default, it returns a dictionary where each 
station id is the key to access metadata about the station. The order how you provide keywords 
is respected and you can influence the result. Keyword arguments are applied sequentially (the 
result from the first keyword is provided as input to the second and so on). With no keyword 
provided `stiltstation.find()` returns a dictionary with ALL Stilt stations.

The following keywords are available:

##### id='STR' | ['STR','STR',...]
Provide a single id as string, or a list of strings.<br>You can provide either STILT or ICOS 
id's mixed together.
	
	stiltstation.find(id=['NOR', 'GAT344'])
	stiltstation.find(id='KIT030')

##### search='STR'
Arbitrary string search will find any occurrence of STR in the station metadata.

	stiltstation.find(search='south')

##### stations=DICT
all actions are performed on this dictionary, rather than dynamically search for all stilt 
station on our server. Can be useful for creating a subset of stations from an existing search.

	myStations = stiltstation.find(search='north')
    refined = stiltstation.find(stations=myStations, country='Finland')
				 
<br><h2>Spatial keywords</h2><br>

##### country='STR' | ['STR','STR',...]
Provide a single country id as string, or a list of strings. You can provide alpha-2, alpha-3 
code (ISO 3166) or the full country name (some translations are available as well). To find all 
STILT stations with geolocation in Norway you can search for either NO, NOR, Norway, Norge.

	stiltstation.find(country=['Swe','norge', 'IT'])

##### bbox=[(lat,lon),(lat,lon)]
Bounding Box. Provide two tuples (wgs84), where the box is defined as TopLeftCorner (NorthWest) 
and BottomRightCorner (SouthEast). The following example returns approximately all stations in 
Scandinavia.

	stiltstation.find(bbox=[(70,5),(55,32)])

##### pinpoint=[lat,lon,distanceKM]
Provide a single point (lat, lon) and the Distance in KM, which creates a bounding box. 
Distance is very roughly translated with 1 degree = 1 km. The bounding box is calculated as 
distance in all directions. For example `distance=200` will create a bounding box of 400 x 400 
km with pinpoint in the centre. If you don't provide a distance, a default value of 200 is used.
```
stiltstation.find(pinpoint=[55.7,13.1,500])		# bounding box ~ 1000km x 1000km
stiltstation.find(pinpoint=[55.7,13.1])			# bounding box ~ 400km x 400km
```

<br><h2>Temporal keywords</h2><br>

Be aware, that the granularity for all temporal keywords is year and month, days are not 
considered in the search. Input format for the dates entry MUST be convertible to data time 
object through pandas.to_datetime().  Accepted formats are:

- datetime.date objs
- FLOAT or INT representing a unix timestamp (seconds since 1970-01-01)
- pandas.datetime
- STR: "YYYY-MM-DD" , "YYYY", "YYYY/MM/DD"

#### sdate='start date'
Stations are returned where results are available for >= start date. 'sdate' is a single entry. 
If you provide sdate AND edate, any station with available data within that date range is 
returned. (accepted formats see above)

    stiltstation.find(sdate= '2018-05-01')

#### edate='end date'
Stations are returned where results are available for <= end date. 'edate' is a single entry. 
If you provide sdate AND edate, any station with available data within that date range is 
returned. (accepted formats see above)

	stiltstation.find(edate='2018-06-01')

#### dates=[]
This will return a list of stations where data is available for any of the provided dates. 
Input format, see sdate,edate. Remember, that only year and month is checked.

	stiltstation.find(dates=['2020-01-01', '2020/05/23'])

#### progress = BOOL
By default a progress bar is displayed while searching all possible STILT stations. With this keyword you can show/hide the progress bar.
	
	stiltstation.find(progress=True)   # DEFAULT, progress bar is displayed
	stiltstation.find(progress=False)  # No progress bar
	
#### outfmt = 'STR'
where string is `dict` | `pandas` | `list` | `map`.
This keyword is ALWAYS executed last, regardless of the position within keyword arguments. By 
default, a `dictionary` is returned. With `pandas` a pandas data frame is returned where the 
station id is indexed, each row contains one station with the same metadata as is available in 
the dictionary [https://pandas.pydata.org/docs/](https://pandas.pydata.org/docs/). List however 
returns a list of STILT station objects. Please see the documentation about<br>
`stiltstation.get(id="")`. Lastly you can choose `map`, which returns a folium map 
[https://python-visualization.github.io/folium/](https://python-visualization.github.io/folium/).
The map can be displayed directly in a Jupyter Notebook, or you can save the map to a html file.

	stiltstation.find(country='Italy', outfmt='pandas') 
	stiltstation.find(country='Italy', outfmt='pandas').save('mymap.html')

### .get(id='', progress=False)
Returns a stilt station object or a list of stilt station objects. A stilt station object, 
gives access to the underlying data (timeseries and footprints). You may provide a STR or
LIST[STR] of STILT id's or the 'result' of a .find() query. The properties of the returned stilt 
object is listed further below.

#### id = STR | LIST[STR]
Provide a string or list of strings representing a STILT station id's.

#### id = DICT | LIST[DICT]
provide a single dictionary, or a list of dictionaries. The dictionaries should be the result of a stiltstation.find() execution.

#### progress = BOOL
By default no progress bar is displayed while assembling the stiltstation object. With this keyword you can show/hide the progress bar. This parameter is only effective while providing id's.

	# return stilt stations based on stiltstation.find(id='STR')
    stiltstation.get('HTM')		    
	stiltstation.get(['KIT','HTM150'], progress = True)

	# return stilt stations based on dictionary or list of dict with a progressbar
	a = stiltstation.find(search='north')
	stiltstation.get(a)
    OR
	stiltstation.get(stiltstation.find(search='south'))

### STILT Object
classmethod **StiltStation(dict)**<br>
Please do not use this class directly. You should load `from icoscp.stilt import stiltstation` 
and then use the function `obj = stiltstation.get('HTM150)` which will return a stilt station 
object. Once you have the object, the following attributes and methods are available:

<h2>Attributes:</h2>

#### .id
Return STILT station ID (e.g. 'HTM150') as string.

#### .locIdent
String with latitude-longitude-altitude of STILT station (e.g. '35.34Nx025.67Ex00150')

#### .alt
Station altitude (in meters above ground level)

#### .lat
Station latitude

#### .lon
Station longitude

#### .name
STILT station long name

#### .icos
None | Dict. If the station is an ICOS station, a dictionary with ICOS metadata is available.

#### .years
List of years for which STILT results are available. Be aware that even if only one day is 
calculated for a year, `year` will be listed.

#### .info
Returns the diction with all metadata.

#### .geoinfo
Dictionary with geographical (country) information, if the station is within a country border.

<h2>Methods:</h2>

#### .get_ts(start_date, end_date, hours=[], columns=''):
STILT concentration time series for a given time period, with optional selection of specific 
hours and columns. Returns time series as a `pandas` data frame.

- start_date : STR, FLOAT/INT (Unix timestamp), datetime object
	- start_date = '2018-01-01'
- end_date : STR, FLOAT/INT (Unix timestamp), datetime object
	- end_date = '2018-01-31'
- hours : STR | INT, optional. If hours is empty or None, ALL Timeslots are returned. For 
  backwards compatibility, input of str format hh:mm is accepted
	- hours = [0,3,6,9,12,15,18,21]
	
			Valid results are returned with LOWER BOUND values.
			Example:    hours = ["02:00",3,4] will return Timeslots for 0, 3
						hours = [2,3,4,5,6] will return Timeslots for 0,3 and 6
						hours = [] return ALL
						hours = ["10", "10:00", 10] returns timeslot 9

- columns : STR, optional
	- Valid entries are `"default", "co2", "co", "rn", "wind", "latlon", "all"`

			default:
				isodate,co2.stilt,co2.fuel,co2.bio, co2.background

			co2
				isodate,co2.stilt,co2.fuel,co2.bio,co2.fuel.coal,
				co2.fuel.oil,co2.fuel.gas,co2.fuel.bio,co2.energy
				co2.transport, co2.industry,co2.others, co2.cement,
				co2.background

			co
				isodate, co.stilt,co.fuel,co.bio,co.fuel.coal
				co.fuel.oil, co.fuel.gas,co.fuel.bio,co.energy
				co.transport,co.industry, co.others, co.cement,
				co.background

			rn
				isodate, rn, rn.era, rn.noah

			wind
				isodate, wind.dir, wind.u, wind.v

			latlon
				isodate, latstart, lonstart

			all
				isodate,co2.stilt,co2.fuel,co2.bio,co2.fuel.coal,
				co2.fuel.oil,co2.fuel.gas,co2.fuel.bio,co2.energy,
				co2.transport, co2.industry,co2.others, co2.cement,
				co2.background, co.stilt,co.fuel,co.bio,co.fuel.coal,
				co.fuel.oil,co.fuel.gas,co.fuel.bio,co.energy,
				co.transport,co.industry,co.others, co.cement,
				co.background,rn, rn.era,rn.noah,wind.dir,
				wind.u,wind.v,latstart,lonstart

#### .get_fp(start_date, end_date, hours=[]):
STILT footprints for a given time period, with optional selection of specific hours.
`Returns` the footprints as `xarray` 
[http://xarray.pydata.org/en/stable/](http://xarray.pydata.org/en/stable/) with latitude, 
longitude, time, and ppm per (micromole m-2 s-1).

- start_date : STR, FLOAT/INT (Unix timestamp), datetime object.
	- start_date = '2018-01-01'
- end_date : STR, FLOAT/INT (Unix timestamp), datetime object.
	- end_date = '2018-01-31'
- hours : STR | INT, optional. If hours is empty or None, ALL Timeslots are returned. For 
  backwards compatibility, input of str format hh:mm is accepted
	- hours = [0,3,6,9,12,15,18,21]
	
			Valid results are returned with LOWER BOUND values.
			Example:    hours = ["02:00",3,4] will return Timeslots for 0, 3
						hours = [2,3,4,5,6] will return Timeslots for 0,3 and 6
						hours = [] return ALL
						hours = ["10", "10:00", 10] returns timeslot 9
<hr>
	
## Sparql
At the ICOS Carbon Portal we store all data and metadata as linked data in a triple store. For 
more information about this approach refer to 
[Semantic Web](https://www.w3.org/standards/semanticweb/), 
[Resource Description Framework (RDF)](https://www.w3.org/RDF/), and 
[Triple Stores](https://en.wikipedia.org/wiki/Triplestore).

This module is a simple interface to the 
[SPARQL endpoint](https://meta.icos-cp.eu/sparqlclient/?type=CSV) at the Carbon Portal. You can 
write your own queries and use the module to query the database or use some of the provided 
built-in queries. 

Load the module with:<br>
`from icoscp.sparql.runsparql import RunSparql`

classmethod **RunSparql(sparql_query='', output_format='txt')**<br>
sparql_query needs to be a valid query. You can test a query directly at the online SPARQL 
endpoint at 
[https://meta.icos-cp.eu/sparqlclient/?type=CSV](https://meta.icos-cp.eu/sparqlclient/?type=CSV).
The output format is by default (txt/json) but you can adjust with the following formats ['json',
'csv', 'dict', 'pandas', 'array', 'html'].


<h2>Attributes:</h2>
<hr>


### **RunSparql.data**
If a query is set and the method .run() was executed, it returns the result from the SPARQL 
endpoint. If no data is available the method returns False (BOOL).

- Return BOOL | STR

### **RunSparql.query = 'query'**
Retrieve or set the query.

- Return STR

### **RunSparql.format = 'fmt'**
Retrieve or set the output format.
	
	fmt = 'json', 'csv', 'dict', 'pandas', 'array', 'html'

- Return STR

### **RunSparql.run()**
This method actually executes the query and formats the result to the output format. If the 
sparql query is not executable because of syntax errors, for example, a TUPLE is returned 
(False, 'Bad Request')

- Return TUPLE | FMT


## Country
Search country information, define global (to icoscp) a common tool to search for country 
information based on a static local file within the library (`country.json`). Search is 
facilitated through Alphanumeric 2 & 3 Code characters and arbitrary text search. Credit to  
[https://github.com/mledoze/countries](https://github.com/mledoze/countries). Further a reverse 
geocoder search is provided through OSM. (credit to 
[https://nominatim.openstreetmap.org](https://nominatim.openstreetmap.org)). 

Please note: in case you provide more than one parameter, the order of keywords is not 
respected. The execution order is always like the function signature and as soon as a result is 
found, it will be returned and the search is stopped.

### country.get(\*\*kwargs)
Accepted keywords: code='', name='', latlon=[], search=''

    Examples:
	.get()                      list of dict: all countries
	.get(code='CH')             dict: Switzerland
	.get(name='greece')         dict: Greece
	.get(latlon=[48.85, 2.35])  dict:
	.get(search='europe')

#### Parameters
    
    code : STR
        Search by ISO 3166-1 2-letter or 3-letter country codes

    name : STR
        search by country name, including alternativ spellings.
        It can be the native name or a partial name.

    latlon : List[]
        List with two integer or floating point numbers representing
        latitude and longitude. BE AWARE: using an external service
        from openstreetmap for reverse geocoding

    search : STR
        arbitrary text search, not case sensitiv, search in all fields

#### Returns

- DICT: if a single country is found
- LIST[DICT]: list of dictionaries if more than one country is found
- BOOL (False) if no result

