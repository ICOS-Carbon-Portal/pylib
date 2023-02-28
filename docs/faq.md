#
Things, which have popped up while using this library, and might be of interest.

## How can I get an overview of a digital object's metadata?
You can use the following code, to print all keys from a nested dictionary. The example extracts the station
information associated with the data object. This information is a 'subset' from the metadata 
`do.meta['specificInfo']['acquisition']['station']` or, yielding the same information, through the convenience property:
`do.station`.
	
    from icoscp.cpb.dobj import Dobj

	dobj = Dobj('j7-Lxlln8_ysi4DEV8qine_v')
	
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

## dobj.station returns None. What am I doing wrong?
The attribute of dobj.station is set only AFTER you have called dobj.data. Not very intuitive and will be rectified in 
a future release.<br> 
** update ** (>=version 0.1.15): The full meta data information about a digital object is available immediately.

## Why can't I access all files within a collection?
Collection is loosely assembled and may contain any kind of files and information. For example, it is possible to 
gather pdf documents and NetCDF and some tabular files in a collection. These files will be presented to you, because 
they are within the collection. **BUT** only tabular files (where a preview is available in the data portal) can be 
accessed directly. In other words, you can NOT expect that you can 'load' all files listed in a collection.

## How can I retrieve the latest/newest version of a dataset?
Sometimes after loading a dataset, .next might return a PID. Hence, you are not looking at the newest version of the 
data. The following code snippet will loop through the pid, returning the newest version:
	
	from icoscp.cpb.dobj import Dobj
	dobj = Dobj('https://meta.icos-cp.eu/objects/lNJPHqvsMuTAh-3DOvJejgYc')
	
	while dobj.valid:
		if dobj.next:
			dobj = Dobj(dobj.next)
		else:
			break
	# Now dobj is the newest version.
	
## Good to Know

- Stations are associated with the stationID. This means that at the moment a combined station, certified for Ecosystem 
AND Atmosphere, has two different stationId's and hence to access ALL data for such a station you need provide a list of
stationId's to find a complete set of data products. Example Norunda, Sweden (stationId "SE-Nor" for Ecosystem, 
stationId "NOR" for Atmosphere).

## Iteration over `station_id_df` displays `station.name` as an index 
The dataframe provided by `station.getIdList` has a column for station names called "name", `pandas.DataFrame` has an 
implementation where each column is turned into a attribute. An iteration over the rows, like in the below example, will not 
give the station name

	from icoscp.station import station
    df = station.getIdList(project='all')
    for _, row in df.iterrows():
        if row.theme in ['ES', 'FluxnetStation']:
            print(row.name, row.id, row.uri)
	
	0 SE-Sto http://meta.icos-cp.eu/resources/stations/ES_SE-Sto
    1 ES-Agu http://meta.icos-cp.eu/resources/stations/FLUXNET_ES-Agu
    ...
    214 GL-ZaF http://meta.icos-cp.eu/resources/stations/ES_GL-ZaF
    215 GL-ZaH http://meta.icos-cp.eu/resources/stations/ES_GL-ZaH

The reason is that each `row` that is unpacked in the loop is a pandas Series object, and the Series object has an attribute 
called `name`, holding the name of the series - in this case it is the dataframe index of the row.

Examples on how to avoid this.

1. Use a dictionary-style call instead of a attribute-style call:

        ...
        for _, row in df.iterrows():
            if row.theme in ['ES', 'FluxnetStation']:
                print(row['name'], row.id, row.uri)
    

2. Print a subframe and avoid the iteration:

	    ...
	    df2 = df[df['theme'].isin(['ES', 'FluxnetStation'])]
	    print(df2[['name', 'id', 'uri']].to_string())
	

3. Use the "name"-column as the index:
	    
		...
		df.set_index('name', inplace=True)
	    for _, row in df.iterrows():
	        if row.theme in ['ES', 'FluxnetStation']:
            print(row.name, row.id, row.uri)

4. Rename the column "name":

        ...
		df.rename(columns={'name': 'station_name'}, inplace=True)
        for _, row in df.iterrows():
            if row.theme in ['ES', 'FluxnetStation']:
                print(row.station_name, row.id, row.uri)
