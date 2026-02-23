import urllib.parse
from typing import Any

from dj_typed_settings.schema import CacheSchema, DatabaseSchema

# This module is adapted from django-environ (MIT Licensed)
# Source: https://github.com/joke2k/django-environ/blob/main/environ/environ.py


def _parse_options(query: str) -> dict[str, Any]:
    options = {}

    if query:
        query_params = urllib.parse.parse_qs(query)

        for key, values in query_params.items():
            value = values[0] if values else None

            # Try to convert to int if possible
            if value and value.isdigit():
                value = int(value)

            options[key] = value

    return options


def parse_database_url(url: str, engine: str | None = None) -> DatabaseSchema:
    """
    Parse a database URL into a Django configuration dictionary.

    Supported schemes:
    - postgres, postgresql, psql -> django.db.backends.postgresql
    - mysql -> django.db.backends.mysql
    - sqlite -> django.db.backends.sqlite3
    - oracle -> django.db.backends.oracle

    Args:
        url: The database URL to parse.
        engine: Optional engine override.

    Returns:
        A DatabaseSchema object suitable for Django's DATABASES setting.
    """
    if not url or not url.strip():
        raise AssertionError("URL is required")

    if url == "sqlite://:memory:":
        return DatabaseSchema(
            ENGINE="django.db.backends.sqlite3",
            NAME=":memory:",
        )

    try:
        parsed = urllib.parse.urlparse(url)
    except ValueError:
        raise ValueError(f"Invalid database URL: {url}") from None

    scheme = parsed.scheme

    if engine:
        db_engine = engine
    else:
        match scheme:
            case "postgres" | "postgresql" | "psql":
                db_engine = "django.db.backends.postgresql"
            case "mysql":
                db_engine = "django.db.backends.mysql"
            case "sqlite":
                db_engine = "django.db.backends.sqlite3"
            case "oracle":
                db_engine = "django.db.backends.oracle"
            case _:
                raise ValueError(f"Unsupported database scheme: {scheme}")

    # Parse path / name
    path = parsed.path

    if scheme == "sqlite":
        if path == "":
            name = ":memory:"
        elif path.startswith("/"):
            name = path[1:]
        else:
            name = path
    else:
        # For others, path is usually /dbname
        name = path[1:] if path.startswith("/") else path

    options = _parse_options(parsed.query)

    return DatabaseSchema(
        ENGINE=db_engine,
        NAME=name or "",
        USER=urllib.parse.unquote(parsed.username or "") or None,
        PASSWORD=urllib.parse.unquote(parsed.password or "") or None,
        HOST=parsed.hostname or None,
        PORT=parsed.port or None,
        OPTIONS=options or {},
    )


def parse_cache_url(url: str, backend: str | None = None) -> CacheSchema:
    """
    Parse a cache URL into a Django configuration dictionary.

    Supported schemes:
    - dbcache -> django.core.cache.backends.db.DatabaseCache
    - dummycache -> django.core.cache.backends.dummy.DummyCache
    - filecache -> django.core.cache.backends.filebased.FileBasedCache
    - locmemcache -> django.core.cache.backends.locmem.LocMemCache
    - memcache -> django.core.cache.backends.memcached.MemcachedCache
    - pymemcache -> django.core.cache.backends.memcached.PyMemcacheCache
    - redis, rediss -> django.core.cache.backends.redis.RedisCache

    Args:
        url: The cache URL to parse.
        backend: Optional backend override.

    Returns:
        A CacheSchema object suitable for Django's CACHES setting.
    """
    if not url or not url.strip():
        raise AssertionError("URL is required")

    try:
        parsed = urllib.parse.urlparse(url)
    except ValueError:
        raise ValueError(f"Invalid cache URL: {url}") from None

    scheme = parsed.scheme

    if backend:
        cache_backend = backend
    else:
        match scheme:
            case "dbcache":
                cache_backend = "django.core.cache.backends.db.DatabaseCache"
            case "dummycache":
                cache_backend = "django.core.cache.backends.dummy.DummyCache"
            case "filecache":
                cache_backend = "django.core.cache.backends.filebased.FileBasedCache"
            case "locmemcache":
                cache_backend = "django.core.cache.backends.locmem.LocMemCache"
            case "memcache":
                cache_backend = "django.core.cache.backends.memcached.MemcachedCache"
            case "pymemcache":
                cache_backend = "django.core.cache.backends.memcached.PyMemcacheCache"
            case "redis" | "rediss":
                cache_backend = "django.core.cache.backends.redis.RedisCache"
            case _:
                raise ValueError(f"Unsupported cache scheme: {scheme}")

    location: str | list[str] | None = ""

    if scheme == "filecache":
        location = parsed.path
    elif scheme in ("redis", "rediss"):
        location = urllib.parse.urlunparse(
            (
                parsed.scheme,
                parsed.netloc,
                parsed.path,
                parsed.params,
                "",
                parsed.fragment,
            )
        )
    elif scheme in ("memcache", "pymemcache"):
        if "," in parsed.netloc:
            location = parsed.netloc.split(",")
        else:
            location = parsed.netloc

        if not parsed.netloc and parsed.path:
            location = "unix:" + parsed.path
    elif scheme == "dbcache":
        # path is /tablename or netloc is tablename
        location = parsed.path.lstrip("/") or parsed.netloc
    elif scheme == "locmemcache":
        location = parsed.netloc or "unique-snowflake"
    elif scheme == "dummycache":
        location = parsed.netloc or "dummy"

    options = _parse_options(parsed.query)

    return CacheSchema(
        BACKEND=cache_backend,
        LOCATION=location or None,
        OPTIONS=options or {},
    )
