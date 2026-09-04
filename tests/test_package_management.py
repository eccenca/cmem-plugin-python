"""Test package management"""

from collections.abc import Iterator

import pytest
from cmem.cmempy.workspace.python import list_packages, uninstall_package
from cmem_plugin_base.testing import TestUserContext

from cmem_plugin_python.package_management import install_missing_packages

PACKAGE_NAME = "example-pypi-package"


@pytest.fixture
def uninstalled_package() -> Iterator[str]:
    """Provide the name of a package which is not installed.

    The package is uninstalled before the test and again afterward, in both cases
    unconditionally, so that neither a leftover from an earlier run nor a failing test
    can leave it behind.
    """
    uninstall_package(PACKAGE_NAME)
    yield PACKAGE_NAME
    uninstall_package(PACKAGE_NAME)


def test_install_missing_packages_success(uninstalled_package: str) -> None:
    """Test installation of missing packages"""
    package_name = uninstalled_package
    context = TestUserContext()
    assert package_name not in [package["name"] for package in list_packages()]
    results = install_missing_packages(package_specs=[package_name], context=context)
    assert package_name in [package["name"] for package in list_packages()]
    assert len(results) == 1
    assert package_name in results
    result = results[package_name]
    assert result.already_install is False
    assert result.success is True
    assert result.forbidden is False
    assert "Installed 1 package" in result.output
    results = install_missing_packages(package_specs=[package_name], context=context)
    result = results[package_name]
    assert result.already_install is True
    assert result.success is True
    assert result.forbidden is False
    assert "Package already installed" in result.output
