"""Test package management"""

from cmem.cmempy.workspace.python import list_packages, uninstall_package
from cmem_plugin_base.testing import TestUserContext

from cmem_plugin_python.package_management import install_missing_packages


def test_install_missing_packages_success() -> None:
    """Test installation of missing packages"""
    package_name = "example-pypi-package"
    context = TestUserContext()
    uninstall_package(package_name)
    assert package_name not in [package["name"] for package in list_packages()]
    results = install_missing_packages(package_specs=[package_name], context=context)
    assert package_name in [package["name"] for package in list_packages()]
    assert len(results) == 1
    assert package_name in results
    result = results[package_name]
    assert result.already_install is False
    assert result.success is True
    assert result.forbidden is False
    assert f"Successfully installed {package_name}" in result.output
    results = install_missing_packages(package_specs=[package_name], context=context)
    result = results[package_name]
    assert result.already_install is True
    assert result.success is True
    assert result.forbidden is False
    assert "Package already installed" in result.output
    uninstall_package(package_name)
