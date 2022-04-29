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
        f'\t\tPlease enter your username or API token (h for help): tade@tadedomain \u21A9\n' \
        f'\t\tPlease enter your password: test_icos_password \u21A9\n\n' \
        f'\tToken example:\n' \
        f'\t\tPlease enter your username or API token (h for help): ' \
        f'cpauthToken=rO0ABXcIAAABgHuHzPl0ABx6b2lzLnpvZ29wb3Vsb3NAbmF0ZWtvLmx1...\u21A9\n' \
        f'\t\t(Login here: https://cpauth.icos-cp.eu/login/ to retrieve you personal API ' \
        f'token. You will find the token at the bottom of the webpage).'
    print(important_notice)
    return


class Authentication:

    def __init__(self):
        # generate_cookie()
        self._valid_credentials = False
        self._cookie_file = os.path.join(tempfile.gettempdir(), 'icos_cookie.txt')
        self._username, self._password, self._token = None, None, None
        # Todo: Rename this method.
        self.work_on_cookie_file()
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
        # Assign credentials read from cookie file to properties.
        self._username, self._password, self._token = \
            [line.split()[1] if len(line.split()) > 1 else None for line in cookie_lines]
        return

    def retrieve_token(self):
        url = 'https://cpauth.icos-cp.eu/password/login'
        data = {'mail': self._username, 'password': self._password}
        response = None
        try:
            response = requests.post(url=url, data=data)
            if response.status_code == 200:
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
            if os.path.exists(self._cookie_file):
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
            # Cookie file contains wrong credentials and needs to be
            # replaced.
            if not self._token and os.path.exists(self._cookie_file):
                os.remove(self._cookie_file)
        # Write valid credentials to cookie file.
        self.write_cookie()
        return

    def write_cookie(self):
        with open(file=self._cookie_file, mode='w+') as cookie_handle:
            cookie_handle.write(f'username: {self._username}\n'
                                f'password: {self._password}\n'
                                f'token: {self._token}')
        return

    def validate_token(self):
        url = 'https://data.icos-cp.eu/objects/hznHbmgfkAkjuQDJ3w73XPQh'
        headers = {'cookie': self._token}
        response = None
        try:
            response = requests.get(url=url, headers=headers)
            # Validate request by `status_code` and by existence of
            # 'Content_Disposition' key in `headers` dictionary.
            # According to https://github.com/ICOS-Carbon-Portal/data
            # if 'Content-Disposition' key exists in the headers the
            # requested file was downloaded successfully.
            if response.status_code == 200 and 'Content-Disposition' in response.headers.keys():
                self._valid_credentials = True
                print('Successful authorization!')
            elif 'Content-Disposition' not in response.headers.keys():
                print(f'Trying to retrieve token for user: {self._username}... ')
            response.raise_for_status()
        except requests.exceptions.HTTPError as error:
            if response.status_code == 403:
                print(f'\n{error}\n{response.text}.\n')
            else:
                print(error)
        return

    def update_cookie(self):
        cookie_lines = \
            [f'{credential_key}: {credential_value}\n' for credential_key, credential_value in
             self._credentials.items()]
        with open(file=self._cookie_file, mode='w') as cookie_handle:
            cookie_handle.writelines(cookie_lines)
        return

    def print_credentials(self):
        print(f'\nusername: {self._username}\n'
              f'password: {self._password}\n'
              f'token: {self._token}\n')
        return


