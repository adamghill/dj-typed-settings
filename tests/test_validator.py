from dataclasses import dataclass
from typing import Any

import pytest

from dj_typed_settings.validator import validate_data_against_schema, validate_type


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
    validate_type("s", int | str, "field")
    validate_type(None, int | None, "field")
    validate_type(1, int | None, "field")

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


@dataclass
class SimpleSchema:
    name: str
    age: int
    tags: list[str]
    meta: dict[str, Any] | None = None


def test_validate_data_against_schema_valid():
    data = {
        "name": "Test",
        "age": 10,
        "tags": ["one", "two"],
        "meta": {"key": "value"},
    }
    # Should not raise
    validate_data_against_schema(data, SimpleSchema)


def test_validate_data_against_schema_valid_optional_missing():
    data = {
        "name": "Test",
        "age": 10,
        "tags": [],
    }
    # Should not raise, meta is optional
    validate_data_against_schema(data, SimpleSchema)


def test_validate_data_against_schema_missing_required():
    data = {
        "name": "Test",
        # age missing
        "tags": [],
    }
    with pytest.raises(ValueError) as exc:
        validate_data_against_schema(data, SimpleSchema)
    assert "Missing required setting: age" in str(exc.value)


def test_validate_data_against_schema_invalid_type():
    data = {
        "name": "Test",
        "age": "wrong",
        "tags": [],
    }
    with pytest.raises(ValueError) as exc:
        validate_data_against_schema(data, SimpleSchema)
    assert "'age' must be int, got str" in str(exc.value)


def test_validate_data_against_schema_ignore_errors():
    data = {
        "name": "Test",
        "age": "wrong",  # Would fail validation
        "tags": [],
    }
    # Should not raise if we ignore 'age'
    validate_data_against_schema(data, SimpleSchema, ignore_errors=["age"])


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


@dataclass
class SchemaWithUnionTypes:
    """Schema to test list/tuple union types similar to Django settings."""

    staticfiles_finders: list | tuple
    installed_apps: list[str] | tuple[str, ...]
    middleware: list[str] | tuple[str, ...]


def test_validate_schema_with_list_tuple_unions():
    """Test that schema validation accepts both lists and tuples for union types."""
    # Test with lists
    data_with_lists = {
        "staticfiles_finders": [
            "django.contrib.staticfiles.finders.FileSystemFinder",
            "django.contrib.staticfiles.finders.AppDirectoriesFinder",
        ],
        "installed_apps": ["django.contrib.admin", "django.contrib.auth"],
        "middleware": ["django.middleware.security.SecurityMiddleware"],
    }
    validate_data_against_schema(data_with_lists, SchemaWithUnionTypes)

    # Test with tuples (this is what Django often uses in global_settings.py)
    data_with_tuples = {
        "staticfiles_finders": (
            "django.contrib.staticfiles.finders.FileSystemFinder",
            "django.contrib.staticfiles.finders.AppDirectoriesFinder",
        ),
        "installed_apps": ("django.contrib.admin", "django.contrib.auth"),
        "middleware": ("django.middleware.security.SecurityMiddleware",),
    }
    validate_data_against_schema(data_with_tuples, SchemaWithUnionTypes)

    # Test with mixed (should also work)
    data_mixed = {
        "staticfiles_finders": [  # list
            "django.contrib.staticfiles.finders.FileSystemFinder",
        ],
        "installed_apps": ("django.contrib.admin",),  # tuple
        "middleware": [],  # empty list
    }
    validate_data_against_schema(data_mixed, SchemaWithUnionTypes)
