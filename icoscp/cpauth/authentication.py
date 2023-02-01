import re
from pprint import pprint
import os
import requests
import tempfile
from icoscp.cpauth.exceptions import AuthenticationError, CredentialsError


def generate_cookie():
    cookie_path = os.path.join(tempfile.gettempdir(), 'icos_cookie.txt')
    with open(file=cookie_path, mode='w+') as cookie_handle:
        cookie_handle.write(f'username: zois.zogopoulos@nateko.lu.se\n'
                            f'password: asdf\n'
                            f'token: ')
    return


def print_help(self):
    important_notice = \
        f'\nImportant notice!\n\n' \
        f'Due to updates in the python library of the ICOS carbon portal, ' \
        f'starting from the next version, user authentication might be required.\n' \
        f'User authentication will only be requested upon accessing data objects. ' \
        f'Meta-data is available without authentication.\n' \
        f'Credentials will be validated by providing a username and password ' \
        f'or an API token.\n' \
        f'\n\tUsername and password example:\n' \
        f'\t\tPlease enter your username or API token (h for help): tade@tadedomain.sth\n' \
        f'\t\tPlease enter your password: test_password\n\n' \
        f'\tToken example:\n' \
        f'\t\tPlease enter your username or API token (h for help): ' \
        f'cpauthToken=rO0ABXcIAAABgHuHzPl0ABx6b2lzLnpvZ29wb3Vsb3NAbmF0ZWtvLmx1...\n' \
        f'\t\t(Login here: https://cpauth.icos-cp.eu/login/ to retrieve you personal API ' \
        f'token. You will find the token at the bottom of the webpage).\n'
    print(important_notice)
    return

import os


class Authentication:

    def __init__(self, username: str = None, password: str = None,
                 token: str = None, read_configuration: bool = True,
                 write_configuration: bool = True,
                 configuration_file: str = None):
        self.valid_token = False
        self.write_configuration = write_configuration
        self.username = None
        self.password = None
        self.token = None
        # Set the configuration file property. Either the user
        # provides a custom file location or the authentication module
        # uses a system specific location.
        self.configuration_file = configuration_file if configuration_file \
            else f'{tempfile.gettempdir()}/car_bone_paw_r_tall'
        # User provides username and password as input.
        if username and password:
            self.username = username
            self.password = password
            # Retrieve and set a valid token using the provided
            # credentials.
            self.retrieve_token()
        # User provides token as input.
        elif token:
            self.token = token
            self.validate_token()
            # Set token property only if the provided token was valid.
            if self.valid_token:
                self.token = token
        # Default case. The user has provided a configuration file or
        # the Authentication constructor was invoked without any
        # parameters.
        elif read_configuration:
            # Retrieve credentials from the configuration file.
            self.retrieve_credentials()
            # Case of set username and password, but not token.
            if self.username and self.password and not self.token:
                # Try to validate using username & password.
                self.retrieve_token()
            # Case of set username, password, and token.
            elif self.username and self.password and self.token:
                # Try to validate token first.
                self.validate_token('no_raise')
                # Try to validate using username & password if token
                # is invalid.
                if not self.valid_token:
                    self.retrieve_token()
            # Case of set token only.
            elif self.token:
                # Try to validate using token.
                self.validate_token()
            # Error handling for wrong credentials' formatting in the
            # configuration file.
            if (not self.username and not self.token)\
                    or (self.username and not self.password and not self.token):
                raise CredentialsError(self.configuration_file)
        # Write valid credentials to the configuration file.
        if self.valid_token and self.write_configuration:
            self.write_credentials()
        return

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, username):
        self._username = username
        return

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, password):
        self._password = password
        return

    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, token):
        self._token = token
        return

    @property
    def valid_token(self):
        return self._valid_token

    @valid_token.setter
    def valid_token(self, valid_token):
        self._valid_token = valid_token
        return

    @property
    def configuration_file(self):
        return self._configuration_file

    @configuration_file.setter
    def configuration_file(self, configuration_file):
        self._configuration_file = configuration_file
        return

    @property
    def write_configuration(self):
        return self._write_configuration

    @write_configuration.setter
    def write_configuration(self, write_configuration):
        self._write_configuration = write_configuration
        return

    def retrieve_token(self) -> None:
        """Retrieve token using username and password."""
        url = 'https://cpauth.icos-cp.eu/password/login'
        data = {'mail': self.username, 'password': self.password}
        response = None
        try:
            # Post credentials to cp-auth and check for validity.
            response = requests.post(url=url, data=data)
            if response.status_code == 200:
                # Retrieve token from headers.
                self.token = response.headers['Set-Cookie'].split()[0]
                # No further validation is needed for the token since
                # it was correctly retrieved (status_code == 200) using
                # username and password.
                self.valid_token = True
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            raise AuthenticationError(response)
        return

    def validate_token(self, *args: str) -> None:
        """Validate input or generated token."""
        url = 'https://cpauth.icos-cp.eu/whoami'
        headers = {'cookie': self.token}
        response = None
        try:
            response = requests.get(url=url, headers=headers)
            if response.status_code == 200:
                self.valid_token = True
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            # Do not raise an exception if all credentials are present
            # in the configuration file, and the provided token is
            # invalid.
            if 'no_raise' not in args:
                raise AuthenticationError(response)
        return

    def retrieve_credentials(self) -> None:
        """Retrieve user's credentials from the configuration file."""
        with open(file=self.configuration_file, mode='r') as configuration_file_handle:
            credentials = configuration_file_handle.read().splitlines()
        token_pattern = r'cpauthToken=[a-zA-Z0-9_=+/]+'
        token_regex = re.compile(token_pattern)
        email_pattern = r'^[a-zA-Z0-9_.+-]{1,64}@[a-zA-Z0-9-.]{3,255}$'
        email_regex = re.compile(email_pattern)
        for credential in credentials:
            if token_regex.match(credential):
                self.token = credential
            elif email_regex.match(credential):
                self.username = credential
            # Prevent password resetting.
            elif not self.password:
                self.password = credential
        return

    def write_credentials(self) -> None:
        """Write validated credentials to specified file."""
        with open(file=self.configuration_file, mode='w') as configuration_file_handle:
            for credential in [self.username, self.password, self.token]:
                if credential:
                    configuration_file_handle.write(f'{credential}\n')
        return

    def get_configuration_location(self) -> None:
        """Print & return the location of the configuration file."""
        configuration_full_path = os.path.abspath(self.configuration_file)
        print(f'Absolute path of the configuration file: '
              f'{configuration_full_path}')
        return

    def get_credentials(self) -> None:
        user_input = input('This action might expose critical information ('
                           'such as username & password) on your screen.\n'
                           'Do you want to continue? [Y/n]: ')
        if user_input == 'Y':
            print(f'\nReading credentials from '
                  f'{os.path.abspath(self.configuration_file)}...\n'
                  f'  username: {self.username}\n'
                  f'  password: {self.password}\n'
                  f'  token: {self.token}')
        return



        # username, *credentials = credentials
        # password, *credentials = credentials if credentials else None
        # token = credentials if credentials else None
        # print(username, password, token, credentials)
        # with open(file=self._cookie_file, mode='r') as cookie_handle:
        #     cookie_lines = cookie_handle.readlines()
        # credentials = list()
        # for line in cookie_lines:
        #     credential = line.split()[1] if len(line.split()) > 1 else None
        #     if credential == 'None':
        #         credential = None
        #     credentials.append(credential)
        # # Assign credentials read from cookie file to properties.
        # self._username, self._password, self._token = credentials
        return


