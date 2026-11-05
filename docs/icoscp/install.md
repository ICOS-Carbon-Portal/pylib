# Installation
The library requires Python version 3.10 or later.

## Pip official release
The recommended way of installation is by using pip:

	pip install icoscp
	
The installation should take care of any dependencies, but to
successfully access any data object from the ICOS Carbon Portal you need
to have a working internet connection.  
  
We would encourage you to use a virtual environment for python to test
this library. For example with mini-conda
[https://docs.conda.io/en/latest/miniconda.html](
https://docs.conda.io/en/latest/miniconda.html) you can create a new
environment with:

- `conda create -n icos python`
- `activate icos`
- `pip install icoscp`

## Upgrade guide
This concerns users of **icoscp** of versions prior to `0.2.0`.

For standalone library users (i.e. outside of a Carbon Portal Jupyter
environment), the package installation (or rather upgrade) procedure must be
followed by the [authentication setup](authentication.md)
(unless you have used **icoscp_core** previously, and configured
authentication with it using the default method).

After that all the working code that depended on older versions should work
(for STILT-related code, [see below](#stilt-related-code-update)),
and no code changes are necessary, but it is highly recommended to replace the
following import
```python
from icoscp.cpb.dobj import Dobj
```
with
```python
from icoscp.dobj import Dobj
```

(i.e. drop `.cpb` from this import's path) everywhere in your scripts and
notebooks. The new `Dobj` class has a legacy status (see the
[library history](index.md#the-history-and-the-new-role-of-the-library)), like
the old one, but contains an improved implementation of the same API.  

<div style="margin-bottom: 1em">
The advantages are:
</div>

- support for metadata access of all data objects (not only the ones whose
  *data* is accessible with the library)
- better performance when fetching the data
- new `metadata` property that contains `DataObject` dataclass from
  `icoscp.core.metaclient` module, which is a type-annotated nested structure
  that was (mostly) automatically produced to faithfully reflect the JSON
  metadata available for the data object from the metadata server.

An effort was made to ensure identical functionality of the new `Dobj` class
when compared with the old one, but there are some differences described
[elsewhere in the documentation](modules.md#original-legacy-dobj).

### STILT-related code update
STILT functionality is available as `icoscp.stilt`, so legacy notebooks
importing `icoscp.stilt` keep working, with only minor changes to the legacy
STILT functionality. If your code imports from `icoscp_stilt` (the separate
library used with **icoscp** `0.2.x`), replace `icoscp_stilt` with
`icoscp.stilt` (underscore replaced with dot). Developers are encouraged to
consult the [STILT documentation](../icoscp_stilt/index.md) to discover new
functionality.
---

## Manual installation
If you would like to install the latest version (branch from GitHub),
you can download / fork the repo navigate to the library folder and
start the installation with:
```shell
pip install .
```

### Cutting Edge
Install directly from our GitHub master branch. Please be aware that
this is not reflecting the official release of the library, but includes
the latest development. Hence, you should think of this as an alpha or
beta version of the new release:
```shell
pip install "git+https://github.com/ICOS-Carbon-Portal/pylib.git#subdirectory=icoscp"
```

## Dependencies
The following modules are required by the library:

- dacite
- folium
- netCDF4
- numpy
- pandas
- requests
- tqdm
- xarray
