# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Read this alongside `.claude/rules/`, which carries the conventions this project
shares with every other plugin generated from the template. What follows is
what is specific to this one.

## What this package is

Two plugins, both of which `exec()` code that a user typed into a task
parameter. That is the product, not an implementation detail: there is no
sandbox, the code runs in the DataIntegration process, and the plugin's own
logic is only the scaffolding around `exec()`.

- `cmem_plugin_python/workflow_task.py` - `PythonCodeWorkflowPlugin`, plugin id
  `cmem_plugin_python-workflow`.
- `cmem_plugin_python/test_transform_operator.py` - `PythonCodeTransformPlugin`,
  plugin id `cmem_plugin_python-transform`. **The `test_` prefix is misleading:
  this is shipped production code**, not a test module.
- `cmem_plugin_python/package_management.py` - `install_missing_packages()`,
  shared by the workflow task's `execute()` and its *Install missing
  dependencies* action.

## The two-phase model of the workflow task

Everything about that task follows from it, and most surprises come from
forgetting the first phase exists.

**Initialization code** runs in `__init__` via `do_init()`, so it runs every
time the task is *loaded* - before each workflow run and before each action,
not only when the task is saved. Its scope starts empty except for `data`, and
what it leaves behind shapes the task: `input_ports`, `output_port`, and
entries in `data` handed to the execution phase. An error here makes the whole
task unusable rather than failing a single run.

**Execution code** runs in `do_execute()` with `inputs`, `context` and `data`
in scope, and hands on whatever it assigns to `result`. Note that
`validate_execute_action` calls it with `context=None` and with
`test_inputs` from the init scope, so code touching `context`
unconditionally works in a workflow and fails in that action.

Neither phase is wrapped in error handling. Exceptions propagate to
DataIntegration, which is deliberate - see the `Caveats` section of the
`documentation` string.

## The documentation string is executable

`workflow_task.py` builds its `documentation` from the `examples_init` and
`examples_execute` `SimpleNamespace` objects, and `tests/test_workflow_task.py`
iterates `vars(examples_init)` and runs every one of them. Adding an example to
the user-facing documentation therefore adds a test case, and breaking one
breaks the suite. Keep new examples runnable against a plain deployment.

## Tests need a deployment

Most of the suite does. `tests/utils.py` defines the `needs_cmem` marker and
the tests which construct `Client.from_env()`, `TestExecutionContext` or
`TestPluginContext` carry it, so a clone without a populated `.env` skips them
instead of erroring. `tests/test_transform.py` and the tests which only exec
initialization code need no deployment and stay unmarked.

The suite also **changes the deployment**: it installs and uninstalls
`example-pypi-package` and `pandas`. The `uninstalled_package` fixture in
`tests/test_package_management.py` removes the package before *and* after the
test so a failing run cannot leave it behind - reuse that pattern rather than
uninstalling inline.

Neither project export under `tests/fixtures/` is used by pytest. They are
imported by hand:
`cmem-plugin-python-testing.project.zip` is the manual validation project
described in `README.md` and is the only thing that exercises port negotiation,
dependency installation and the transform operator inside a real workflow;
`cmem_plugin_python_testing.project.zip` (underscores) is an unreferenced CSV
demo from 2023.

## Commands

```sh
task                       # list all tasks
task check                 # ruff, mypy, deptry, trivy, pytest - the CI suite
task format:fix            # ruff format + safe autofixes
poetry run pytest tests/test_workflow_task.py::test_validate_init_action  # one test
task install               # build + cmemc admin workspace python install (ask first)
task uninstall             # remove the plugin from the deployment (ask first)
```

`install` and `uninstall` come from `.tasks-plugin.yml` and act on the
deployment configured in `.env`.

## Lint

`ruff` runs with `select = ["ALL"]`. The three `exec()` calls - two in
`workflow_task.py`, one in `test_transform_operator.py` - carry
`# nosec  # noqa: S102`, which is the one sanctioned suppression in this
package: the rule forbids exactly what the plugin exists to do. Do not add
further `noqa` comments or extend the `ignore` list to make a check pass.
