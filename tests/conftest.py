"""Shared fixtures for the icoscp test suite."""

# Standard library imports.
import os

# STILT const.py picks mock-data paths when MODE != 'production'; pytest loads
# conftest before collecting modules, so this is set before const.py imports.
os.environ['MODE'] = 'test'

from typing import Any, Optional

# Related third party imports.
import pytest
from icoscp.core.metacore import (
    DataAcquisition,
    DataObject,
    DataObjectSpec,
    DataProduction,
    DataSubmission,
    DataTheme,
    Licence,
    Organization,
    Position,
    Project,
    References,
    SpatioTemporalMeta,
    Station,
    StationTimeSeriesMeta,
    TemporalCoverage,
    TimeInterval,
    UriResource,
    ValueType,
    VarMeta,
)

HASH = "0_cVw9NF9ngffZ1NQ5lXJ9CY"
OBJECT_URI = f"https://meta.icos-cp.eu/objects/{HASH}"

STATION_LAT = 60.1
STATION_LON = 17.5
STATION_ALT = 12.0


def _uri_resource(uri: str = OBJECT_URI,
                  label: Optional[str] = "label") -> UriResource:
    return UriResource(uri=uri, label=label, comments=[])


def _organization() -> Organization:
    return Organization(
        self=_uri_resource(uri="https://meta.icos-cp.eu/resources/org"),
        name="Some Organization",
        email=None,
        website=None,
        webpageDetails=None,
    )


def _position(lat: float = STATION_LAT, lon: float = STATION_LON,
              alt: Optional[float] = STATION_ALT) -> Position:
    return Position(lat=lat, lon=lon, alt=alt, label=None, uri=None)


def _station(location: Optional[Position]) -> Station:
    return Station(
        org=_organization(),
        id="STA",
        location=location,
        coverage=None,
        responsibleOrganization=None,
        pictures=[],
        specificInfo=None,
        countryCode="SE",
        funding=None,
    )


def _data_submission() -> DataSubmission:
    return DataSubmission(
        submitter=_organization(),
        start="2020-01-01T00:00:00Z",
        stop="2020-01-02T00:00:00Z",
    )


def _data_object_spec() -> DataObjectSpec:
    return DataObjectSpec(
        self=_uri_resource(uri="https://meta.icos-cp.eu/resources/spec"),
        project=Project(
            self=_uri_resource(
                uri="https://meta.icos-cp.eu/resources/project"),
            keywords=None,
        ),
        theme=DataTheme(
            self=_uri_resource(
                uri="https://meta.icos-cp.eu/resources/theme"),
            icon="https://meta.icos-cp.eu/icon.png",
            markerIcon=None,
        ),
        format=None,
        encoding=_uri_resource(
            uri="https://meta.icos-cp.eu/resources/encoding"),
        dataLevel=2,
        specificDatasetType="StationTimeSeries",
        datasetSpec=None,
        documentation=[],
        keywords=None,
    )


def _data_production() -> DataProduction:
    return DataProduction(
        creator=_organization(),
        contributors=[],
        host=None,
        comment=None,
        sources=[],
        documentation=None,
        dateTime="2020-01-03T00:00:00Z",
    )


def _var_meta(label: str) -> VarMeta:
    return VarMeta(
        model=_uri_resource(uri="https://meta.icos-cp.eu/resources/model"),
        label=label,
        valueType=ValueType(
            self=_uri_resource(
                uri="https://meta.icos-cp.eu/resources/valuetype"),
            quantityKind=None,
            unit="ppm",
        ),
        valueFormat=None,
        isFlagFor=None,
        minMax=None,
        instrumentDeployments=None,
    )


def _station_time_series_meta(
        station: Station,
        columns: Optional[list[VarMeta]]) -> StationTimeSeriesMeta:
    return StationTimeSeriesMeta(
        acquisition=DataAcquisition(
            station=station,
            site=None,
            interval=None,
            instrument=None,
            samplingPoint=None,
            samplingHeight=None,
        ),
        productionInfo=_data_production(),
        nRows=10,
        coverage=None,
        columns=columns,
    )


def _spatio_temporal_meta(station: Station) -> SpatioTemporalMeta:
    return SpatioTemporalMeta(
        title="Spatio temporal object",
        description=None,
        spatial=_position(),
        temporal=TemporalCoverage(
            interval=TimeInterval(
                start="2020-01-01T00:00:00Z",
                stop="2020-01-02T00:00:00Z",
            ),
            resolution=None,
        ),
        station=station,
        samplingHeight=None,
        productionInfo=_data_production(),
        variables=None,
    )


def _references(licence: Optional[Licence]) -> References:
    return References(
        citationString="A citation string.",
        citationBibTex="@misc{...}",
        citationRis="TY  - DATA",
        doi=None,
        keywords=None,
        authors=None,
        title="A title",
        temporalCoverageDisplay=None,
        acknowledgements=None,
        licence=licence,
    )


def make_licence() -> Licence:
    """Build a real Licence dataclass instance."""
    return Licence(
        url="https://creativecommons.org/licenses/by/4.0/",
        name="CC BY 4.0",
        webpage="https://data.icos-cp.eu/licence",
        baseLicence="https://creativecommons.org/licenses/by/4.0/legalcode",
    )


def make_dataobject(
        specific_info: Optional[Any] = None,
        licence: Optional[Licence] = None,
        location: Optional[Position] = None,
        columns: Optional[list[VarMeta]] = None,
) -> DataObject:
    """Build a complete, valid DataObject for tests.

    Defaults to a station-time-series object with two columns and a
    station that has a location. Overrides:
    - ``specific_info``: supply a SpatioTemporalMeta (or other) to
      replace the default StationTimeSeriesMeta.
    - ``licence``: a Licence instance, or None for no licence.
    - ``location``: a Position for the station, or None for no
      location (station still present).
    - ``columns``: list of VarMeta for the station-time-series case.
    """
    if columns is None:
        columns = [_var_meta("TIMESTAMP"), _var_meta("co2")]
    if specific_info is None:
        station = _station(location=location)
        specific_info = _station_time_series_meta(
            station=station, columns=columns)
    return DataObject(
        hash=HASH,
        accessUrl=OBJECT_URI,
        pid=f"11676/{HASH}",
        doi=None,
        fileName="data.csv",
        size=1024,
        submission=_data_submission(),
        specification=_data_object_spec(),
        specificInfo=specific_info,
        previousVersion=None,
        nextVersion=None,
        latestVersion=OBJECT_URI,
        parentCollections=[],
        references=_references(licence=licence),
    )


def make_spatiotemporal_dataobject() -> DataObject:
    """Build a DataObject whose specificInfo is SpatioTemporalMeta."""
    station = _station(location=_position())
    return make_dataobject(
        specific_info=_spatio_temporal_meta(station=station))


@pytest.fixture
def dataobject() -> DataObject:
    """Default station-time-series DataObject with a station location."""
    return make_dataobject(location=_position(), licence=make_licence())


@pytest.fixture
def dataobject_no_location() -> DataObject:
    """Station-time-series DataObject whose station has no location."""
    return make_dataobject(location=None)


@pytest.fixture
def dataobject_no_licence() -> DataObject:
    """Station-time-series DataObject without a licence."""
    return make_dataobject(location=_position(), licence=None)


@pytest.fixture
def dataobject_spatiotemporal() -> DataObject:
    """DataObject whose specificInfo is a SpatioTemporalMeta."""
    return make_spatiotemporal_dataobject()
