import pytest

from dj_typed_settings.env_parser import parse_database_url

DB_DEFAULTS = {
    "ATOMIC_REQUESTS": False,
    "AUTOCOMMIT": True,
    "CONN_MAX_AGE": 0,
    "OPTIONS": {},
    "TEST": {},
    "CONN_HEALTH_CHECKS": False,
}

CACHE_DEFAULTS = {
    "OPTIONS": {},
}


def test_parse_postgres():
    url = "postgres://user:password@localhost:5432/dbname"
    config = parse_database_url(url)
    assert config.to_dict() == {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "dbname",
        "USER": "user",
        "PASSWORD": "password",
        "HOST": "localhost",
        "PORT": 5432,
        **DB_DEFAULTS,
    }


def test_parse_postgres_no_port():
    url = "postgres://user:password@localhost/dbname"
    config = parse_database_url(url)
    assert config.to_dict() == {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "dbname",
        "USER": "user",
        "PASSWORD": "password",
        "HOST": "localhost",
        **DB_DEFAULTS,
    }


def test_parse_mysql():
    url = "mysql://user:password@127.0.0.1:3306/dbname"
    config = parse_database_url(url)
    assert config.to_dict() == {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "dbname",
        "USER": "user",
        "PASSWORD": "password",
        "HOST": "127.0.0.1",
        "PORT": 3306,
        **DB_DEFAULTS,
    }


def test_parse_sqlite_memory():
    url = "sqlite://:memory:"
    config = parse_database_url(url)
    assert config.to_dict() == {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
        **DB_DEFAULTS,
    }


def test_parse_sqlite_file():
    url = "sqlite:///path/to/db.sqlite3"
    config = parse_database_url(url)
    assert config.to_dict() == {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "path/to/db.sqlite3",
        **DB_DEFAULTS,
    }


def test_parse_sqlite_absolute_file():
    url = "sqlite:////absolute/path/to/db.sqlite3"
    config = parse_database_url(url)
    assert config.to_dict() == {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "/absolute/path/to/db.sqlite3",
        **DB_DEFAULTS,
    }


def test_parse_oracle():
    url = "oracle://user:password@localhost:1521/xe"
    config = parse_database_url(url)
    assert config.to_dict() == {
        "ENGINE": "django.db.backends.oracle",
        "NAME": "xe",
        "USER": "user",
        "PASSWORD": "password",
        "HOST": "localhost",
        "PORT": 1521,
        **DB_DEFAULTS,
    }


def test_parse_custom_engine():
    url = "custom://user:password@localhost/dbname"
    config = parse_database_url(url, engine="my.custom.backend")
    assert config.to_dict() == {
        "ENGINE": "my.custom.backend",
        "NAME": "dbname",
        "USER": "user",
        "PASSWORD": "password",
        "HOST": "localhost",
        **DB_DEFAULTS,
    }


def test_parse_unsupported_scheme():
    url = "unsupported://user:password@localhost/dbname"
    with pytest.raises(ValueError, match="Unsupported database scheme: unsupported"):
        parse_database_url(url)


def test_parse_options():
    url = "postgres://user:password@localhost/dbname?conn_max_age=600&atomic_requests=True"
    config = parse_database_url(url)

    # Check options specifically
    assert config.OPTIONS == {
        "conn_max_age": 600,
        "atomic_requests": "True",
    }

    # Verify defaults are still there but OPTIONS is updated
    # Note: parsing logic puts parsed options into OPTIONS dict.
    # So assertions on the full dict should expect OPTIONS to be populated.
    expected = {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "dbname",
        "USER": "user",
        "PASSWORD": "password",
        "HOST": "localhost",
        **DB_DEFAULTS,
    }
    expected["OPTIONS"] = {
        "conn_max_age": 600,
        "atomic_requests": "True",
    }
    assert config.to_dict() == expected


def test_parse_ipv6():
    # IPv6 addresses in URLs are enclosed in brackets
    url = "postgres://user:password@[::1]:5432/dbname"
    config = parse_database_url(url)
    assert config.to_dict() == {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "dbname",
        "USER": "user",
        "PASSWORD": "password",
        "HOST": "::1",
        "PORT": 5432,
        **DB_DEFAULTS,
    }


def test_parse_database_url_empty():
    with pytest.raises(AssertionError, match="URL is required"):
        parse_database_url("")

    with pytest.raises(AssertionError, match="URL is required"):
        parse_database_url("   ")

    with pytest.raises(AssertionError, match="URL is required"):
        parse_database_url(None)  # type: ignore
