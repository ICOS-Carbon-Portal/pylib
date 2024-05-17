# Legacy modules

These modules contain code that may be gradually deprecated in favour of new
code in `icoscp_stilt.stilt`. The following documentation and the code it
describes have been with minimal changes moved from `icoscp` library prior
to version `0.2.0`

## stiltstation

load the module with:

```Python
	from icoscp_stilt import stiltstation
```
Two functions are available: one to find STILT stations and one to extract the STILT station as 
an object, which gives access to the data (time series and footprints).

### .find(\*\*kwargs)
This is the main function to find STILT stations. By default, it returns a dictionary where each 
station id is the key to access metadata about the station. The order how you provide keywords 
is respected and you can influence the result. Keyword arguments are applied sequentially (the 
result from the first keyword is provided as input to the second and so on). With no keyword 
provided `stiltstation.find()` returns a dictionary with ALL Stilt stations.

The following keywords are available:

#### id='STR' | ['STR','STR',...]
Provide a single id as string, or a list of strings.<br>You can provide either STILT or ICOS 
id's mixed together.
	
	stiltstation.find(id=['NOR', 'GAT344'])
	stiltstation.find(id='KIT030')

#### search='STR'
Arbitrary string search will find any occurrence of STR in the station metadata.

	stiltstation.find(search='south')

##### stations=DICT
all actions are performed on this dictionary, rather than dynamically search for all stilt 
station on our server. Can be useful for creating a subset of stations from an existing search.

	myStations = stiltstation.find(search='north')
    refined = stiltstation.find(stations=myStations, country='Finland')
				 
<br><h2>Spatial keywords</h2><br>

#### country='STR' | ['STR','STR',...]
Provide a single country id as string, or a list of strings. You can provide alpha-2, alpha-3 
code (ISO 3166) or the full country name (some translations are available as well). To find all 
STILT stations with geolocation in Norway you can search for either NO, NOR, Norway, Norge.

	stiltstation.find(country=['Swe','norge', 'IT'])

#### project='icos'
This option will retrieve all STILT stations that are ICOS stations.

#### bbox=[(lat,lon),(lat,lon)]
Bounding Box. Provide two tuples (wgs84), where the box is defined as TopLeftCorner (NorthWest) 
and BottomRightCorner (SouthEast). The following example returns approximately all stations in 
Scandinavia.

	stiltstation.find(bbox=[(70,5),(55,32)])

#### pinpoint=[lat,lon,distanceKM]
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
where string is `dict` | `pandas` | `list` | `map` | `avail`.
This keyword is ALWAYS executed last, regardless of the position within keyword arguments. By 
default, a `dictionary` is returned. With `pandas` a pandas DataFrame is returned where the 
station id is indexed, each row contains one station with the same metadata as is available in 
the dictionary [https://pandas.pydata.org/docs/](https://pandas.pydata.org/docs/). List however 
returns a list of STILT station objects. Please see the documentation about<br>
`stiltstation.get(id="")`. The choice `map`, returns a folium map 
[https://python-visualization.github.io/folium/](https://python-visualization.github.io/folium/).
The map can be displayed directly in a Jupyter Notebook, or you can save the map to a html file.

	stiltstation.find(country='Italy', outfmt='pandas') 
	stiltstation.find(country='Italy', outfmt='pandas').save('mymap.html')

Finally, the choice `avail` will return a pandas DataFrame where availability of timeseries data 
per STILT station is gathered for each year. 

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

## stiltobj
Internal-implementation module

### STILT Object
classmethod **StiltStation(dict)**<br>
Please do not use this class directly. You should load `from icoscp_stilt import stiltstation` 
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
Returns a dictionary with all metadata.

#### .geoinfo
Dictionary with geographical (country) information, if the station is within a country border.

<h2>Methods:</h2>

#### .get_ts(start_date, end_date, hours=None, columns=''):
STILT concentration time series for a given time period, with optional selection of specific 
hours and columns. Returns time series as a `pandas.DataFrame`.

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
				isodate, co2.stilt, co2.bio, co2.fuel, co2.cement, co2.background

			co2
				isodate, co2.stilt, co2.bio, co2.fuel, co2.cement,
				co2.bio.gee, co2.bio.resp, co2.fuel.coal, co2.fuel.oil, co2.fuel.gas,
				co2.fuel.bio, co2.fuel.waste, co2.energy, co2.transport, co2.industry,
				co2.residential, co2.other_categories, co2.background

			co
				isodate, co.stilt, co.fuel, co.cement, 
				co.fuel.coal, co.fuel.oil, co.fuel.gas, 
				co.fuel.bio, co.fuel.waste, co.energy
				co.transport, co.industry, co.residential, 
				co.other_categories, co.background

			rn
				isodate, rn, rn.era, rn.noah

			wind
				isodate, wind.dir, wind.u, wind.v

			latlon
				isodate, latstart, lonstart

			all
				isodate, co2.stilt, co2.bio, co2.fuel, co2.cement, 
				co2.bio.gee, co2.bio.resp, 
				co2.fuel.coal, co2.fuel.oil, co2.fuel.gas, 
				co2.fuel.bio, co2.fuel.waste, 
				co2.energy, co2.transport, co2.industry,
				co2.residential, co2.other_categories,
				co2.background,
				co.stilt, co.fuel, co.cement,
				co.fuel.coal, co.fuel.oil, co.fuel.gas,
				co.fuel.bio, co.fuel.waste, 
				co.energy, co.transport, co.industry,
				co.residential, co.other_categories,
				co.background,
				rn, rn.era, rn.noah, wind.dir,
				wind.u, wind.v, latstart, lonstart

#### .get_fp(start_date, end_date, hours=None):
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

#### .get_dobj_list():
If the stiltstation has a corresponding ICOS station, this function will return a dictionary filled with corresponding data objects. A sparql query is executed with ICOS Station id and the sampling height as constraint, returning all data objects (Level 1, 2, 3).

Returns: List of DICT Each dictionary with the following keys: [dobj,hasNextVersion,spec,fileName,size,submTime,timeStart,timeEnd]

Example output:
	
		[{
			'dobj': 'https://meta.icos-cp.eu/objects/1DZZOAmmB8YAfYPvXuHMj7Er',
			'hasNextVersion': 'false',
			'spec': 'http://meta.icos-cp.eu/resources/cpmeta/atcN2oNrtGrowingDataObject',
			'fileName': 'ICOS_ATC_NRT_OXK_2022-03-01_2023-02-27_23.0_534_N2O.zip',
			'size': '110076',
			'submTime': '2023-02-28T11:16:27.804Z',
			'timeStart': '2022-03-01T00:00:00Z',
			'timeEnd': '2023-02-27T23:00:00Z'
		},
		...