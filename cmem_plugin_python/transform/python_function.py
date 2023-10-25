"""Python function transform plugin module"""
from typing import Sequence

from cmem_plugin_base.dataintegration.description import (
    Plugin,
    PluginParameter,
)
from cmem_plugin_base.dataintegration.parameter.code import PythonCode
from cmem_plugin_base.dataintegration.plugins import TransformPlugin

EXAMPLE_CODE = """result = str(inputs) """


@Plugin(
    label="Python Code",
    plugin_id="cmem_plugin_python-transform",
    parameters=[
        PluginParameter(
            name="source_code",
            label="Source Code",
        ),
    ],
)
class PythonTransform(TransformPlugin):
    """Python Function Plugin"""

    def __init__(
            self,
            source_code: PythonCode = PythonCode(EXAMPLE_CODE)
    ):
        self.source_code = source_code

    def transform(self, inputs: Sequence[Sequence[str]]):
        # pylint: disable=exec-used
        scope = {
            "inputs": inputs
        }
        exec(  # nosec
            str(self.source_code),
            scope
        )
        return scope["result"]
