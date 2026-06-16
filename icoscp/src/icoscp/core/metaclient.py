from .envri import EnvriConfig
from .sparql import SparqlResults, sparql_select as sparql_select_generic
from .queries.speclist import dobj_spec_lite_list, parse_dobj_spec_lite, DobjSpecLite
from .queries.dataobjlist import DataObjectLite, parse_dobj_lite, dataobj_lite_list
from .queries.dataobjlist import Filter, OrderBy, OrderByProp, CategorySelector
from .queries.stationlist import station_lite_list, parse_station, StationLite
from .metacore import CPJson, parse_cp_json
from .metacore import DataObject as VanillaDataObject, StaticCollection as VanillaStaticCollection
from .rolemeta import StationWithStaff
from .geofeaturemeta import GeoFeatureWithGeo, Point
from .http import http_request
from typing import Type, TypeAlias, Literal, Any, Optional
from dataclasses import dataclass

# the following are needed for convenient re-export by the end user
from .queries.dataobjlist import TimeFilter, SizeFilter, SamplingHeightFilter, GeoIntersectFilter
from .queries.dataobjlist import box_intersect
# and the following to suppress warnings about unused imports:
_needed_classes: TypeAlias = TimeFilter | SizeFilter | SamplingHeightFilter | GeoIntersectFilter | Point
_needed_method = box_intersect

@dataclass(frozen=True)
class DataObject(VanillaDataObject):
	coverageGeo: dict[str, Any]

@dataclass(frozen=True)
class StaticCollection(VanillaStaticCollection):
	coverage: Optional[GeoFeatureWithGeo]

@dataclass(frozen=True)
class Station(StationWithStaff):
	coverage: Optional[GeoFeatureWithGeo]

