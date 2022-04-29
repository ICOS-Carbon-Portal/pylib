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
                self._token = response.headers['Set-Cookie'].split('=')[1]
                self._valid_credentials = True
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
            if not os.path.exists(self._cookie_file):
                test_string = input('\tPlease enter your username or API token: ')
                if '@' in test_string:
                    self._username = test_string
                    self._password = input('\tPlease enter your password: ')
                    self.retrieve_token()
                else:
                    self._token = test_string
                    self.validate_token()
            elif os.path.exists(self._cookie_file):
                self.retrieve_credentials()
                if self._token:
                    self.validate_token()
            # Cookie file contains wrong credentials and needs to be
            # replaced.
            if not self._token and os.path.exists(self._cookie_file):
                os.remove(self._cookie_file)
        # Write valid credentials to cookie file.
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


