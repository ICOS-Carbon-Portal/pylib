from .envri import ICOS_CONFIG
from .bootstrap import Bootstrap
from .sparql import as_string, as_uri
from .metacore import URI

bootstrap = Bootstrap(ICOS_CONFIG)
auth, meta, data = bootstrap.fromPasswordFile()

ONTOLOGY_PREFIX: str = "http://meta.icos-cp.eu/ontologies/cpmeta/"

def onto_uri(suffix: str) -> str:
	return ONTOLOGY_PREFIX + suffix

ATMO_STATION  = onto_uri("AS")
ECO_STATION   = onto_uri("ES")
OCEAN_STATION = onto_uri("OS")


_station_class_lookup: dict[URI, str] | None = None

def station_class_lookup() -> dict[URI, str]:
	"""
	ICOS-specific utility function producing lookup of station class by
	station URI. Caches the result after the first call. The cache can
	be dropped by setting `_station_class_lookup` to `None`

	:returns: dictionary from station URI id to the station class string
	"""
	global _station_class_lookup
	if _station_class_lookup is not None:
		return _station_class_lookup
	statClassQuery = f"select * where{{?station <{onto_uri('hasStationClass')}> ?class}}"
	_station_class_lookup = {
		as_uri('station', row): as_string('class', row)
			for row in meta.sparql_select(statClassQuery).bindings
	}
	return _station_class_lookup
