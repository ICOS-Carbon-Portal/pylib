"""Tests for icoscp.dobj.Dobj wrapping icoscp.core metadata types."""

# Asserts are the idiomatic pytest assertion mechanism.
# ruff: noqa: S101

# Standard library imports.
from unittest import mock

# Related third party imports.
import pytest

# Local application/library specific imports.
from conftest import (
    HASH,
    OBJECT_URI,
    STATION_ALT,
    STATION_LAT,
    STATION_LON,
    make_licence,
)
from icoscp.core.metacore import DataObject

from icoscp import dobj
from icoscp.exceptions import MetaTypeError, UriValueError


@pytest.mark.parametrize("raw_uri", [
    OBJECT_URI,
    f"11676/{HASH}",
    HASH,
])
def test_standardize_uri_normalizes_all_pid_forms(raw_uri: str) -> None:
    assert dobj.Dobj.standardize_uri(data_obj_uri=raw_uri) == OBJECT_URI


def test_init_with_non_str_raises_uri_value_error() -> None:
    with pytest.raises(UriValueError):
        dobj.Dobj(123)


def _build(metadata: DataObject) -> dobj.Dobj:
    """Construct a Dobj while get_dobj_meta is patched (no network)."""
    with mock.patch.object(dobj.meta, "get_dobj_meta",
                           return_value=metadata):
        return dobj.Dobj(HASH)


def test_citation_returns_reference_citation_string(
        dataobject: DataObject) -> None:
    instance = _build(dataobject)
    assert instance.citation == dataobject.references.citationString


def test_licence_returns_licence_dict_when_present(
        dataobject: DataObject) -> None:
    instance = _build(dataobject)
    expected = make_licence()
    assert instance.licence == {
        "baseLicence": expected.baseLicence,
        "name": expected.name,
        "url": expected.url,
        "webpage": expected.webpage,
    }


def test_licence_returns_none_when_absent(
        dataobject_no_licence: DataObject) -> None:
    instance = _build(dataobject_no_licence)
    assert instance.licence is None


def test_lat_lon_alt_return_position_values(
        dataobject: DataObject) -> None:
    instance = _build(dataobject)
    assert instance.lat == STATION_LAT
    assert instance.lon == STATION_LON
    assert instance.alt == STATION_ALT


def test_lat_lon_alt_return_none_without_location(
        dataobject_no_location: DataObject) -> None:
    instance = _build(dataobject_no_location)
    assert instance._station_meta is not None
    assert instance.lat is None
    assert instance.lon is None
    assert instance.alt is None


def test_colnames_returns_column_labels(
        dataobject: DataObject) -> None:
    instance = _build(dataobject)
    assert instance.colNames == ["TIMESTAMP", "co2"]


def test_colnames_raises_on_spatiotemporal(
        dataobject_spatiotemporal: DataObject) -> None:
    instance = _build(dataobject_spatiotemporal)
    with pytest.raises(MetaTypeError):
        _ = instance.colNames
