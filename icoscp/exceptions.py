class AuthenticationError(Exception):

    def __init__(self, response=None):
        if response is None:
            exception_message = 'Missing credentials.'
        elif response.status_code == 401 and 'expired' in response.text:
            exception_message = 'Authentication token has expired.'
        elif response.status_code == 401 and 'missing' in response.text:
            exception_message = \
                'Authentication token is missing or has a wrong format.'
        elif response.status_code == 403 and 'Incorrect' in response.text:
            exception_message = 'Incorrect user name or password.'
        else:
            exception_message = f'{response.text}.'
        super().__init__(exception_message)
