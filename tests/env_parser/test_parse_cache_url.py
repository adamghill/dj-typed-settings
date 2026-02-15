import pytest

from dj_typed_settings.env_parser import parse_cache_url

CACHE_DEFAULTS = {
    "OPTIONS": {},
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


def test_parse_cache_url_empty():
    with pytest.raises(AssertionError, match="URL is required"):
        parse_cache_url("")

    with pytest.raises(AssertionError, match="URL is required"):
        parse_cache_url("   ")

    with pytest.raises(AssertionError, match="URL is required"):
        parse_cache_url(None)  # type: ignore
