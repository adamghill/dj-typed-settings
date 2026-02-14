import logging

from dj_typed_settings import DATABASE
from dj_typed_settings.validator import validate_settings


def test_validate_settings_valid(caplog):
    caplog.set_level(logging.DEBUG)
    settings_dict = {
        "SECRET_KEY": "my-secret-key",
        "DEBUG": True,
        "INSTALLED_APPS": ["django.contrib.admin", "django.contrib.auth"],
        "DATABASES": {
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": "db.sqlite3",
            }
        },
        "TYPED_SETTINGS_IGNORE_ERRORS": [],
    }

    validate_settings(settings_dict)

    assert "Validating Settings..." in caplog.text
    assert "✅ Settings are valid." in caplog.text


def test_validate_settings_alias(caplog):
    caplog.set_level(logging.DEBUG)
    settings_dict = {
        "SECRET_KEY": "my-secret-key",
        "DATABASES": {
            "default": DATABASE(
                ENGINE="django.db.backends.sqlite3",
                NAME="db.sqlite3",
            )
        },
    }

    validate_settings(settings_dict)

    assert "Validating Settings..." in caplog.text
    assert "✅ Settings are valid." in caplog.text


def test_validate_settings_databases_default_invalid_key(caplog):
    caplog.set_level(logging.DEBUG)
    settings_dict = {
        "SECRET_KEY": "my-secret-key",
        "DATABASES": {
            "default": {
                "INVALID_KEY": "django.db.backends.sqlite3",
            }
        },
    }

    validate_settings(settings_dict)

    assert "Validating Settings..." in caplog.text
    assert "❌ INVALID SETTINGS" in caplog.text
    assert "Invalid key 'INVALID_KEY' in DATABASES['default']" in caplog.text


def test_validate_settings_extra(caplog):
    caplog.set_level(logging.DEBUG)
    settings_dict = {
        "SECRET_KEY": "my-secret-key",
        "SOME_NEW_SETTING": "hello",
    }

    validate_settings(settings_dict)

    assert "Validating Settings..." in caplog.text
    assert "✅ Settings are valid." in caplog.text


def test_validate_settings_invalid_missing_required(caplog):
    # Missing SECRET_KEY
    caplog.set_level(logging.DEBUG)
    settings_dict = {
        "DEBUG": True,
    }

    validate_settings(settings_dict)

    assert "Validating Settings..." in caplog.text
    assert "❌ INVALID SETTINGS" in caplog.text
    assert "Missing required setting: SECRET_KEY" in caplog.text


def test_validate_settings_invalid_type(caplog):
    caplog.set_level(logging.DEBUG)
    settings_dict = {
        "SECRET_KEY": "key",
        "DEBUG": "not-a-bool",  # Should be bool
    }

    validate_settings(settings_dict)

    assert "Validating Settings..." in caplog.text
    assert "❌ INVALID SETTINGS" in caplog.text
    assert (
        "if 'DEBUG' is specified, it must be a bool, but got str" in caplog.text.lower()
        or "'debug' must be bool, got str" in caplog.text.lower()
    )


def test_validate_settings_ignore_errors(caplog):
    caplog.set_level(logging.DEBUG)
    settings_dict = {
        "SECRET_KEY": "key",
        "DEBUG": "not-a-bool",  # Should be bool, but we ignore it
        "TYPED_SETTINGS_IGNORE_ERRORS": ["DEBUG"],
    }

    validate_settings(settings_dict)

    assert "Validating Settings..." in caplog.text
    assert "✅ Settings are valid." in caplog.text


def test_validate_settings_ignore_database_invalid_key(caplog):
    """Test ignoring a specific invalid key in a database config using dotted path."""
    caplog.set_level(logging.DEBUG)
    settings_dict = {
        "SECRET_KEY": "my-secret-key",
        "DATABASES": {
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": "db.sqlite3",
                "INVALID_KEY": "should-be-ignored",
            }
        },
        "TYPED_SETTINGS_IGNORE_ERRORS": ["DATABASES.default.INVALID_KEY"],
    }

    validate_settings(settings_dict)

    assert "Validating Settings..." in caplog.text
    assert "✅ Settings are valid." in caplog.text


def test_validate_settings_ignore_entire_database(caplog):
    """Test ignoring an entire database config using dotted path."""
    caplog.set_level(logging.DEBUG)
    settings_dict = {
        "SECRET_KEY": "my-secret-key",
        "DATABASES": {
            "default": {
                "INVALID_KEY": "should-be-ignored",
                "ANOTHER_INVALID": "also-ignored",
            }
        },
        "TYPED_SETTINGS_IGNORE_ERRORS": ["DATABASES.default"],
    }

    validate_settings(settings_dict)

    assert "Validating Settings..." in caplog.text
    assert "✅ Settings are valid." in caplog.text


