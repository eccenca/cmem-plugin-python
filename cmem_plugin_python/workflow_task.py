"""Python code workflow plugin module"""

from collections.abc import Sequence
from types import SimpleNamespace
from typing import Any

from cmem_plugin_base.dataintegration.client import get_client
from cmem_plugin_base.dataintegration.context import ExecutionContext, PluginContext
from cmem_plugin_base.dataintegration.description import Icon, Plugin, PluginAction, PluginParameter
from cmem_plugin_base.dataintegration.entity import Entities
from cmem_plugin_base.dataintegration.parameter.code import PythonCode
from cmem_plugin_base.dataintegration.plugins import WorkflowPlugin

from cmem_plugin_python.package_management import (
    InstallationResult,
    format_installation_results,
    install_missing_packages,
)

docu_links = SimpleNamespace()
docu_links.entities = (
    "https://documentation.eccenca.com/latest/develop/python-plugins/development/#entities"
)
docu_links.context = (
    "https://documentation.eccenca.com/latest/develop/python-plugins/development/#context-objects"
)

examples_init = SimpleNamespace()
examples_init.no_input_ports = """# no input ports (empty list)
# e.g. if you fetch data from the web
from cmem_plugin_base.dataintegration import ports
input_ports = ports.FixedNumberOfInputs([])"""
examples_init.single_input_flexible = """# A single port with flexible schema
# e.g. to process everything that comes in
from cmem_plugin_base.dataintegration import ports
input_ports = ports.FixedNumberOfInputs(
    [ports.FlexibleSchemaPort()]
)"""
examples_init.single_input_fixed = """# A single port with a fixed schema
# e.g. to fetch data from a dataset
from cmem_plugin_base.dataintegration import ports, entity
my_schema = entity.EntitySchema(
    type_uri="urn:x-example:output",
    paths=[
        entity.EntityPath("name"),
        entity.EntityPath("description")
    ]
)
input_ports = ports.FixedNumberOfInputs(
    [ports.FixedSchemaPort(schema=my_schema)]
)"""
examples_init.no_output = """# no output port
# e.g. if you post data to the web
output_port = None"""
examples_init.fixed_output = """# An output port with a fixed schema
from cmem_plugin_base.dataintegration import ports, entity
my_schema = entity.EntitySchema(
    type_uri="urn:x-example:output",
    paths=[
        entity.EntityPath("name"),
        entity.EntityPath("description")
    ]
)
output_port = ports.FixedSchemaPort(schema=my_schema)"""

examples_init.test_inputs = """# entities used by the "Validate execution phase" action
from cmem_plugin_base.dataintegration import entity
test_inputs = [
    entity.Entities(
        entities=[
            entity.Entity(uri="urn:uuid:test", values=[["Example"], ["A test entity"]])
        ],
        schema=entity.EntitySchema(
            type_uri="urn:x-example:output",
            paths=[
                entity.EntityPath("name"),
                entity.EntityPath("description")
            ]
        )
    )
]"""

examples_execute = SimpleNamespace()
examples_execute.take_first = """# take the entities from the first input port
# and copy it to the output port
try:
    result = inputs[0]
except IndexError:
    raise ValueError("Please connect a task to the first input port.")
"""
examples_execute.randoms = """# Create 1000 random strings and output them with a custom schema
from uuid import uuid4
from secrets import token_hex
from cmem_plugin_base.dataintegration import entity
my_schema = entity.EntitySchema(
    type_uri="urn:x-example:random",
    paths=[entity.EntityPath("random")]
)
entities = []
for _ in range(1000):
    entity_uri = "urn:uuid:" + str(uuid4())
    values = [[token_hex(10)]]
    entities.append(
        entity.Entity(uri=entity_uri, values=values)
    )
result = entity.Entities(entities=entities, schema=my_schema)
"""

