# Examples

## Monthly CO2 averages

This example uses `icoscp_core` functionality to merge, monthly-average and
plot CO2 molar fraction data from selected stations, sampled at certain
heights. See [discover data types](getting_started.md#discover-data-types)
to find out how to discover a URL for a data type.

```Python
from icoscp_core.icos import data, meta, ATMO_STATION
import pandas as pd
import numpy as np

# Swedish atmospheric stations whose metadata is supplied to the Carbon Portal
# by the Atmospheric Thematic Center
se_atmo_stations = [
    s for s in meta.list_stations(ATMO_STATION)
    if s.country_code=='SE'
]

# Find basic metadata for CO2 release data sampled at at least 100 m above the ground
se_co2_from_100 = [
    dobj for dobj in meta.list_data_objects(
        # URL for official ICOS CO2 molar fraction release data
        datatype='http://meta.icos-cp.eu/resources/cpmeta/atcCo2L2DataObject',
        station=se_atmo_stations
    )
    if dobj.sampling_height >= 100
]

# prepare an empty pandas DataFrame to merge the data into
merged_co2 = pd.DataFrame(columns=['TIMESTAMP', 'co2'])

# batch-fetch the interesting columns and iterate through the results
for dobj, arrs in data.batch_get_columns_as_arrays(se_co2_from_100, ['TIMESTAMP', 'co2']):
    st_uri = dobj.station_uri
    # ICOS atmospheric station URIs end with underscore followed by a 3-letter station ID
	# this ID is convenient to use as a suffix to rename 'co2' with
    station_id = st_uri[st_uri.rfind('_'):]
    df = pd.DataFrame(arrs)
    # next line would be needed if `keep_bad_data` flag in batch_get_columns_as_arrays was set to True
    #df.loc[df['Flag'] != 'O', 'co2'] = np.nan 
    del df['Flag']
    merged_co2 = pd.merge(merged_co2, df, on='TIMESTAMP', how='outer', suffixes=('', station_id))

del merged_co2['co2']

# compute monthly averages
by_month = merged_co2.groupby(pd.Grouper(key='TIMESTAMP', freq='M')).mean().reset_index()

# Let us retrieve column metadata to construct Y-axis plot label

# fetch detailed metadata for one of the data objects (they all have same columns)
dobj_meta = meta.get_dobj_meta(se_co2_from_100[0])

# get 'value type' part of column metadata for co2 column
columns_meta = dobj_meta.specificInfo.columns
co2_value_type = [col for col in columns_meta if col.label=='co2'][0].valueType

# construct the Y-axis label from the value type data structure
co2_axis_label = f'{co2_value_type.self.label} [{co2_value_type.unit}]'

# plotting should work in Jupyter
by_month.plot(x='TIMESTAMP', ylabel=co2_axis_label);
```