def test_validate_settings_databases_multiple_invalid_keys(caplog):
    """Test that multiple invalid keys are all reported."""
    caplog.set_level(logging.DEBUG)
    settings_dict = {
        "SECRET_KEY": "my-secret-key",
        "DATABASES": {
            "default": {
                "INVALID_KEY": "value1",
                "ANOTHER_INVALID": "value2",
            }
        },
    }

    validate_settings(settings_dict)

    assert "Validating Settings..." in caplog.text
    assert "❌ INVALID SETTINGS" in caplog.text
    assert "Invalid key 'INVALID_KEY' in DATABASES['default']" in caplog.text
    assert "Invalid key 'ANOTHER_INVALID' in DATABASES['default']" in caplog.text


# ===== Type Validation Tests =====


def test_validate_settings_caches_not_dict(caplog):
    """Test that CACHES must be a dict."""
    caplog.set_level(logging.DEBUG)
    settings_dict = {
        "SECRET_KEY": "my-secret-key",
        "CACHES": "not-a-dict",  # Should be dict
    }

    validate_settings(settings_dict)

    assert "Validating Settings..." in caplog.text
    assert "❌ INVALID SETTINGS" in caplog.text
    assert "'CACHES' must be a dict, got str" in caplog.text


def test_validate_settings_caches_value_not_dict(caplog):
    """Test that CACHES values must be dicts."""
    caplog.set_level(logging.DEBUG)
    settings_dict = {
        "SECRET_KEY": "my-secret-key",
        "CACHES": {
            "default": "not-a-dict",  # Should be dict
        },
    }

    validate_settings(settings_dict)

    assert "Validating Settings..." in caplog.text
    assert "❌ INVALID SETTINGS" in caplog.text
    assert "'CACHES['default']' must be a dict, got str" in caplog.text


def test_validate_settings_templates_not_list(caplog):
    """Test that TEMPLATES must be a list."""
    caplog.set_level(logging.DEBUG)
    settings_dict = {
        "SECRET_KEY": "my-secret-key",
        "TEMPLATES": "not-a-list",  # Should be list
    }

    validate_settings(settings_dict)

    assert "Validating Settings..." in caplog.text
    assert "❌ INVALID SETTINGS" in caplog.text
    assert (
        "'TEMPLATES' must be a list or tuple, but got str" in caplog.text
        or "If 'TEMPLATES' is specified, it must be a list or tuple, but got str" in caplog.text
    )


def test_validate_settings_templates_item_not_dict(caplog):
    """Test that TEMPLATES items must be dicts."""
    caplog.set_level(logging.DEBUG)
    settings_dict = {
        "SECRET_KEY": "my-secret-key",
        "TEMPLATES": ["not-a-dict"],  # Items should be dicts
    }

    validate_settings(settings_dict)

    assert "Validating Settings..." in caplog.text
    assert "❌ INVALID SETTINGS" in caplog.text
    # Union type validation fails generically for items
    assert (
        "'TEMPLATES' must be a list or tuple, but got list" in caplog.text
        or "If 'TEMPLATES' is specified, it must be a list or tuple, but got list" in caplog.text
    )


def test_validate_settings_auth_password_validators_not_list(caplog):
    """Test that AUTH_PASSWORD_VALIDATORS must be a list."""
    caplog.set_level(logging.DEBUG)
    settings_dict = {
        "SECRET_KEY": "my-secret-key",
        "AUTH_PASSWORD_VALIDATORS": "not-a-list",  # Should be list
    }

    validate_settings(settings_dict)

    assert "Validating Settings..." in caplog.text
    assert "❌ INVALID SETTINGS" in caplog.text
    assert (
        "'AUTH_PASSWORD_VALIDATORS' must be a list or tuple, but got str" in caplog.text
        or "If 'AUTH_PASSWORD_VALIDATORS' is specified, it must be a list or tuple, but got str" in caplog.text
    )


def test_validate_settings_auth_password_validators_item_not_dict(caplog):
    """Test that AUTH_PASSWORD_VALIDATORS items must be dicts."""
    caplog.set_level(logging.DEBUG)
    settings_dict = {
        "SECRET_KEY": "my-secret-key",
        "AUTH_PASSWORD_VALIDATORS": ["not-a-dict"],  # Items should be dicts
    }

    validate_settings(settings_dict)

    assert "Validating Settings..." in caplog.text
    assert "❌ INVALID SETTINGS" in caplog.text
    # Union type validation fails generically for items
    assert (
        "'AUTH_PASSWORD_VALIDATORS' must be a list or tuple, but got list" in caplog.text
        or "If 'AUTH_PASSWORD_VALIDATORS' is specified, it must be a list or tuple, but got list" in caplog.text
    )


