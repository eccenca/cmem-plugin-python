"""Test package management"""

from cmem_client.client import Client

from cmem_plugin_python.package_management import (
    InstallationResult,
    format_installation_results,
    install_missing_packages,
)
from tests.utils import needs_cmem


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
    # not the installer's wording: uv and pip phrase a successful install differently
    assert package_name in result.output
    results = install_missing_packages(package_specs=[package_name], client=client)
    result = results[package_name]
    assert result.already_install is True
    assert result.success is True
    assert result.forbidden is False
    assert "Package already installed" in result.output


def installation_result(**kwargs: object) -> InstallationResult:
    """Build an installation result with the given deviations from a plain success"""
    values: dict = {"success": True, "output": "Installed 1 package", "forbidden": False}
    values.update(kwargs)
    return InstallationResult(**values)


def test_format_installation_results_without_packages() -> None:
    """Test the report of an action which had nothing to install"""
    assert format_installation_results({}) == "No packages installed."


def test_format_installation_results_reports_plugin_errors() -> None:
    """Test that plugins which failed to register end up in the report"""
    report = format_installation_results(
        {
            "quiet-package": installation_result(),
            "loud-package": installation_result(plugin_errors=["MyPlugin: boom"]),
        }
    )
    assert "# quiet-package" in report
    assert "Plugins which failed to register" in report
    assert "- MyPlugin: boom" in report
    assert report.count("Plugins which failed to register") == 1
