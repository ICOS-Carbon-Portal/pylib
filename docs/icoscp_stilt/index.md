# ICOS Carbon Portal STILT module icoscp.stilt
ICOS Carbon Portal offers online services to [calculate your own STILT
footprints](https://stilt.icos-cp.eu/worker/) and [visualize the results](
https://stilt.icos-cp.eu/viewer/). Find out more on our website
[https://www.icos-cp.eu/data-services/tools/stilt-footprint](
https://www.icos-cp.eu/data-services/tools/stilt-footprint).

This module offers access to information about the STILT "stations",
calculated footprints and time series results. Please note that the
calculated **footprints** are only accessible if the code is executed on
[Carbon Portal's Jupyter notebooks](
https://icos-carbon-portal.github.io/jupyter/).

## Background and history
This module was a separate library, `icoscp_stilt`, during the `0.2.x`
releases of **icoscp**, and is now part of **icoscp** again.

In addition, it contains a newer submodule `icoscp.stilt.stilt` with new
functionality designed to closer match the server APIs and to be performant.

## Upgrade notes
STILT functionality is part of **icoscp**, as `icoscp.stilt`. Code written
for the separate `icoscp_stilt` library (used with **icoscp** `0.2.x`) needs
its imports updated by replacing
```Python
from icoscp_stilt import stiltstation
```
with
```Python
from icoscp.stilt import stiltstation
```

Compared with **icoscp** versions prior to `0.2.0`, handling of
country-association of the STILT stations is simplified, which was made
possible by a change on the server side that enforced ISO-3166 alpha-2
country code
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