# ===== CACHES Validation Tests =====


def test_validate_settings_caches_invalid_key(caplog):
    """Test that invalid keys in CACHES are caught."""
    caplog.set_level(logging.DEBUG)
    settings_dict = {
        "SECRET_KEY": "my-secret-key",
        "CACHES": {
            "default": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
                "INVALID_KEY": "should-fail",
            }
        },
    }

    validate_settings(settings_dict)

    assert "Validating Settings..." in caplog.text
    assert "❌ INVALID SETTINGS" in caplog.text
    assert "Invalid key 'INVALID_KEY' in CACHES['default']" in caplog.text


def test_validate_settings_ignore_cache_invalid_key(caplog):
    """Test ignoring a specific invalid key in a cache config using dotted path."""
    caplog.set_level(logging.DEBUG)
    settings_dict = {
        "SECRET_KEY": "my-secret-key",
        "CACHES": {
            "default": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
                "INVALID_KEY": "should-be-ignored",
            }
        },
        "TYPED_SETTINGS_IGNORE_ERRORS": ["CACHES.default.INVALID_KEY"],
    }

    validate_settings(settings_dict)

    assert "Validating Settings..." in caplog.text
    assert "✅ Settings are valid." in caplog.text


def test_validate_settings_ignore_entire_cache(caplog):
    """Test ignoring an entire cache config using dotted path."""
    caplog.set_level(logging.DEBUG)
    settings_dict = {
        "SECRET_KEY": "my-secret-key",
        "CACHES": {
            "default": {
                "INVALID_KEY": "should-be-ignored",
                "ANOTHER_INVALID": "also-ignored",
            }
        },
        "TYPED_SETTINGS_IGNORE_ERRORS": ["CACHES.default"],
    }

    validate_settings(settings_dict)

    assert "Validating Settings..." in caplog.text
    assert "✅ Settings are valid." in caplog.text


# ===== TEMPLATES Validation Tests =====


def test_validate_settings_templates_invalid_key(caplog):
    """Test that invalid keys in TEMPLATES are caught."""
    caplog.set_level(logging.DEBUG)
    settings_dict = {
        "SECRET_KEY": "my-secret-key",
        "TEMPLATES": [
            {
                "BACKEND": "django.template.backends.django.DjangoTemplates",
                "INVALID_KEY": "should-fail",
            }
        ],
    }

    validate_settings(settings_dict)

    assert "Validating Settings..." in caplog.text
    assert "❌ INVALID SETTINGS" in caplog.text
    assert "Invalid key 'INVALID_KEY' in TEMPLATES[0]" in caplog.text


def test_validate_settings_ignore_template_invalid_key(caplog):
    """Test ignoring a specific invalid key in a template config using dotted path."""
    caplog.set_level(logging.DEBUG)
    settings_dict = {
        "SECRET_KEY": "my-secret-key",
        "TEMPLATES": [
            {
                "BACKEND": "django.template.backends.django.DjangoTemplates",
                "INVALID_KEY": "should-be-ignored",
            }
        ],
        "TYPED_SETTINGS_IGNORE_ERRORS": ["TEMPLATES.0.INVALID_KEY"],
    }

    validate_settings(settings_dict)

    assert "Validating Settings..." in caplog.text
    assert "✅ Settings are valid." in caplog.text


def test_validate_settings_ignore_entire_template(caplog):
    """Test ignoring an entire template config using dotted path."""
    caplog.set_level(logging.DEBUG)
    settings_dict = {
        "SECRET_KEY": "my-secret-key",
        "TEMPLATES": [
            {
                "INVALID_KEY": "should-be-ignored",
                "ANOTHER_INVALID": "also-ignored",
            }
        ],
        "TYPED_SETTINGS_IGNORE_ERRORS": ["TEMPLATES.0"],
    }

    validate_settings(settings_dict)

    assert "Validating Settings..." in caplog.text
    assert "✅ Settings are valid." in caplog.text


# ===== AUTH_PASSWORD_VALIDATORS Validation Tests =====