cmem_full = "eccenca Corporate Memory"
cmem = "Corporate Memory"
documentation = f"""
This workflow task executes arbitrary Python source code as a step of a workflow 😈

The code lives on the task itself and is split into two phases: initialization code, which runs
whenever the task is loaded and determines the shape of the task, and execution code, which runs
when the workflow reaches the task.

Everything that flows through the task is decided by that code. The initialization code declares
which input ports the task offers and whether it provides an output port at all; the execution
code receives the entities that arrived on those ports and prepares the entities handed to the
next task. Without an explicit declaration, the task accepts a flexible number of flexible schema
inputs and provides a flexible schema output.

Use it to prototype a step that no shipped task covers, and turn the result into a proper plugin
once the code has settled. To run Python on single values inside a transformation instead of on a
whole workflow step, use the **Python Code** transform operator.

## <a id="parameter_doc_init_code">Initialization</a>

The initialization code is optional.
It is used to configure the input and output ports of the task as well as to
prepare data for the execution phase.
Note that the execution scope of this code is empty.
All used objects need to be imported first.

### Specify input ports

To specify input ports, you have to define the variable `input_ports`.
Here are some valid examples.
If you do not specify any input ports, the default
behavior is a flexible number of flexible schema input ports.

``` python
{examples_init.no_input_ports}
```

``` python
{examples_init.single_input_flexible}
```

``` python
{examples_init.single_input_fixed}
```

### Specify the output port

To specify the output port, you have to define the variable `output_port`.
Here are some valid examples.
If you do not specify the output port, the default behavior is a flexible schema output port.

``` python
{examples_init.no_output}
```

``` python
{examples_init.fixed_output}
```

### Additional Data

In addition to input and output port specifications, you can provide additional data for
the task execution phase by manipulating the `data` dictionary.

``` python
data["my_schema"] = my_schema  # in case you used a schema example above
data["output"] = ":-)"
```

### Test input

The **Validate execution phase** action has no workflow around it and therefore no incoming
entities of its own.
It uses whatever the initialization code leaves in the variable `test_inputs`, a `Sequence` of
`Entities`, and runs with no inputs at all when that variable is not defined.

``` python
{examples_init.test_inputs}
```

## <a id="parameter_doc_execute_code">Execution</a>

The execution code is interpreted in the context of an executed workflow.
The following variables are available in the scope of the code execution:

- `inputs` - a `Sequence` of `Entities`, which represents the data which will be passed to
   the task in the workflow. Have a look at [the entities documentation]({docu_links.entities})
   for more information.
- `context` - an `ExecutionContext` object, which holds information about the system,
   the user the current task, and more. Have a look at
   [the context object documentation]({docu_links.context}) for more information.
- `data` - a `dict` of arbitrary data, which was optionally added by the initialization code.

To provide data for the next workflow task in the workflow, a `result`
variable of type `Entities` needs to be prepared.
A task which does not prepare a `result` hands nothing on to the next task.

Here are some valid examples:

``` python
{examples_execute.take_first}
```

``` python
{examples_execute.randoms}
```

### Using {cmem_full} APIs

To access {cmem} APIs, build a client from the execution context:

``` python
from cmem_plugin_base.dataintegration.client import get_client
client = get_client(context)
```

The client takes its connection URLs from the deployment the workflow runs in and authenticates
every request as the user who started the workflow.
What it offers is documented with
[cmem-client](https://pypi.org/project/cmem-client/), which is installed alongside
`cmem-plugin-base`.

## Caveats

The code is executed without a sandbox, in the process which runs the workflow and with the
permissions of that process.
Whoever may edit this task may run whatever that process can run, so treat access to it
accordingly.

The initialization code runs every time the task is loaded, not only when it is saved: before
each workflow run and before each of the actions above.
Code with side effects therefore runs far more often than expected, and an error in it makes the
whole task unusable rather than only failing a single run.

**Validate execution phase** runs the execution code outside of a workflow.
There is no execution context in that scope - `context` is `None` - and the action reports at
most the first ten entities of the result.
Code which uses `context` unconditionally fails there while working in a real run.

Neither validation action installs dependencies.
Packages are installed by the workflow run itself and by the **Install missing dependencies**
action, so validate code which imports them only after installing.

## <a id="parameter_doc_dependencies">Dependencies</a>

Dependencies are matched by package name only.
A package which is already installed is left at the version which is there, and a version
specifier is not understood and leads to a fresh installation attempt on every run.

An installation which fails stops the task before the execution code runs at all, because the
deployment rejects the request and the error is not caught.
A misspelled dependency therefore fails the workflow run rather than the import, and the
**Install missing dependencies** action reports the error instead of its per package output.
"""


