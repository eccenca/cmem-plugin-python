"""Python code transform plugin module"""
from collections.abc import Sequence
from typing import Any

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
        PluginParameter(name="source_code", label="Source Code", default_value=EXAMPLE_CODE),
    ],
)
class PythonCodeTransformPlugin(TransformPlugin):
    """Python Code Transform Plugin"""

    def __init__(self, source_code: PythonCode):
        self.source_code = source_code

    def transform(self, inputs: Sequence[Sequence[str]]) -> Sequence[str]:
        """Transform a collection of values."""
        # pylint: disable=exec-used
        self.log.info("Start doing bad things with custom code.")
        scope: dict[str, Any] = {"inputs": inputs}
        exec(str(self.source_code), scope)  # nosec  # noqa: S102
        result: Sequence[str] = scope["result"]
        return result
