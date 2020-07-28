# Installation


This library is in active development and may change at any time. We do our best to keep the function calls and parameters consistent, but without a guarantee. You can follow the development on Github. At the moment the master branch is found at https://github.com/ICOS-Carbon-Portal/jupyter.  Create an issue to leave comments, suggestions or if you find something not working as expected. The library has not been tested on many different operating systems and environments, hence we appreciate you telling us what is good and bad. 

The library is developed with  Python 3.7.x and we assume that any recent Python distribution should work.
If you have trouble to run the library, we are very keen to know why. Please get in contact.

## pip official release

The recommended way of installation is by using pip:

	pip install icoscp
	
the installation should take care of any dependencies, but to successfully access any data object from the ICOS Carbon Portal you need to have a working internet connection.

We would encourage you to use a virtual environment for python to test this library.
For example with mini-conda (https://docs.conda.io/en/latest/miniconda.html) you can create a new environment with:

- `conda create -n icos python`
- `activate icos`
- `pip install icoscp`

## Manaual installation
If you would like to install the latest version (branch from Github), you can download / fork the repo and install the library with:

- `pip install .`
<br>or<br>
- `python setup.py install`


## dependencies
the following modules are required by the library:

	requests
	pandas
	tqdm
	

<hr>cd20200715