import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, TypeAlias

import pandas as pd
import requests
import xarray as xr
from dacite import from_dict
from icoscp_core.cpb import ArraysDict
from icoscp_core.icos import data, meta, station_class_lookup
from icoscp_core.queries.dataobjlist import DataObjectLite

from .const import (
    HTTP_TIMEOUT_SEC,
    ICOS_STATION_PREFIX,
    STILT_VIEWER,
    STILTINFO,
    STILTPATH,
    STILTRAW,
    STILTTS,
)

URL: TypeAlias = str

@dataclass(frozen=True)
class StiltStation:
    """
    Dataclass for metadata of a STILT 'station'

    Attributes:
        `id` (string): STILT station id
        `name` (string): station name
        `lat` (float): WGC-84 latitude; its multiple by 100 must be an integer
        `lon` (float): WGC-84 longitude; its multiple by 100 must be an integer
        `alt` (int): altitude above the ground level
        `countryCode` (str): ISO 3166-1 alpha-2 country code (two letters,
            e.g. SE)
        `years` (list[int]): years for which calculations for this station are
            available
        `icosId` (str | None): if applicable, corresponding station ID in the
            ICOS Carbon Portal metadata
        `icosHeight` (float | None): if applicable, corresponding sampling
            height at a station in the ICOS Carbon Portal metadata
    """
    id: str
    name: str | None
    lat: float
    lon: float
    alt: int
    countryCode: str
    years: list[int]
    icosId: str | None
    icosHeight: float | None

    @property
    def is_icos_proper(self) -> bool:
        """
        Boolean property indicating whether the station corresponds to a
        proper ICOS station.
        """
        if self.icosId is None: return False
        uri = ICOS_STATION_PREFIX + self.icosId
        return uri in station_class_lookup()

    @property
    def has_observation_data(self) -> bool:
        """
        Boolean property indicating whether the station corresponds to a
        station in ICOS Carbon Portal. Does not mean that this is a 'proper'
        ICOS station, as ICOS Carbon Portal contains data from some other
        stations, too.
        """
        return self.icosId is not None

@dataclass(frozen=True)
class ObservationResult:
    dobj: DataObjectLite
    columns: ArraysDict

@dataclass(frozen=True)
class ObservationDfResult:
    dobj: DataObjectLite
    df: pd.DataFrame

def list_stations() -> list[StiltStation]:
    """
    Fetches metadata for all known STILT stations

    :return:
        A list of `StiltStation` instances
    """
    http_resp = requests.get(STILTINFO, headers={"Accept": "application/json"},
                             timeout=HTTP_TIMEOUT_SEC)
    http_resp.raise_for_status()
    js: list[dict[str, Any]] = http_resp.json()
    return [from_dict(StiltStation, ss) for ss in js]

def fetch_result_ts(
    station_id: str,
    from_date: str,
    to_date: str,
    columns: list[str] | None = None,
    *,
    raw: bool = False
) -> pd.DataFrame:
    """
    Method to fetch time-series results of STILT calculation

    :param `station_id` (str): STILT station id

    :param `from_date` (str): ISO-8601 start date, inclusive

    :param `to_date` (str): ISO-8601 end date, inclusive

    :param `columns` (list[str] | None): optional list of columns of interest;
        if omitted, all columns are returned; the column containing the
        timestamp is called `isodate`.

    :param `raw` (bool): optional raw-data flag; indicates whether the raw
        STILT time series output should be returned instead of the
        grouped/calculated one; note that raw data is not cached and therefore
        fetching can be slow; False by default

    :return: pandas DataFrame with the requested time series
    """
    http_resp = requests.post(
        url=STILTRAW if raw else STILTTS,
        json={
            'stationId': station_id,
            'fromDate': from_date,
            'toDate': to_date,
            'columns': columns
        },
        timeout=HTTP_TIMEOUT_SEC
    )
    http_resp.raise_for_status()
    df = pd.DataFrame.from_records( # type: ignore broken pandas
        http_resp.json(),
        columns=columns
    )
    if 'isodate' in df.columns:
        df['isodate'] = pd.to_datetime(df['isodate'], unit='s') # type: ignore
    return df

def available_year_months(station: StiltStation) -> dict[int, list[str]]:
    """
    List months for which calculations have been performed for a station.
    Works only on ICOS Jupyter Hub.

    :param `station` (StiltStation): the STILT station of interest

    :return: a dictionary with int years as keys and month numbers as
        list[str] as values
    """
    return {year: available_months(station.id, year) for year in station.years}

def available_months(station_id: str, year: int) -> list[str]:
    """
    For a STILT station and a year, list months for which any calculations
    have been performed. Works only on ICOS Jupyter Hub.

    :param `station_id` (str): STILT station id

    :param `year` (int): the year of interest

    :return (list[str]): the list of month numbers as two-character strings
    """
    year_path = _year_path(station_id, year)
    return sorted([
        sub.name
        for sub in year_path.iterdir()
        if sub.is_dir() and sub.name.isdigit() and 1 <= int(sub.name) <= 12
    ]) if os.path.exists(year_path) else []


def list_footprints(station_id: str, from_date: str, to_date: str) -> list[datetime]:
    """
    Within a time interval, list time slots for which footprints are available
    for a station

    :param `station_id` (str): STILT station id

    :param `from_date` (str): ISO-8601 start date, inclusive

    :param `to_date` (str): ISO-8601 end date, inclusive

    :return (list[datetime]): a list of timezone-agnostic `datetime` instances
        representing the time slots
    """
    params = {'stationId': station_id, 'fromDate': from_date, 'toDate': to_date}
    http_resp = requests.get(STILT_VIEWER + "listfootprints",
                             params=params,
                             timeout=HTTP_TIMEOUT_SEC)
    http_resp.raise_for_status()
    js: list[str] = http_resp.json()
    return [datetime.fromisoformat(ts) for ts in js]


