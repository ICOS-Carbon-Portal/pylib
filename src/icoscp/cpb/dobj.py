from icoscp_core.icos import meta, data, auth
from icoscp_core.metacore import DataObject, URI, StationTimeSeriesMeta
from icoscp_todo import constants as c
from icoscp_todo.exceptions import UriValueError, FormatValueError, \
    MetaTypeError
from typing import Optional, Any, TypedDict
from dataclasses import asdict
import pandas as pd


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
    def citation(self) -> Optional[str]:
        # Mypy will complain if we set the return statement without
        # the None fallback.
        return self.metadata.references.citationString or None

    @property
    # def licence(self) -> dict[str, Optional[str]]:
    #     licence = self.metadata.references.licence
    #     return {
    #         "baseLicence": licence.baseLicence,
    #         "name": licence.name,
    #         "url": licence.url,
    #         "webpage": licence.webpage
    #     }
    def licence(self) -> LicenceDict:
        licence = self.metadata.references.licence
        return LicenceDict(
            baseLicence=licence.baseLicence,
            name=licence.name,
            url=licence.url,
            webpage=licence.webpage
        )

    @property
    def previous(self) -> Optional[URI | list[URI]]:
        return self.metadata.previousVersion

    @property
    def next(self) -> Optional[URI | list[URI]]:
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

    def get_citation(self, format: str = "plain") -> Optional[str]:
        """
        Extract the citation string in the requested format.

        :param format: The format of the citation ("plain", "bibtex",
         or "ris").
        :return: The citation string in the specified format.
        :raise FormatValueError: A ValueError is raised when an
         unsupported format is provided.
        """

        references = self.metadata.references
        format_attr = {
            "plain": "citationString",
            "bibtex": "citationBibTex",
            "ris": "citationRis"
        }.get(format)
        if format_attr is not None:
            citation = getattr(references, format_attr)
            return str(citation) if citation else None
        else:
            raise FormatValueError(unsupported_format=format)

    def variables(self) -> pd.DataFrame:
        """
        Extracts all variables from a metadata object.

        Please remember that this list contains variables which are
        "preview-able" at https://data.icoscp.eu. These variables are
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

