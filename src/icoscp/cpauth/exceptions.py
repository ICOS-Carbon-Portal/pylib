import warnings
import icoscp.const as CPC


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
        '\nThe ICOS Carbon Portal python library (>=0.1.20) requires user authentication for external users.\n'
        f'Only credentials used for password sign-in at {CPC.CP_AUTH} can be used for authentication.\n'
        'Internal users (ICOS CP Jupyter Notebook services) are exempt.\n'
        f'For the authentication module documentation, follow this link: {CPC.DOC_M_AUTH}\n'
        f'To suppress this message we refer to the documentation here: {CPC.DOC_FAQ_WARNINGS}'
    )
    warnings.warn(warning, category=FutureWarning)
    return


def warn_for_authentication_bypass(reason: AuthenticationError = None) -> None:
    warning = (
        f'\nYour authentication at the ICOS Carbon Portal was unsuccessful due to: {reason}\n'
        'Falling back to anonymous data access. Please, revisit your authentication configuration\n'
        f'({CPC.DOC_M_AUTH}).\n'
        f'Authentication will become mandatory (icoscp >= 0.1.20) for external users.'
        )
    warnings.warn(warning, category=UserWarning)
    return
