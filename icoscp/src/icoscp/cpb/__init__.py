"""
    The cpb module gives you access to a binary representation of
    digital data objects hosted at the ICOS Carbon Portal.
    Any data column (x,y axis) you can "preview" on the data portal
    ( https://data.icos-cp.eu/portal/ ) is accessible from this module.
    You need to know the digital object ID (URL, persistent identification)
    or have a SPARQL query providing this information.
"""
import warnings

warnings.simplefilter('always', UserWarning)
old_dob_warning = (
    "\nIt is highly recommended to replace the following import:\n"
    '"from icoscp.cpb.dobj import Dobj"\n'
    "  with\n"
    '"from icoscp.dobj import Dobj"\n'
    "Find out more here: "
    "https://icos-carbon-portal.github.io/pylib/icoscp/install/#upgrade-guide"
)
warnings.warn(old_dob_warning, UserWarning, stacklevel=2)
