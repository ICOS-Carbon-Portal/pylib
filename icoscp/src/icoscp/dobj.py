# Standard library imports.
from dataclasses import asdict
from typing import Optional, Any, TypedDict, TypeAlias, Literal
import warnings

# Related third party imports.
from icoscp_core.icos import meta, bootstrap
from icoscp import cpauth
from icoscp_core.metacore import DataObject, URI, StationTimeSeriesMeta, \
    Station, Position
from icoscp_core.queries.dataobjlist import DataObjectLite
import pandas as pd

# Local application/library specific imports.
import icoscp.const as c
from icoscp.exceptions import UriValueError, FormatValueError, MetaTypeError, \
    MetaValueError


CitationFormat: TypeAlias = Literal["plain", "bibtex", "ris"]


class LicenceDict(TypedDict):
    baseLicence: Optional[str]
    name: str
    url: str
    webpage: str


class Dobj:
    def __init__(self, digitalObject: str | DataObjectLite | Any) -> None:
        if (not isinstance(digitalObject, str) and
                not isinstance(digitalObject, DataObjectLite)):
            raise UriValueError
        if isinstance(digitalObject, str):
            self.data_obj_uri = \
                self.standardize_uri(data_obj_uri=digitalObject)
            self.metadata: DataObject = \
                meta.get_dobj_meta(dobj=self.data_obj_uri)
        else:
            self.metadata: DataObject = \
                meta.get_dobj_meta(dobj=self.data_obj_uri)

    @staticmethod
    def standardize_uri(data_obj_uri: str) -> str:
        if c.ICOS_LANDING_PAGE_PREFIX in data_obj_uri:
            standardized_pid = data_obj_uri
        elif data_obj_uri.startswith(c.ICOS_HANDLE_PREFIX):
            object_hash = data_obj_uri.split(c.ICOS_HANDLE_PREFIX)[1]
            standardized_pid = f"{c.ICOS_LANDING_PAGE_PREFIX}{object_hash}"
        else:
            standardized_pid = f"{c.ICOS_LANDING_PAGE_PREFIX}/{data_obj_uri}"
        return standardized_pid

    @property
    def id(self) -> str:
        return self.data_obj_uri

    @property
    def dobj(self) -> str:
        return self.data_obj_uri

    @property
    def valid(self) -> bool:
        warnings.warn(
            message=(
                "In the next release, the property 'Dobj.valid' will be "
                "deprecated."),
            category=FutureWarning)
        return True

    @property
    def info(self) -> dict[str, Optional[Any]]:
        """Same as Dobj.meta"""
        warnings.warn(
            message=(
                "In the next release, the property 'Dobj.info' will be "
                "deprecated. Please, use 'Dobj.meta' instead."),
            category=FutureWarning)
        return self.meta

    @property
    def meta(self) -> dict[str, Optional[Any]]:
        return asdict(self.metadata)

    @property
    def citation(self) -> str | None:
        return self.metadata.references.citationString

    def get_citation(self, format: CitationFormat = "plain") -> str | None:
        """
        Extract the citation string in the requested format.

        :param format: The format of the citation ("plain", "bibtex",
            or "ris").
        :return: The citation string in the specified format.
        :raise FormatValueError: A ValueError is raised when an
            unsupported format is provided.
        """
        references = self.metadata.references
        citation = None
        match format:
            case "plain":
                citation = references.citationString
            case "bibtex":
                citation = references.citationBibTex
            case "ris":
                citation = references.citationRis
            case _:  # type: ignore
                raise FormatValueError(unsupported_format=format)
        return citation

    @property
    def licence(self) -> LicenceDict | None:
        licence = self.metadata.references.licence
        return LicenceDict(
            baseLicence=licence.baseLicence,
            name=licence.name,
            url=licence.url,
            webpage=licence.webpage
        ) if licence else None

    @property
    def previous(self) -> URI | list[URI] | None:
        return self.metadata.previousVersion

    @property
    def next(self) -> URI | list[URI] | None:
        return self.metadata.nextVersion

    @property
    def colNames(self) -> list[str] | None:
        specific_info = self.metadata.specificInfo
        if isinstance(specific_info, StationTimeSeriesMeta):
            columns = specific_info.columns
            return [column.label for column in columns] if columns else None
        else:
            raise MetaTypeError(unsupported_type=specific_info,
                                caller="colNames")

    @property
    def lat(self) -> float | None:
        p = self._position
        return None if p is None else p.lat

    @property
    def lon(self) -> float | None:
        p = self._position
        return None if p is None else p.lon

    @property
    def alt(self) -> float | None:
        p = self._position
        return None if p is None else p.alt

    @property
    def elevation(self) -> float | None:
        warnings.warn(
            message=(
                "In the next release, the property 'Dobj.elevation' will be "
                "deprecated. Please, use 'Dobj.alt' instead."),
            category=FutureWarning)
        return self.alt

    @property
    def station(self) -> dict[str, Any]:
        s = self._station_meta
        if s is None:
            raise ValueError
        return asdict(s)

    @property
    def _station_meta(self) -> Station | None:
        spec_info = self.metadata.specificInfo
        return spec_info.acquisition.station \
            if isinstance(spec_info, StationTimeSeriesMeta) \
            else spec_info.station

    @property
    def _position(self) -> Position | None:
        s = self._station_meta
        return None if s is None else s.location

    @property
    def data(self) -> pd.DataFrame:
        return self.get(columns=None)

    @property
    def variables(self) -> pd.DataFrame:
        """
        Extracts all variables from a metadata object.

        Please remember that this list contains variables which are
        "preview-able" at https://data.icos-cp.eu. These variables are
        considered the most useful for a quick glance. More variables
        may be available, if you download the data to your computer.

        :return: A pandas dataframe containing the preview-able
          variables.

        :raise MetaTypeError: A MetaTypeError is raised when an
         unsupported format is provided.
        """

        spec_info = self.metadata.specificInfo
        is_time_series = isinstance(spec_info, StationTimeSeriesMeta)
        cols = spec_info.columns if is_time_series else spec_info.variables
        if cols is None:
            raise MetaValueError
        return pd.DataFrame({
            "name": [v.label for v in cols],
            "unit": [v.valueType.unit for v in cols],
            "type": [v.valueType.self.label for v in cols],
            "format": [v.valueFormat if is_time_series
                       else c.FLOAT_64_VALUEFORMAT
                       for v in cols]
        })

    def get(self, columns: list[str] | None = None) -> pd.DataFrame:
        """
        Get data for the selected columns, or all columns.

        :return: A pandas dataframe generated using a standardized
         plain CSV serialization of a tabular data object.
        """

        data_client = bootstrap.fromAuthProvider(cpauth)
        df = pd.DataFrame(data_client.get_columns_as_arrays(dobj=self.metadata,
                                                     columns=columns))
        df = df.reindex(sorted(df.columns), axis=1)  # type: ignore
        return df

    def getColumns(self, columns: list[str] | None = None) -> pd.DataFrame:
        """Same as Dobj.get()"""
        warnings.warn(
            message=(
                "In the next release, the method 'Dobj.getColumns()' will be "
                "deprecated. Please, use 'Dobj.get()' instead."),
            category=FutureWarning)
        return self.get(columns=columns)
