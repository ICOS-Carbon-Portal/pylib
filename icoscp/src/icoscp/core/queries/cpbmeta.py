import json
from dataclasses import dataclass

from ..metaclient import MetadataClient
from ..metacore import URI
from ..sparql import Binding, as_uri, as_int, as_opt_str, as_string, as_opt_bool

@dataclass(frozen=True)
class CpbMetaData:
	dobj: URI
	obj_spec: URI
	dataset_spec: URI
	obj_format: URI
	n_rows: int
	col_names: list[str] | None

@dataclass(frozen=True)
class DatasetCol:
	col_title: str
	val_format: URI
	is_optional: bool
	is_regex: bool
	flag_col: str | None


def get_cpb_meta(dobjs: list[URI], meta: MetadataClient) -> list[CpbMetaData]:
	query = f"""
		prefix cpmeta: <http://meta.icos-cp.eu/ontologies/cpmeta/>
		select * where{{
			values ?dobj {{ <{'> <'.join(dobjs)}> }}
			?dobj cpmeta:hasObjectSpec ?objSpec ; cpmeta:hasNumberOfRows ?nRows .
			?objSpec cpmeta:containsDataset ?dsSpec ; cpmeta:hasFormat ?objFormat .
			optional{{?dobj cpmeta:hasActualColumnNames ?colNames }}
		}}"""
	return [_parse_cpb_meta(binding) for binding in meta.sparql_select(query).bindings]

def _parse_cpb_meta(binding: Binding) -> CpbMetaData:
	col_names_json = as_opt_str("colNames", binding)
	return CpbMetaData(
		dobj=as_uri("dobj", binding),
		obj_spec=as_uri("objSpec", binding),
		dataset_spec=as_uri("dsSpec", binding),
		obj_format=as_uri("objFormat", binding),
		n_rows=as_int("nRows", binding),
		col_names=json.loads(col_names_json) if col_names_json else None
	)

def get_dataset_cols(dataset_spec: URI, meta: MetadataClient) -> list[DatasetCol]:
	query = f"""
		prefix cpmeta: <http://meta.icos-cp.eu/ontologies/cpmeta/>
		select ?colTitle ?valFormat ?isOptional ?isRegex ?flagColTitle where{{
			<{dataset_spec}> cpmeta:hasColumn ?col .
			?col cpmeta:hasColumnTitle ?colTitle ; cpmeta:hasValueFormat ?valFormat .
			optional{{?col cpmeta:isOptionalColumn ?isOptional}}
			optional{{?col cpmeta:isRegexColumn ?isRegex}}
			optional{{
				?flagCol cpmeta:isQualityFlagFor ?col ; cpmeta:hasColumnTitle ?flagColTitle .
				<{dataset_spec}> cpmeta:hasColumn ?flagCol .
			}}
		}}"""
	return [
		DatasetCol(
			col_title=as_string("colTitle", binding),
			val_format=as_uri("valFormat", binding),
			is_optional=as_opt_bool("isOptional", binding) or False,
			is_regex=as_opt_bool("isRegex", binding) or False,
			flag_col=as_opt_str("flagColTitle", binding)
		)
		for binding in meta.sparql_select(query).bindings
	]

def get_good_flags_per_spec(obj_specs: list[URI], meta: MetadataClient) -> dict[URI, list[str]]:
	uniq_obj_specs = [spec for spec in {spec for spec in obj_specs}]
	query = f"""
		prefix cpmeta: <http://meta.icos-cp.eu/ontologies/cpmeta/>
		select ?objFormat (group_concat(?goodFlag; separator=";") as ?goodFlags) where{{
			values ?spec {{ <{'> <'.join(uniq_obj_specs)}> }}
			?spec cpmeta:hasFormat ?objFormat .
			optional {{?objFormat cpmeta:hasGoodFlagValue ?goodFlag}}
		}}
		group by ?objFormat
	"""
	q_res = meta.sparql_select(query)
	joined = {
		as_uri("objFormat", binding): as_opt_str("goodFlags", binding)
		for binding in q_res.bindings
	}
	return {
		spec: flags.split(';')
		for spec, flags in joined.items()
		if flags
	}
