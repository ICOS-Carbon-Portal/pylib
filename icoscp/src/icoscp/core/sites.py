from .envri import SITES_CONFIG
from .bootstrap import Bootstrap

bootstrap = Bootstrap(SITES_CONFIG)

auth, meta, data = bootstrap.fromPasswordFile()
