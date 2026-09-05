"""Fixtures shared by the tests"""

from collections.abc import Iterator

import pytest
from cmem_client.client import Client

PACKAGE_NAME = "example-pypi-package"
"""A tiny package which exists on PyPI and which no deployment installs by itself"""


def uninstall(package_name: str) -> None:
    """Uninstall a package, whether or not it is currently installed"""
    Client.from_env().python_packages.delete_item(package_name, skip_if_missing=True)


@pytest.fixture
def uninstalled_package() -> Iterator[str]:
    """Provide the name of a package which is not installed.

    The package is uninstalled before the test and again afterwards, in both cases
    unconditionally, so that neither a leftover from an earlier run nor a failing test
    can leave it behind.

    Only this package is ever removed from the deployment: a test which needs a second
    dependency uses one that is installed anyway, so that a failing run cannot take a
    package away from everybody else who works there.
    """
    uninstall(PACKAGE_NAME)
    yield PACKAGE_NAME
    uninstall(PACKAGE_NAME)
