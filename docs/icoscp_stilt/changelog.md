# Changelog

## 0.1.4
- #### dependencies
    - Drop the pandas upper version cap and fix deprecated pandas APIs.
- #### fmap.py
    - Remove folium's Stamen tile layers.

## 0.1.3
- #### dependencies
    - Relax pandas upper dependency from `<2` to `<=2.2.3`.

## 0.1.2
- #### stiltobj.py
    - Refactor the code in the `get_ts()` function and request timeseries data
      using JSON content instead of raw string data to address a bug that
      affects data retrieval when using special characters.
- #### dependencies
    - Version pin library's dependencies.

## 0.1.1  
- #### stilt.py
    - Refactor `load_footprint()` function and implement `load_footprints()`.
    - Return basic dobj metadata together with observation results in 
      `fetch_observations()` and `fetch_observations_pandas()` functions.

## 0.1.0
Publish `stilt` as its own standalone Python library to [https://pypi.org/](
https://pypi.org/).

## version < 0.1.0
For changes prior to 0.1.0 we refer to the changelog [here](
https://icos-carbon-portal.github.io/pylib/icoscp/changelog/#020), since 
`icoscp_stilt` used to be part of the `icoscp` library.
