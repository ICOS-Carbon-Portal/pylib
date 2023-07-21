# ICOS Carbon Portal Python Package
<table>
    <tr>
        <td>Latest Release</td>
        <td>
            <a href="https://pypi.org/project/icoscp/"/>
            <img src="https://badge.fury.io/py/icoscp.svg"/>
        </td>
    </tr>
    <tr>
        <td>PyPI Downloads</td>
        <td>
            <a href="https://pepy.tech/project/icoscp"/>
            <img src="https://static.pepy.tech/personalized-badge/icoscp?period=total&units=international_system&left_color=black&right_color=orange&left_text=Downloads"/>
        </td>
    </tr>
</table>

## About ICOS

The Integrated Carbon Observation System, ICOS, is a European-wide greenhouse gas research infrastructure. ICOS produces standardised data on greenhouse gas concentrations in the atmosphere, as well as on carbon fluxes between the atmosphere, earth and oceans. This information is being used by scientists as well as by decision makers in predicting and mitigating climate change. The high-quality and open ICOS data is based on the measurements from over 130 stations across Europe. For more information about the ICOS station network, data quality control and assurance, and much more, please read the [ICOS Handbook 2022](https://www.icos-cp.eu/sites/default/files/2022-03/ICOS_handbook_2022_WEB.pdf), or visit our website [https://www.icos-cp.eu/](https://www.icos-cp.eu/).

This package is under active development. Please be aware that changes to names of functions and classes are possible without further notice. Please do feedback any recommendations, issues, etc. if you try it out.


What is the package about?
In essence this package allows you to have direct access to data objects from the ICOS CarbonPortal where a "Preview" is available. It is an easy access to data objects hosted at the ICOS Carbon Portal (https://data.icos-cp.eu/). By using this library you can load data files directly into memory.

Please be aware, that by either downloading data, or accessing data directly through this library, you agree and accept, that all ICOS data is provided under a <a href="https://data.icos-cp.eu/licence" target="_blank">CC BY 4.0 licence <img src="https://www.icos-cp.eu/sites/default/files/inline-images/creativecommons.png"></a>

## Installation
The latest release is available on [https://pypi.org/project/icoscp/](https://pypi.org/project/icoscp/). You can simply run

`pip install icoscp`

If you need the cutting edge version you may install the library directly from github with

`pip install git+https://github.com/ICOS-Carbon-Portal/pylib.git`

We would encourage you to use a virtual environment for python to test this library.
For example with [Miniconda](https://docs.conda.io/en/latest/miniconda.html) you can create a new environment with:

- `conda create -n icos python`
- `activate icos`
- `pip install icoscp`

## Documentation
The full documentation about the library and all the modules are available at [https://icos-carbon-portal.github.io/pylib/](https://icos-carbon-portal.github.io/pylib/)


## Development

For instructions about how to go about extending and testing this software, please see <development.md>
