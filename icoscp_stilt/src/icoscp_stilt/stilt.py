import os
import requests
import pandas as pd
import xarray as xr
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass
from dacite import from_dict
from typing import Any, TypeAlias, Tuple
from icoscp_core.icos import meta, data
from icoscp_core.cpb import ArraysDict
from icoscp_core.queries.dataobjlist import DataObjectLite
from .const import *

URL: TypeAlias = str

@dataclass(frozen=True)
class StiltStation:
    id: str
    name: str | None
    lat: float
    lon: float
    alt: int
    countryCode: str
    years: list[int]
    icosId: str | None
    icosHeight: float | None

def list_stations() -> list[StiltStation]:
    http_resp = requests.get(STILTINFO, headers={"Accept": "application/json"})
    http_resp.raise_for_status()
    js: list[dict[str, Any]] = http_resp.json()
    return [from_dict(StiltStation, ss) for ss in js]

def fetch_result_ts(
    station_id: str,
    from_date: str,
    to_date: str,
    columns: list[str] | None = None,
    raw: bool = False
) -> pd.DataFrame:
    http_resp = requests.post(
        url=STILTRAW if raw else STILTTS,
        json={
            'stationId': station_id,
            'fromDate': from_date,
            'toDate': to_date,
            'columns': columns
        }
    )
    http_resp.raise_for_status()
    df = pd.DataFrame.from_records( # type: ignore broken pandas
        http_resp.json(),
        columns=columns
    )
    if 'isodate' in df.columns:
        df['isodate'] = pd.to_datetime(df['isodate'], unit='s')# type: ignore
    return df

def available_year_months(station: StiltStation) -> dict[int, list[str]]:
    return {year: available_months(station.id, year) for year in station.years}

def available_months(station_id: str, year: int) -> list[str]:
    year_path = _year_path(station_id, year)
    return sorted([
        sub.name
        for sub in year_path.iterdir()
        if sub.is_dir() and sub.name.isdigit() and 1 <= int(sub.name) <= 12
    ]) if os.path.exists(year_path) else []


def list_footprints(station_id: str, from_date: str, to_date: str) -> list[datetime]:
    params = {'stationId': station_id, 'fromDate': from_date, 'toDate': to_date}
    http_resp = requests.get(STILT_VIEWER + "listfootprints", params=params)
    http_resp.raise_for_status()
    js: list[str] = http_resp.json()
    return [datetime.fromisoformat(ts) for ts in js]


def load_footprint(station_id: str, dt: datetime) -> xr.DataArray:
    m_str = str(dt.month).zfill(2)
    slot_str = f'{dt.year}x{m_str}x{str(dt.day).zfill(2)}x{str(dt.hour).zfill(2)}'
    fp_path = _year_path(station_id, dt.year) / m_str / slot_str / 'foot'
    if not os.path.exists(fp_path):
        raise FileNotFoundError(f"No footprint found for time {dt} for station {station_id}")
    return xr.open_dataarray(fp_path) # type: ignore

def fetch_observations_pandas(
    spec: URL,
    stations: list[StiltStation],
    columns: list[str] | None = None
) -> dict[str, pd.DataFrame]:
    return {
        id: pd.DataFrame(arrs)
        for id, arrs in fetch_observations(spec, stations, columns).items()
    }

def fetch_observations(
    spec: URL,
    stations: list[StiltStation],
    columns: list[str] | None = None
) -> dict[str, ArraysDict]:

    icos2ss: dict[Tuple[URL, float], StiltStation] = {
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
        ss.id: arrs
        for dobj, arrs in data.batch_get_columns_as_arrays(dobjs_to_fetch, columns)
        for ss in lookup_ss(dobj)
    }


def _year_path(station_id: str, year: int) -> Path:
    if not os.path.exists(STILTPATH):
        m = "This functionality is only available on a Jupyter Hub from Carbon Portal"
        raise RuntimeError(m)
    return Path(STILTPATH) / station_id / str(year)
