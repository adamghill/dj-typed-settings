import inspect

import pytest
from django.test import override_settings

from dj_typed_settings import settings


def test_settings_proxy_standard_setting():
    """Test accessing a standard Django setting via the proxy."""

    # We can override it to be sure
    with override_settings(DEBUG=True):
        assert settings.DEBUG is True
        assert isinstance(settings.DEBUG, bool)

    with override_settings(DEBUG=False):
        assert settings.DEBUG is False

    assert isinstance(settings.SECRET_KEY, (str, type(None)))


@override_settings(MyCustomSetting="custom_value")
def test_settings_proxy_custom_setting():
    """Test accessing a custom setting (not in schema) via the proxy."""
    # The proxy should delegate to the overridden setting
    assert settings.MyCustomSetting == "custom_value"

    # Verify type
    assert isinstance(settings.MyCustomSetting, str)


def test_settings_proxy_attribute_error():
    """Test that accessing a non-existent setting raises AttributeError."""
    with pytest.raises(AttributeError):
        _ = settings.NON_EXISTENT_SETTING


def test_settings_proxy_is_module_like():
    """The settings object should behave like a module for import purposes."""
    # It's actually an instance of a class, but utilized like a module.
    assert hasattr(settings, "DEBUG")


def test_docstrings_in_schema():
    """Verify that SettingsSchema has docstrings for fields."""
    from dj_typed_settings.schema import SettingsSchema

    source = inspect.getsource(SettingsSchema)
    assert '"""' in source
    assert "A secret key for this particular Django installation" in source
