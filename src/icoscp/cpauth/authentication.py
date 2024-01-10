# Standard library imports.
from datetime import datetime
from typing import Optional
import base64
import binascii
import getpass
import json
import os

# Related third party imports.
import requests

# Local library imports.
from icoscp.cpauth.exceptions import AuthenticationError, CredentialsError, \
    warn_for_authentication


def init_auth():
    """Initialize authentication configuration."""
    input_username = input('Enter your username: ')
    input_password = getpass.getpass('Enter your password: ')
    Authentication(username=input_username, password=input_password)
    return


class Authentication:
    """
    A class used to authenticate a user on https://cpauth.icos-cp.eu.

    The authentication class is a tool that provides access to data
    objects at the ICOS Carbon Portal, by providing a valid username
    and password, or by using an API token, which can be supplied in a
    number of different ways.

    Attributes:
        username: str, optional, default=None
            The username required for authentication.
        password: str, optional, default=None
            Τhe password required for authentication.
        token: str, optional, default=None
            The authentication token allows data access without the
            need for a username and password. The token can be
            manually retrieved from https://cpauth.icos-cp.eu after
            signing in with a password. Please note that the token has
            a limited lifespan (100'000 seconds) and must be refreshed
            periodically to maintain data access.
        read_configuration: bool, optional, default=True
            This attribute controls whether the configuration is read
            from a file. The default setting is to read from a
            system-specific location.
        write_configuration: bool, optional, default=True
            This attribute controls whether valid configuration will
            be stored to a system-specific location.
        configuration_file: str, optional, default=None
            This attribute specifies the path to the configuration
            file. By default, the configuration file is located in a
            directory called icoscp in the user's home directory.

    Examples:
        >>> from icoscp.cpauth.authentication import Authentication
        >>> Authentication()

        >>> from icoscp.cpauth.authentication import Authentication
        >>> Authentication(username='test@some.where', password='12345')

    """

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
        self.token_information = None
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
            if os.path.getsize(self.configuration_file):
                # Retrieve credentials from the configuration file.
                self._retrieve_credentials()
            # Case of set username and password, but not token.
            if self.username and self._password and not self.token:
                # Try to validate using username & password.
                self._retrieve_token()
            # Case of set username, password, and token.
            elif self.username and self._password and self.token:
                self._validate_token('no_raise')
                if self.valid_token:
                    self._extract_token_information()
                # Try to validate using username & password if token
                # is invalid.
                else:
                    self._retrieve_token('reset_config')
                    self._extract_token_information()
            # Case of set token only.
            elif self.token:
                self._validate_token()
                self._extract_token_information()
            elif not self.write_configuration:
                self._initialize_no_store()
            else:
                warn_for_authentication()
                self._initialize()
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
            if self.valid_token:
                self._extract_token_information()
        # User provides username only. In this case credentials will
        # not be stored.
        elif self.username and not self._password:
            self.write_configuration = False
            self._initialize_no_store()
        # User provides token as input.
        elif self.token:
            self._validate_token()
            if self.valid_token:
                self._extract_token_information()
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
        """Prompt and reset user's credentials."""
        user_input = str()
        configuration_file_size = os.path.getsize(self.configuration_file)
        # Case of present configuration file with written content.
        if os.path.getsize(self.configuration_file):
            user_input = input(
                'Detected wrongly formatted content in configuration\n'
                f'file: \'{self.configuration_file}\'.\n'
                'This action will reset your configuration file.\n'
                'Do you want to continue? [Y/n]: '
            )
        # Case of user's confirmation or empty configuration.
        if user_input == 'Y' or configuration_file_size == 0:
            self.username = input('Enter your username: ')
            self._password = getpass.getpass('Enter your password: ')
            self._retrieve_token()
            if self.valid_token:
                self._extract_token_information()
            if self.write_configuration:
                self._write_credentials()
        return

    def _initialize_no_store(self) -> None:
        """Prompt, authenticate, & discard user password."""
        if not self._username:
            self.username = input('Enter your username: ')
        self._password = getpass.getpass('Enter your password: ')
        self._retrieve_token()
        self._extract_token_information()
        return

    def _set_standard_configuration_path(self) -> None:
        """Set & create the standard configuration locations."""
        configuration_dir = os.path.join(os.path.expanduser('~'), 'icoscp')
        os.makedirs(configuration_dir, exist_ok=True)
        self.configuration_file = os.path.join(configuration_dir,
                                               '.icos_carbon_portal')
        with open(self.configuration_file, 'a'):
            os.utime(self.configuration_file)
        return

    def _retrieve_token(self, *args: str) -> None:
        """Retrieve token using username and password."""
        url = 'https://cpauth.icos-cp.eu/password/login'
        data = {'mail': self.username, 'password': self._password}
        response = None
        try:
            # Post credentials to cp-auth and check for validity.
            response = requests.post(url=url, data=data)
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            if "reset_config" in args:
                raise AuthenticationError("reset_config", response=response,
                                          config_file=self.configuration_file)
            else:
                raise AuthenticationError(response=response)
        else:
            if response.status_code == 200:
                # Retrieve token from headers.
                self.token = response.headers['Set-Cookie'].split()[0]
                # No further validation is needed for the token since
                # it was correctly retrieved (status_code == 200) using
                # username and password.
                self.valid_token = True
        return

    def _validate_token(self, *args: str) -> None:
        """Validate input or generated token (update this for token expiry case)."""
        url = 'https://cpauth.icos-cp.eu/whoami'
        headers = {'cookie': self.token}
        response = None
        # Validate given token.
        try:
            response = requests.get(url=url, headers=headers)
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            # Raise an exception (else-clause) if the token has
            # expired, or it is invalid, and it is the only provided
            # credential.
            # In other cases (if-clause) the module will try to
            # retrieve the token using username & password and the
            # exception control is handled elsewhere.
            if 'no_raise' in args:
                pass
            else:
                raise AuthenticationError(config_file=self.configuration_file,
                                          response=response)
        else:
            if response.status_code == 200:
                self.valid_token = True
        return

    def _retrieve_credentials(self) -> None:
        """Retrieve user's credentials from the configuration file."""
        with open(file=self.configuration_file, mode='r') as json_handle:
            credentials = json.load(json_handle)
        if 'username' in credentials.keys():
            self.username = credentials['username']
        if 'password' in credentials.keys():
            self._extract_password(credentials['password'])
        if 'token' in credentials.keys():
            self.token = credentials['token']
        return

    def _extract_token_information(self) -> None:
        try:
            binary_token = base64.b64decode(
                self.token.split('cpauthToken=')[-1]
            )
        except binascii.Error as e:
            pass
        except AttributeError as e:
            pass
        else:
            # Check for the record separator character in the binary
            # token.
            if ord('\x1e') in binary_token:
                record_separator_index = binary_token.index(ord('\x1e'))
                # Get the index of the character just before the
                # record separator character.
                square_bracket_index = record_separator_index - 1
                # Just before the record separator character, there
                # must be a closing square bracket character ']'. Only
                # in that case extract the token information.
                if binary_token[square_bracket_index] == ord(']'):
                    # Extract only the relevant part of the binary
                    # token.
                    binary_information = \
                        binary_token[0:square_bracket_index+1]
                    token_information = json.loads(
                        binary_information.decode(encoding='utf-8')
                    )
                    self.token_information = dict(zip(
                        ['token_expiration', 'username', 'source'],
                        token_information
                    ))
        return

    def _write_credentials(self) -> None:
        """Write validated credentials to configuration file."""
        credentials = dict({
            'username': self.username,
            'password': self._encode_password() if self._password else None,
            'token': self.token
        })
        with open(file=self.configuration_file, mode='w') as json_file_handle:
            json.dump(credentials, json_file_handle)
        return

    def _encode_password(self):
        """Base64 encode given password."""
        password_bytes = self._password.encode(encoding='utf-8')
        b64_password_bytes = base64.b64encode(password_bytes)
        b64_password_string = b64_password_bytes.decode(encoding='utf-8')
        return b64_password_string

    def _extract_password(self, password_value: Optional[str]) -> None:
        """Decode or extract clear text password."""
        try:
            password_bytes = base64.b64decode(password_value)
            self._password = password_bytes.decode(encoding='utf-8')
        # Password in file was not encoded.
        except binascii.Error:
            self._password = password_value
        # Password in file was None.
        except TypeError:
            self._password = None
        except UnicodeDecodeError:
            self._password = None
        return

    def __str__(self):
        """Handle printing of the Authentication class."""
        dt_token_expiration = datetime.fromtimestamp(
            self.token_information['token_expiration']/1000.0
        )
        dt_now = datetime.now()
        time_to_expiration = dt_token_expiration - dt_now
        token_information = (
            f'Username: {self.token_information["username"]}\n'
            f'Token will expire in: {time_to_expiration}\n'
            f'Login source: {self.token_information["source"]}\n'
            f'Path to configuration file: '
            f'\'{os.path.abspath(self.configuration_file)}\''
        )
        return token_information

    def _print_credentials(self) -> None:
        user_input = input('This action might expose critical information ('
                           'such as username & password) on your screen.\n'
                           'Do you want to continue? [Y/n]: ')
        if user_input == 'Y':
            print(f'  username: {self.username}\n'
                  f'  password: {self._password}\n'
                  f'  token: {self.token}')
        return

