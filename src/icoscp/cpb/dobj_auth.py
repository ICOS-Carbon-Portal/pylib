import traceback
from icoscp_core.icos import auth
from icoscp_core.auth import PasswordAuth, TokenAuth, parse_auth_token


def wrap_auth(external_auth: PasswordAuth | TokenAuth = None) -> str:
    # If a user provides preconfigured authentication then
    # try to get the cookie, else prompt for credentials.
    auth_type = external_auth if external_auth else auth
    cookie_value = None
    try:
        cookie_value = auth_type.get_token().cookie_value
    except Exception:
        try:
            auth_sel = input(
                '1. Username & password\n2. Token\nPlease, choose '
                'authentication method (1 or 2) and press enter: ')
            if auth_sel == '1':
                auth_type.init_config_file()
                cookie_value = auth_type.get_token().cookie_value
            elif auth_sel == '2':
                input_cookie = input('Please, paste your token: ')
                cookie_value = (
                    parse_auth_token(cookie_value=input_cookie)
                    ).cookie_value
            else:
                raise Exception('Invalid selection. Please, try again.')
        except Exception as e:
            if 'Invalid selection' in str(e):
                raise Exception('Invalid selection. Please, try again.')
            else:
                raise Exception('Incorrect credentials. Please, try again.') from None
        else:
            return cookie_value
    else:
        return cookie_value
