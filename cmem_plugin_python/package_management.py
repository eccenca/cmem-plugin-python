"""Shared Code for Package Management"""

from cmem_client.client import Client
from cmem_client.models.python_install import PythonInstallResult
from pydantic import BaseModel, Field


class InstallationResult(BaseModel):
    """Result of a package installation"""

    success: bool
    output: str
    forbidden: bool
    already_install: bool = False
    plugin_errors: list[str] = Field(default_factory=list)


def installation_output(install_result: PythonInstallResult) -> str:
    """Join the output fields of an installation result.

    DataIntegration 24.1 and later report everything in `output`, while older
    deployments filled `standardOutput` and `errorOutput` instead, so all three are
    joined rather than picking one of them.
    """
    parts = [install_result.output, install_result.standard_output, install_result.error_output]
    return "\n".join(part for part in parts if part)


def install_missing_packages(
    package_specs: list[str], client: Client
) -> dict[str, InstallationResult]:
    """Install missing packages"""
    packages = client.python_packages
    results: dict[str, InstallationResult] = {}
    for package_spec in package_specs:
        if package_spec in packages:
            version = packages[package_spec].version
            installed = f" ({version})" if version else ""
            results[package_spec] = InstallationResult(
                success=True,
                output=f"Package already installed: {package_spec}{installed}",
                forbidden=False,
                already_install=True,
            )
            continue
        install_result = packages.install_by_name(package_spec)
        # forbidden is not a field of PythonInstallResult, so it arrives in model_extra -
        # read the field first, so the value survives cmem-client modelling it later
        extra = install_result.model_extra or {}
        results[package_spec] = InstallationResult(
            success=install_result.success,
            output=installation_output(install_result),
            forbidden=getattr(install_result, "forbidden", extra.get("forbidden", False)),
            plugin_errors=[str(error) for error in install_result.plugin_errors],
        )
    return results


def format_installation_results(results: dict[str, InstallationResult]) -> str:
    """Render installation results as the markdown an action reports"""
    if not results:
        return "No packages installed."
    output = []
    for package, result in results.items():
        output.append(f"# {package}\n\n{result.output}\n")
        if result.plugin_errors:
            output.append("Plugins which failed to register:\n")
            output.extend(f"- {error}" for error in result.plugin_errors)
    return "\n".join(output)
