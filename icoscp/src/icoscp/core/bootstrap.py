import os
from .envri import EnvriConfig
from .auth import AuthTokenProvider, ConfigFileAuth, PasswordAuth, TokenAuth
from .metaclient import MetadataClient
from .dataclient import DataClient
from typing import Tuple

class Bootstrap():
	def __init__(self, conf: EnvriConfig) -> None:
		self._conf = conf
		data_path_var = "PORTAL_DATA_PATH_" + conf.envri.upper()
		data_path = os.environ.get(data_path_var)
		self._data_path = data_path if data_path is not None and len(data_path) > 0 else None


	def fromPasswordFile(
		self, conf_file_path: str | None = None
	) -> Tuple[ConfigFileAuth, MetadataClient, DataClient]:
		auth = ConfigFileAuth(self._conf, conf_file_path)
		data = DataClient(self._conf, auth, self._data_path)
		return auth, data.meta, data

	def fromCookieToken(self, token: str) -> Tuple[MetadataClient, DataClient]:
		auth = TokenAuth(token)
		data = DataClient(self._conf, auth, self._data_path)
		return data.meta, data

	def fromCredentials(self, user_id: str, password: str) -> Tuple[MetadataClient, DataClient]:
		auth = PasswordAuth(user_id, password, self._conf)
		data = DataClient(self._conf, auth, self._data_path)
		return data.meta, data

	def fromAuthProvider(self, auth: AuthTokenProvider) -> DataClient:
		return DataClient(self._conf, auth, self._data_path)
