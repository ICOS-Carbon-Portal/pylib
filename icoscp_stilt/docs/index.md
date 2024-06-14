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
radically simplified with this new release. This was made possible by a
change on the server side that guaranteed ISO-3166 alpha-2 country code
association with every STILT station. The previously-utilized geo lookup of
countries thus became redundant. Also, in the context of STILT, detailed
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

## Getting started
The library is published to PyPI.

As stated above, the [legacy functionality](modules.md#legacy-modules) is
still available, but for new code the developers are encouraged to consider
the new module `icoscp_stilt.stilt` as the first choice.

The following code demonstrates the new functionality.

```Python
from icoscp_stilt import stilt
from icoscp_stilt.const import CP_OBSPACK_CO2_SPEC

# list of stilt.StiltStation dataclass instances
stations = stilt.list_stations()

station_info_lookup = {s.id: s for s in stations}

# example: Hyltemossa station, altitude 150 m
htm_info = station_info_lookup['HTM150']
>>> htm_info
StiltStation(
    id='HTM150', name='Hyltemossa', lat=56.1, lon=13.42, alt=150,
    countryCode='SE',
    years=[2006, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022],
    icosId='HTM', icosHeight=150.0
)


# years for which the station has calculation results
htm_years = htm_info.years

# grouped STILT time series results, all columns, as pandas DataFrame
# can be slow when fetching first time after calculation
htm_time_series_result = stilt.fetch_result_ts('HTM150', '2022-01-01', '2022-01-31')

# list of time-series columns (~60)
ts_columns = htm_time_series_result.columns

# fetch selected columns only
htm_ts_ch4_basics = stilt.fetch_result_ts('HTM150', '2022-01-01', '2022-01-31', columns=['isodate', 'ch4.stilt', 'metadata'])

# raw STILT time series results, all columns, as pandas DataFrame
# always slow, as these results are not cached
htm_time_series_raw = stilt.fetch_result_ts('HTM150', '2022-01-01', '2022-01-31', raw=True)

# list of raw time-series columns (~800)
ts_columns_raw = htm_time_series_raw.columns

# find months for which calculation was run
>>> stilt.available_months('KRE250', 2022)
['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']

# find all months for all years for which calculation was run
htm_yearmonths = stilt.available_year_months(htm_info)

# list footprint time slots that were computed for a station within date interval
htm_slots_jan2022 = stilt.list_footprints('HTM150', '2022-01-01', '2022-01-31')

# load footprint for one time slot
htm_fp_example = stilt.load_footprint('HTM150', htm_slots_jan2022[0])

# filter stations
de_stations = [s for s in stations if s.countryCode == 'DE']

# fetch observations for the German stations as numpy array dicts
# interesting columns are requested explicitly (all returned otherwise)
# using bare numpy gives maximum performance
de_co2_numpy = stilt.fetch_observations(CP_OBSPACK_CO2_SPEC, de_stations, ['value', 'time'])

# same as previous example, but returning pandas DataFrames instead
# performance may be worse, especially on Jupyter
de_co2_pandas = stilt.fetch_observations_pandas(CP_OBSPACK_CO2_SPEC, de_stations, ['value', 'time'])
```

## Getting help

All the methods in the new `stilt` module have a Python documentation
accessible by standard means, for example:

```
help(stilt.fetch_observations)
```