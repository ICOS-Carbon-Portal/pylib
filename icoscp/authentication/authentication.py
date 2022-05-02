from pprint import pprint
import os
import requests
import tempfile


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
        f'\t\tPlease enter your username or API token (h for help): tade@tadedomain.sth \u21A9\n' \
        f'\t\tPlease enter your password: test_password \u21A9\n\n' \
        f'\tToken example:\n' \
        f'\t\tPlease enter your username or API token (h for help): ' \
        f'cpauthToken=rO0ABXcIAAABgHuHzPl0ABx6b2lzLnpvZ29wb3Vsb3NAbmF0ZWtvLmx1...\u21A9\n' \
        f'\t\t(Login here: https://cpauth.icos-cp.eu/login/ to retrieve you personal API ' \
        f'token. You will find the token at the bottom of the webpage).\n'
    print(important_notice)
    return


class Authentication:

    def __init__(self):
        # generate_cookie()
        self._using_token = True
        self._valid_credentials = False
        self._cookie_file = os.path.join(tempfile.gettempdir(), 'icos_cookie.txt')
        self._username, self._password, self._token = None, None, None
        # Todo: Rename this method.
        self.work_on_cookie_file()
        return

    @property
    def using_token(self):
        return self._using_token

    @using_token.setter
    def using_token(self, using_token):
        self._using_token = using_token
        return

    @property
    def valid_credentials(self):
        return self._valid_credentials

    @valid_credentials.setter
    def valid_credentials(self, valid_credentials):
        self._valid_credentials = valid_credentials
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
    def cookie_file(self):
        return self._cookie_file

    @cookie_file.setter
    def cookie_file(self, cookie_file):
        self._cookie_file = cookie_file
        return

    def retrieve_credentials(self):
        with open(file=self._cookie_file, mode='r') as cookie_handle:
            cookie_lines = cookie_handle.readlines()
        credentials = list()
        for line in cookie_lines:
            credential = line.split()[1] if len(line.split()) > 1 else None
            if credential == 'None':
                credential = None
            credentials.append(credential)
        # Assign credentials read from cookie file to properties.
        self._username, self._password, self._token = credentials
        return

    def retrieve_token(self):
        url = 'https://cpauth.icos-cp.eu/password/login'
        data = {'mail': self._username, 'password': self._password}
        response = None
        try:
            response = requests.post(url=url, data=data)
            if response.status_code == 200:
                self._using_token = False
                self._token = response.headers['Set-Cookie']
                self.validate_token()
            response.raise_for_status()
        except requests.exceptions.HTTPError as error:
            if response.status_code == 403:
                print(f'\n{error}\n{response.text}.\n')
            else:
                print(error)
        return

    def work_on_cookie_file(self):
        # Repeat until user enters valid credentials.
        while not self._valid_credentials:
            # Read and validate credentials in already existing cookie.
            if os.path.exists(self._cookie_file) and os.stat(self._cookie_file).st_size > 0:
                self.retrieve_credentials()
                if self._token:
                    self.validate_token()
                if self._username and self._password and not self._valid_credentials:
                    self.retrieve_token()
                if not self._valid_credentials:
                    os.remove(self._cookie_file)
            # Cookie file is not available in the file system.
            # Request user's credentials.
            else:
                self.request_credentials()
            # Cookie file contains wrong credentials and needs to be
            # replaced.
            if not self._token and os.path.exists(self._cookie_file):
                os.remove(self._cookie_file)
        # Write valid credentials to cookie file.
        self.write_cookie()
        return

    def request_credentials(self):
        user_input = input('Please enter your username or API token (h for help): ')
        if user_input == 'h':
            print_help(self)
        elif '@' in user_input:
            self._username = user_input
            self._password = input('Please enter your password: ')
            self.retrieve_token()
        else:
            self._token = user_input
            self.validate_token()
        return

    def write_cookie(self):
        with open(file=self._cookie_file, mode='w+') as cookie_handle:
            cookie_handle.write(f'username: {self._username}\n'
                                f'password: {self._password}\n'
                                f'token: {self._token}')
        return

    def validate_token(self):
        url = 'https://cpauth.icos-cp.eu/whoami'
        headers = {'cookie': self._token}
        response = None
        try:
            response = requests.get(url=url, headers=headers)
            if response.status_code == 200:
                self._valid_credentials = True
                print(f'\U0001f464{response.json()["email"]}\U0001f464 authorized using '
                      f'{"token" if self._using_token else "username & password"}.')
            response.raise_for_status()
        except requests.exceptions.HTTPError as error:
            if response.status_code == 403:
                print(f'\n{error}\n{response.text}.\n')
            else:
                print(f'\n{error}\n{response.text}.\n')
        return

    def update_cookie(self):
        cookie_lines = \
            [f'{credential_key}: {credential_value}\n' for credential_key, credential_value in
             self._credentials.items()]
        with open(file=self._cookie_file, mode='w') as cookie_handle:
            cookie_handle.writelines(cookie_lines)
        return

    def print_credentials(self):
        print(f'\nusername: {self._username}, {type(self._username)}\n'
              f'password: {self._password}, {type(self._password)}\n'
              f'token: {self._token}, {type(self._token)}\n')
        return


