import pytest

from dj_typed_settings.alias import (
    AUTH_PASSWORD_VALIDATOR,
    CACHE,
    DATABASE,
    TEMPLATE,
)


def test_template_alias():
    data = TEMPLATE(BACKEND="my.backend", DIRS=["t"])
    assert data["BACKEND"] == "my.backend"
    assert data["DIRS"] == ["t"]


def test_template_alias_missing_backend():
    with pytest.raises(TypeError) as exc:
        TEMPLATE(DIRS=["t"])
    assert "missing 1 required positional argument" in str(exc.value)


def test_database_alias():
    data = DATABASE(ENGINE="my.engine", NAME="db")
    assert data["ENGINE"] == "my.engine"
    assert data["NAME"] == "db"


def test_database_alias_missing():
    with pytest.raises(TypeError) as exc:
        DATABASE(NAME="db")
    assert "missing 1 required positional argument" in str(exc.value)

    with pytest.raises(TypeError) as exc:
        DATABASE(ENGINE="e")
    assert "missing 1 required positional argument" in str(exc.value)


def test_cache_alias():
    data = CACHE(
        BACKEND="django.core.cache.backends.locmem.LocMemCache",
        LOCATION="unique-snowflake",
        TIMEOUT=300,
        OPTIONS={"MAX_ENTRIES": 1000},
    )
    assert data["BACKEND"] == "django.core.cache.backends.locmem.LocMemCache"
    assert data["LOCATION"] == "unique-snowflake"
    assert data["TIMEOUT"] == 300
    assert data["OPTIONS"] == {"MAX_ENTRIES": 1000}


def test_cache_alias_missing_backend():
    with pytest.raises(TypeError) as exc:
        CACHE(LOCATION="loc")
    assert "missing 1 required positional argument" in str(exc.value)


def test_auth_password_validator_alias():
    data = AUTH_PASSWORD_VALIDATOR(
        NAME="django.contrib.auth.password_validation.MinimumLengthValidator",
        OPTIONS={"min_length": 9},
    )
    assert data["NAME"] == "django.contrib.auth.password_validation.MinimumLengthValidator"
    assert data["OPTIONS"] == {"min_length": 9}


def test_auth_password_validator_alias_missing_name():
    with pytest.raises(TypeError) as exc:
        AUTH_PASSWORD_VALIDATOR(OPTIONS={})
    assert "missing 1 required positional argument" in str(exc.value)