def test_validate_settings_auth_password_validators_invalid_key(caplog):
    """Test that invalid keys in AUTH_PASSWORD_VALIDATORS are caught."""
    caplog.set_level(logging.DEBUG)
    settings_dict = {
        "SECRET_KEY": "my-secret-key",
        "AUTH_PASSWORD_VALIDATORS": [
            {
                "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
                "INVALID_KEY": "should-fail",
            }
        ],
    }

    validate_settings(settings_dict)

    assert "Validating Settings..." in caplog.text
    assert "❌ INVALID SETTINGS" in caplog.text
    assert "Invalid key 'INVALID_KEY' in AUTH_PASSWORD_VALIDATORS[0]" in caplog.text


def test_validate_settings_ignore_validator_invalid_key(caplog):
    """Test ignoring a specific invalid key in a validator config using dotted path."""
    caplog.set_level(logging.DEBUG)
    settings_dict = {
        "SECRET_KEY": "my-secret-key",
        "AUTH_PASSWORD_VALIDATORS": [
            {
                "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
                "INVALID_KEY": "should-be-ignored",
            }
        ],
        "TYPED_SETTINGS_IGNORE_ERRORS": ["AUTH_PASSWORD_VALIDATORS.0.INVALID_KEY"],
    }

    validate_settings(settings_dict)

    assert "Validating Settings..." in caplog.text
    assert "✅ Settings are valid." in caplog.text


def test_validate_settings_ignore_entire_validator(caplog):
    """Test ignoring an entire validator config using dotted path."""
    caplog.set_level(logging.DEBUG)
    settings_dict = {
        "SECRET_KEY": "my-secret-key",
        "AUTH_PASSWORD_VALIDATORS": [
            {
                "INVALID_KEY": "should-be-ignored",
                "ANOTHER_INVALID": "also-ignored",
            }
        ],
        "TYPED_SETTINGS_IGNORE_ERRORS": ["AUTH_PASSWORD_VALIDATORS.0"],
    }

    validate_settings(settings_dict)

    assert "Validating Settings..." in caplog.text
    assert "✅ Settings are valid." in caplog.text


def test_validate_settings_databases_typo_suggestion(caplog):
    """Test that similar key names are suggested for typos."""
    caplog.set_level(logging.DEBUG)
    settings_dict = {
        "SECRET_KEY": "my-secret-key",
        "DATABASES": {
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAEM": "db.sqlite3",  # Typo: should be NAME
            }
        },
    }

    validate_settings(settings_dict)

    assert "Validating Settings..." in caplog.text
    assert "❌ INVALID SETTINGS" in caplog.text
    assert "Invalid key 'NAEM' in DATABASES['default']" in caplog.text
    assert "Did you mean: NAME?" in caplog.text


def test_validate_settings_caches_typo_suggestion(caplog):
    """Test that similar key names are suggested for typos in CACHES."""
    caplog.set_level(logging.DEBUG)
    settings_dict = {
        "SECRET_KEY": "my-secret-key",
        "CACHES": {
            "default": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
                "LOCTION": "should-suggest-LOCATION",  # Typo
            }
        },
    }

    validate_settings(settings_dict)

    assert "Validating Settings..." in caplog.text
    assert "❌ INVALID SETTINGS" in caplog.text
    assert "Invalid key 'LOCTION' in CACHES['default']" in caplog.text
    assert "Did you mean:" in caplog.text
    assert "LOCATION" in caplog.text  # Should suggest LOCATION (and possibly others like OPTIONS)


def test_validate_settings_top_level_typo_debug(caplog):
    """Test that top-level setting typos are caught (e.g., DEBG instead of DEBUG)."""
    caplog.set_level(logging.DEBUG)
    settings_dict = {
        "SECRET_KEY": "my-secret-key",
        "DEBG": True,  # Typo: should be DEBUG
    }

    validate_settings(settings_dict)

    assert "Validating Settings..." in caplog.text
    # Typos are now just debug warnings, not invalid settings
    # assert "❌ INVALID SETTINGS" in caplog.text
    assert "Unknown setting 'DEBG'" in caplog.text
    assert "Did you mean: DEBUG?" in caplog.text


def test_validate_settings_top_level_typo_installed_apps(caplog):
    """Test that top-level setting typos are caught for INSTALLED_APPS."""
    caplog.set_level(logging.DEBUG)
    settings_dict = {
        "SECRET_KEY": "my-secret-key",
        "INSTALED_APPS": ["django.contrib.admin"],  # Typo: missing L
    }

    validate_settings(settings_dict)

    assert "Validating Settings..." in caplog.text
    # assert "❌ INVALID SETTINGS" in caplog.text
    assert "Unknown setting 'INSTALED_APPS'" in caplog.text
    assert "Did you mean:" in caplog.text
    assert "INSTALLED_APPS" in caplog.text
