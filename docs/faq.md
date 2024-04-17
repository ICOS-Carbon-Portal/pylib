# (potentially) Frequently Asked Questions

Please see [examples](examples.md) for possible unswers to questions not covered here.

### `icoscp_core` is very different from the old `icoscp`, do I have to rewrite everything?
No, your code depending on the older version will continue working. No code got removed from `icoscp` with release `0.2.0`. But you may benefit from the new `icoscp_core` features for new developments, and from gradual porting of your older code to using `icoscp_core`.


### How can I retrieve the latest/newest version of a dataset?

```python
from icoscp_core.icos import meta
dobj = meta.get_dobj_meta('https://meta.icos-cp.eu/objects/lNJPHqvsMuTAh-3DOvJejgYc')

latest_version_uri = dobj.latestVersion
```

### How do I suppress warnings?
Internally the `icoscp` python library uses the `warnings` module to provide
useful information to the users.

  - `future warning` messages are connected to components of the library that
    will change in a future release. Here is an example of a `future warning`
    message:

        /pylib/icoscp/cpauth/exceptions.py:28: FutureWarning:
        Due to updates in the python library of the ICOS carbon portal, starting from
        the next version, user authentication might be required.
        warnings.warn(warning, category=FutureWarning)

    To suppress such a message, users need to add the code below in their 
    scripts:

        import warnings
        warnings.simplefilter("ignore", FutureWarning)

  - `user warning` messages are used to notify the user that there is something 
    potentially incorrect or risky in the program, but that the program is 
    still able to run. Here is an example of a `user warning` message:
 
            /pylib/icoscp/cpauth/exceptions.py:39: UserWarning:
            Your authentication was unsuccessful. Falling back to anonymous data access.
            Please, revisit your authentication configuration or have a look at the
            documentation. Authentication will become mandatory for data access.
            warnings.warn(warning, category=UserWarning)

    To suppress such a message, users need to add the code below in their 
    scripts:

        import warnings
        warnings.simplefilter("ignore", UserWarning)

### Where is the documentation for the cpauth module?
The documentation for the authentication module can be found in the 
installation section [here](install.md#authentication). 

