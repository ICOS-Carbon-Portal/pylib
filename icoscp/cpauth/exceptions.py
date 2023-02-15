import warnings


class AuthenticationError(Exception):

    def __init__(self, response=None):
        if response is None:
            exception_message = 'Missing credentials'
        else:
            exception_message = response.text
        # elif response.status_code == 401 and 'expired' in response.text:
        #     exception_message = 'Authentication token has expired'
        # elif response.status_code == 401 and 'missing' in response.text:
        #     exception_message = \
        #         'Authentication token is missing or has a wrong format'
        # elif response.status_code == 403 and 'Incorrect' in response.text:
        #     exception_message = 'Incorrect user name or password'
        # else:
        #     exception_message = f'{response.text}.'
        super().__init__(exception_message)


class CredentialsError(Exception):

    def __init__(self, configuration_file):
        exception_message = f'Incomplete login information in file: \'{configuration_file}\''
        super().__init__(exception_message)


def warn_for_authentication() -> None:
    warning = \
        f'Due to updates in the python library of the ICOS carbon portal, ' \
        f'starting\nfrom the next version, user authentication might be ' \
        f'required. For more information, please, follow this link: ' \
        f'[link to documentation]'
    warnings.warn(warning, category=FutureWarning)
    return


def warn_for_authentication_bypass() -> None:
    warning = \
        f'Your authentication was unsuccessful. Falling back to anonymous ' \
        f'data access... \nPlease, revisit your authentication ' \
        f'configurations or have a look at the documentation here: ' \
        f'[link to documentation].\n' \
        f'Authentication will gradually become mandatory for data access.'
    warnings.warn(warning, category=UserWarning)
    return