def load_footprint(station_id: str, dt: datetime) -> xr.DataArray:
    """
    Load a single footprint as an xarray DataArray. Works only on ICOS
    Jupyter Hub.

    :param `station_id` (str): STILT station id

    :param `dt` (datetime): the time slot of interest

    :return (DataArray): xarray DataArray instance with the footprint data
    """
    fp_path = _footprint_path(station_id, dt)
    return xr.open_dataarray(fp_path)# type: ignore


def load_footprints(station_id: str, dts: list[datetime]) -> xr.Dataset:
    """
    Load a number of footprints as an xarray spatial dataset. Works only
    on ICOS Jupyter Hub.

    :param `station_id` (str): STILT station id

    :param `dts` (list[datetime]): the time slots of interest

    :return (DataArray): xarray DataArray instance with the footprint data
    """
    fp_paths = [_footprint_path(station_id, dt) for dt in dts]

    # Concatenate xarrays on time axis:
    fp = xr.open_mfdataset( # type: ignore
        fp_paths, combine='by_coords',
        data_vars='minimal', coords='minimal',
        compat='override', parallel=True,
        decode_cf=False
    )
    # now check for CF compatibility
    fp = xr.decode_cf(fp)
    # Format time attributes:
    fp.time.attrs["standard_name"] = "time"
    fp.time.attrs["axis"] = "T"

    # Format latitude attributes:
    fp.lat.attrs["axis"] = "Y"
    fp.lat.attrs["standard_name"] = "latitude"

    # Format longitude attributes:
    fp.lon.attrs["axis"] = "X"
    fp.lon.attrs["standard_name"] = "longitude"
    return fp


def fetch_observations_pandas(
    spec: URL,
    stations: list[StiltStation],
    columns: list[str] | None = None
) -> dict[str, ObservationDfResult]:
    """
    Batch-fetch observational datasets for a number of STILT stations

    :param `spec` (str): the URL for the data type of interest; see for
    example `CP_OBSPACK_CO2_SPEC` constant in `const` module

    :param `stations` (list[StiltStation]): the STILT stations of interest

    :param `columns` (list[str | None]): optional list of columns of interest
    within the observational datasets; if omitted, all columns are included
    in the result

    :return (dict[str, ObservationDfResult]): a dictionary with STILT station IDs as
    keys and instances of ObservationDfResult as values
    """
    return {
        st_id: ObservationDfResult(obs_res.dobj, pd.DataFrame(obs_res.columns))
        for st_id, obs_res in fetch_observations(spec, stations, columns).items()
    }

def fetch_observations(
    spec: URL,
    stations: list[StiltStation],
    columns: list[str] | None = None
) -> dict[str, ObservationResult]:
    """
    Batch-fetch observational datasets for a number of STILT stations. Is a
    lower-level and better-performing version of `fetch_observations_pandas`.
    The latter method is in fact implemented as a simple transformation of
    this method's result. The only difference is that the returned dictionary
    does not contain pandas DataFrames, but a dictionary of numpy arrays for
    each column name being a dictionary key.

    :param `spec` (str): the URL for the data type of interest; see for
    example `CP_OBSPACK_CO2_SPEC` constant in `const` module

    :param `stations` (list[StiltStation]): the STILT stations of interest

    :param `columns` (list[str | None]): optional list of columns of interest
    within the observational datasets; if omitted, all columns are included
    in the result

    :return (dict[str, ObservationResult]): a dictionary with STILT station IDs as
    keys and ObservationResult instances as values
    """

    icos2ss: dict[tuple[URL, float], StiltStation] = {
        (ICOS_STATION_PREFIX + s.icosId, s.icosHeight or float(s.alt)): s
        for s in stations
        if s.icosId is not None
    }

    def lookup_ss(dobj: DataObjectLite) -> list[StiltStation]:
        icos_uri = dobj.station_uri
        samp_height = dobj.sampling_height
        if icos_uri is None or samp_height is None: return []
        ss = icos2ss.get((icos_uri, samp_height))
        if ss is None: return []
        return [ss]

    icos_stations: list[URL] = list({uri for (uri, _) in icos2ss.keys()})

    dobjs_to_fetch: list[DataObjectLite] = [
        dobj for dobj in meta.list_data_objects(spec, icos_stations)
        if lookup_ss(dobj)
    ]
    return {
        ss.id: ObservationResult(dobj, cols)
        for dobj, cols in data.batch_get_columns_as_arrays(dobjs_to_fetch, columns)
        for ss in lookup_ss(dobj)
    }


def _year_path(station_id: str, year: int) -> Path:
    if not os.path.exists(STILTPATH):
        m = "This functionality is only available on a Jupyter Hub from Carbon Portal"
        raise RuntimeError(m)
    return Path(STILTPATH) / station_id / str(year)

def _footprint_path(station_id: str, dt: datetime) -> Path:
    m_str = str(dt.month).zfill(2)
    slot_str = f'{dt.year}x{m_str}x{str(dt.day).zfill(2)}x{str(dt.hour).zfill(2)}'
    fp_path = _year_path(station_id, dt.year) / m_str / slot_str / 'foot'
    if not os.path.exists(fp_path):
        msg = f"No footprint found for time {dt} for station {station_id}"
        raise FileNotFoundError(msg)
    return fp_path