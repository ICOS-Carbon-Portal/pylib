import os
import requests
from datetime import datetime
from dataclasses import dataclass
from dacite import from_dict
from .const import STILT_VIEWER, STILTINFO, STILTPATH
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

def list_footprints(station_id: str, from_date: str, to_date: str) -> list[datetime]:
    params = {'stationId': station_id, 'fromDate': from_date, 'toDate': to_date}
    http_resp = requests.get(STILT_VIEWER + "listfootprints", params=params)
    http_resp.raise_for_status()
    js: list[str] = http_resp.json()
    return [datetime.fromisoformat(ts) for ts in js]


def merge_footprints():
    if not os.path.exists(STILTPATH):
        raise RuntimeError("""
Please be aware, that the STILT module is not supported to run
locally (outside of the Virtual Environment at the ICOS Carbon
Portal). You must use one of our Jupyter Services.
Visit https://www.icos-cp.eu/data-services/tools/jupyter-notebook
for further information. Or you may use our online STILT viewer
application https://stilt.icos-cp.eu/viewer/.
""")
    return None
