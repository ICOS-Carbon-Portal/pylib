## how to publish a new version to pypi

make sure you have a python environment with:

- mkdocs

`pip install mkdocs`

### documentation setup
In the repository root folder you will find a file 'mkdocs.yml'. This is the file wher the navigation is setup. All documentation files at /docs/*.md need to be references here.

### update the documentation

Download the repo and navigate to the root folder. Start a local mkdocs instance, for an instant build and control.

`mkdocs serve`

open a browser and have a look at the documentation:

`http://127.0.0.1:8000/`

Now you can change, update the files you would like in /docs/*.md and the changes are instantly visible in the browser.

Once you are happy with the changes
1. update the github repository
2. publish the documentation with
mkdocs gh-deploy

**remember** that the pypi.org website points directly to this documentation, but the master branch of the repository is most likely the "latest" and not the published version..