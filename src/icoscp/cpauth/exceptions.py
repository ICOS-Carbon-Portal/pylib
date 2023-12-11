import warnings
import icoscp.const as CPC
import sys, traceback


def exception_hook(exception_type, value, tb):
    trace = traceback.format_tb(tb, limit=1)
    trace = trace[0].split("\n")[0]
    exc = traceback.format_exception_only(exception_type, value)[0]
    print(trace + "\n" + exc)
    return


sys.excepthook = exception_hook

class AuthenticationError(Exception):

    def __init__(self, response=None):
        self.exception_message = None
        if response is None:
            exception_message = 'Missing credentials.'
        elif response.status_code == 401:
            if 'Authentication token has expired' in response.text:
                exception_message = 'Authentication token has expired.'
            # All cases except token expiration have a more technical
            # explanation in the response message, so make it simpler.
            else:
                exception_message = (
                    f'Invalid token format. Please re-enter your token.'
                )
        else:
            exception_message = f'{response.text}.'
        self.exception_message = exception_message
        super().__init__(exception_message)
        return


class CredentialsError(Exception):

    def __init__(self, configuration_file):
        exception_message = f'Incomplete login information in file: \'{configuration_file}\''
        super().__init__(exception_message)


def warn_for_authentication() -> None:
    warning = (
        '\nThe ICOS Carbon Portal python library (>=0.1.20) requires user'
        ' authentication for external users.\n'
        f'Only credentials used for password sign-in at {CPC.CP_AUTH} can be'
        f' used for authentication.\n'
        'Internal users (ICOS CP Jupyter Notebook services) are exempt.\n'
        'For the authentication module documentation, follow this link: '
        f'{CPC.DOC_M_AUTH}\n'
        'To suppress this message we refer to the documentation here: '
        f'{CPC.DOC_FAQ_WARNINGS}'
    )
    warnings.warn(warning, category=FutureWarning)
    return

