import warnings
import icoscp.const as CPC
import sys, traceback
from typing import Optional
from IPython.core.getipython import get_ipython
ipython = get_ipython()

def hide_traceback(exc_tuple=None, filename=None, tb_offset=None,
                   exception_only=False, running_compiled_code=False):
    print(exc_tuple)
    etype, value, tb = sys.exc_info()
    return ipython._showtraceback(
        etype, value, ipython.InteractiveTB.get_exception_only(etype, value)
    )

def exception_hook(exception_type, value, tb):
    if exception_type in [AuthenticationError, CredentialsError]:
        traceback.print_exception(exception_type, value, tb, limit=1)
    else:
        # Handle standard exceptions
        traceback.print_exception(exception_type, value, tb)
    return

# Limit traceback stack.
if ipython:
    ipython.showtraceback = hide_traceback
else:
    sys.excepthook = exception_hook



class AuthenticationError(Exception):

    def __init__(self, config_file: Optional[str] = None, response=None):
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
                    f"Token and/or password in {config_file} have"
                    " invalid format. Please remove your configuration file."
                )
        else:
            exception_message = f'{response.text}.'
        self.exception_message = exception_message
        super().__init__(exception_message)
        return


class CredentialsError(Exception):

    def __init__(self, configuration_file):
        exception_message = \
            f'Incomplete login information in file: \'{configuration_file}\''
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
    )
    warnings.warn(warning, category=Warning)
    sys.stderr.flush()
    return

