import os
import requests
import pandas as pd
import xarray as xr
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass
from dacite import from_dict
from typing import Any, TypeAlias
from icoscp_core.icos import meta
from icoscp_core.queries.dataobjlist import DataObjectLite
from icoscp_core.queries.dataobjlist import SamplingHeightFilter
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

def find_co2_observations(station: StiltStation) -> DataObjectLite | None:
    return _get_observation_dobj(OBS_SPEC_CO2, station)

def find_ch4_observations(station: StiltStation) -> DataObjectLite | None:
    return _get_observation_dobj(OBS_SPEC_CH4, station)

def list_footprints(station_id: str, from_date: str, to_date: str) -> list[datetime]:
    params = {'stationId': station_id, 'fromDate': from_date, 'toDate': to_date}
    http_resp = requests.get(STILT_VIEWER + "listfootprints", params=params)
    http_resp.raise_for_status()
    js: list[str] = http_resp.json()
    return [datetime.fromisoformat(ts) for ts in js]


def load_footprint(station_id: str, dt: datetime) -> xr.DataArray:
    if not os.path.exists(STILTPATH):
        m = "This functionality is only available on a Jupyter Hub from Carbon Portal"
        raise RuntimeError(m)
    m_str = str(dt.month).zfill(2)
    slot_str = f'{dt.year}x{m_str}x{str(dt.day).zfill(2)}x{str(dt.hour).zfill(2)}'
    fp_path = Path(STILTPATH) / station_id / str(dt.year) / m_str / slot_str / 'foot'
    if not os.path.exists(fp_path):
        raise FileNotFoundError(f"No footprint found for time {dt} for station {station_id}")
    return xr.open_dataarray(fp_path) # type: ignore


def _get_observation_dobj(spec: URL, station: StiltStation) -> DataObjectLite | None:
    if station.icosId is None: return None

    sampl_height: float = station.icosHeight or float(station.alt)
    dobjs = meta.list_data_objects(
        datatype=spec,
        station=ICOS_STATION_PREFIX + station.icosId,
        filters=[SamplingHeightFilter("=", sampl_height)]
    )
    return dobjs[0] if dobjs else None
