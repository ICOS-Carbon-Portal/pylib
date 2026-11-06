import importlib
import pkgutil

import pytest

import icoscp

MODULES = [m.name for m in pkgutil.walk_packages(icoscp.__path__, "icoscp.")]


@pytest.mark.parametrize("name", MODULES)
def test_module_imports(name):
    importlib.import_module(name)
