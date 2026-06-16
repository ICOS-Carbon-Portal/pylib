from dataclasses import dataclass

from ..sparql import Binding, as_int, as_uri, as_string, as_opt_uri
from ..envri import EnvriConfig
from ..metacore import UriResource, DatasetType


@dataclass(frozen=True)
class DobjSpecLite(UriResource):
	"""
	Dataclass representing  data type (i.e. type of a data object, or data
	object specification). Extends UriResource.

	Attributes:
		`uri` (string):
			URI id of the data type. Inherited from UriResource
		`label` (string):
			user-friendly label of this data type. Inherited from UriResource
		`data_level` (int):
			0 for raw observational data,
			1 for automatically produced observational data products,
			2 for quality-controlled observational data products,
			3 for elaborated products
		`dataset_type` (string):
			'StationTimeSeries' for tabular single-station observational data
			'SpatioTemporal' for objects with both temporal and geo coverage
		`dataset_spec_uri` (string):
			URI reference to metadata about the dataset variables
		`theme` (UriResource):
			repository-specific data theme (e.g. Ocean or Ecosystem for ICOS);
			is itself a dataclass with `uri` and `label` properties
		`project` (UriResource):
			repository-specific data affiliation project (e.g. ICOS, GCP,
			SITES AquaNet);
			is itself a dataclass with `uri` and `label` properties
		`format` (UriResource):
			data object format, e.g. CSV, NetCDF, arbitrary ZIP, etc;
			is itself a dataclass with `uri` and `label` properties
	"""
	data_level: int
	dataset_type: DatasetType
	dataset_spec_uri: str | None
	theme: UriResource
	project: UriResource
	format: UriResource
	@property
	def has_data_access(self) -> bool:
		return self.dataset_type == "StationTimeSeries" and self.dataset_spec_uri is not None

def dobj_spec_lite_list(conf: EnvriConfig) -> str:
	return f"""
prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
prefix cpmeta: <http://meta.icos-cp.eu/ontologies/cpmeta/>
prefix xsd: <http://www.w3.org/2001/XMLSchema#>
select * where{{
	?spec cpmeta:hasDataLevel ?level ;
		cpmeta:hasAssociatedProject ?project ;
		cpmeta:hasFormat ?format ;
		cpmeta:hasSpecificDatasetType ?dsType .
	FILTER NOT EXISTS {{?project cpmeta:hasHideFromSearchPolicy "true"^^xsd:boolean}}
	FILTER(STRSTARTS(str(?spec), "{conf.meta_instance_prefix}"))
	?spec rdfs:label ?specLabel ; cpmeta:hasDataTheme ?theme .
	?theme rdfs:label ?themeLabel .
	?project rdfs:label ?projectLabel .
	?format rdfs:label ?formatLabel .
	optional {{?spec cpmeta:containsDataset ?ds_spec_uri}}
}}
order by ?specLabel"""

def parse_dobj_spec_lite(row: Binding) -> DobjSpecLite:
	dsType: DatasetType
	match as_uri("dsType", row):
		case "http://meta.icos-cp.eu/ontologies/cpmeta/stationTimeSeriesDataset":
			dsType = "StationTimeSeries"
		case "http://meta.icos-cp.eu/ontologies/cpmeta/spatioTemporalDataset":
			dsType = "SpatioTemporal"
		case bad:
			raise ValueError(f"Unexpected URI representing a dataset type: {bad}")

	return DobjSpecLite(
		uri = as_uri("spec", row),
		label = as_string("specLabel", row),
		comments = [],
		data_level = as_int("level", row),
		project = UriResource(
			uri = as_uri("project", row),
			label = as_string("projectLabel", row),
			comments = []
		),
		theme = UriResource(
			uri = as_uri("theme", row),
			label = as_string("themeLabel", row),
			comments = []
		),
		format = UriResource(
			uri = as_uri("format", row),
			label = as_string("formatLabel", row),
			comments = []
		),
		dataset_type = dsType,
		dataset_spec_uri = as_opt_uri("ds_spec_uri", row)
	)
