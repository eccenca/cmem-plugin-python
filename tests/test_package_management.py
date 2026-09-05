"""Test package management"""

from collections.abc import Iterator

import pytest
from cmem_client.client import Client

from cmem_plugin_python.package_management import install_missing_packages
from tests.utils import needs_cmem

PACKAGE_NAME = "example-pypi-package"


def uninstall(package_name: str) -> None:
    """Uninstall a package, whether or not it is currently installed"""
    Client.from_env().python_packages.delete_item(package_name, skip_if_missing=True)


@pytest.fixture
def uninstalled_package() -> Iterator[str]:
    """Provide the name of a package which is not installed.

    The package is uninstalled before the test and again afterwards, in both cases
    unconditionally, so that neither a leftover from an earlier run nor a failing test
    can leave it behind.
    """
    uninstall(PACKAGE_NAME)
    yield PACKAGE_NAME
    uninstall(PACKAGE_NAME)


@needs_cmem
def test_install_missing_packages_success(uninstalled_package: str) -> None:
    """Test installation of missing packages"""
    package_name = uninstalled_package
    client = Client.from_env()
    assert package_name not in client.python_packages
    results = install_missing_packages(package_specs=[package_name], client=client)
    assert package_name in client.python_packages
    assert len(results) == 1
    assert package_name in results
    result = results[package_name]
    assert result.already_install is False
    assert result.success is True
    assert result.forbidden is False
    assert "Installed 1 package" in result.output
    results = install_missing_packages(package_specs=[package_name], client=client)
    result = results[package_name]
    assert result.already_install is True
    assert result.success is True
    assert result.forbidden is False
    assert "Package already installed" in result.output
