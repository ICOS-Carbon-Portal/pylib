# Authentication
To ensure users' licence acceptance when accessing data objects
through the `icoscp` Python library, authentication is required. Users
must either have ICOS Carbon Portal login credentials or
log in to Carbon Portal using another mechanism
[https://cpauth.icos-cp.eu/login/](https://cpauth.icos-cp.eu/login/)
to obtain the token to access ICOS data.

Users also need to read and accept the ICOS Data Licence in their
[user profile](https://cpauth.icos-cp.eu/).

**Metadata-only access does not require authentication.**

Users with direct access to the data files,
namely, **users of our [ICOS Jupyter services](
https://www.icos-cp.eu/data-services/tools/jupyter-notebook), are
not required to configure authentication**.

In order to fetch data, users make their requests to data objects and
must provide an API token to do so. For security reasons the API token is
valid for 100'000 seconds (27 hours) and may therefore need to be refreshed;
this process is automated when using credentials-based authentication (see
below).

Authentication can be initialized in a number of ways. **Please note** that
when using other approaches than the default one (see below), it becomes
necessary to use the `data` value (instance of `DataClient` class) obtained
in the process of authentication bootstrap, rather than the default instance
obtained by import `from icoscp_core.icos import data` used in the code
examples in this documentation.

## By credentials file (default)
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

## By custom credentials file
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

## By authentication token (prototyping)
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

## By explicit credentials (advanced option)
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
