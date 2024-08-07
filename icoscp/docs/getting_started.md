# Getting started with icoscp_core
The examples in this section can be tried on a public Jupyter Hub running
Python3 notebooks, where the library is preinstalled, for example
[https://exploredata.icos-cp.eu/](https://exploredata.icos-cp.eu/)

Please, click [here](
https://www.icos-cp.eu/data-services/tools/jupyter-notebook/exploredata-password)
to request access to the Explore-Data service.

If run on a standalone machine rather than an ICOS Carbon Portal Jupyter Hub
instance, the data access examples assume that the authentication has been
configured as explained in the next section.

## General note on metadata
An important background information on ICOS metadata is that all the
metadata-represented entities (data objects, data types, documents,
collections, measurement stations, people, etc) are identified by URIs. The
metadata-access methods usually accept these URIs (or their lists) as input
arguments.

## Discover data types
Data type is the main "dimension" used to classify the ICOS data objects. It's
an "umbrella" term aggregating a number of other metadata properties, such as
label, data level, project, theme, object format, etc.

```python
from icoscp_core.icos import meta
# fetches the list of known data types, including metadata associated with them
data_types = meta.list_datatypes()

data_type_names = [dt.label for dt in data_types]
data_type_uris = [dt.uri for dt in data_types]

# data types with data access
previewable_datatypes = [dt for dt in data_types if dt.has_data_access]
```

## Discover stations
All measurement stations in ICOS metadata have a property called station id.
However, this id is not guaranteed to be unique to a station, as it is
sometimes reused by co-located stations, and sometimes two "incarnations" of
a station, ICOS and "pre-ICOS" one, coexist in the metadata for a while. The
only true id is a URI.

```Python
from icoscp_core.icos import meta, ATMO_STATION

# fetch lists of stations, with basic metadata
icos_stations = meta.list_stations()
atmo_stations = meta.list_stations(ATMO_STATION)
all_known_stations = meta.list_stations(False)

# get fully detailed metadata for a station
htm_uri = 'http://meta.icos-cp.eu/resources/stations/AS_HTM'
htm_station_meta = meta.get_station_meta(htm_uri)
```

## List data objects
To select and filter (using various criteria), sort and list data objects,
one can use `list_data_objects` method. All its arguments are optional, and
by default it returns 100 latest (by upload time) data objects.

```python
from icoscp_core.icos import meta
# discovered/chosen data type uri for ICOS ATC CO2 Release
co2_release_dt = 'http://meta.icos-cp.eu/resources/cpmeta/atcCo2L2DataObject'
latest_co2_release = meta.list_data_objects(datatype=co2_release_dt)

latest_htm_co2_release = meta.list_data_objects(datatype=co2_release_dt, station=htm_uri)
```

## Batch data access
For lists of uniform data objects of the same data type (or, more generally and
exactly, sharing variable metadata), like  `latest_co2_release` from the
previous example, the most efficient way of fetching the data is as follows:

```python
from icoscp_core.icos import data
co2_release_data = data.batch_get_columns_as_arrays(latest_co2_release, ['TIMESTAMP', 'co2'])
```

The result of this call is an iterator ("lazy" sequence) that gets evaluated
when used (iterated). Each element of the iterator is a pair, where the first
value is an element from `latest_co2_release`, and the second value is a
dictionary mapping variable names to numpy arrays with their values. This
output can be used as is for many purposes, but if it is desirable to convert
it to pandas DataFrames, it can be done like so (preserving the "lazyness"):

```python
import pandas as pd
co2_release_data_pd = ( (dobj, pd.DataFrame(arrs)) for dobj, arrs in co2_release_data)
```

## Examples

See [Examples](examples.md#examples) for more lengthy examples using all of the
functionality introduced above.

## Accessing documentation
As this library depends on `icoscp_core`, all the functionality of the latter
can be used, not only the examples from above. It is introduced on the
[PyPi project page](https://pypi.org/project/icoscp_core/), and the source code
is [available from GitHub](https://github.com/ICOS-Carbon-Portal/data/tree/master/src/main/python/icoscp_core).

To discover all the rich possibilities of filtering, sorting and paging the
lists of the data objects, it is helpful to read the Python docstring of
`list_data_objects` method:

```python
from icoscp_core.icos import meta
help(meta.list_data_objects)
```

The method signature is not easily readable due to expansion of type
annotations, but the docstring explains the method parameters in detail.

The output from `list_data_objects` is a list of `DataObjectLite` instances.
Documentation of this class can be accessed as follows:

```python
from icoscp_core.metaclient import DataObjectLite
help(DataObjectLite)
```

Similarly, the output from `list_datatypes` is a list of `DobjSpecLite`
instances, whose docstring is accessible like so:

```python
from icoscp_core.metaclient import DobjSpecLite
help(DobjSpecLite)
```

Naturally, one can also request Python help on the whole `meta` constant (which
is in fact an instance of class `MetaClient`), and on `data` constant (which is
an instance of `DataClient`), and on all the methods therein:

```python
from icoscp_core.icos import meta, data
help(meta)
help(meta.get_dobj_meta)
help(meta.get_collection_meta)
help(meta.get_station_meta)
help(data)
help(data.batch_get_columns_as_arrays)
help(data.get_columns_as_arrays)
```

Finally, `MetaClient`'s methods fetching detailed metadata (e.g.
`get_dobj_meta`, `get_collection_meta`, `get_station_meta`) return classes who
are (or whose constituents are) defined inside module `icoscp_core.metacore`.
This module is not available in the source code on GitHub because it is
autogenerated and auto-imported, but can be very instructive to examine and use
as a reference. Due to type annotations, it effectively contains metadata
specification for all the entities available from the metadata repository.
Standalone library users can find it inside their Python installation folder
(can be `venv` or `.venv` if using a virtual Python environment) at location
`lib/icoscp_core/metacore.py`. Jupyter users can inspect the classes in this
module by calling `help` on it:

```python
from icoscp_core import metacore
help(metacore)
```
