## how to publish a new version to pypi

make sure you have a python environment with:

- setuptools
- twine

`pip install setuptools twine --upgrade`


### create the distribution files

I highly recommend you delete the folder "build" if you have one, then run

python setup.py sdist bdist_wheel



### upload to testpi (with the latest version...)
twine upload --repository testpypi dist/icoscp-0.1.7.tar.gz

### test installation from testpi

- create a new python environment

run pip to install from test.pypi.org but add extra link, so that dependencies can be installed automatically.
Further, remember to adjust the 'version' after icoscp==    otherwise you may end up with an old version.

- pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple "icoscp==0.1.0rc1"

### Finally, upload the release to the real pypi.org...

- twine upload dist/icoscp-0.1.20.tar.gz