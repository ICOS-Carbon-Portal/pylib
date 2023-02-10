# Standard library imports.
import getpass
import json
import os

# Related third party imports.
from icoscp.cpauth.exceptions import AuthenticationError, CredentialsError
import requests


class Authentication:

    def __init__(self, username: str = None, password: str = None,
                 token: str = None, read_configuration: bool = True,
                 write_configuration: bool = True,
                 configuration_file: str = None,
                 initialize: bool = False):
        self.valid_token = False
        self.username = username
        # Set user password as private property in a conventional
        # setup, as a hint to other developers not to access it
        # publicly (Python doesn't enforce private properties).
        self._password = password
        self.token = token
        self.read_configuration = read_configuration
        self.write_configuration = write_configuration
        # Set the configuration file property. Either the user
        # provides a custom file location or the authentication module
        # uses a system specific location.
        self.configuration_file = configuration_file
        if not self.configuration_file:
            self._set_standard_configuration_path()
        # Default case. The user has provided a configuration file or
        # the Authentication constructor was invoked without any
        # parameters. None of the other arguments were supplied.
        if (self.read_configuration
                and not (self.username or
                         self._password or
                         self.token or
                         initialize)):
            # Retrieve credentials from the configuration file.
            self._retrieve_credentials()
            # Case of set username and password, but not token.
            if self.username and self._password and not self.token:
                # Try to validate using username & password.
                self._retrieve_token()
            # Case of set username, password, and token.
            elif self.username and self._password and self.token:
                # Try to validate token first.
                self._validate_token('no_raise')
                # Try to validate using username & password if token
                # is invalid.
                if not self.valid_token:
                    self._retrieve_token()
            # Case of set token only.
            elif self.token:
                # Try to validate using token.
                self._validate_token()
            # Error handling for wrong credentials' formatting in the
            # configuration file.
            if (not self.username and not self.token)\
                    or (self.username and not self._password and not self.token):
                raise CredentialsError(self.configuration_file)
        # User provides username and password as input.
        elif self.username and self._password:
            # Retrieve and set a valid token using the provided
            # credentials.
            self._retrieve_token()
        # User provides token as input.
        elif self.token:
            self._validate_token()
        # User provides initialization flag. The module will prompt
        # for username and password.
        elif initialize:
            self._initialize()
        # Write valid credentials to the configuration file.
        if self.valid_token and self.write_configuration:
            self._write_credentials()
        return

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, username):
        self._username = username
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

    def _initialize(self) -> None:
        """Prompts and resets user's credentials."""
        user_input = str()
        configuration_file_size = os.path.getsize(self.configuration_file)
        # Case of present configuration file with written content.
        if os.path.getsize(self.configuration_file):
            user_input = input(
                f'Content detected in file {self.configuration_file}\n'
                f'This action will reset your configuration file.\n'
                f'Do you want to continue? [Y/n]: ')
        # Case of user's confirmation or empty configuration.
        if user_input == 'Y' or configuration_file_size == 0:
            self.username = input('Enter your username: ')
            self._password = getpass.getpass('Enter your password: ')
            self._retrieve_token()
            if self.valid_token:
                self._write_credentials()
        return

    def _set_standard_configuration_path(self) -> None:
        """Set & create the standard configuration locations."""
        configuration_dir = os.path.join(os.path.expanduser('~'), 'icoscp')
        os.makedirs(configuration_dir, exist_ok=True)
        self.configuration_file = os.path.join(configuration_dir,
                                               '.car_bone_paw_r_tall')
        with open(self.configuration_file, 'a'):
            os.utime(self.configuration_file)

        return

    def _retrieve_token(self) -> None:
        """Retrieve token using username and password."""
        url = 'https://cpauth.icos-cp.eu/password/login'
        data = {'mail': self.username, 'password': self._password}
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

    def _validate_token(self, *args: str) -> None:
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

    def _retrieve_credentials(self) -> None:
        """Retrieve user's credentials from the configuration file."""
        with open(file=self.configuration_file, mode='r') as json_handle:
            credentials = json.load(json_handle)
        if 'username' in credentials.keys():
            self.username = credentials['username']
        if 'password' in credentials.keys():
            self._password = credentials['password']
        if 'token' in credentials.keys():
            self.token = credentials['token']
        return

    def _write_credentials(self) -> None:
        """Write validated credentials to configuration file."""
        credentials = dict({
            'username': self.username,
            'password': self._password,
            'token': self.token
        })
        with open(file=self.configuration_file, mode='w') as json_file_handle:
            json.dump(credentials, json_file_handle)
        return

    def print_configuration_location(self) -> None:
        """Print & return the location of the configuration file."""
        print(f'Absolute path to the configuration file: '
              f'{os.path.abspath(self.configuration_file)}')
        return

    def print_credentials(self) -> None:
        user_input = input('This action might expose critical information ('
                           'such as username & password) on your screen.\n'
                           'Do you want to continue? [Y/n]: ')
        if user_input == 'Y':
            print(f'  username: {self.username}\n'
                  f'  password: {self._password}\n'
                  f'  token: {self.token}')
        return
