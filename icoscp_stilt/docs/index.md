# ICOS Carbon Portal library icoscp_stilt


ICOS Carbon Portal offers online services to [calculate your own STILT
footprints](https://stilt.icos-cp.eu/worker/) and [visualize the results]
(https://stilt.icos-cp.eu/viewer/). Find out more on our website
[https://www.icos-cp.eu/data-services/tools/stilt-footprint](
https://www.icos-cp.eu/data-services/tools/stilt-footprint).

This library offers access to information about the STILT "stations",
calculated footprints and time series results. Please note that the
calculated **footprints** are only accessible if the code is executed on
[Carbon Portal's Jupyter notebooks]
(https://icos-carbon-portal.github.io/jupyter/).

## Background and history
This library contains functionality split out of library `icoscp` prior to
`0.2.0` release, in order to relieve the latter of the specialized STILT code
and its dependencies.

In addition, the library contains a new module `icoscp_stilt.stilt` with new
functionality designed to closer match the server APIs and to be performant.

## Upgrade notes
Releases of `icoscp` version `0.2.0` and `icoscp_stilt` version `0.1.0`
constitute a substantial change. For STILT functionality, the change implies
a necessity to update the existing code by replacing the import
```Python
from icoscp.stilt import stiltstation
```
with
```Python
from icoscp_stilt import stiltstation
```

## Getting started

The library is published to PyPI.

As stated above, the [legacy functionality](modules.md#legacy-modules) is
still available, but for new code the developers are encouraged to consider
the new model `icoscp_stilt.stilt`.

```Python
from icoscp_stilt import stilt
stations = stilt.list_stations()

station_info_lookup = {s.id: s for s in stations}

htm_info = station_info_lookup['HTM150']
htm_years = htm_info.years

htm_time_series_result = stilt.fetch_result_ts('HTM150', '2022-01-01', '2022-01-31')
```
