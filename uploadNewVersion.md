## how to publish a new version to pypi

make sure you have python environment with:

- setuptools
- twine

`pip install setuptools twine --upgrade`


### create the distribution files

python setup.py sdist bdist_wheel



### upload to testpi
twine upload --repository testpypi dist/*

### test installation from testpi

- create a new python environment

run pip to install from test.pypi.org but add extra link, so that dependencies can be installed automatically.
Further, remember to adjust the 'verion' after icoscp==    otherwise you may end up with an old version.

- pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple "icoscp==0.1.0rc1"

### Finally, upload the release to the real pypi.org...


