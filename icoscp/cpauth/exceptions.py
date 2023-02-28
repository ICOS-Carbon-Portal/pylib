import warnings
import icoscp.const as CPC


class AuthenticationError(Exception):

    def __init__(self, response=None):
        self.exception_message = None

        if response is None:
            exception_message = 'Missing credentials'
        elif response.status_code == 401 and 'expired' in response.text:
            exception_message = 'Authentication token has expired'
        elif response.status_code == 401 and 'missing' in response.text:
            exception_message = \
                'Authentication token is missing or has a wrong format'
        elif response.status_code == 403 and 'Incorrect' in response.text:
            exception_message = 'Incorrect user name or password'
        else:
            exception_message = response.text
        self.exception_message = exception_message
        super().__init__(exception_message)


class CredentialsError(Exception):

    def __init__(self, configuration_file):
        exception_message = f'Incomplete login information in file: \'{configuration_file}\''
        super().__init__(exception_message)


def warn_for_authentication() -> None:
    warning = (
        '\nDue to updates in the python library of the ICOS carbon portal, '
        'starting from\n'
        'this version, user authentication might be required. Only '
        'credentials used\n'
        f'for password sign-in at {CPC.CP_AUTH} can be'
        ' used for authentication.\n'
        'For more information regarding the authentication module, please, '
        f'follow this link:\n{CPC.DOC_M_AUTH}\n'
        'To suppress this message we refer to the documentation here:\n'
        f'{CPC.DOC_FAQ_WARNINGS}'
    )
    warnings.warn(warning, category=FutureWarning)
    return


def warn_for_authentication_bypass(reason: AuthenticationError = None) -> None:
    warning = (
        f'\nYour authentication was unsuccessful due to: {reason}.\nFalling '
        'back to anonymous data access. Please, revisit your '
        'authentication\nconfiguration. Authentication will become '
        'mandatory for data access.\n'
        'To suppress this message we refer to the documentation here:\n'
        f'{CPC.DOC_FAQ_WARNINGS}'
        )
    warnings.warn(warning, category=UserWarning)
    return
