"""Plugin tests."""


from cmem_plugin_base.dataintegration.parameter.code import PythonCode

from cmem_plugin_python.transform.python_function import PythonTransform


def test_transform_execution_with_inputs():
    """Test with inputs"""
    source_code = PythonCode("""
result = len(inputs[0][0])
#from secrets import token_hex
#length = len(inputs[0][0])
#result = token_hex(length)
""")
    result = PythonTransform(source_code=source_code).transform(
        inputs=[["2000-05-22", "2021-12-12", "1904-02-29"]]
    )
    assert result == 10
