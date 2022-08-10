# Installation

This library is in active development and may change at any time. We do our best to keep the function calls and parameters consistent, but without a guarantee. You can follow the development on [Github](https://github.com/ICOS-Carbon-Portal/pylib). Create an issue to leave comments, suggestions or if you find something not working as expected. The library has not been tested on many different operating systems and environments, hence we appreciate you telling us what is good and bad. 

The library is developed with  Python 3.x and we assume that any recent Python distribution should work. If you have any trouble running the library, we are very keen to know why. Please get in touch ( jupyter-info@icos-cp.eu )

## Pip official release

The recommended way of installation is by using pip:

	pip install icoscp
	
The installation should take care of any dependencies, but to successfully access any data object from the ICOS Carbon Portal you need to have a working internet connection.

We would encourage you to use a virtual environment for python to test this library. For example with mini-conda [https://docs.conda.io/en/latest/miniconda.html](https://docs.conda.io/en/latest/miniconda.html) you can create a new environment with:

- `conda create -n icos python`
- `activate icos`
- `pip install icoscp`

## Manual installation
If you would like to install the latest version (branch from Github), you can download / fork the repo navigate to the library folder and start the installation with:

- `pip install .`
<br>or<br>
- `python setup.py install`

### Cutting Edge
Install directly from our github master branch. Please be aware that this is not reflecting the official release of the library, but includes the latest development. Hence you should think of this as an alpha or beta version of the new release:<br>
`pip install git+https://github.com/ICOS-Carbon-Portal/pylib.git`

## Dependencies
The following modules are required by the library:

	- requests
	- pandas
	- tqdm
	- folium
