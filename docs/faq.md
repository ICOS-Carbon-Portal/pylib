Things, which have popped up while using this library, and might be of interest

## Q&A

Q: dobj.station returns None<br>
A: The attribute of dobj.station is set only AFTER you have called dobj.data. Not very intuitive and will be rectified in a future release.

Q: Collection data not available<br>
A: Collection is loosely assembled and may contain any kind of files and information. For example it is possible to gather pdf documents and NetCDF and some tabular files in a collection. These files will be presented to you, because they are within the collection. BUT only tabular files (where a preview is available in the data portal) can be accessed directly.
With other words, you can NOT expect that you can 'load' all files listed in a collection.

## Good to Know

- Stations are associated with the stationID. This means that at the moment a combined 
 station, certified for Ecosystem AND Atmosphere, has two different stationId's and hence to access ALL data for such a station you need provide a list of stationId's to find a complete set of data products.
	Example Norunda, Sweden (stationId "SE-Nor" for Ecosystem, stationId "NOR" for Atmosphere).

