set shell := ['/bin/bash', '-cu']

@_default:
    just --list --unsorted --justfile {{justfile()}}


# HATCH
# show hatch metadata
metadata:
    hatch project metadata

# hatch build
build:
    hatch build

# remove build artifacts
clean:
    hatch run clean


# PYTEST
# pytest collection
collect *args:
    hatch run pytest --collect-only {{args}}

# run tests using hatch
test *args:
    hatch run test {{args}}

# generate and show html of coverage
covhtml:
    hatch run covhtml
