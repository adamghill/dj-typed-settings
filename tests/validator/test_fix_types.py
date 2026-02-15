from dj_typed_settings.validator import fix_types


def test_fix_types():
    # Use some settings that are likely in SettingsSchema
    settings_globals = {
        "DEBUG": "True",
        "ALLOWED_HOSTS": "localhost,127.0.0.1",
        "EMAIL_PORT": "25",
        "UNKNOWN_SETTING": "string",
    }

    fix_types(settings_globals)

    assert settings_globals["DEBUG"] is True
    assert settings_globals["ALLOWED_HOSTS"] == ["localhost", "127.0.0.1"]
    assert settings_globals["EMAIL_PORT"] == 25
    assert settings_globals["UNKNOWN_SETTING"] == "string"
