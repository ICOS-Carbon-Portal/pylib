from icoscp_core.auth import AuthTokenProvider, AuthToken
from icoscp_core.icos import auth


class AuthProvider(AuthTokenProvider):
    _auth: AuthTokenProvider

    def __init__(self):
        self._auth = auth

    def init_by(self, provider: AuthTokenProvider):
        self._auth = provider

    def get_token(self) -> AuthToken:
        try:
            return self._auth.get_token()
        except Exception as e:
            msg = ("Authentication error. Please configure authentication "
                   "according to https://icos-carbon-portal.github.io/pylib/"
                   "install/#configure-your-authentication")
            raise Exception(msg) from None

    @property
    def cookie_value(self) -> str:
        return self.get_token().cookie_value
