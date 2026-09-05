"""Plugin tests."""

from typing import TYPE_CHECKING

import pytest
from cmem_client.client import Client
from cmem_plugin_base.dataintegration.parameter.code import PythonCode
from cmem_plugin_base.testing import TestExecutionContext, TestPluginContext

from cmem_plugin_python.package_management import InstallationResult
from cmem_plugin_python.workflow_task import (
    PythonCodeWorkflowPlugin,
    examples_execute,
    examples_init,
)
from tests.utils import needs_cmem

if TYPE_CHECKING:
    from cmem_plugin_base.dataintegration.entity import Entities


@needs_cmem
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


@needs_cmem
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


@needs_cmem
def test_example_execution_with_dependencies(uninstalled_package: str) -> None:
    """Test execution of examples with declared dependencies"""
    # the second dependency is a package the deployment has anyway, which covers the
    # already installed branch without taking a package away from other users
    installed_package = "cmem-plugin-base"
    packages = Client.from_env().python_packages
    assert uninstalled_package not in packages
    assert installed_package in packages

    randoms = PythonCodeWorkflowPlugin(
        init_code=PythonCode(""),
        execute_code=PythonCode(examples_execute.randoms),
        dependencies=f"{uninstalled_package},{installed_package}",
    )
    randoms.execute(inputs=[], context=TestExecutionContext())

    packages = Client.from_env().python_packages
    assert uninstalled_package in packages
    assert installed_package in packages


@needs_cmem
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


def test_validate_execute_action_with_none_result() -> None:
    """Test Validate execute action with an explicit result of None"""
    assert (
        "No result provided"
        in PythonCodeWorkflowPlugin(
            init_code=PythonCode(""),
            execute_code=PythonCode("result = None"),
        ).validate_execute_action()
    )


def test_validate_execute_action_resets_data() -> None:
    """Test that the action starts from the data of a fresh initialization run"""
    counting_code = PythonCode(
        """from cmem_plugin_base.dataintegration import entity
data["count"] += 1
result = entity.Entities(
    entities=[entity.Entity(uri="urn:x-example:run", values=[[str(data["count"])]])],
    schema=entity.EntitySchema(
        type_uri="urn:x-example:count", paths=[entity.EntityPath("count")]
    ),
)"""
    )
    plugin = PythonCodeWorkflowPlugin(
        init_code=PythonCode('data["count"] = 0'), execute_code=counting_code
    )
    for _ in range(3):
        assert "['1']" in plugin.validate_execute_action()


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


@needs_cmem
def test_install_missing_packages_action(uninstalled_package: str) -> None:
    """Test install_missing_packages_action action"""
    package_name = uninstalled_package
    plugin = PythonCodeWorkflowPlugin(
        init_code=PythonCode(""), execute_code=PythonCode(""), dependencies=package_name
    )
    assert package_name not in plugin.list_packages_action(context=TestPluginContext())
    assert package_name in plugin.install_missing_packages_action(context=TestPluginContext())
    assert package_name in plugin.list_packages_action(context=TestPluginContext())
    assert f"Package already installed: {package_name}" in plugin.install_missing_packages_action(
        context=TestPluginContext()
    )

    plugin = PythonCodeWorkflowPlugin(init_code=PythonCode(""), execute_code=PythonCode(""))
    assert "No packages installed" in plugin.install_missing_packages_action(
        context=TestPluginContext()
    )


def test_log_installation_results(caplog: pytest.LogCaptureFixture) -> None:
    """Test that a failed installation and failing plugins reach the log"""
    plugin = PythonCodeWorkflowPlugin(init_code=PythonCode(""), execute_code=PythonCode(""))
    plugin.log_installation_results(
        {
            "broken-package": InstallationResult(
                success=False, output="no matching distribution", forbidden=False
            ),
            "unregistered-package": InstallationResult(
                success=True,
                output="Installed 1 package",
                forbidden=False,
                plugin_errors=["MyPlugin: boom"],
            ),
            "fine-package": InstallationResult(success=True, output="", forbidden=False),
        }
    )
    assert "Installation of broken-package failed: no matching distribution" in caplog.text
    assert "unregistered-package was installed, but plugins failed to register" in caplog.text
    assert "fine-package" not in caplog.text
