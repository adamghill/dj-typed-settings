from typing import get_args, get_type_hints

from dj_typed_settings import alias


def test_alias_types():
    hints = get_type_hints(alias.TEMPLATE)

    backend_type = hints["BACKEND"]
    # Should be TemplateBackendType | str which is Union[Literal[...], str]

    # Check that it contains "django.template.backends.django.DjangoTemplates" in the Literal part
    args = get_args(backend_type)
    # args should be (Literal[...], str) or (str, Literal[...])

    literal_part = next(arg for arg in args if get_args(arg))
    assert "django.template.backends.django.DjangoTemplates" in get_args(literal_part)

    # Database
    hints = get_type_hints(alias.DATABASE)
    engine_type = hints["ENGINE"]
    args = get_args(engine_type)
    literal_part = next(arg for arg in args if get_args(arg))
    assert "django.db.backends.postgresql" in get_args(literal_part)

    # Cache
    hints = get_type_hints(alias.CACHE)
    backend_type = hints["BACKEND"]
    args = get_args(backend_type)
    literal_part = next(arg for arg in args if get_args(arg))
    assert "django.core.cache.backends.db.DatabaseCache" in get_args(literal_part)

    # Auth Password Validator
    hints = get_type_hints(alias.AUTH_PASSWORD_VALIDATOR)
    name_type = hints["NAME"]
    args = get_args(name_type)
    literal_part = next(arg for arg in args if get_args(arg))
    assert "django.contrib.auth.password_validation.UserAttributeSimilarityValidator" in get_args(literal_part)
