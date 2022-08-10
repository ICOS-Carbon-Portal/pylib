Things, which have popped up while using this library, and might be of interest

## Q&A
### Q1:
The new meta data available in a digital object has many nested dictionaries. Can I print all the keys to get an overview of what information is available?<br>
A: You can use the following code, to print all keys from a nested dictionary. The example extracts the station information associated with the data object. This information is a 'subset' from the metadata `do.meta['specificInfo']['acquisition']['station']` or,  yielding the same information, through the convenience property: `do.station`.

	from icoscp.cpb.dobj import Dobj
	do = Dobj('j7-Lxlln8_ysi4DEV8qine_v')
	
	def get_keys(dictionary):
		result = []
		for key, value in dictionary.items():
			if type(value) is dict:
				new_keys = get_keys(value)
				result.append(key)
				for innerkey in new_keys:
					result.append(f'{key}/{innerkey}')
			else:
				result.append(key)
		return result

	metadata = do.station
	keys = get_keys(metadata)
	print(keys)
	
output of all **keys** for the station metadata:

`
 'id',
 'location',
 'location/alt',
 'location/label',
 'location/lat',
 'location/lon',
 'org',
 'org/name',
 'org/self',
 'org/self/comments',
 'org/self/label',
 'org/self/uri',
 'pictures',
 'responsibleOrganization',
 'responsibleOrganization/name',
 'responsibleOrganization/self',
 'responsibleOrganization/self/comments',
 'responsibleOrganization/self/label',
 'responsibleOrganization/self/uri',
 'responsibleOrganization/website',
 'specificInfo',
 'specificInfo/_type',
 'specificInfo/countryCode',
 'specificInfo/discontinued',
 'specificInfo/documentation',
 'specificInfo/labelingDate',
 'specificInfo/stationClass',
 'specificInfo/theme',
 'specificInfo/theme/icon',
 'specificInfo/theme/markerIcon',
 'specificInfo/theme/self',
 'specificInfo/theme/self/comments',
 'specificInfo/theme/self/label',
 'specificInfo/theme/self/uri',
 'specificInfo/timeZoneOffset',
 'specificInfo/wigosId'
`

### Q2:
dobj.station returns None<br>
A: The attribute of dobj.station is set only AFTER you have called dobj.data. Not very intuitive and will be rectified in a future release.<br>
** update ** (>=version 0.1.15): The full meta data information about a digital object is available immediately.

### Q3:
Collection data not available<br>
A: Collection is loosely assembled and may contain any kind of files and information. For example it is possible to gather pdf documents and NetCDF and some tabular files in a collection. These files will be presented to you, because they are within the collection. BUT only tabular files (where a preview is available in the data portal) can be accessed directly.
With other words, you can NOT expect that you can 'load' all files listed in a collection.

### Q4:
I have loaded a dataset, but found out that .next returns a PID. Hence I am not looking at the newest data. How can I retrieve the latest/newest version?

A: The following code snippet will loop through the pid, returning the newest version:
	
	from icoscp.cpb.dobj import Dobj
	dobj = Dobj('https://meta.icos-cp.eu/objects/lNJPHqvsMuTAh-3DOvJejgYc')
	
	while dobj.valid:
		if dobj.next:
			dobj = Dobj(dobj.next)
		else:
			break
	# now dobj is the newest version
	
## Good to Know

- Stations are associated with the stationID. This means that at the moment a combined 
 station, certified for Ecosystem AND Atmosphere, has two different stationId's and hence to access ALL data for such a station you need provide a list of stationId's to find a complete set of data products.
	Example Norunda, Sweden (stationId "SE-Nor" for Ecosystem, stationId "NOR" for Atmosphere).