# class Authentication:
#
#     def __init__(self, username=None, password=None, token=None,
#                  file=None
#                  write_configuration=False):
#         self._username = username
#         self._password = password
#         self._token = token
#         self._valid_token = False
#         self._configuration_file = None
#         # Call the `write_configuration` setter.
#         self.write_configuration = write_configuration
#         # Authenticate using username and password.
#         if self._username is not None and self._password is not None:
#             self.retrieve_token(self._username, self._password)
#         # Authenticate using user token.
#         elif self._token is not None:
#             self.validate_token()
#         # Authenticate using token from configuration.
#         elif self._configuration_file:
#             self.read_configuration()
#         # User wants to store the valid token to configuration file for
#         # reusability.
#         if self._valid_token and self._write_configuration:
#             self.store_information()
#         elif not self._valid_token:
#             raise AuthenticationError
#         return
#
#     @property
#     def username(self):
#         return self._username
#
#     @username.setter
#     def username(self, username):
#         self._username = username
#         return
#
#     @property
#     def password(self):
#         return self._password
#
#     @password.setter
#     def password(self, password):
#         self._password = password
#         return
#
#     @property
#     def token(self):
#         return self._token
#
#     @token.setter
#     def token(self, token):
#         self._token = token
#         return
#
#     @property
#     def valid_token(self):
#         return self._valid_token
#
#     @valid_token.setter
#     def valid_token(self, valid_token):
#         self._valid_token = valid_token
#         return
#
#     @property
#     def write_configuration(self):
#         return self._write_configuration
#
#     @write_configuration.setter
#     def write_configuration(self, write_configuration):
#         self._write_configuration = write_configuration
#         # User specified default configuration path.
#         if type(self._write_configuration) == bool \
#                 and self._write_configuration:
#             self._configuration_file = os.path.join('configuration.py')
#             self.touch_configuration()
#         # User specified a custom configuration path.
#         elif type(self._write_configuration) == str:
#             self._configuration_file = os.path.join(self._write_configuration,
#                                                     'configuration.py')
#             # Create all intermediate directories if needed.
#             os.makedirs(self._write_configuration, exist_ok=True)
#             self.touch_configuration()
#         return
#
#     @property
#     def configuration_file(self):
#         return self._configuration_file
#
#     @configuration_file.setter
#     def configuration_file(self, configuration_file):
#         self._configuration_file = configuration_file
#         return
#
#     def read_configuration(self):
#         if os.path.exists(self._configuration_file):
#             with open(file=self._configuration_file, mode='r') as \
#                     configuration_handle:
#                 self._token = configuration_handle.read()
#                 self.validate_token()
#         return
#
#     def store_information(self):
#         with open(file=const.CONFIGURATION_FILE, mode='w+') as \
#                 configuration_handle:
#             configuration_handle.write(self._token)
#         return
#
#     def retrieve_token(self, username, password):
#         url = 'https://cpauth.icos-cp.eu/password/login'
#         data = {'mail': username, 'password': password}
#         response = None
#         try:
#             response = requests.post(url=url, data=data)
#             if response.status_code == 200:
#                 # Retrieve token from headers.
#                 self._token = response.headers['Set-Cookie'].split()[0]
#                 # No further validation is needed for the token since
#                 # it was correctly retrieved (status_code == 200) using
#                 # username and password.
#                 self._valid_token = True
#             response.raise_for_status()
#         except requests.exceptions.HTTPError:
#             raise AuthenticationError(response)
#         return
#
#     @property
#     def using_token(self):
#         return self._using_token
#
#     @using_token.setter
#     def using_token(self, using_token):
#         self._using_token = using_token
#         return
#
#     @property
#     def valid_credentials(self):
#         return self._valid_credentials
#
#     @valid_credentials.setter
#     def valid_credentials(self, valid_credentials):
#         self._valid_credentials = valid_credentials
#         return
#
#
#
#     @property
#     def cookie_file(self):
#         return self._cookie_file
#
#     @cookie_file.setter
#     def cookie_file(self, cookie_file):
#         self._cookie_file = cookie_file
#         return
#

