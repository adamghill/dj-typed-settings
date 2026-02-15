import logging

from dj_typed_settings.validator import validate_settings


def test_validate_settings_path_support(caplog, tmp_path):
    caplog.set_level(logging.DEBUG)

    base_dir = tmp_path

    settings_dict = {
        "SECRET_KEY": "my-secret-key",
        "BASE_DIR": base_dir,
        "STATICFILES_DIRS": [
            base_dir / "static",
        ],
        "TEMPLATES": [
            {
                "BACKEND": "django.template.backends.django.DjangoTemplates",
                "DIRS": [base_dir / "templates"],
            }
        ],
    }

    validate_settings(settings_dict)

    assert "Validating Settings..." in caplog.text
    assert "✅ Settings are valid." in caplog.text


def test_validate_settings_union_error_clausality(caplog):
    """Verify that Union error messages are specific when a base type matches."""
    caplog.set_level(logging.DEBUG)

    settings_dict = {
        "SECRET_KEY": "my-secret-key",
        "STATICFILES_DIRS": [
            123,  # Should be str or Path
        ],
    }

    validate_settings(settings_dict)

    assert "Validating Settings..." in caplog.text
    assert "❌ INVALID SETTINGS" in caplog.text
    # It should say it must be a str or Path, not generic "must be list or tuple"
    assert "If 'STATICFILES_DIRS[0]' is specified, it must be a str or Path, but got int" in caplog.text
