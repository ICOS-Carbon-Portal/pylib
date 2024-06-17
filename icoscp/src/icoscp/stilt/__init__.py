import warnings

warnings.simplefilter('always', UserWarning)
stilt_warning = (
    "\nThe icoscp STILT module has been moved to a new dedicated library: "
    "https://icos-carbon-portal.github.io/pylib/icoscp_stilt/\n"
    'To import it use: "from icoscp_stilt import stilt"'
)
warnings.warn(stilt_warning, UserWarning, stacklevel=2)
