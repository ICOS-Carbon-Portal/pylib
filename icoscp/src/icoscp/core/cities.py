from .envri import CITIES_CONFIG
from .bootstrap import Bootstrap

bootstrap = Bootstrap(CITIES_CONFIG)

auth, meta, data = bootstrap.fromPasswordFile()

MID_LOW_COST_STATION = "http://meta.icos-cp.eu/ontologies/cpmeta/CityMidLowCostStation"
MUNICH_MID_LOW_COST_STATION = "http://meta.icos-cp.eu/ontologies/cpmeta/MunichMidLow"
PARIS_MID_LOW_COST_STATION = "http://meta.icos-cp.eu/ontologies/cpmeta/ParisMidLow"
ZURICH_MID_LOW_COST_STATION = "http://meta.icos-cp.eu/ontologies/cpmeta/ZurichMidLow"
