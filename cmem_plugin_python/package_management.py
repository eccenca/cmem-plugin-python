"""Shared Code for Package Management"""

from cmem.cmempy.workspace.python import install_package_by_name, list_packages
from cmem_plugin_base.dataintegration.context import UserContext
from cmem_plugin_base.dataintegration.utils import setup_cmempy_user_access
from pydantic import BaseModel


class InstallationResult(BaseModel):
    """Result of the install_package_by_name call"""

    success: bool
    output: str
    forbidden: bool
    already_install: bool = False


def install_missing_packages(
    package_specs: list[str], context: UserContext
) -> dict[str, InstallationResult]:
    """Install missing packages"""
    setup_cmempy_user_access(context=context)
    installed_package: dict[str, str] = {
        package["name"]: package["name"] for package in list_packages()
    }
    results = {}
    for package_spec in package_specs:
        if package_spec not in installed_package:
            setup_cmempy_user_access(context=context)
            result = InstallationResult(**install_package_by_name(package_name=package_spec))
            results[package_spec] = result
        else:
            version = installed_package[package_spec]
            result = InstallationResult(
                success=True,
                output=f"Package already installed: {package_spec} ({version})",
                forbidden=False,
                already_install=True,
            )
            results[package_spec] = result
    return results
