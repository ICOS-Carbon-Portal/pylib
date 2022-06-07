# Changelog for cpb module update (0.1.14 -> 0.1.15)


- Dobj change to read metadata from http request
- add new script to extract metadata from server *metadata.py*
- remove properties: _info1, _info2, _info3 from Dobj.
- change .info (consisted of info 1,2,3,) and return .meta instead
- references to server calls moved to constants
- change .colNames: returns now a list of strings with all variable names
- license is extracted dynamically from the metadata per object.
- citation is NO longer a property but a method, to allow for returning different formats. Without argument it returns a 'plain' citation string. Argument options are 'bibtex', 'ris', 'plain') -> .citation('bibtex'|'ris'|'plain')
- print(Dobj) output of __str__ changed to plain citation string, instead of pid

- rename dtype_dict.py to dtype.py

- add new property: .previous -> return the pid/url of the previous version of this file
- add new property: .next -> return the pid/url of the next version of this file

- .get(columns=None)  [method] returns all data by default. Provides the possibility to extract specific columns from the data set. Expected is a list of column names, which then returns only the selected columns. Non valid entries are removed from the list (if only non valid entries are provided, an empty list by default returns all columns)
- remove .getColumns(columns=None)

Please be aware, that `.data` `.get()` will return ALL columns if executed on the Carbon Portal server.
								
								