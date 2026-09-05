"""Markers and helpers shared by the tests"""

import os

import pytest

needs_cmem = pytest.mark.skipif(
    os.environ.get("CMEM_BASE_URI", "") == "",
    reason="Needs eccenca Corporate Memory configuration",
)
"""Skip a test that needs an eccenca Corporate Memory deployment.

Skipping rather than failing is what keeps the suite green in a pipeline
without secrets, and lets a contributor run `task check` on a fresh clone.

Any test constructing TestExecutionContext or TestPluginContext needs this,
even when the plugin itself never calls Corporate Memory: those contexts build
a TestUserContext, which fetches a real OAuth token on construction.
"""
