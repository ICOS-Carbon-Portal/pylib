from typing import Literal, TypeAlias
from dataclasses import dataclass

Envri: TypeAlias = Literal["ICOS", "SITES", "ICOSCities"]

@dataclass(frozen=True)
class EnvriConfig:
	envri: Envri
	sparql_endpoint: str
	meta_instance_prefix: str
	auth_service_base_url: str
	data_service_base_url: str
	default_station_type_url: str
	token_name: str
	site_used: bool

ICOS_CONFIG = EnvriConfig(
	envri = "ICOS",
	sparql_endpoint = "https://meta.icos-cp.eu/sparql",
	meta_instance_prefix = "http://meta.icos-cp.eu/",
	auth_service_base_url = "https://cpauth.icos-cp.eu/",
	data_service_base_url = "https://data.icos-cp.eu",
	default_station_type_url = "http://meta.icos-cp.eu/ontologies/cpmeta/IcosStation",
	token_name = "cpauthToken",
	site_used = False
)

SITES_CONFIG = EnvriConfig(
	envri = "SITES",
	sparql_endpoint = "https://meta.fieldsites.se/sparql",
	meta_instance_prefix = "https://meta.fieldsites.se/",
	auth_service_base_url = "https://auth.fieldsites.se/",
	data_service_base_url = "https://data.fieldsites.se",
	default_station_type_url = "https://meta.fieldsites.se/ontologies/sites/Station",
	token_name = "fieldsitesToken",
	site_used = True
)

CITIES_CONFIG = EnvriConfig(
	envri = "ICOSCities",
	sparql_endpoint = "https://citymeta.icos-cp.eu/sparql",
	meta_instance_prefix = "https://citymeta.icos-cp.eu/",
	auth_service_base_url = "https://cpauth.icos-cp.eu/",
	data_service_base_url = "https://citydata.icos-cp.eu",
	default_station_type_url = "http://meta.icos-cp.eu/ontologies/cpmeta/IcosCitiesStation",
	token_name = "cpauthToken",
	site_used = False
)

ENVRIES: dict[Envri, EnvriConfig] = {
	"ICOS": ICOS_CONFIG,
	"SITES": SITES_CONFIG,
	"ICOSCities": CITIES_CONFIG
}
