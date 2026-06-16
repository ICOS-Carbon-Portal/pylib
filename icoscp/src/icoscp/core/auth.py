import base64
import getpass
import json
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta
from http.client import HTTPResponse
from typing import TypeAlias, Literal, Optional, Any

from .envri import EnvriConfig
from .http import http_request, Method

AuthSource: TypeAlias = Literal["Password", "Saml", "Orcid", "Facebook", "AtmoAccess"]
FreshnessMargin: timedelta = timedelta(hours = 1)
ExpiryMargin: timedelta = timedelta(seconds = 10)

@dataclass(frozen=True)
class AuthToken:
	user_id: str
	auth_source: AuthSource
	expiry_time: datetime
	cookie_value: str

	def _will_expire_in(self, delta: timedelta) -> bool:
		return (datetime.now() + delta) > self.expiry_time

	def is_expired(self) -> bool:
		return self._will_expire_in(ExpiryMargin)
	def is_fresh(self) -> bool:
		return not self._will_expire_in(FreshnessMargin)

class AuthTokenProvider(ABC):
	@abstractmethod
	def get_token(self) -> AuthToken:
		pass

class TokenAuth(AuthTokenProvider):
	def __init__(self, token_or_cookie: AuthToken | str) -> None:
		if type(token_or_cookie) is AuthToken:
			self._token = token_or_cookie
		elif type(token_or_cookie) is str:
			self._token = parse_auth_token(token_or_cookie)
		else:
			raise ValueError(f"Bad argument to ConstAuthTokenProvider, expected AuthToken or the cookie value string")

	def get_token(self) -> AuthToken:
		t = self._token
		if t.is_expired():
			raise Exception(f"Authentication token expiration time is {t.expiry_time}, too late to use it")
		return t

class PasswordAuth(AuthTokenProvider):
	def __init__(self, user_id: str, password: str, conf: EnvriConfig, init_token: AuthToken | None = None) -> None:
		self._user_id = user_id
		self._password = password
		self._conf = conf
		self._token = init_token

	@property
	def has_fresh_token(self) -> bool:
		return (not not self._token) and self._token.is_fresh()

	def get_token(self) -> AuthToken:
		t = self._token
		if t and t.is_fresh():
			return t
		else:
			self._token = fetch_auth_token(self._user_id, self._password, self._conf)
			return self._token

	def save_to_file(self, file_path: str) -> None:
		data = {
			"user_id": self._user_id,
			"password": PasswordAuth.encode_password(self._password)
		}
		token = self._token
		if token:
			data["cookie_value"] = token.cookie_value
		with open(file_path, "w") as conf_file:
			json.dump(data, conf_file)

	@staticmethod
	def load_from_file(file_path: str, conf: EnvriConfig) -> "PasswordAuth":
		if not os.path.exists(file_path):
			docs_url = "https://github.com/ICOS-Carbon-Portal/data/tree/master/src/main/python/icoscp_core#authentication"
			raise Exception(f"Authentication config file not found at {file_path}. " +
				f"Please initialize authentication according to {docs_url} \n" +
				"(Remember to use Repository-specific imports in 'from icoscp_core.<repo> import auth')")
		with open(file_path, 'r') as conf_file:
			js = json.load(conf_file)
			user_id: str = js["user_id"]
			password: str = PasswordAuth.decode_password(js["password"])
			token: Optional[AuthToken] = None
			cookie_value: str | None = js.get("cookie_value")
			if cookie_value:
				token = parse_auth_token(cookie_value)
			return PasswordAuth(user_id, password, conf, token)

	@staticmethod
	def decode_password(encoded: str) -> str:
		return PasswordAuth._invert(bytes.fromhex(encoded)).decode()

	@staticmethod
	def encode_password(password: str) -> str:
		return PasswordAuth._invert(bytes(password, "utf-8")).hex()

	@staticmethod
	def _invert(barray: bytes) -> bytes:
		return bytes([~byte & 0xFF for byte in barray])

class ConfigFileAuth(AuthTokenProvider):
	def __init__(self, conf: EnvriConfig, conf_file_path: str | None = None) -> None:
		self._conf = conf
		if conf_file_path:
			self._conf_file_path = conf_file_path
		else:
			basedir = os.path.join(os.path.expanduser("~"), ".icoscp")
			os.makedirs(basedir, exist_ok = True)
			self._conf_file_path = os.path.join(basedir, conf.token_name + "_auth_conf.json")

		self._provider: PasswordAuth | None = None

	def get_token(self) -> AuthToken:
		inner = self._provider
		if not inner:
			inner = PasswordAuth.load_from_file(self._conf_file_path, self._conf)
			self._provider = inner

		has_fresh: bool = inner.has_fresh_token
		token = inner.get_token()
		if not has_fresh:
			inner.save_to_file(self._conf_file_path)
		return token

	def init_config_file(self) -> None:
		user_id = input("Enter your username: ")
		password = getpass.getpass("Enter your password: ")
		inner = PasswordAuth(user_id, password, self._conf)
		inner.save_to_file(self._conf_file_path)
		self._provider = inner

def parse_auth_token(cookie_value: str) -> AuthToken:
	eq_idx = cookie_value.find("=")

	if eq_idx < 0 or eq_idx > 100:
		raise ValueError(f"Authentication token cookie value must contain '=' sign " +
			"close to the start of the string, but it was {cookie_value}")

	token_base64 = cookie_value[eq_idx + 1:]
	token_bin = base64.b64decode(token_base64)
	sep_idx = token_bin.index(ord('\x1e'))

	if sep_idx < 0:
		raise ValueError(f"Bad auth cookie format, missing expected separator byte 0x1e in: {token_base64}")

	ts_millis, user_id, auth_source = json.loads(token_bin[0:sep_idx].decode())

	expiry_time = datetime.fromtimestamp(ts_millis / 1000)
	return AuthToken(user_id, auth_source, expiry_time, cookie_value)


def fetch_auth_token(user_id: str, password: str, conf: EnvriConfig) -> AuthToken:
	url = conf.auth_service_base_url + "password/login"
	data = {'mail': user_id, 'password': password}
	headers = {"Content-Type": "application/x-www-form-urlencoded"}
	resp = http_request(url, "Fetching auth token", "POST", headers, data)
	cookie = resp.getheader("Set-Cookie")
	if cookie is None:
		raise Exception(f"Could not fetch auth token from {url}\nMissing value for header 'Set-Cookie'")
	else:
		cookie_value = cookie.split()[0]
		return parse_auth_token(cookie_value)

def http_auth_request(
	url: str,
	error_hint: str,
	auth: AuthTokenProvider,
	method: Method = "GET",
	headers: dict[str, str] = {},
	data: str | dict[str, Any] | None = None
) -> HTTPResponse:
	h = headers.copy()
	h['Cookie'] = auth.get_token().cookie_value
	return http_request(url, error_hint, method, h, data)