@Plugin(
    label="Python Code",
    icon=Icon(file_name="python_icon.svg", package=__package__),
    plugin_id="cmem_plugin_python-workflow",
    description="Run arbitrary Python code as a workflow task.",
    documentation=documentation,
    actions=[
        PluginAction(
            name="validate_init_action",
            label="Validate initialization phase",
            description="Run the initialization code and report the ports and data it declares.",
        ),
        PluginAction(
            name="validate_execute_action",
            label="Validate execution phase",
            description="Run the execution code outside of a workflow and report what it returns.",
        ),
        PluginAction(
            name="list_packages_action",
            label="List packages",
            description="List the Python packages installed in the deployment, with versions.",
        ),
        PluginAction(
            name="install_missing_packages_action",
            label="Install missing dependencies",
            description="Install the declared dependencies which are not installed yet.",
        ),
    ],
    parameters=[
        PluginParameter(
            name="init_code",
            label="Initialization Code",
            description="Python code which shapes the task and runs whenever the task is loaded."
            " Leaving it empty keeps the default ports.",
            default_value="",
        ),
        PluginParameter(
            name="execute_code",
            label="Execution Code",
            description="Python code which runs when the workflow reaches this task.",
            default_value="",
        ),
        PluginParameter(
            name="dependencies",
            label="Dependencies",
            description="Comma-separated package names which are installed into the deployment"
            " before the execution code runs, e.g. 'pandas, requests'. Version specifiers are"
            " not supported.",
            default_value="",
        ),
    ],
)
class PythonCodeWorkflowPlugin(WorkflowPlugin):
    """Python Code Workflow Plugin"""

    init_code: str
    execute_code: str
    data: dict
    dependencies: list[str]

    def __init__(self, init_code: PythonCode, execute_code: PythonCode, dependencies: str = ""):
        self.init_code = str(init_code)
        self.execute_code = str(execute_code)
        self.dependencies = (
            [] if dependencies.strip() == "" else [_.strip() for _ in dependencies.split(",")]
        )
        scope = self.do_init()
        if "input_ports" in scope:
            self.input_ports = scope["input_ports"]
        if "output_port" in scope:
            self.output_port = scope["output_port"]
        self.data = scope.get("data", {})

    def do_init(self) -> dict[str, Any]:
        """Run initialization phase"""
        scope: dict[str, Any] = {"data": {}}
        exec(str(self.init_code), scope)  # nosec  # noqa: S102
        return scope

    def validate_init_action(self) -> str:
        """Run the init code and report results."""
        scope = self.do_init()

        output = "# Input ports definition (`input_ports`)\n"
        if "input_ports" in scope:
            output += "``` python\n"
            output += f"{scope['input_ports']!r}\n"
            output += "```\n"
        else:
            output += "No input ports defined.\n"

        output += "# Output port definition (`output_port`)\n"
        if "output_port" in scope:
            output += "``` python\n"
            output += f"{scope['output_port']!r}\n"
            output += "```\n"
        else:
            output += "No output port defined.\n"

        output += "# Data for the execution phase (`data`)\n"
        if scope["data"]:
            for key, value in scope["data"].items():
                output += f"## `{key}`\n"
                output += "``` python\n"
                output += f"{value!r}\n"
                output += "```\n"
        else:
            output += "No data provided.\n"
        return output

    def do_execute(
        self, inputs: Sequence[Entities], context: ExecutionContext | None, data: dict
    ) -> dict[str, Any]:
        """Run execution phase"""
        scope: dict[str, Any] = {"inputs": inputs, "context": context, "data": data}
        exec(str(self.execute_code), scope)  # nosec  # noqa: S102
        return scope

    def validate_execute_action(self) -> str:
        """Run the execute code and report results."""
        init_scope = self.do_init()
        test_inputs = init_scope.get("test_inputs", [])
        # the data of the fresh init scope, not self.data: the constructor's dict is mutated by
        # every run of the execution code, so re-using it accumulates across action calls
        scope = self.do_execute(test_inputs, None, init_scope.get("data", {}))
        result: Entities | None = scope.get("result")
        if result is not None:
            output = "# Schema\n"
            output += "``` python\n"
            output += f"{result.schema!r}\n"
            output += "```\n"
            output += "# Entities (max. 10)\n"
            for entity in list(result.entities)[:10]:
                output += "``` python\n"
                output += f"{entity.values!r}\n"
                output += "```\n"
        else:
            output = "No result provided.\n"
        return output

    def list_packages_action(self, context: PluginContext) -> str:
        """List Packages action"""
        packages = get_client(context).python_packages
        output = [f"- {name} ({package.version})" for name, package in packages.items()]
        return "\n".join(output)

    def install_missing_packages_action(self, context: PluginContext) -> str:
        """Install Missing Packages action"""
        results = install_missing_packages(
            package_specs=self.dependencies, client=get_client(context)
        )
        return format_installation_results(results)

    def log_installation_results(self, results: dict[str, InstallationResult]) -> None:
        """Log what the installation of the declared dependencies reported.

        An installation which answers with an error does not raise, so without this the
        code fails later at the import with nothing in the log to explain why.
        """
        for package, result in results.items():
            if not result.success:
                self.log.error(f"Installation of {package} failed: {result.output}")
            elif result.plugin_errors:
                self.log.warning(
                    f"Package {package} was installed, but plugins failed to register:"
                    f" {', '.join(result.plugin_errors)}"
                )

    def execute(self, inputs: Sequence[Entities], context: ExecutionContext) -> Entities | None:
        """Start the plugin in workflow context."""
        self.log.info("Start doing bad things with custom code.")
        if self.dependencies:
            self.log_installation_results(
                install_missing_packages(
                    package_specs=self.dependencies, client=get_client(context)
                )
            )
        scope = self.do_execute(inputs, context, self.data)
        return scope.get("result")
