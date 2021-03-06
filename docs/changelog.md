# Changelog

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




