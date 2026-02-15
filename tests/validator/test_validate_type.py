from typing import Any

import pytest

from dj_typed_settings.validator import validate_type


def test_validate_type_basic():
    validate_type(1, int, "field")
    validate_type("string", str, "field")
    validate_type(True, bool, "field")

    with pytest.raises(ValueError):
        validate_type("1", int, "field")

    with pytest.raises(ValueError):
        validate_type(1, str, "field")


def test_validate_type_list():
    validate_type(["a", "b"], list[str], "field")
    validate_type([], list, "field")

    with pytest.raises(ValueError):
        validate_type("not a list", list[str], "field")


def test_validate_type_dict():
    validate_type({"a": 1}, dict[str, int], "field")
    validate_type({}, dict, "field")

    with pytest.raises(ValueError):
        validate_type("not a dict", dict[str, int], "field")


def test_validate_type_union_optional():
    validate_type(1, int | str, "field")
    validate_type("123", int | str, "field")
    validate_type(None, int | None, "field")
    validate_type(1, int | None, "field")

    # Now "s" invalid because str | int implies numeric string
    with pytest.raises(ValueError) as exc:
        validate_type("s", int | str, "field")
    assert "must be a valid integer string" in str(exc.value)

    with pytest.raises(ValueError) as exc:
        validate_type(1.5, int | str, "field")
    assert "If 'field' is specified, it must be a int or str, but got float" in str(exc.value)

    with pytest.raises(ValueError) as exc:
        validate_type("s", int | None, "field")
    assert "If 'field' is specified, it must be a int, but got str" in str(exc.value)


def test_validate_type_any():
    validate_type(1, Any, "field")
    validate_type("s", Any, "field")
    validate_type(None, Any, "field")


def test_validate_type_list_tuple_union():
    """Test that list | tuple union type accepts both lists and tuples."""
    # Both should be accepted
    validate_type([], list | tuple, "field")
    validate_type((), list | tuple, "field")
    validate_type(["a", "b"], list | tuple, "field")
    validate_type(("a", "b"), list | tuple, "field")

    # Should reject other types
    with pytest.raises(ValueError):
        validate_type("not a list or tuple", list | tuple, "field")

    with pytest.raises(ValueError):
        validate_type(123, list | tuple, "field")


def test_validate_type_tuple_list_union():
    """Test that tuple | list union type accepts both tuples and lists."""
    # Both should be accepted
    validate_type([], tuple | list, "field")
    validate_type((), tuple | list, "field")
    validate_type(["a", "b"], tuple | list, "field")
    validate_type(("a", "b"), tuple | list, "field")

    # Should reject other types
    with pytest.raises(ValueError):
        validate_type("not a tuple or list", tuple | list, "field")


def test_validate_str_int_union_checks_digits():
    """
    Test that a Union[str, int] (or str | int) enforces that if the value is a string,
    it must be a digit string (or empty), not arbitrary text.
    Relevant for PORT settings.
    """
    # Valid cases
    validate_type(123, str | int, "field")
    validate_type("123", str | int, "field")
    validate_type("", str | int, "field")  # Empty string allowed (e.g. default port)

    # Invalid case: arbitrary string
    with pytest.raises(ValueError) as exc:
        validate_type("invalid_port", str | int, "field")
    assert "field" in str(exc.value)
    assert "must be a valid integer string" in str(exc.value)