#
#
#
#     def work_on_cookie_file(self):
#         # Repeat until user enters valid credentials.
#         while not self._valid_credentials:
#             # Read and validate credentials in already existing cookie.
#             if os.path.exists(self._cookie_file) and os.stat(self._cookie_file).st_size > 0:
#                 self.retrieve_credentials()
#                 if self._token:
#                     self.validate_token()
#                 if self._username and self._password and not self._valid_credentials:
#                     self.retrieve_token()
#                 if not self._valid_credentials:
#                     os.remove(self._cookie_file)
#             # Cookie file is not available in the file system.
#             # Request user's credentials.
#             else:
#                 self.request_credentials()
#             # Cookie file contains wrong credentials and needs to be
#             # replaced.
#             if not self._token and os.path.exists(self._cookie_file):
#                 os.remove(self._cookie_file)
#         # Write valid credentials to cookie file.
#         self.write_cookie()
#         return
#
#     def request_credentials(self):
#         user_input = input('Please enter your username or API token (h for help, e to exit): ')
#         if user_input == 'h':
#             print_help(self)
#             exit(0)
#         elif user_input == 'e':
#             exit(0)
#         elif '@' in user_input:
#             self._username = user_input
#             self._password = input('Please enter your password: ')
#             self.retrieve_token()
#         else:
#             self._token = user_input
#             self.validate_token()
#         return
#
#     def write_cookie(self):
#         with open(file=self._cookie_file, mode='w+') as cookie_handle:
#             cookie_handle.write(f'username: {self._username}\n'
#                                 f'password: {self._password}\n'
#                                 f'token: {self._token}')
#         return
#
#     def validate_token(self):
#         url = 'https://cpauth.icos-cp.eu/whoami'
#         headers = {'cookie': self._token}
#         response = None
#         try:
#             response = requests.get(url=url, headers=headers)
#             if response.status_code == 200:
#                 self._valid_token = True
#             response.raise_for_status()
#         except requests.exceptions.HTTPError:
#             raise AuthenticationError(response)
#         return
#
#     # def validate_token_pre_kados(self):
#     #     url = 'https://cpauth.icos-cp.eu/whoami'
#     #     headers = {'cookie': self._token}
#     #     response = None
#     #     try:
#     #         response = requests.get(url=url, headers=headers)
#     #         if response.status_code == 200:
#     #             self._valid_credentials = True
#     #             print(f'User --{response.json()["email"]}-- was authorized using '
#     #                   f'{"an API token" if self._using_token else "username & password"}.')
#     #         response.raise_for_status()
#     #     except requests.exceptions.HTTPError as error:
#     #         print(f'\t{response.text}\t{error}')
#     #     return
#
#     def update_cookie(self):
#         cookie_lines = \
#             [f'{credential_key}: {credential_value}\n' for credential_key, credential_value in
#              self._credentials.items()]
#         with open(file=self._cookie_file, mode='w') as cookie_handle:
#             cookie_handle.writelines(cookie_lines)
#         return
#
#     def print_credentials(self):
#         print(f'\nusername: {self._username}, {type(self._username)}\n'
#               f'password: {self._password}, {type(self._password)}\n'
#               f'token: {self._token}, {type(self._token)}\n')
#         return
#
#     def touch_configuration(self):
#         with open(file=self._configuration_file, mode='w+') as file_handle:
#             pass
#         return
