from icoscp_core.auth import AuthTokenProvider, AuthToken
from icoscp_core.auth import TokenAuth, PasswordAuth
from icoscp_core.icos import auth, ICOS_CONFIG


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
        except Exception as e:
            msg = "Authentication error. Please configure authentication according to " \
                "https://icos-carbon-portal.github.io/pylib/modules/#authentication"
            raise Exception(msg) from None

    @property
    def cookie_value(self) -> str:
        return self.get_token().cookie_value
