"""Plugin tests."""

from typing import TYPE_CHECKING

import pytest
from cmem.cmempy.workspace.python import list_packages, uninstall_package
from cmem_plugin_base.dataintegration.parameter.code import PythonCode
from cmem_plugin_base.testing import TestExecutionContext, TestPluginContext

from cmem_plugin_python.workflow_task import (
    PythonCodeWorkflowPlugin,
    examples_execute,
    examples_init,
)

if TYPE_CHECKING:
    from cmem_plugin_base.dataintegration.entity import Entities


def test_workflow_execution() -> None:
    """Test with inputs"""
    init_code = PythonCode(
        """# init code
pass
        """
    )
    execute_code = PythonCode(
        """# execute code
entities = None
schema = None
        """
    )
    plugin = PythonCodeWorkflowPlugin(init_code=init_code, execute_code=execute_code)
    entities = plugin.execute(inputs=[], context=TestExecutionContext())
    assert entities is None


def test_example_init_code() -> None:
    """Run initialization for all init examples"""
    for init_code in vars(examples_init).values():
        PythonCodeWorkflowPlugin(init_code=PythonCode(init_code), execute_code=PythonCode(""))


def test_example_execution() -> None:
    """Test execution of examples"""
    # run 'randoms' first, then feed output to `take_first`
    random_size = 1000
    randoms = PythonCodeWorkflowPlugin(
        init_code=PythonCode(""), execute_code=PythonCode(examples_execute.randoms)
    )
    randoms_result: Entities = randoms.execute(inputs=[], context=TestExecutionContext())
    assert len(list(randoms_result.entities)) == random_size

    take_first = PythonCodeWorkflowPlugin(
        init_code=PythonCode(""), execute_code=PythonCode(examples_execute.take_first)
    )
    with pytest.raises(ValueError, match="Please connect a task to the first input port"):
        take_first.execute(inputs=[], context=TestExecutionContext())
    take_first_result: Entities = take_first.execute(
        inputs=[randoms_result], context=TestExecutionContext()
    )
    assert len(list(take_first_result.entities)) == random_size


def test_example_execution_with_dependencies() -> None:
    """Test execution of examples"""
    example_package = "example-pypi-package"
    pandas_package = "pandas"
    dependencies = f"{example_package},{pandas_package}"

    uninstall_package(example_package)
    uninstall_package(pandas_package)

    packages = [package["name"] for package in list_packages()]
    assert example_package not in packages
    assert pandas_package not in packages
    randoms = PythonCodeWorkflowPlugin(
        init_code=PythonCode(""),
        execute_code=PythonCode(examples_execute.randoms),
        dependencies=dependencies,
    )
    randoms.execute(inputs=[], context=TestExecutionContext())
    packages = [package["name"] for package in list_packages()]
    assert example_package in packages
    assert pandas_package in packages
    uninstall_package(example_package)
    uninstall_package(pandas_package)


def test_list_packages_action() -> None:
    """List packages action"""
    assert "cmem-plugin-base" in PythonCodeWorkflowPlugin(
        init_code=PythonCode(""), execute_code=PythonCode("")
    ).list_packages_action(context=TestPluginContext())


def test_validate_init_action() -> None:
    """Test Validate init action"""
    assert (
        "No input ports defined"
        in PythonCodeWorkflowPlugin(
            init_code=PythonCode(""),
            execute_code=PythonCode(""),
        ).validate_init_action()
    )
    assert (
        "FixedNumberOfInputs"
        in PythonCodeWorkflowPlugin(
            init_code=PythonCode(examples_init.no_input_ports),
            execute_code=PythonCode(""),
        ).validate_init_action()
    )
    assert (
        "FixedSchemaPort"
        in PythonCodeWorkflowPlugin(
            init_code=PythonCode(examples_init.fixed_output),
            execute_code=PythonCode(""),
        ).validate_init_action()
    )
    assert (
        "here"
        in PythonCodeWorkflowPlugin(
            init_code=PythonCode("data['testing'] = 'here'"),
            execute_code=PythonCode(""),
        ).validate_init_action()
    )


def test_validate_init_action_fail() -> None:
    """Test Validate init action fails"""
    with pytest.raises(SyntaxError, match=r"'\[' was never closed"):
        PythonCodeWorkflowPlugin(
            init_code=PythonCode("["),
            execute_code=PythonCode("["),
        ).validate_init_action()
    with pytest.raises(NameError, match="name 'not_here' is not defined"):
        PythonCodeWorkflowPlugin(
            init_code=PythonCode("not_here()"),
            execute_code=PythonCode("not_here()"),
        ).validate_init_action()
    with pytest.raises(ModuleNotFoundError, match="No module named 'not_here'"):
        PythonCodeWorkflowPlugin(
            init_code=PythonCode("from not_here import maybe"),
            execute_code=PythonCode("from not_here import maybe"),
        ).validate_init_action()


def test_validate_execute_action() -> None:
    """Test Validate execute action"""
    assert (
        "No result provided"
        in PythonCodeWorkflowPlugin(
            init_code=PythonCode(examples_init.no_input_ports),
            execute_code=PythonCode(""),
        ).validate_execute_action()
    )
    assert (
        "EntitySchema"
        in PythonCodeWorkflowPlugin(
            init_code=PythonCode(examples_init.no_input_ports),
            execute_code=PythonCode(examples_execute.randoms),
        ).validate_execute_action()
    )


def test_validate_execute_action_fail() -> None:
    """Test Validate execute action fails"""
    with pytest.raises(SyntaxError, match=r"'\[' was never closed"):
        PythonCodeWorkflowPlugin(
            init_code=PythonCode("["),
            execute_code=PythonCode("["),
        ).validate_execute_action()
    with pytest.raises(NameError, match="name 'not_here' is not defined"):
        PythonCodeWorkflowPlugin(
            init_code=PythonCode("not_here()"),
            execute_code=PythonCode("not_here()"),
        ).validate_execute_action()
    with pytest.raises(ModuleNotFoundError, match="No module named 'not_here'"):
        PythonCodeWorkflowPlugin(
            init_code=PythonCode("from not_here import maybe"),
            execute_code=PythonCode("from not_here import maybe"),
        ).validate_execute_action()


def test_install_missing_packages_action() -> None:
    """Test install_missing_packages_action action"""
    package_name = "example-pypi-package"
    uninstall_package(package_name)
    plugin = PythonCodeWorkflowPlugin(
        init_code=PythonCode(""), execute_code=PythonCode(""), dependencies=package_name
    )
    assert package_name not in plugin.list_packages_action(context=TestPluginContext())
    assert package_name in plugin.install_missing_packages_action(context=TestPluginContext())
    assert package_name in plugin.list_packages_action(context=TestPluginContext())
    assert f"Package already installed: {package_name}" in plugin.install_missing_packages_action(
        context=TestPluginContext()
    )
    uninstall_package(package_name)

    plugin = PythonCodeWorkflowPlugin(init_code=PythonCode(""), execute_code=PythonCode(""))
    assert "No packages installed" in plugin.install_missing_packages_action(
        context=TestPluginContext()
    )