class MetadataClient:
	def __init__(self, envri_conf: EnvriConfig):
		self._envri_conf = envri_conf

	def sparql_select(self, query: str, disable_cache: bool = False) -> SparqlResults:
		"""
		Runs a SPARQL SELECT query against the SPARQL endpoint exposed
		by the Repository.

		:param `query`:
			A string containing the query
		:param `disable_cache`:
			A boolean flag indicating whether to accept cached SPARQL
			responses or disable the cache. By default the cache is
			enabled.
		:return:
			An instance of `SparqlResults` data class, declared in
			`sparql` module of this library.
		"""
		endpoint = self._envri_conf.sparql_endpoint
		return sparql_select_generic(endpoint, query, disable_cache)

	def list_datatypes(self) -> list[DobjSpecLite]:
		"""
		List available data types. Presense of data of these types is
		not guaranteed.

		:return:
			List of `DobjSpecLite` objects with basic information about
			the data types: URI id `uri`, `label`, `project`, `theme`,
			`data_level`, `dataset_type` (`'StationTimeSeries'` for
			station-specific time series dataset or `'SpatioTemporal'`
			for a more general dataset with spatial and temporal
			coverages, which can optionally be associated with a
			station), and optional dataset specification URI
			`dataset_spec_uri`, presense of which indicates that data
			of this type must have certain column/variable metadata.
			Data objects with `'StationTimeSeries'` datasets and non-
			empty `dataset_spec_uri` can be fetched as CSV or as a
			dictionary of readily parsed arrays using DataClient
			(obtainable as e.g. `from icoscp_core.<repo> import data`).
		"""
		query = dobj_spec_lite_list(self._envri_conf)
		qres = self.sparql_select(query)
		return [parse_dobj_spec_lite(b) for b in qres.bindings]

	def list_stations(self, of_station_type_uri: str | None | Literal[False] = None ) -> list[StationLite]:
		"""
		List basic information about available stations. Presense of
		data from/for these stations is not guaranteed, as there may
		not have been any data from this station uploaded.

		:param `of_station_type_uri`: The URI of the type of
		interesting station (in RDF metadata, the rdf:type of the
		station resource, or a supertype of the interesting types).
		If omitted, a default type specific to the Repository
		context is used (e.g. only the ICOS stations for ICOS
		Repository). Look in `icoscp_core.<repo>` package for your
		Repository for defined constants for different interesting
		types of stations. For example, `icoscp_core.icos.ATMO_STATION`
		for ICOS Atmosphere stations. To get all stations without any
		filtering, use `False`.

		:return: A list of `StationLite` objects with basic
		information about the stations, defined in package
		`queries.stationlist`
		"""

		station_type: str | None = None
		if of_station_type_uri is None:
			station_type = self._envri_conf.default_station_type_url
		elif type(of_station_type_uri) == str:
			station_type = of_station_type_uri

		query = station_lite_list(station_type, self._envri_conf)
		qres = self.sparql_select(query)
		return [parse_station(b) for b in qres.bindings]

	def list_data_objects(
		self,
		datatype: CategorySelector = None,
		station: CategorySelector = None,
		filters: list[Filter] = [],
		include_deprecated: bool = False,
		order_by: OrderBy | OrderByProp | None = {"prop": "submTime", "descending": True},
		limit: int = 100,
		offset: int = 0
	) -> list[DataObjectLite]:
		"""
		Method for listing, selecting, filtering, sorting, and paging
		through the lists of, data objects.

		:param `datatype`: either a `DobjSpecLite` object (obtainable
		from `list_datatypes` method), or a URI identifying a datatype,
		or a list of either of the two, or `None` (default) for all
		datatypes.

		:param `station`: either a `StationLite` object (obtainable
		from `list_stations` method), or a URI identifying a station, or
		a list of either of the two, or `None` (default) for all
		stations.

		:param `filters`: a list of filters, each filter being either
		`TimeFilter` for filtering by submission time, or data start- or
		stop time, `SizeFilter` for filtering by file size,
		`SamplingHeightFilter` for filtering by sampling height
		(applicable only to data objects with sampling height metadata),
		or `GeoIntersectFilter` for geospatial filtering;
		the list is empty by default.

		:param `include_deprecated`: boolean flag to include deprecated
		(i.e. such that have a newer version with explicit metadata
		link) data objects in the list; `False` by default.

		:param `order_by`: either `OrderByProp` --- a property to sort
		the objects by, in ascending order (one of strings 'submTime',
		'timeStart', 'timeEnd', 'size', 'fileName') or a dictionary of
		the form {"prop": OrderByProp, "descending": bool}, or None for
		no sorting. By default, the results are sorted by submission
		time in descending order.

		:param `limit`: the maximum size of the list to return; 100 by
		default; values above 10000 are ignored and 10000 is used.

		:param `offset`: the results page offset; 0 by default.

		:return: a list of `DataObjectLite` instances with basic data
		object metadata (defined in `queries.dataobjlist` package).
		"""
		query = dataobj_lite_list(datatype, station, filters, include_deprecated, order_by, limit, offset)
		qres = self.sparql_select(query)
		return [parse_dobj_lite(b) for b in qres.bindings]

	def get_dobj_meta(self, dobj: str | DataObjectLite) -> DataObject:
		"""
		Get fully detailed metadata of a data object

		:param `dobj`: either a landing page URI or an instance of
		`DataObjectLite` class (obtainable with `list_data_objects`
		method)

		:return: Python dataclass `DataObject` whose definition was
		generated by automatically transforming the corresponding data
		portal code; it closely mimicks the JSON metadata returned by
		the data portal back end from the data object landing page.
		"""
		dobj_uri: str

		if type(dobj) == str: dobj_uri = dobj
		elif type(dobj) == DataObjectLite: dobj_uri = dobj.uri
		else: raise ValueError("dobj must be either landing page URL or an instance of DataObjectLite")

		return _get_json_meta(dobj_uri, DataObject)
	
	def get_station_meta(self, station: str | StationLite) -> Station:
		"""
		Get fully detailed metadata of a station

		:param `station`: either a station URI id or an instance of
		`StationLite` class (obtainable with `list_stations` method)

		:return: Python dataclass `Station` whose definition was
		generated by automatically transforming the corresponding data
		portal code; it closely mimicks the JSON metadata returned by
		the data portal back end from the station URI id.
		"""
		station_uri: str

		if type(station) == str: station_uri = station
		elif type(station) == StationLite: station_uri = station.uri
		else: raise ValueError("Station must be either landing page URL or an instance of StationLite")

		return _get_json_meta(station_uri.replace("http://", "https://"), Station)

	def get_collection_meta(self, coll_uri: str) -> StaticCollection:
		"""
		Get metadata of a collection

		:param `coll_uri`: a string with URI of the collection's landing page

		:return: Python dataclass `StaticCollection` whose definition was
		generated by automatically transforming the corresponding data
		portal code; it closely mimicks the JSON metadata returned by
		the data portal back end from the collection URI id.
		"""
		return _get_json_meta(coll_uri, StaticCollection)

def _get_json_meta(url: str, data_class: Type[CPJson]) -> CPJson:
	headers = {"Accept": "application/json"}
	resp = http_request(url, "Fetching JSON metadata", headers=headers)
	return parse_cp_json(resp.read().decode(), data_class=data_class)
