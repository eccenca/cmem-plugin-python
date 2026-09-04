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

documentation = """
This transform operator executes arbitrary Python source code inside of a transformation 😈

The code receives `inputs`, a `Sequence` of `Sequence[str]`: the outer sequence holds one entry
per operator connected to the input, the inner one the values that operator produced.
It has to assign a `Sequence[str]` to the variable `result`, which becomes the values this
operator passes on.
A run which leaves `result` undefined fails.

``` python
# uppercase every value which arrives on the first input
result = [value.upper() for value in inputs[0]]
```

Use it to prototype a conversion that none of the shipped operators covers, and turn the result
into a proper transform plugin once the code has settled.
To run Python on a whole workflow step rather than on single values, use the **Python Code**
workflow task, which can also declare ports and install packages.

## Caveats

The code is executed without a sandbox, in the process which runs the transformation and with the
permissions of that process.
Whoever may edit this operator may run whatever that process can run, so treat access to it
accordingly.

The scope of the code holds nothing but `inputs`.
There is no execution context, so the code can neither authenticate against the
eccenca Corporate Memory APIs nor write to the log of the running activity.

This operator installs nothing.
Imports have to resolve against the packages which are already installed in the deployment - the
**Python Code** workflow task is the place where packages are declared and installed.

The code is compiled and executed again on every call, so keep it cheap and avoid setup work
which would better be done once, outside of the transformation.
"""


@Plugin(
    label="Python Code",
    plugin_id="cmem_plugin_python-transform",
    description="Run arbitrary Python code as part of a transformation.",
    documentation=documentation,
    parameters=[
        PluginParameter(
            name="source_code",
            label="Source Code",
            description="Python code which turns the incoming values into the outgoing ones by"
            " assigning them to the variable 'result'.",
            default_value=EXAMPLE_CODE,
        ),
    ],
)
class PythonCodeTransformPlugin(TransformPlugin):
    """Python Code Transform Plugin"""

    def __init__(self, source_code: PythonCode):
        self.source_code = source_code

    def transform(self, inputs: Sequence[Sequence[str]]) -> Sequence[str]:
        """Transform a collection of values."""
        self.log.info("Start doing bad things with custom code.")
        scope: dict[str, Any] = {"inputs": inputs}
        exec(str(self.source_code), scope)  # nosec # noqa: S102
        result: Sequence[str] = scope["result"]
        return result
