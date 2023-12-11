"""Plugin tests."""
from typing import TYPE_CHECKING

import pytest
from cmem_plugin_base.dataintegration.parameter.code import PythonCode

from cmem_plugin_python.workflow import PythonCodeWorkflowPlugin, examples_execute, examples_init
from tests.utils import TestExecutionContext

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
