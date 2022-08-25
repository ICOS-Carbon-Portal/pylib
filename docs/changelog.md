# Changelog

## 0.1.16
 - #### stiltobj
     - Increase perfomance to load footprint data faster by 25%.
       Xarray has default value of decode_cf=True, changed to False.
 - #### sparql
     - Remove methods with unused queries `cpbGetInfo(dobj)` and `cpbGetSchemaDetail(formatSpec)`.
     - Speed up queries in methods `objectSpec(spec='atcCo2L2DataObject', station='', limit=0)`, 
     `getStations(station = '')`, `get_coords_icos_stations_atc()`, and `get_icos_stations_atc_L1()`.

## 0.1.15
 - #### cpb module
     - Dobj change to read metadata from http request. Instead of using sparql queries, a http request is used to load 
       the same meta data as available from the website.
     - Add new script to extract metadata from server `metadata.py`.
     - Add new property `.meta` returns a dictionary based on the meta data available from the landing page of a data 
       object containing a very rich set of information. An example: 
       [https://meta.icos-cp.eu/objects/M8STRfcQfU4Yj7Uy0snHvlve/meta.json](
       https://meta.icos-cp.eu/objects/M8STRfcQfU4Yj7Uy0snHvlve/meta.json)
     - Add new property: `.previous` Return the pid/url of the previous version of this file if available.
     - Add new property: `.next` -> Return the pid/url of the next version of this file if available.
     - Add new property: `.variables` Return a PandasDataFrame with metadata for all variables 
       ['name', 'unit', 'type', 'format'].
     - Add new property: `.alt` Returns altitude of station, the same as `.elevation`.
     - Remove properties: `._info1`, `._info2`, `._info3` from Dobj.
     - Change `.info` (consisted of info 1,2,3,) and return `.meta` instead.
     - Change `.station`: Returns a dictionary with a subset of .meta describing the station.
     - Change of `.colNames`: returns now a list of strings with all variable names instead of a pandas core series.
     - License is extracted dynamically from the metadata per object.
     - Add new method `get_citation(format='plain')`. Returns the citation by default as plain string, the same as 
       .citation (property) which internally calls this method. Argument options are ('bibtex', 'ris', 'plain') -> 
       `.citation('bibtex'|'ris'|'plain')`.
     - `print(Dobj)` output of \_\_str\_\_ changed to plain citation string, instead of pid.
     - References to server calls moved to `const.py`.
     - Rename file dtype_dict.py to dtype.py for better readability.
     - add simple unit test and implement initial assertions for the cpb module.
 - #### Access to data
     - `.data` [property] will always return all columns.
     - `.get(columns=None)` [method] returns all data by default. Provides the possibility to extract specific columns 
       from the data set. Expected is a list of column names, which then returns only the selected columns. Non valid 
       entries are removed from the list (if only non valid entries are provided, an empty list by default returns all 
       columns). Please be aware, that `.get()` will ALWAYS return ALL columns if executed on the Carbon Portal server. 
       Valid entries can be obtained with `.colNames` or `.variables['name'].
     - `.getColumns(columns=None)`, this is exactly the same as .get(columns='None'). We keep this function for
       compatibility to previous versions.
 - #### Other changes
     - add `icon` argument to `station.getIdList()` function.
     - regenerate STILT module's static `stations.json`.
     - resolve deprecation warnings from `numpy` calls.
     - implement `stiltstation.find()` by `project`.
     - add `outfmt='avail'` argument to `stiltstation.find()` function to generate an availability table for 
       `STILT stations`.
     - fix `stiltstation.find(outfmt='list')`.
     - fix `print(stiltobj)` by removing country information. Country information can still be retrieved using the
       `.info` attribute of the `StilStation` object. 

## 0.1.14
- update `get_ts()` to case-insensitive and include `co2.bio.gee` and `co2.bio.resp` in the 
  `co2` results
- correctly redirect nominatim requests when icos nominatim is unable to reverse geocode.

## 0.1.13
- rework directory listing of STILT stations and ignore queued but empty stations

## 0.1.12
- fix `stiltstation.find()` to return all STILT stations
- switch to ICOS reverse geocoder as default
- precompute all known stations to speed up search functions
- if possible, use ICOS station's latitude/longitude when reverse geocoding a STILT station for 
  precision

## 0.1.11
- rework process of requesting stilt stations
- add a progress bar when requesting stilt stations
- update user information when using the stilt module
- add stilt data reporting to the back-end

## 0.1.10
- adjust pylib version reported to the back-end
- include non-code files to distribution
- inform users when wrongly accessing the Stilt module locally

## 0.1.9
- add Stilt module and documentation
- add local country information
- add folium map extension to `getIdList()` function

## 0.1.8
- change licence on https://pypi.org/project/icoscp/ to https://www.icos-cp.eu/data-services/about-data-portal/data-license
- adjust portal use internal flag

## 0.1.7
- add licence attribute to Dobj()
- handle single str input to station.getList()
- stats report distinguish between intern/external usage
- remove _checkdata flag from station.info()
- update documentation

## 0.1.6
- 2021/03/29
- add sparql queries for availability table
- typos and additions to documentation
- move changelog to separate file

## 0.1.5
- 2020/10/20
- fix bug introduced with v 0.1.4
- datasets with optional columns where not loaded if data object specifications mismatched the list of columns

## 0.1.4
-2020/10/16
- add support for regex columns

## 0.1.3
- 2020/10/01
- Add module 'collection' to support loading data products. See [Modules / collection](modules.md#collection)
- Change behaviour of Dobj to keep data persistent. The pandas data frame is now persistent stored as pandas dataframe in the object. Older versions did query the server every time for the data. A new attribute is available: `Dobj.data` which returns the pandas dataframe. This change in behaviour is controlled with `Dobj._datapersistent = True` (default), and can be reverted by setting it to False. 
- A new attribute `Dobj.id` is available (which is equivalent to Dobj.dobj) but is more human understandable. Dobj.id retrieves or sets the PID/URI.

## 0.1.2
- 2020/07/15
- first public version to pypi.org




