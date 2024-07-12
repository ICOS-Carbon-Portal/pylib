# Legacy modules
The following legacy modules are available in the library to find and access
data hosted at the Carbon Portal. After a successful installation into
your python environment you should be able to load the modules with:

- `from icoscp.dobj import Dobj` (recommended)
- `from icoscp.cpb.dobj import Dobj`
- `from icoscp.station import station`
- `from icoscp.collection import collection`
- `from icoscp.sparql.runsparql import RunSparql`
- `from icoscp.sparql import sparqls`

## Dobj
This is the basic module to load a **d**igital **obj**ect (data set)
into memory. You need to know a valid persistent identifier (PID/URL) to
access the data. Either you can browse the [data portal](
https://data.icos-cp.eu) to find PIDs or you can use the "station"
package to find PIDs programmatically (see section [station](#station)
).  
  
In essence each data object is linked to a unique and persistent
identifier in the form of a URL. Hence, each data object has an online
landing page. If you select any data object on 
[https://data.icos-cp.eu](https://data.icos-cp.eu) and then navigate to
the PID link (which looks like `11676/pli1C0sX-HE2KpQQIvuYhX01`) you end
up on the 'landing' page of the document. If you look at the address bar
of your browser, you will see a URL similar to 
[https://meta.icos-cp.eu/objects/pli1C0sX-HE2KpQQIvuYhX01](
https://meta.icos-cp.eu/objects/pli1C0sX-HE2KpQQIvuYhX01). To access the
data you need to know this URL or the last part of the URL
(`pli1C0sX-HE2KpQQIvuYhX01`).

Load the module and initialise the Dobj class with a PID.  
The following statements yield the same result:

```python
from icoscp.dobj import Dobj

dobj = Dobj('https://meta.icos-cp.eu/objects/pli1C0sX-HE2KpQQIvuYhX01')
dobj = Dobj('11676/pli1C0sX-HE2KpQQIvuYhX01')
dobj = Dobj('pli1C0sX-HE2KpQQIvuYhX01')
```

### Properties

#### Dobj.alt
Retrieve the float value representing the altitude above sea level of the
station associated with the Dobj. Be aware, this is not the sampling height for
the data. If the station does not have a specified altitude, return `None`.

Example:
```python
from icoscp.dobj import Dobj

dobj = Dobj('https://meta.icos-cp.eu/objects/pli1C0sX-HE2KpQQIvuYhX01')
altitude = dobj.alt
```

#### Dobj.citation
Return the citation string linked to the Dobj in plain string format.
  
Example:
```python
from icoscp.dobj import Dobj

dobj = Dobj('https://meta.icos-cp.eu/objects/pli1C0sX-HE2KpQQIvuYhX01')
citation = dobj.citation
```
*See also class method [Dobj.get_citation()](#dobjget_citationformat)*

#### Dobj.colNames
Return a list of available column names for a station-specific time
series data object or `None` if no column names are available. This
information is part of the [Dobj.meta](#dobjmeta) property, which holds
all the available metadata.  
Raise a `MetaTypeError` exception for spatiotemporal data objects.

Example:
```python
from icoscp.dobj import Dobj

dobj = Dobj('https://meta.icos-cp.eu/objects/j7-Lxlln8_ysi4DEV8qine_v')
column_names = dobj.colNames
```

#### Dobj.data
Retrieve the actual data for the PID in Pandas DataFrame format.

Example:
```python
from icoscp.dobj import Dobj

dobj = Dobj('https://meta.icos-cp.eu/objects/j7-Lxlln8_ysi4DEV8qine_v')
data = dobj.data
```

#### Dobj.dobj
Retrieve the PID for the Dobj.

Example:
```python
from icoscp.dobj import Dobj

dobj = Dobj('https://meta.icos-cp.eu/objects/pli1C0sX-HE2KpQQIvuYhX01')
pid = dobj.dobj
```
*See also [Dobj.id](#dobjid)*

#### Dobj.elevation
Retrieve the float value representing the elevation above sea level of the
station associated with the Dobj. Be aware, this is not the sampling height for
the data. If the station does not have a specified elevation, return `None`.  
This property will be deprecated in the next release.

Example:
```python
from icoscp.dobj import Dobj

dobj = Dobj('https://meta.icos-cp.eu/objects/pli1C0sX-HE2KpQQIvuYhX01')
elevation = dobj.elevation
```
*See also [Dobj.alt](#dobjalt)*

#### Dobj.id
Retrieve the PID for the Dobj.

Example:
```python
from icoscp.dobj import Dobj

dobj = Dobj('https://meta.icos-cp.eu/objects/pli1C0sX-HE2KpQQIvuYhX01')
pid = dobj.id
```
*See also [Dobj.dobj](#dobjdobj)*


#### Dobj.info
Return a dictionary based on the metadata available from the landing
page of the ICOS Carbon Portal website.  
This property will be deprecated in the next release.

Example:
```python
from icoscp.dobj import Dobj
from pprint import pprint

dobj = Dobj('https://meta.icos-cp.eu/objects/pli1C0sX-HE2KpQQIvuYhX01')
pprint(dobj.info)
```
*See also [Dobj.meta](#dobjmeta)*

#### Dobj.lat
Retrieve the float value representing the latitude of the station associated
with the Dobj. If the station does not have a specified latitude, return
`None`.

Example:
```python
from icoscp.dobj import Dobj

dobj = Dobj('https://meta.icos-cp.eu/objects/pli1C0sX-HE2KpQQIvuYhX01')
latitude = dobj.lat
```

#### Dobj.licence
Return a dictionary with these keys: 'baseLicence', 'name', 'url', 
'webpage', containing information about the dataset's associated
license.

Example:
```python
from icoscp.dobj import Dobj

dobj = Dobj('https://meta.icos-cp.eu/objects/pli1C0sX-HE2KpQQIvuYhX01')
latitude = dobj.lat
```

#### Dobj.lon
Retrieve the float value representing the longitude of the station associated
with the Dobj. If the station does not have a specified longitude, return
`None`.

Example:
```python
from icoscp.dobj import Dobj

dobj = Dobj('https://meta.icos-cp.eu/objects/pli1C0sX-HE2KpQQIvuYhX01')
longitude = dobj.lon
```

#### Dobj.meta
Return a dictionary based on the metadata available from the landing
page of the ICOS Carbon Portal website. Every data object has a rich
set of metadata available. You can download an [example](
https://meta.icos-cp.eu/objects/pli1C0sX-HE2KpQQIvuYhX01/meta.json) from the
data portal. This will then be parsed into a python dictionary representing the
metadata from ICOS. Some of the important key properties, like
'previous', 'next', 'citation', e.t.c., are extracted for easy access and
made available as properties.
  
Example:
```python
from icoscp.dobj import Dobj
from pprint import pprint

dobj = Dobj('https://meta.icos-cp.eu/objects/pli1C0sX-HE2KpQQIvuYhX01')
pprint(dobj.meta)
```

#### Dobj.next
Return a landing page in the form of a string, featuring the next
version of this data object if it exists.  
Return `None` if a next version does not exist.

Example:
```python
from icoscp.dobj import Dobj

dobj = Dobj('https://meta.icos-cp.eu/objects/j7-Lxlln8_ysi4DEV8qine_v')
next_version = dobj.next
```

#### Dobj.previous
Return a landing page in the form of a string, featuring the previous
version of this data object if it exists.  
Return `None` if a previous version does not exist.

Example:
```python
from icoscp.dobj import Dobj

dobj = Dobj('https://meta.icos-cp.eu/objects/j7-Lxlln8_ysi4DEV8qine_v')
previous_version = dobj.previous
```

#### Dobj.station
Return a dictionary containing metadata associated with the station
corresponding to the Dobj. Please be aware that prior to version 0.1.15 this
has returned a string with station id, which is now available as station['id'].

Example:
```python
from icoscp.dobj import Dobj

dobj = Dobj('https://meta.icos-cp.eu/objects/j7-Lxlln8_ysi4DEV8qine_v')
station_meta = dobj.station
```

#### Dobj.valid
Return the validity of a Dobj as a boolean. This is kept for backwards
compatibility reasons. From icoscp 0.2.0 and onwards, the Dobj class cannot be
instantiated with an invalid PID, thus this will always return `True`.  
This property will be deprecated in the next release.

Example:
```python
from icoscp.dobj import Dobj

dobj = Dobj('https://meta.icos-cp.eu/objects/pli1C0sX-HE2KpQQIvuYhX01')
validity = dobj.valid
```

#### Dobj.variables
Return a Pandas DataFrame providing access to all available variables,
including the name, unit, type, and the landing page for the format used
(int, float, char, ...).  
Raise a `MetaValueError` exception if no variable information is
available.

The following example and its output shows the variables of an
atmospheric methane concentration data object:
```python
from icoscp.dobj import Dobj

dobj = Dobj('https://meta.icos-cp.eu/objects/zjNZLdVDcVUNwonvJIN5GQ3b')
variables = dobj.variables
print(variables)
```

Output:

| index | name      | unit       | type                                    | format                                                   |
|-------|-----------|------------|-----------------------------------------|----------------------------------------------------------| 
| 0     | TIMESTAMP | None       | time instant, UTC                       | http://meta.icos-cp.eu/ontologies/cpmeta/iso8601dateTime |
| 1     | Flag      | None       | quality flag                            | http://meta.icos-cp.eu/ontologies/cpmeta/bmpChar         |
| 2     | NbPoints  | None       | number of points                        | http://meta.icos-cp.eu/ontologies/cpmeta/int32           |
| 3     | ch4       | nmol mol-1 | CH4 mixing ratio (dry mole fraction)    | http://meta.icos-cp.eu/ontologies/cpmeta/float32         |
| 4     | Stdev     | nmol mol-1 | standard deviation of gas mole fraction | http://meta.icos-cp.eu/ontologies/cpmeta/float32         |

### Methods

#### Dobj.get(columns)
Retrieve the actual data for the PID in Pandas DataFrame format.
You have the option to retrieve only selected
columns (or variables) using a list of variables as an input argument. Only
valid and unique entries will be returned. You can see valid entries with
[Dobj.colNames](#dobjcolnames) or [Dobj.variables](#dobjvariables). If columns
are not provided, or if none of the provided variables are valid, or if you
work with local data, the default DataFrame (with all columns) will be
returned.

Example:
```python
from icoscp.dobj import Dobj

dobj = Dobj('https://meta.icos-cp.eu/objects/j7-Lxlln8_ysi4DEV8qine_v')
col_names = dobj.colNames
# or
# col_names = dobj.variables['name'].to_list()
data = dobj.get(columns=col_names)
```


#### Dobj.getColumns(columns)
Retrieve the actual data for the PID in Pandas DataFrame format.  

Example:
```python
from icoscp.dobj import Dobj

dobj = Dobj('https://meta.icos-cp.eu/objects/j7-Lxlln8_ysi4DEV8qine_v')
col_names = dobj.colNames
# or
# col_names = dobj.variables['name'].to_list()
data = dobj.getColumns(columns=col_names)
```

*See also [Dobj.get(columns)](#dobjgetcolumns) and [Dobj.data](#dobjdata)*

#### Dobj.get_citation(format)
Return the citation string in different formats. By default, a plain 
formatted string is returned.  
Possible formats are:

- **plain** : (default) a simple string
- **bibtex** : [wikipedia](https://en.wikipedia.org/wiki/BibTeX)
- **ris** : [wikipedia]( https://en.wikipedia.org/wiki/RIS_(file_format))

Example:
```python
from icoscp.dobj import Dobj

dobj = Dobj('https://meta.icos-cp.eu/objects/pli1C0sX-HE2KpQQIvuYhX01')
ris_citation = dobj.get_citation('ris')
```
*See also [Dobj.citation](#dobjcitation)*

---

## Original legacy Dobj
The actual original legacy (prior to version `0.2.0`) `Dobj` class resides in
module `icoscp.cpb.dobj`. Most code is recommended to migrate to the new
implementation of this class residing in module `icoscp.dobj`, but the old
class is preserved to avoid breaking any dependent code by library update,
and additionally, there are some known differences between the versions,
documented below.

### Dobj initialization
Using `from icoscp.cpb.dobj import Dobj`, you can initialize the Dobj class in
one of the following ways:
```python
from icoscp.cpb.dobj import Dobj

my_dobj = Dobj('https://meta.icos-cp.eu/objects/pli1C0sX-HE2KpQQIvuYhX01')
my_dobj = Dobj('11676/pli1C0sX-HE2KpQQIvuYhX01')
my_dobj = Dobj('pli1C0sX-HE2KpQQIvuYhX01')
```
or create an 'empty' Dobj instance and set the identifier later:
```python
from icoscp.cpb.dobj import Dobj

dobj = Dobj()
dobj.dobj = 'https://meta.icos-cp.eu/objects/pli1C0sX-HE2KpQQIvuYhX01'
```

Using `from icoscp.dobj import Dobj`, instantiating an 'empty' Dobj class, and
setting the identifier later will result in a `TypeError`. This functionality
was removed to preserve the `Dobj` class state and prevent unexpected behavior.


### Dobj datetime conversion control
(Not available in the new implementation, as all datetime conversions are
handled by `pandas` library in a uniform way)

**Dobj.dateTimeConvert = True**
The binary data representation provides a UTC Timestamp as Unix-timestamp with
start point of 1970-01-01 00:00:00. By default, when using
`from icoscp.cpb.dobj import Dobj` this is converted to a DateTimeObject of
type `pandas._libs.tslibs.timestamps.Timestamp`. If you prefer to have the raw
Unix-timestamp (**numpy.float64**), set
`Dobj.dateTimeConvert = False` prior to load the data with **.get()** or **.data** or **.getColumns()**.

- Return BOOL

### **Dobj.size()**
(Not available in the new implementation. To get data object size in bytes
from the new `Dobj` class, call `Dobj.metadata.size` or `Dobj.meta['size']`)

The real size of the dobj in [bytes, KB, MB, TB]. Since this object may contain the data, it is 
no longer just a pointer to data.

- Return TUPLE (int32, STR), where int32 represents the size and STR the unit. Example output 
  looks like: (4.353, 'MB')

---

## Station
The station module provides a search facility to explore ICOS stations and find associated data 
objects and data products. There is a lot of information available about the ICOS stations, 
partner countries, measured variables and much more in the 
[ICOS Handbook](https://www.icos-cp.eu/sites/default/files/2022-03/ICOS_Handbook_2022_web.pdf).
load the module with:

	from icoscp.station import station

classmethod **station.Station()**<br>
The station object is primarily a data structure to store the associated metadata. The metadata 
is provided with specific and complex Sparql queries. It is possible to instantiate this 
class on its own, but we recommend using the convenience functions `station.getIdList()` 
`station.get('StationID')` `station.getList()`  as described further below to create the 
station object. Once you have a created valid station object a list of attributes are available:


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
The `station.getIdList` takes several parameters: 
```
project: str = 'ICOS' 
theme: list = None 
sort: str = 'name'
outfmt: str = 'pandas'
icon=None
``` 
The default call `station.getIdList()`, which is the same as 
```
station.getIdList(project='ICOS', sort='name')
```
returns a Pandas DataFrame with columns:


`['uri', 'id', 'name', 'icosClass', 'country', 'lat', 'lon', 'elevation', 'stationTheme', 'firstName', 'lastName', 'email', 'siteType', 'project', 'theme']`

By default, ICOS certified stations are returned. If project is set to `'all'`, all known 
stations (to the Carbon Portal) are returned. By default, the DataFrame is sorted by the column `name`. You 
can provide any column name as sorting parameter. The `'id'` of the record, can be used to 
instantiate a station. Hence, it is easy to adjust and filter these records and use the column 
`'id'` as input for `station.get()`. 

The theme parameter can be set to either `'AS'`, `'ES'` or `'OS'`, or a list with a combination of these strings. 
Here `'AS'`, `'ES` and `'OS'` are short for atmospheric, ecosystem and ocean stations.    

Thus, 
```
station.getIdList(theme='AS')
```
will return a DataFrame with all atmospheric ICOS stations. 

If the optional argument `outfmt='map'` is provided
```
station.getIdList(project='ALL', outfmt='map', icon=None)
```
a folium map is created with, in this case, all stations (since we use `project='ALL'`). Stations without a fixed location (like 
measurements collected from instrumented Ships of Opportunity) will not be included in the map. 
Each marker in the map represents a station and contains station related information. A user can
further customize the style of the map by providing the `icon` argument `[None, 'flag', 'path/to/image.png']`.

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
(where `coll` represents a `pandas.DataFrame`, similar to the output from .getIdList()). BUT 
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

- Return STR

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

This will return a `pandas.DataFrame`, listing all available collections at the data portal. The 
DataFrame contains the following columns: 
`['collection', 'doi', 'title', 'description', 'dobj', 'count']`. We would recommend that you 
pay close attention to the `count`. We have collections with many data objects associated. If 
you just want to play around, select a collection with less than 10 objects.

- `collection` contains the PID/URI for the collection. This is the ID you need to provide for 
the .get(CollectionId) function. Please be aware that you need to provide the full URI.<br>
Example: .get('https://meta.icos-cp.eu/collections/n7cIMHIyqHJKBeF_3jjgptHP')
- `dobj` contains a list (LIST[STR]) of all PID/URI associated data objects.<br>
- `count` tells you how many data objects are associated with this collection.
<br><br>
- Returns a pandas DataFrame 

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

<hr>  
