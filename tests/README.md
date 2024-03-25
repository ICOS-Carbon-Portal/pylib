### In a nutshell
- Slim down, refactor/modernize, and test `__get_stations()`.
- Introduce and test `get_stn_info()`.
- Introduce `parse_loc()`.
- Introduce and test `get_geo_info()`.
- Refactor and test existing `__station_name()`.
---
### <u>Details</u>
#### 20240312
- Introduce environmental variable to switch between production & test
  mode in `icoscp/__init__.py`.
- Reversed buggy `WORLD.empty` in countries module.
#### 20240313
- In `icoscp/const.py`, move all testing-related constants within the
  production-test switch.
- Replicate and add mock data for stilt-stations in
  `tests/stiltstation-mock-data/stiltweb/`.
#### 20240314
- Replicate and add more mock data for stilt-stations in
  `tests/stiltstation-mock-data/stiltweb/`.
- Read json-files in `tests/stiltstation-mock-data/station-metadata/`
  using a more coherent way.
#### 20240320
- In the static station metadata, email, firstName, and lastName are
  randomized (due to the `getIdList()` call within), hence they are
  excluded from testing.
#### 20240322
- Fix comments in `__get_stations()`.
- Group all static files related to `test_stiltstation.py` under
  `tests/stiltstation-mock-data/`.
---
### TODO
- Document how to replicate and add more mock data.
  (script on Zois's JupyterHub).
- Maybe test parse_loc().
