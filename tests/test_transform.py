"""Plugin tests."""

from cmem_plugin_base.dataintegration.parameter.code import PythonCode

from cmem_plugin_python.test_transform_operator import PythonCodeTransformPlugin


def test_transform_execution_with_inputs() -> None:
    """Test with inputs"""
    source_code = PythonCode("result = len(inputs[0][0])")
    source_value = "abcdef"
    result = PythonCodeTransformPlugin(source_code=source_code).transform(inputs=[[source_value]])
    assert result == len(source_value)
