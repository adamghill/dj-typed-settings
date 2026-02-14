# ruff: noqa: N802, N803
from typing import Any

from dj_typed_settings.schema import (
    AuthPasswordValidatorSchema,
    CacheSchema,
    DatabaseSchema,
    TemplateSchema,
)


def TEMPLATE(
    BACKEND: str,
    DIRS: list[str] | None = None,
    APP_DIRS: bool = False,  # noqa: FBT001, FBT002
    OPTIONS: dict[str, Any] | None = None,
    **kwargs,
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
    ENGINE: str,
    NAME: str,
    OPTIONS: dict[str, Any] | None = None,
    **kwargs,
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
    BACKEND: str,
    LOCATION: str | None = None,
    TIMEOUT: int | None = None,
    KEY_PREFIX: str | None = None,
    VERSION: int | None = None,
    OPTIONS: dict[str, Any] | None = None,
    **kwargs,
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
    NAME: str,
    OPTIONS: dict[str, Any] | None = None,
    **kwargs,
) -> dict[str, Any]:
    """
    Typed helper for defining a Django Auth Password Validator configuration.
    """

    # Validate required fields
    if not NAME.strip():
        raise ValueError("AUTH_PASSWORD_VALIDATOR requires 'NAME' argument.")

    model = AuthPasswordValidatorSchema(NAME=NAME, OPTIONS=OPTIONS or {}, **kwargs)

    return model.to_dict()
