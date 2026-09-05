<!-- markdownlint-disable MD012 MD013 MD024 MD033 -->
# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/) and this project adheres to [Semantic Versioning](https://semver.org/)

## [Unreleased]

### Changed

- updated dependencies and template
  - **breaking:** the package now requires Python 3.13, up from 3.11, so it no longer
    installs into a deployment which runs an older interpreter
- renamed the labels a user sees: the code parameters are now **Initialization Code** and
  **Execution Code** rather than a sentence each, and the action is **List packages**
- the shipped default of the transform operator hands the incoming values on unchanged,
  instead of assigning a single string, which DataIntegration passed on as one value per
  character
- reworked the user facing documentation of both tasks
  - Python Code workflow task: describes the ports, the `test_inputs` variable of the
    **Validate execution phase** action, and the caveats around sandboxing, repeated
    initialization and dependency installation
  - Python Code transform operator: added a task description, a working example and the
    caveats around scope, packages and repeated execution
  - added descriptions to the initialization code, execution code and source code parameters
  - the documented way to reach the Corporate Memory APIs is now `get_client` instead of the
    deprecated `setup_cmempy_user_access`
  - fixed the stale link to the context object documentation
- the plugin talks to the deployment through `cmem-client` only - the deprecated
  `cmem-cmempy` dependency and all `setup_cmempy_user_access` calls are gone
  - **breaking:** `setup_cmempy_user_access` also set `OAUTH_GRANT_TYPE` and
    `OAUTH_ACCESS_TOKEN` in the environment of the whole process, which task code
    calling `cmem.cmempy.*` could rely on without setting up access itself. That side
    effect is gone, so such code now has to authenticate on its own - the documented
    way is `get_client(context)`

### Fixed

- the **Install missing dependencies** action reports the installed version of an
  already installed package instead of repeating its name
- the **Validate execution phase** action no longer fails with an `AttributeError`
  when the execution code assigns `result = None`, which is the documented way of
  handing nothing to the next task
- the **Validate execution phase** action starts from the `data` its initialization
  code builds, instead of carrying the mutations of earlier action runs
- the documented behavior of a failed dependency installation: it stops the task
  before the execution code runs, rather than letting the import fail later
- an installation which reports an error is logged, and plugins which fail to register
  after it are logged and shown by the **Install missing dependencies** action, instead
  of being discarded so that only the later import error was visible
- the **Dependencies** and **Source Code** parameters link to their documentation, which
  the missing anchors kept out of reach
- the documentation of the transform operator no longer claims the code scope holds
  nothing but `inputs`: it holds the Python builtins as well
- an already installed package whose version the deployment does not report is no longer
  announced as `(None)`

## [1.2.1] 2025-09-18

### Fixed

- cmem-plugin-base dependency specification


## [1.2.0] 2025-05-12 - Yanked

### Added

- Python Code Workflow Task
  - Custom Action: Validate initialization phase - run the init code and report results
  - Custom Action: Validate execution phase - run the execute code and report results
  - Custom Action: List Packages - Show installed python packages with version
  - Custom Action: Install Missing Dependencies - Install missing dependency packages
  - Parameter: Dependencies - Comma-separated list of package names


## [1.1.0] 2024-12-05

### Added

- more documentation

### Fixed

- example code highlightning in documentation


## [1.0.1] 2023-12-11

### Fixed

- change log


## [1.0.0] 2023-12-11

### Added

- initial version with transform and workflow plugin

