import pytest

from dj_typed_settings import fix_types
from dj_typed_settings.validator import cast_to_type


def test_cast_to_bool():
    assert cast_to_type("True", bool) is True
    assert cast_to_type("true", bool) is True
    assert cast_to_type("1", bool) is True
    assert cast_to_type("False", bool) is False
    assert cast_to_type("false", bool) is False
    assert cast_to_type("0", bool) is False
    assert cast_to_type("maybe", bool) == "maybe"


def test_cast_to_int():
    assert cast_to_type("123", int) == 123
    assert cast_to_type("abc", int) == "abc"


def test_cast_to_float():
    assert cast_to_type("1.23", float) == 1.23
    assert cast_to_type("abc", float) == "abc"


def test_cast_to_list():
    assert cast_to_type("a,b,c", list) == ["a", "b", "c"]
    assert cast_to_type("a | b | c", list, list_delimiter="|") == ["a", "b", "c"]


def test_cast_to_list_of_int():
    assert cast_to_type("1,2,3", list[int]) == [1, 2, 3]


def test_cast_to_optional():
    assert cast_to_type("123", int | None) == 123
    assert cast_to_type("None", int | None) is None
    assert cast_to_type(None, int | None) is None


def test_fix_types():
    # Use some settings that are likely in SettingsSchema
    settings_globals = {
        "DEBUG": "True",
        "ALLOWED_HOSTS": "localhost,127.0.0.1",
        "EMAIL_PORT": "25",
        "UNKNOWN_SETTING": "string",
    }

    fix_types(settings_globals)

    assert settings_globals["DEBUG"] is True
    assert settings_globals["ALLOWED_HOSTS"] == ["localhost", "127.0.0.1"]
    assert settings_globals["EMAIL_PORT"] == 25
    assert settings_globals["UNKNOWN_SETTING"] == "string"


@pytest.mark.parametrize(
    "value,expected",
    [
        ("True", True),
        ("1", True),
        ("False", False),
        ("0", False),
    ],
)
def test_bool_conversions(value, expected):
    assert cast_to_type(value, bool) == expected
