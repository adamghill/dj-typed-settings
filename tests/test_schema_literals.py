from typing import get_args, get_type_hints

from dj_typed_settings.schema import (
    AuthPasswordValidatorSchema,
    CacheSchema,
    DatabaseSchema,
    TaskSchema,
    TemplateSchema,
)


def test_template_schema_backend_literal():
    type_hints = get_type_hints(TemplateSchema)
    backend_type = type_hints["BACKEND"]

    # BACKEND is defined as Literal[...] | str
    # get_args(backend_type) should return (Literal[...], str)
    # The first arg should be the Literal
    literal_part = get_args(backend_type)[0]

    # Now get the values from the Literal
    allowed_values = get_args(literal_part)

    expected_values = {
        "django.template.backends.django.DjangoTemplates",
        "django.template.backends.jinja2.Jinja2",
    }

    assert set(allowed_values) == expected_values


def test_task_schema_backend_literal():
    type_hints = get_type_hints(TaskSchema)
    backend_type = type_hints["BACKEND"]

    literal_part = get_args(backend_type)[0]
    allowed_values = get_args(literal_part)

    expected_values = {
        "django.tasks.backends.immediate.ImmediateBackend",
        "django.tasks.backends.dummy.DummyBackend",
    }

    assert set(allowed_values) == expected_values


def test_cache_schema_backend_literal():
    type_hints = get_type_hints(CacheSchema)
    backend_type = type_hints["BACKEND"]

    literal_part = get_args(backend_type)[0]
    allowed_values = get_args(literal_part)

    expected_values = {
        "django.core.cache.backends.db.DatabaseCache",
        "django.core.cache.backends.dummy.DummyCache",
        "django.core.cache.backends.filebased.FileBasedCache",
        "django.core.cache.backends.locmem.LocMemCache",
        "django.core.cache.backends.memcached.PyMemcacheCache",
        "django.core.cache.backends.memcached.PyLibMCCache",
        "django.core.cache.backends.redis.RedisCache",
    }

    assert set(allowed_values) == expected_values


def test_database_schema_engine_literal():
    type_hints = get_type_hints(DatabaseSchema)
    engine_type = type_hints["ENGINE"]

    literal_part = get_args(engine_type)[0]
    allowed_values = get_args(literal_part)

    expected_values = {
        "django.db.backends.postgresql",
        "django.db.backends.mysql",
        "django.db.backends.sqlite3",
        "django.db.backends.oracle",
    }

    assert set(allowed_values) == expected_values


def test_auth_password_validator_schema_name_literal():
    type_hints = get_type_hints(AuthPasswordValidatorSchema)
    name_type = type_hints["NAME"]

    literal_part = get_args(name_type)[0]
    allowed_values = get_args(literal_part)

    expected_values = {
        "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
        "django.contrib.auth.password_validation.MinimumLengthValidator",
        "django.contrib.auth.password_validation.CommonPasswordValidator",
        "django.contrib.auth.password_validation.NumericPasswordValidator",
    }

    assert set(allowed_values) == expected_values
