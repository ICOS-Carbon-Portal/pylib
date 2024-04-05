# Installation
This is a legacy library that is under active support and maintenance
for the foreseeable future.  
  
For new projects, developers are advised to
**consider [icoscp_core](https://pypi.org/project/icoscp_core/)**,
unless it is explicitly known that some specific icoscp feature is
required.
  
We do our best to keep the function calls and parameters
consistent, but without a guarantee. You can follow the development on 
[GitHub repository](https://github.com/ICOS-Carbon-Portal/pylib). Create
an issue to leave comments, suggestions or if you find something not
working as expected. The library has not been tested on many different
operating systems and environments, hence we appreciate you telling us
what is good and bad.  
  
The library is developed with  Python 3.x, and we assume that any
recent Python distribution should work. If you have any trouble running
the library, we are very keen to know why. Please get in touch: 
jupyter-info@icos-cp.eu

## Pip official release
The recommended way of installation is by using pip:

	pip install icoscp
	
The installation should take care of any dependencies, but to
successfully access any data object from the ICOS Carbon Portal you need
to have a working internet connection.  
  
We would encourage you to use a virtual environment for python to test
this library. For example with mini-conda
[https://docs.conda.io/en/latest/miniconda.html](
https://docs.conda.io/en/latest/miniconda.html) you can create a new
environment with:

- `conda create -n icos python`
- `activate icos`
- `pip install icoscp`

## Authentication
To ensure users' **licence** acceptance, when **accessing data objects**
through the icoscp Python library, authentication is required. Users
MUST either have ICOS Carbon Portal login credentials or
log in to Carbon Portal using another mechanism
[https://cpauth.icos-cp.eu/login/](https://cpauth.icos-cp.eu/login/)
to obtain the token to access ICOS data.

In order to fetch data, users make their requests to data objects and
must provide an API token to do so. The `cpauth` module helps to
retrieve the ICOS API token using a variety of ways. Authentication is
required only for off-server data access (users who are not using our
ICOS Jupyter services). Users with direct access to the data files,
namely, **users of our [ICOS Jupyter services](
https://www.icos-cp.eu/data-services/tools/jupyter-notebook), are
excluded from authentication**. Metadata access remains unaffected from
these changes. For security reasons the API token is valid for 100'000
seconds (27 hours) and must be refreshed regularly; thus the
authentication process can be automated to simplify the user experience.

### Configure your authentication
Authentication can be initialized in a number of ways.

#### Credentials and token cache file (default)
This approach should only be used on machines the developer trusts.

A username/password account for the [ICOS](https://cpauth.icos-cp.eu/)
authentication service is required for this. Obfuscated (not readable by
humans) password is stored in a file on the local machine in a **default
user-specific folder**. To initialize this file, run the following code
interactively (only needs to be once for every machine):

```Python
from icoscp import auth
auth.init_config_file()
```

After the initialization step is done, access to the metadata and data
services is achieved using the [Dobj module](modules.md#dobj).

As an alternative, the developer may choose to use a specific file to
store the credentials and token cache. In this scenario, data and
metadata access is achieved as follows:

```Python
from icoscp_core.icos import bootstrap
auth, meta, data = bootstrap.fromPasswordFile("<desired path to the file>")

# The next line needs to be run interactively (only once per file).
auth.init_config_file()
```

#### Static authentication token (prototyping)
This option is good for testing, on a public machine or in general. Its
only disadvantage is that the tokens have limited period of validity
(100000 seconds, less than 28 hours), but this is precisely what makes
it acceptable to include them directly in the Python source code.

The token can be obtained from the "My Account" page ([ICOS](
https://cpauth.icos-cp.eu/)), which can be accessed by logging in
using one of the supported authentication mechanisms (username/password,
university sign-in, OAuth sign in). After this the bootstrapping can be
done as follows:

```Python
from icoscp import auth

cookie_token = 'cpauthToken=WzE2OTY2NzQ5OD...'
auth.init_by_token(cookie_token)
```

#### Explicit credentials (advanced option)

The user may choose to use their own mechanism of providing the
credentials to initialize the authentication. This should be considered
as an advanced option. **(Please do not put your password as clear text
in your Python code!)** This can be achieved as follows:

```Python
from icoscp import auth

auth.init_by_credentials(username='rbon@portoca.lis', password='pa$$w0rd')
```

---

## Manual installation
If you would like to install the latest version (branch from GitHub),
you can download / fork the repo navigate to the library folder and
start the installation with:

`pip install .`  
or  
`python setup.py install`

### Cutting Edge
Install directly from our GitHub master branch. Please be aware that
this is not reflecting the official release of the library, but includes
the latest development. Hence, you should think of this as an alpha or
beta version of the new release:  
`pip install git+https://github.com/ICOS-Carbon-Portal/pylib.git`

## Dependencies
The following modules are required by the library:

    - fiona
    - folium
    - geopandas
    - icoscp_core
    - pandas
    - requests
    - tqdm
