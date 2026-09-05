"""Shared Code for Package Management"""

from cmem_client.client import Client
from pydantic import BaseModel


class InstallationResult(BaseModel):
    """Result of a package installation"""

    success: bool
    output: str
    forbidden: bool
    already_install: bool = False


def install_missing_packages(
    package_specs: list[str], client: Client
) -> dict[str, InstallationResult]:
    """Install missing packages"""
    packages = client.python_packages
    results: dict[str, InstallationResult] = {}
    for package_spec in package_specs:
        if package_spec in packages:
            version = packages[package_spec].version
            results[package_spec] = InstallationResult(
                success=True,
                output=f"Package already installed: {package_spec} ({version})",
                forbidden=False,
                already_install=True,
            )
            continue
        install_result = packages.install_by_name(package_spec)
        # cmem-client does not model the forbidden flag of the API response, so it
        # arrives in model_extra instead of as a field of PythonInstallResult
        extra = install_result.model_extra or {}
        results[package_spec] = InstallationResult(
            success=install_result.success,
            output=install_result.output,
            forbidden=bool(extra.get("forbidden", False)),
        )
    return results
