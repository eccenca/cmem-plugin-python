<!-- markdownlint-disable MD012 MD013 MD024 MD033 -->
# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/) and this project adheres to [Semantic Versioning](https://semver.org/)

## [Unreleased]

### Changed

- updated dependencies and template
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

