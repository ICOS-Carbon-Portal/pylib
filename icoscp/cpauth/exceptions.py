import warnings
import icoscp.const as constants


class AuthenticationError(Exception):

    def __init__(self, response=None):
        if response is None:
            exception_message = 'Missing credentials'
        else:
            exception_message = response.text
        super().__init__(exception_message)


class CredentialsError(Exception):

    def __init__(self, configuration_file):
        exception_message = f'Incomplete login information in file: \'{configuration_file}\''
        super().__init__(exception_message)


def warn_for_authentication() -> None:
    warning = \
        f'\nDue to updates in the python library of the ICOS carbon portal, ' \
        f'starting from\nthe next version, user authentication might be ' \
        f'required. For more information,\nplease, follow this link: ' \
        f'{constants.PYLIB_DOC}modules/#authentication'
    warnings.warn(warning, category=FutureWarning)
    return


def warn_for_authentication_bypass() -> None:
    warning = \
        f'\nYour authentication was unsuccessful. Falling back to anonymous ' \
        f'data access.\nPlease, revisit your authentication configuration' \
        f' or have a look at the\ndocumentation here: ' \
        f'{constants.PYLIB_DOC}modules/#authentication.\n' \
        f'Authentication will become mandatory for data access.'
    warnings.warn(warning, category=UserWarning)
    return
