"""Plugin tests."""

from cmem_plugin_base.dataintegration.parameter.code import PythonCode

from cmem_plugin_python.test_transform_operator import (
    EXAMPLE_CODE,
    EXAMPLE_UPPERCASE,
    PythonCodeTransformPlugin,
)


def transform(source_code: str, inputs: list[list[str]]) -> list[str]:
    """Run the operator over the given inputs"""
    plugin = PythonCodeTransformPlugin(source_code=PythonCode(source_code))
    return list(plugin.transform(inputs=inputs))


def test_transform_execution_with_inputs() -> None:
    """Test with inputs"""
    assert transform("result = [str(len(value)) for value in inputs[0]]", [["abcdef", "xy"]]) == [
        "6",
        "2",
    ]


def test_default_source_code() -> None:
    """Test that the shipped default hands the incoming values on one by one"""
    assert transform(EXAMPLE_CODE, [["a", "b"]]) == ["a", "b"]


def test_documented_example() -> None:
    """Test the example shown in the task documentation"""
    assert transform(EXAMPLE_UPPERCASE, [["a", "b"]]) == ["A", "B"]


def test_several_inputs() -> None:
    """Test that every connected input arrives as its own sequence"""
    assert transform(
        "result = [value for values in inputs for value in values]", [["a"], ["b"]]
    ) == [
        "a",
        "b",
    ]


def test_empty_input() -> None:
    """Test that an input without values yields no values"""
    assert transform(EXAMPLE_CODE, [[]]) == []
