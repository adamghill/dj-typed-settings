import pytest

from dj_typed_settings.env_parser import parse_cache_url, parse_database_url

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
    # Check options specifically, confusing to check whole dict with overridden defaults
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


def test_parse_cache_dummy():
    url = "dummycache://"
    config = parse_cache_url(url)
    assert config.to_dict() == {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
        "LOCATION": "dummy",
        **CACHE_DEFAULTS,
    }


def test_parse_cache_file():
    url = "filecache:///tmp/django_cache"
    config = parse_cache_url(url)
    assert config.to_dict() == {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": "/tmp/django_cache",  # noqa: S108
        **CACHE_DEFAULTS,
    }


def test_parse_cache_db():
    url = "dbcache://my_cache_table"
    config = parse_cache_url(url)
    assert config.to_dict() == {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "my_cache_table",
        **CACHE_DEFAULTS,
    }


def test_parse_cache_locmem():
    url = "locmemcache://my-snowflake"
    config = parse_cache_url(url)
    assert config.to_dict() == {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "my-snowflake",
        **CACHE_DEFAULTS,
    }


def test_parse_cache_redis():
    url = "redis://127.0.0.1:6379/1"
    config = parse_cache_url(url)
    assert config.to_dict() == {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        **CACHE_DEFAULTS,
    }


def test_parse_cache_redis_options():
    url = "redis://127.0.0.1:6379/1?ignore_exceptions=True"
    config = parse_cache_url(url)
    expected = {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        **CACHE_DEFAULTS,
    }
    expected["OPTIONS"] = {"ignore_exceptions": "True"}
    assert config.to_dict() == expected


def test_parse_cache_memcached():
    url = "memcache://127.0.0.1:11211"
    config = parse_cache_url(url)
    assert config.to_dict() == {
        "BACKEND": "django.core.cache.backends.memcached.MemcachedCache",
        "LOCATION": "127.0.0.1:11211",
        **CACHE_DEFAULTS,
    }


def test_parse_cache_memcached_multiple():
    url = "memcache://127.0.0.1:11211,127.0.0.1:11212"
    config = parse_cache_url(url)
    assert config.to_dict() == {
        "BACKEND": "django.core.cache.backends.memcached.MemcachedCache",
        "LOCATION": ["127.0.0.1:11211", "127.0.0.1:11212"],
        **CACHE_DEFAULTS,
    }


def test_parse_database_url_empty():
    with pytest.raises(AssertionError, match="URL is required"):
        parse_database_url("")

    with pytest.raises(AssertionError, match="URL is required"):
        parse_database_url("   ")

    with pytest.raises(AssertionError, match="URL is required"):
        parse_database_url(None)  # type: ignore


def test_parse_cache_url_empty():
    with pytest.raises(AssertionError, match="URL is required"):
        parse_cache_url("")

    with pytest.raises(AssertionError, match="URL is required"):
        parse_cache_url("   ")

    with pytest.raises(AssertionError, match="URL is required"):
        parse_cache_url(None)  # type: ignore
