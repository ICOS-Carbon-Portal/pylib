# Installation
The library requires Python version 3.10 or later.

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

## Upgrade guide
This concerns users of **icoscp** of versions prior to `0.2.0`.

For standalone library users (i.e. outside of a Carbon Portal Jupyter
environment), the installation procedure must be followed by the
[authentication setup](#authentication) (unless you have used **icoscp_core**
previously, and configured authentication with it using the default method).

After that all the working code that depended on older versions should work,
and no code changes are necessary, but it is highly recommended to replace the
following import
```python
from icoscp.cpb.dobj import Dobj
```
with
```python
from icoscp.dobj import Dobj
```

(i.e. drop `.cpb` from this import's path) everywhere in your scripts and
notebooks. The new `Dobj` class has a legacy status (see the
[library history](index.md#the-history-and-the-new-role-of-the-library)), like
the old one, but contains an improved implementation of the same API.  

<div style="margin-bottom: 1em">
The advantages are:
</div>

- support for metadata access of all data objects (not only the ones whose
  *data* is accessible with the library)
- better performance when fetching the data
- new `metadata` property that contains `DataObject` dataclass from
  `icoscp_core.metaclient` module, which is a type-annotated nested structure
  that was (mostly) automatically produced to faithfully reflect the JSON
  metadata available for the data object from the metadata server.

An effort was made to ensure identical functionality of the new `Dobj` class
when compared with the old one, but there are some subtle differences described
[elsewhere in the documentation](modules.md#known-differences-between-dobjs).

## Authentication
To ensure users' **licence** acceptance, when **accessing data objects**
through the `icoscp` Python library, authentication is required. Users
MUST either have ICOS Carbon Portal login credentials or
log in to Carbon Portal using another mechanism
[https://cpauth.icos-cp.eu/login/](https://cpauth.icos-cp.eu/login/)
to obtain the token to access ICOS data.

Users also need to read and accept the ICOS Data Licence in their
[user profile](https://cpauth.icos-cp.eu/).

Metadata-only access does not require authentication.

Users with direct access to the data files,
namely, **users of our [ICOS Jupyter services](
https://www.icos-cp.eu/data-services/tools/jupyter-notebook), are
not required to configure authentication**.

In order to fetch data, users make their requests to data objects and
must provide an API token to do so. For security reasons the API token is
valid for 100'000 seconds (27 hours) and may therefore need to be refreshed;
this process is possible to automate.

Authentication can be initialized in a number of ways.

### By credentials file (default)
This approach should only be used on machines the developer trusts.

A username/password account for the [ICOS](https://cpauth.icos-cp.eu/)
authentication service is required for this. Obfuscated (not readable by
humans) password is stored in a file on the local machine in a **default
user-specific folder**. To initialize this file, run the following code
interactively (only needs to be done once for every machine):

```Python
from icoscp_core.icos import auth
auth.init_config_file()
```

After the initialization step is done in this way, access to the data can be
achieved using both the new `icoscp_core` machinery and the legacy
[Dobj classes](modules.md#dobj).

### By custom credentials file
The developer may wish to use a specific file to store obfuscated
credentials and token cache. In this scenario, data and
metadata access are achieved as follows:

```Python
from icoscp_core.icos import bootstrap
auth, meta, data = bootstrap.fromPasswordFile("<desired path to the file>")
# The next line needs to be run interactively (only once per file).
auth.init_config_file()
```

If the legacy library functionality will be used, the following extra step is
needed as well:

```Python
from icoscp import cpauth
cpauth.init_by(auth)
```

### By authentication token (prototyping)
This option is good for testing, on a public machine or in general. Its
only disadvantage is that the tokens have limited period of validity
(100'000 seconds, less than 28 hours), but this is precisely what makes
it acceptable to include them directly in the Python source code.

The token can be obtained from the "My Account" page ([ICOS](
https://cpauth.icos-cp.eu/)), which can be accessed by logging in
using one of the supported authentication mechanisms (username/password,
university sign-in, OAuth sign in). After this the bootstrapping can be
done as follows:

```Python
from icoscp_core.icos import bootstrap
cookie_token = 'cpauthToken=WzE2OTY2NzQ5OD...'
meta, data = bootstrap.fromCookieToken(cookie_token)
```

If the legacy library functionality will be used, the following extra step is
needed as well:

```Python
from icoscp import cpauth
cpauth.init_by(data.auth)
```

### By explicit credentials (advanced option)
The user may choose to use their own mechanism of providing the
credentials to initialize the authentication. This should be considered
as an advanced option. **(Please do not put your password as clear text
in your Python code!)** This can be achieved as follows:

```Python
from icoscp_core.icos import bootstrap
meta, data = bootstrap.fromCredentials(username_variable, password_containing_variable)
```

If the legacy library functionality will be used, the following extra step is
needed as well:

```Python
from icoscp import cpauth
cpauth.init_by(data.auth)
```

---

## Manual installation
If you would like to install the latest version (branch from GitHub),
you can download / fork the repo navigate to the library folder and
start the installation with:
```shell
pip install .
```

### Cutting Edge
Install directly from our GitHub master branch. Please be aware that
this is not reflecting the official release of the library, but includes
the latest development. Hence, you should think of this as an alpha or
beta version of the new release:
```shell
pip install git+https://github.com/ICOS-Carbon-Portal/pylib.git
```

## Dependencies
The following modules are required by the library:

- fiona
- folium
- geopandas
- icoscp_core
- pandas
- requests
- tqdm
