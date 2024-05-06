import os
import requests
from pandas import DataFrame
from datetime import datetime
from dataclasses import dataclass
from dacite import from_dict
from .const import *
from typing import Any

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
) -> DataFrame:
    http_resp = requests.post(
        url=STILTRAW if raw else STILTTS,
        data={
            'stationId': station_id,
            'fromDate': from_date,
            'toDate': to_date,
            'columns': columns
        },
        headers={'Content-Type': 'application/json'}
    )
    http_resp.raise_for_status()
    return DataFrame.from_records(http_resp.json()) # type: ignore broken pandas

def list_footprints(station_id: str, from_date: str, to_date: str) -> list[datetime]:
    params = {'stationId': station_id, 'fromDate': from_date, 'toDate': to_date}
    http_resp = requests.get(STILT_VIEWER + "listfootprints", params=params)
    http_resp.raise_for_status()
    js: list[str] = http_resp.json()
    return [datetime.fromisoformat(ts) for ts in js]


def load_footprint(dt: datetime):
    if not os.path.exists(STILTPATH):
        m = "This functionality is only available on a Jupyter Hub from Carbon Portal"
        raise RuntimeError(m)
    return None

