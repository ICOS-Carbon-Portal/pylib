from .bootstrap import Bootstrap
from .envri import SITES_CONFIG

bootstrap = Bootstrap(SITES_CONFIG)

auth, meta, data = bootstrap.fromPasswordFile()
