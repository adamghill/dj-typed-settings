# ruff: noqa: N802, N803
from typing import Annotated, Any

from dj_typed_settings.schema import (
    AuthPasswordValidatorSchema,
    CacheSchema,
    DatabaseSchema,
    TemplateSchema,
)


def TEMPLATE(
    BACKEND: Annotated[str, "The template backend to use."],
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


def DATABASE(
    ENGINE: Annotated[str, "The database backend to use."],
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


def CACHE(
    BACKEND: Annotated[str, "The cache backend to use."],
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


def AUTH_PASSWORD_VALIDATOR(
    NAME: Annotated[str, "The dotted path to the password validator class."],
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
