# ruff: noqa: N802, N803
from typing import Annotated, Any, Literal, overload

from dj_typed_settings.schema import (
    AuthPasswordValidatorNameType,
    AuthPasswordValidatorSchema,
    CacheBackendType,
    CacheSchema,
    DatabaseEngineType,
    DatabaseSchema,
    TemplateBackendType,
    TemplateSchema,
)


@overload
def TEMPLATE(
    # Explicitly list the literals to ensure IDEs show them in hover/autocomplete
    BACKEND: Literal[
        "django.template.backends.django.DjangoTemplates",
        "django.template.backends.jinja2.Jinja2",
    ],
    DIRS: Annotated[list[str] | None, "Directories where the engine should look for template source files."] = None,
    APP_DIRS: Annotated[bool, "Whether to look for template source files inside installed applications."] = False,  # noqa: FBT002
    OPTIONS: Annotated[dict[str, Any] | None, "Extra parameters to pass to the template backend."] = None,
    **kwargs: Annotated[Any, "Extra parameters to pass to the template backend."],
) -> dict[str, Any]: ...


@overload
def TEMPLATE(
    BACKEND: str,
    DIRS: Annotated[list[str] | None, "Directories where the engine should look for template source files."] = None,
    APP_DIRS: Annotated[bool, "Whether to look for template source files inside installed applications."] = False,  # noqa: FBT002
    OPTIONS: Annotated[dict[str, Any] | None, "Extra parameters to pass to the template backend."] = None,
    **kwargs: Annotated[Any, "Extra parameters to pass to the template backend."],
) -> dict[str, Any]: ...


def TEMPLATE(
    BACKEND: TemplateBackendType | str,
    DIRS: Annotated[list[str] | None, "Directories where the engine should look for template source files."] = None,
    APP_DIRS: Annotated[bool, "Whether to look for template source files inside installed applications."] = False,  # noqa: FBT002
    OPTIONS: Annotated[dict[str, Any] | None, "Extra parameters to pass to the template backend."] = None,
    **kwargs: Annotated[Any, "Extra parameters to pass to the template backend."],
) -> dict[str, Any]:
    """
    Typed helper for defining a Django Template backend configuration.
    """

    # Validate required fields
    if not BACKEND.strip():
        raise ValueError("TEMPLATE requires 'BACKEND' argument.")

    model = TemplateSchema(BACKEND=BACKEND, DIRS=DIRS or [], APP_DIRS=APP_DIRS, OPTIONS=OPTIONS or {}, **kwargs)

    return model.to_dict()


@overload
def DATABASE(
    # Explicitly list the literals to ensure IDEs show them in hover/autocomplete
    ENGINE: Literal[
        "django.db.backends.postgresql",
        "django.db.backends.mysql",
        "django.db.backends.sqlite3",
        "django.db.backends.oracle",
    ],
    NAME: Annotated[str, "The name of the database to use."],
    OPTIONS: Annotated[dict[str, Any] | None, "Extra parameters to use when connecting to the database."] = None,
    **kwargs: Annotated[Any, "Extra parameters to use when connecting to the database."],
) -> dict[str, Any]: ...


@overload
def DATABASE(
    ENGINE: str,
    NAME: Annotated[str, "The name of the database to use."],
    OPTIONS: Annotated[dict[str, Any] | None, "Extra parameters to use when connecting to the database."] = None,
    **kwargs: Annotated[Any, "Extra parameters to use when connecting to the database."],
) -> dict[str, Any]: ...


def DATABASE(
    ENGINE: DatabaseEngineType | str,
    NAME: Annotated[str, "The name of the database to use."],
    OPTIONS: Annotated[dict[str, Any] | None, "Extra parameters to use when connecting to the database."] = None,
    **kwargs: Annotated[Any, "Extra parameters to use when connecting to the database."],
) -> dict[str, Any]:
    """
    Typed helper for defining a Django Database configuration.
    """

    # Validate required fields
    if not ENGINE.strip():
        raise ValueError("DATABASE requires 'ENGINE' argument.")
    if not NAME.strip():
        raise ValueError("DATABASE requires 'NAME' argument.")

    model = DatabaseSchema(ENGINE=ENGINE, NAME=NAME, OPTIONS=OPTIONS or {}, **kwargs)

    return model.to_dict()


