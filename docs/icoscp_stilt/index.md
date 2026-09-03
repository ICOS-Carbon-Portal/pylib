# ICOS Carbon Portal library icoscp_stilt
ICOS Carbon Portal offers online services to [calculate your own STILT
footprints](https://stilt.icos-cp.eu/worker/) and [visualize the results](
https://stilt.icos-cp.eu/viewer/). Find out more on our website
[https://www.icos-cp.eu/data-services/tools/stilt-footprint](
https://www.icos-cp.eu/data-services/tools/stilt-footprint).

This library offers access to information about the STILT "stations",
calculated footprints and time series results. Please note that the
calculated **footprints** are only accessible if the code is executed on
[Carbon Portal's Jupyter notebooks](
https://icos-carbon-portal.github.io/jupyter/).

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

Additionally, handling of country-association of the STILT stations is
simplified in this new release, which was made possible by a
change on the server side that enforced ISO-3166 alpha-2 country code
association with every STILT station. (Geo-lookup of country used previously
thus became redundant). Also, for the STILT station metadata, detailed
country metadata was deemed unnecessary, retaining the country code only,
with a possibility of country name lookup. This resulted in a potential
breaking change for the existing STILT-related Jupyter notebooks, namely
country filtering in `stiltstation.find` method needs to use the two-letter
country codes rather than the previously arbitrary choice of country names or
3-letter codes, for example:

```Python
stiltstation.find(country='SE')
```
instead of the previously-allowed
```Python
stiltstation.find(country='swe')
```
or
```Python
stiltstation.find(country='Sweden')
```

Also, selecting multiple countries at once is not supported in the legacy code
any more.

In general, library users are encouraged to switch to using the new
functionality (`stilt` module) instead whenever possible (see the code
examples below).

