# Overview

This project is maintained using [hatch](https://hatch.pypa.io/latest/) a
modern python project manager.

Hatch helps with, building, testing and releasing this package.


## Installing hatch

Unless you have other preferences, use [pipx](https://hatch.pypa.io/latest/) to
install hatch. Pipx will "Install and Run Python Applications in Isolated
Environments".

First install pipx:

    $ pip install --user pipx

Then use pipx to install hatch:

    $ pipx install hatch


## Use hatch for development

Hatch is configured entirely through [pyproject.toml](pyproject.toml).



### Run tests

    $ hatch run test

This will run a hatch "script". A script is a series of shell commands that
runs within a python virtual environment. Hatch will automatically create the
virtual environment as needed.

In the case of "test" it's a script defined as

    "pytest {args:tests}"

So in when executing "hatch run test", hatch will:
* Create a new virtual environment
* Populate it with the specified dependencies (pandas, requests, pytest, et)
* Execute "pytest {args:tests}" - i.e if you pass any arguments to "hatch run
  tests" they will appear here, defaulting to "tests"


### Show test coverage

    $ hatch run cov
    $ hatch run covhtml


This will run pytest under coverage, generate an html report, and open the
report in your browser.


### Build the package

    $ hatch build

This creates an sdist and a wheel file in dist/.


### Clean up

    $ hatch run clean


### Check current version and bump version
For more information, see the [official hatch documentation about versioning](https://hatch.pypa.io/latest/version/)

    $ hatch version
    0.1.18

    $ hatch version patch
    Old: 0.1.18
    New: 0.1.19


### Release a new version to pypi


    # make sure all test are passing
    $ hatch run test

    # create dist/*
    $ hatch build

    # release to test.pypi
    $ hatch release -r test

    # release to pypi
    $ hatch release


### Update documentation

Download the repo and navigate to the root folder. Start a local mkdocs
instance, for an instant build and control.

`hatch run mkdocs serve`

Open a browser and have a look at the documentation:

`http://127.0.0.1:8000/`

Now you can change, update the files you would like in /docs/*.md and the
changes are instantly visible in the browser.

Once you are happy with the changes
1. update the github repository
2. publish the documentation with
`hatch run mkdocs gh-deploy`

**remember** that the pypi.org website points directly to this documentation,
but the master branch of the repository is most likely the "latest" and not the
published version..


## Sample workflow

1. Write some code.
2. Run the tests
`hatch run test`
3. Run tests (using coverage) and see the report
`hatch run cov; hatch run covhtml`
4. Build the wheel
`hatch build`
5. Publish to testpypi
`hatch publish -r test`



## Advanced usage

### Run test matrix
