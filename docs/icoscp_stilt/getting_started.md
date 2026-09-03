# Getting started with the new icoscp_stilt

The library is published to PyPI.

As stated in [Background and history](index.md#background-and-history),
the [legacy functionality](modules.md#legacy-modules) is
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
htm_info
```
Here is the output of the above code.

    StiltStation(
        id='HTM150', name='Hyltemossa', lat=56.1, lon=13.42, alt=150,
        countryCode='SE',
        years=[2006, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022],
        icosId='HTM', icosHeight=150.0
    )

```Python
# years for which the station has calculation results
htm_years = htm_info.years

# grouped STILT time series results, all columns, as pandas DataFrame
# can be slow when fetching first time after calculation
htm_time_series_result = stilt.fetch_result_ts('HTM150', '2022-01-01', '2022-01-31')

# list of time-series columns (~60)
ts_columns = htm_time_series_result.columns

# fetch selected columns only
htm_ts_ch4_basics = stilt.fetch_result_ts('HTM150', '2022-01-01', '2022-01-31', columns=['isodate', 'ch4.stilt', 'metadata'])

# find months for which calculation was run
stilt.available_months('KRE250', 2022)

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