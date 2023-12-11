"""Python code workflow plugin module"""
from collections.abc import Sequence

from cmem_plugin_base.dataintegration.context import ExecutionContext
from cmem_plugin_base.dataintegration.description import Icon, Plugin, PluginParameter
from cmem_plugin_base.dataintegration.entity import Entities
from cmem_plugin_base.dataintegration.parameter.code import PythonCode
from cmem_plugin_base.dataintegration.plugins import WorkflowPlugin


@Plugin(
    label="Python Code",
    icon=Icon(file_name="custom.svg", package=__package__),
    plugin_id="cmem_plugin_python-workflow",
    parameters=[
        PluginParameter(
            name="init_code",
            label="Source Code (Initialization)",
        ),
        PluginParameter(
            name="execute_code",
            label="Source Code (Execution)",
        ),
    ],
)
class PythonCodeWorkflowPlugin(WorkflowPlugin):
    """Python Code Workflow Plugin"""

    example_init = """result = str(inputs) """
    example_execute = """result = str(inputs) """

    def __init__(self, init_code: PythonCode, execute_code: PythonCode):
        self.init_code = str(init_code)
        self.execute_code = str(execute_code)
        scope: dict = {}
        exec(str(self.init_code), scope)  # nosec  # noqa: S102
        for _ in scope:
            setattr(self, _, scope[_])

    def execute(self, inputs: Sequence[Entities], context: ExecutionContext) -> Entities | None:
        """Start the plugin in workflow context."""
        self.log.info("Start doing bad things with custom code.")
        scope = {"inputs": inputs, "context": context}
        exec(str(self.execute_code), scope)  # nosec  # noqa: S102
        try:
            entities = scope["entities"]
        except KeyError as error:
            raise ValueError(
                "Python execution code needs to prepare a variable 'entities'"
                " of type 'Iterator[cmem_plugin_base.dataintegration.entity.Entity]'."
            ) from error
        try:
            schema = scope["schema"]
        except KeyError as error:
            raise ValueError(
                "Python execution code needs to prepare a variable 'schema'"
                " of type 'cmem_plugin_base.dataintegration.entity.EntitySchema'."
            ) from error
        return Entities(entities=entities, schema=schema)
