# Changelog

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




