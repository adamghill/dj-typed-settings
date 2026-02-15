from dataclasses import dataclass
from typing import Any

import pytest

from dj_typed_settings.schema import BaseSchema
from dj_typed_settings.validator import validate_data_against_schema


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
    validate_data_against_schema(data_mixed, SchemaWithUnionTypes)


def test_validate_nested_schema_object():
    """
    Test validation when a nested field is a Schema object (MutableMapping) instead of a dict.
    This reproduces the issue where 'DATABASES' entries are DatabaseSchema objects.
    """

    @dataclass
    class InnerSchema(BaseSchema):
        name: str

    @dataclass
    class OuterSchema(BaseSchema):
        inner: InnerSchema
        mapping: dict[str, InnerSchema]

    # Test 1: Direct nesting
    inner_obj = InnerSchema(name="foo")
    data = {
        "inner": inner_obj,
        "mapping": {"key": inner_obj},
    }

    # This should pass if validator supports Mapping/Schema objects
    validate_data_against_schema(data, OuterSchema)
