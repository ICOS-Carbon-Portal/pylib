from datetime import datetime
from typing import TypeAlias, TypeVar, Optional, Any, Callable
from dataclasses import dataclass
import re
import json

from .http import http_request

@dataclass(frozen=True)
class BoundUri:
	uri: str

@dataclass(frozen=True)
class BoundLiteral:
	value: str
	datatype: Optional[str]

BoundValue: TypeAlias = BoundUri | BoundLiteral

Binding: TypeAlias = dict[str, BoundValue]

@dataclass(frozen=True)
class SparqlResults:
	variable_names: list[str]
	bindings: list[Binding]

def as_uri(varname: str, binding: Binding) -> str:
	bv = _lookup(varname, binding)
	if type(bv) is BoundUri:
		return bv.uri
	else:
		raise _type_error(varname, "a uri value", bv)

ResT = TypeVar('ResT')
SparqlVarParser: TypeAlias = Callable[[str, Binding], ResT]

def _as_type(xsd_type: str | None, parser: Callable[[str], ResT]) -> SparqlVarParser[ResT]:
	return lambda varname, binding:(
		parser(_lookup_literal_value(varname, xsd_type, binding))
	)

def _as_opt(plain: SparqlVarParser[ResT]) -> SparqlVarParser[ResT | None]:
	return lambda varname, binding: plain(varname, binding) if varname in binding.keys() else None

as_bool: SparqlVarParser[bool] = _as_type("boolean", lambda s: True if s.lower() == "true" else False)
as_int: SparqlVarParser[int] = _as_type("integer", lambda s: int(s))
as_double: SparqlVarParser[float] = _as_type("double", lambda s: float(s))
as_float: SparqlVarParser[float] = _as_type("float", lambda s: float(s))
as_long: SparqlVarParser[int] = _as_type("long", lambda s: int(s))
as_string: SparqlVarParser[str] = _as_type(None, lambda s: s)
as_datetime: SparqlVarParser[datetime] = _as_type(
	xsd_type = "dateTime",
	parser = lambda s: datetime.fromisoformat(re.sub(r'Z$', '+00:00', s))
)
as_opt_bool = _as_opt(as_bool)
as_opt_double = _as_opt(as_double)
as_opt_float = _as_opt(as_float)
as_opt_str = _as_opt(as_string)
as_opt_uri = _as_opt(as_uri)

def _lookup(varname: str, binding: Binding) -> BoundValue:
	v = binding.get(varname)
	if not v:
		raise ValueError(f"Variable {varname} had no bound values in SPARQL response")
	else:
		return v

def _lookup_literal_value(varname: str, datatype: Optional[str], binding: Binding) -> str:
	bv = _lookup(varname, binding)
	if type(bv) is BoundLiteral:
		if not(datatype) or bv.datatype == ("http://www.w3.org/2001/XMLSchema#" + datatype):
			return bv.value
		else:
			raise _type_error(varname, f"literal datatype {datatype}", bv)
	else:
		raise _type_error(varname, "a literal", bv)

def _type_error(varname: str, expected: str, bv: BoundValue) -> ValueError:
	msg = f"Was expecting {expected}, got value {bv} for variable {varname} in SPARQL results"
	return ValueError(msg)

def get_sparql_select_json(endpoint: str, query: str, disable_cache: bool) -> Any:
	headers: dict[str, str] = {"Accept": "application/json"}
	if disable_cache:
		headers["Cache-Control"] = "no-cache"
		headers["Pragma"] = "no-cache"
	resp = http_request(endpoint, "SPARQL SELECT", "POST", headers, query)
	return json.loads(resp.read())

def sparql_select(endpoint: str, query: str, disable_cache: bool) -> SparqlResults:
	js = get_sparql_select_json(endpoint, query, disable_cache)
	varnames: list[str] = js["head"]["vars"]
	binding_dicts: list[dict[str, Any]] = js["results"]["bindings"]
	bindings = [{key: _parse_bound_value(v) for key, v in b_dict.items()} for b_dict in binding_dicts]
	return SparqlResults(varnames, bindings)

def _parse_bound_value(v: Any) -> BoundValue:
	match v["type"]:
		case "uri": return BoundUri(uri = v["value"])
		case "literal": return BoundLiteral(value = v["value"], datatype=v.get("datatype"))
		case "bnode": raise ValueError("Blank nodes in SPARQL return results are not supported by this" +
			" library. Please re-formulate your query.")
		case bad: raise ValueError(f"Unexpected result type encountered in SPARQL response: {bad}")
