from icoscp_core import icos

from icoscp_core.icos import meta, data
from icoscp_core.metacore import DataObject, URI, StationTimeSeriesMeta
from icoscp_todo import constants as c
from icoscp_todo.exceptions import UriValueError, FormatValueError, \
    MetaTypeError
from typing import Optional, Any, TypedDict, TypeAlias, Literal
from dataclasses import asdict
import pandas as pd

CitationFormat: TypeAlias = Literal["plain", "bibtex", "ris"]

class LicenceDict(TypedDict):
    baseLicence: Optional[str]
    name: str
    url: str
    webpage: str


class Dobj:
    def __init__(self, digitalObject: str) -> None:
        if isinstance(digitalObject, str):
            self.data_obj_uri = \
                self.standardize_uri(data_obj_uri=digitalObject)
            self.metadata: DataObject = \
                meta.get_dobj_meta(dobj=self.data_obj_uri)
        else:
            raise UriValueError

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
    def info(self) -> dict[str, Optional[Any]]:
        return self.meta

    @property
    def meta(self) -> dict[str, Optional[Any]]:
        return asdict(self.metadata)

    @property
    def citation(self) -> str | None:
        return self.metadata.references.citationString

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
    def colNames(self) -> Optional[list[str]]:
        specific_info = self.metadata.specificInfo
        if isinstance(specific_info, StationTimeSeriesMeta):
            columns = specific_info.columns
            return [column.label for column in columns] if columns else None
        else:
            raise MetaTypeError(unsupported_type=specific_info,
                                caller="colNames")

    @property
    def data(self) -> pd.DataFrame:
        return self.get(columns=None)

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
        match format:
            case "plain":  return references.citationString
            case "bibtex": return references.citationBibTex
            case "ris":    return references.citationRis
            case _:        raise FormatValueError(unsupported_format=format) # type: ignore

    def variables(self) -> pd.DataFrame:
        """
        Extracts all variables from a metadata object.

        Please remember that this list contains variables which are
        "preview-able" at https://data.icos-cp.eu. These variables are
        considered the most useful for a quick glance. More variables
        may be available, If you download the data to your computer.

        :return: A pandas dataframe containing the preview-able
          variables.

        :raise MetaTypeError: A MetaTypeError is raised when an
         unsupported format is provided.
        """

        specific_info = self.metadata.specificInfo
        if isinstance(specific_info, StationTimeSeriesMeta):
            column_series = pd.Series(specific_info.columns)
            return pd.DataFrame({
                "name": column_series.apply(lambda v: v.label),
                "unit": column_series.apply(lambda v: v.valueType.unit),
                "type": column_series.apply(lambda v: v.valueType.self.label),
                "format": column_series.apply(lambda v: v.valueFormat)
            })
        else:
            raise MetaTypeError(unsupported_type=specific_info,
                                caller="variables")

    def get(self, columns: Optional[list[str]]) -> pd.DataFrame:
        """
        Todo:

        :return: A pandas dataframe generated using a standardized
         plain CSV serialization of a tabular data object.
        """

        df = pd.read_csv(data.get_csv_byte_stream(dobj=self.data_obj_uri,
                                                  cols=columns))
        df = df.reindex(sorted(df.columns), axis=1)
        if "TIMESTAMP" in df.columns:
            df["TIMESTAMP"] = \
                pd.to_datetime(df["TIMESTAMP"]).dt.tz_localize(None)
        return df

