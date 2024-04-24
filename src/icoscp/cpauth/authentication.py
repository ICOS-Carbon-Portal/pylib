from icoscp_core.auth import (AuthToken, AuthTokenProvider, PasswordAuth,
                              TokenAuth)
from icoscp_core.icos import ICOS_CONFIG, auth


class AuthProvider(AuthTokenProvider):
    _auth: AuthTokenProvider

    def __init__(self):
        self._auth = auth

    def init_config_file(self) -> None:
        auth.init_config_file()

    def init_by_token(self, cookie_token: str) -> None:
        self._auth = TokenAuth(cookie_token)

    def init_by_credentials(self, username: str, password: str):
        self._auth = PasswordAuth(username, password, ICOS_CONFIG)

    def get_token(self) -> AuthToken:
        try:
            return self._auth.get_token()
        except Exception:
            msg = ("Authentication error. Please configure authentication "
                   "according to https://icos-carbon-portal.github.io/pylib/"
                   "install/#configure-your-authentication")
            raise Exception(msg) from None

    @property
    def cookie_value(self) -> str:
        return self.get_token().cookie_value