@overload
def CACHE(
    # Explicitly list the literals to ensure IDEs show them in hover/autocomplete
    BACKEND: Literal[
        "django.core.cache.backends.db.DatabaseCache",
        "django.core.cache.backends.dummy.DummyCache",
        "django.core.cache.backends.filebased.FileBasedCache",
        "django.core.cache.backends.locmem.LocMemCache",
        "django.core.cache.backends.memcached.PyMemcacheCache",
        "django.core.cache.backends.memcached.PyLibMCCache",
        "django.core.cache.backends.redis.RedisCache",
    ],
    LOCATION: Annotated[str | None, "The location of the cache to use."] = None,
    TIMEOUT: Annotated[int | None, "The number of seconds before a cache entry is considered stale."] = None,
    KEY_PREFIX: Annotated[
        str | None, "A string that will be automatically included (prepended) to all cache keys."
    ] = None,
    VERSION: Annotated[int | None, "The default version number for cache keys."] = None,
    OPTIONS: Annotated[dict[str, Any] | None, "Extra parameters to pass to the cache backend."] = None,
    **kwargs: Annotated[Any, "Extra parameters to pass to the cache backend."],
) -> dict[str, Any]: ...


@overload
def CACHE(
    BACKEND: str,
    LOCATION: Annotated[str | None, "The location of the cache to use."] = None,
    TIMEOUT: Annotated[int | None, "The number of seconds before a cache entry is considered stale."] = None,
    KEY_PREFIX: Annotated[
        str | None, "A string that will be automatically included (prepended) to all cache keys."
    ] = None,
    VERSION: Annotated[int | None, "The default version number for cache keys."] = None,
    OPTIONS: Annotated[dict[str, Any] | None, "Extra parameters to pass to the cache backend."] = None,
    **kwargs: Annotated[Any, "Extra parameters to pass to the cache backend."],
) -> dict[str, Any]: ...


def CACHE(
    BACKEND: CacheBackendType | str,
    LOCATION: Annotated[str | None, "The location of the cache to use."] = None,
    TIMEOUT: Annotated[int | None, "The number of seconds before a cache entry is considered stale."] = None,
    KEY_PREFIX: Annotated[
        str | None, "A string that will be automatically included (prepended) to all cache keys."
    ] = None,
    VERSION: Annotated[int | None, "The default version number for cache keys."] = None,
    OPTIONS: Annotated[dict[str, Any] | None, "Extra parameters to pass to the cache backend."] = None,
    **kwargs: Annotated[Any, "Extra parameters to pass to the cache backend."],
) -> dict[str, Any]:
    """
    Typed helper for defining a Django Cache backend configuration.
    """

    # Validate required fields
    if not BACKEND.strip():
        raise ValueError("CACHE requires 'BACKEND' argument.")

    model = CacheSchema(
        BACKEND=BACKEND,
        LOCATION=LOCATION,
        TIMEOUT=TIMEOUT,
        KEY_PREFIX=KEY_PREFIX,
        VERSION=VERSION,
        OPTIONS=OPTIONS or {},
        **kwargs,
    )

    return model.to_dict()


@overload
def AUTH_PASSWORD_VALIDATOR(
    # Explicitly list the literals to ensure IDEs show them in hover/autocomplete
    NAME: Literal[
        "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
        "django.contrib.auth.password_validation.MinimumLengthValidator",
        "django.contrib.auth.password_validation.CommonPasswordValidator",
        "django.contrib.auth.password_validation.NumericPasswordValidator",
    ],
    OPTIONS: Annotated[dict[str, Any] | None, "Optional parameters for the password validator."] = None,
    **kwargs: Annotated[Any, "Optional parameters for the password validator."],
) -> dict[str, Any]: ...


@overload
def AUTH_PASSWORD_VALIDATOR(
    NAME: str,
    OPTIONS: Annotated[dict[str, Any] | None, "Optional parameters for the password validator."] = None,
    **kwargs: Annotated[Any, "Optional parameters for the password validator."],
) -> dict[str, Any]: ...


def AUTH_PASSWORD_VALIDATOR(
    NAME: AuthPasswordValidatorNameType | str,
    OPTIONS: Annotated[dict[str, Any] | None, "Optional parameters for the password validator."] = None,
    **kwargs: Annotated[Any, "Optional parameters for the password validator."],
) -> dict[str, Any]:
    """
    Typed helper for defining a Django Auth Password Validator configuration.
    """

    # Validate required fields
    if not NAME.strip():
        raise ValueError("AUTH_PASSWORD_VALIDATOR requires 'NAME' argument.")

    model = AuthPasswordValidatorSchema(NAME=NAME, OPTIONS=OPTIONS or {}, **kwargs)

    return model.to_dict()
