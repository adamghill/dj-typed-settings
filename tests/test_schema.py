import pytest

from dj_typed_settings.schema import DatabaseSchema, SettingsSchema, TemplateSchema


def test_template_schema_defaults():
    schema = TemplateSchema(BACKEND="django.template.backends.django.DjangoTemplates")
    assert schema.BACKEND == "django.template.backends.django.DjangoTemplates"
    assert schema.DIRS == []
    assert schema.APP_DIRS is False
    assert schema.OPTIONS == {}
    assert schema.NAME is None


def test_template_schema_to_dict():
    schema = TemplateSchema(
        BACKEND="django.template.backends.django.DjangoTemplates",
        DIRS=["templates"],
        APP_DIRS=True,
        OPTIONS={"context_processors": []},
    )
    data = schema.to_dict()
    assert data["BACKEND"] == "django.template.backends.django.DjangoTemplates"
    assert data["DIRS"] == ["templates"]
    assert data["APP_DIRS"] is True
    assert data["OPTIONS"] == {"context_processors": []}
    assert "NAME" not in data  # None values should be excluded


def test_database_schema_defaults():
    schema = DatabaseSchema(ENGINE="django.db.backends.postgresql", NAME="mydb")
    assert schema.ENGINE == "django.db.backends.postgresql"
    assert schema.NAME == "mydb"
    assert schema.USER is None
    assert schema.PASSWORD is None
    assert schema.HOST is None
    assert schema.PORT is None
    assert schema.ATOMIC_REQUESTS is False
    assert schema.AUTOCOMMIT is True
    assert schema.CONN_MAX_AGE == 0
    assert schema.OPTIONS == {}
    assert schema.TIME_ZONE is None
    assert schema.TEST == {}


def test_database_schema_to_dict():
    schema = DatabaseSchema(
        ENGINE="django.db.backends.postgresql",
        NAME="mydb",
        USER="user",
        PASSWORD="password",
        HOST="localhost",
        PORT="5432",
    )
    data = schema.to_dict()
    assert data["ENGINE"] == "django.db.backends.postgresql"
    assert data["NAME"] == "mydb"
    assert data["USER"] == "user"
    assert data["PASSWORD"] == "password"
    assert data["HOST"] == "localhost"
    assert data["PORT"] == "5432"
    assert "ATOMIC_REQUESTS" in data  # Booleans with defaults are included
    assert "TIME_ZONE" not in data  # None values excluded


def test_settings_schema_init():
    # Only testing that it can be initialized with required fields
    schema = SettingsSchema(
        SECRET_KEY="secret",
    )
    assert schema.SECRET_KEY == "secret"
    assert schema.DEBUG is False
    assert schema.INSTALLED_APPS == []


def test_settings_schema_to_dict():
    schema = SettingsSchema(
        SECRET_KEY="secret",
        DEBUG=True,
        INSTALLED_APPS=["django.contrib.admin"],
    )
    data = schema.to_dict()
    assert data["SECRET_KEY"] == "secret"
    assert data["DEBUG"] is True
    assert data["INSTALLED_APPS"] == ["django.contrib.admin"]
    assert "ROOT_URLCONF" not in data  # None values should be excluded


def test_schema_dict_behavior():
    """Test that schemas behave like dictionaries (Mapping protocol)."""
    schema = DatabaseSchema(
        ENGINE="django.db.backends.postgresql",
        NAME="mydb",
        USER="user",
        # HOST, PORT, PASSWORD are None
    )

    # Test __getitem__
    assert schema["ENGINE"] == "django.db.backends.postgresql"
    assert schema["NAME"] == "mydb"
    assert schema["USER"] == "user"
    assert schema["HOST"] is None  # Now returns None instead of raising KeyError

    # Test missing keys (Only truly missing keys raise KeyError)
    with pytest.raises(KeyError):
        _ = schema["INVALID_KEY"]

    # Test get()
    assert schema.get("ENGINE") == "django.db.backends.postgresql"
    assert schema.get("HOST") is None
    assert schema.get("HOST", "default") is None  # get returns value if key exists (even if None)

    # Test __len__
    # All fields are now included in len, regardless of value
    # DatabaseSchema has many fields. Let's not hardcode exact number but ensure it's > 9
    assert len(schema) > 9

    # Test __iter__ / keys()
    keys = list(schema.keys())
    assert "ENGINE" in keys
    assert "NAME" in keys
    assert "USER" in keys
    assert "HOST" in keys  # Now included

    # Test values()
    values = list(schema.values())
    assert "django.db.backends.postgresql" in values
    assert "mydb" in values
    assert None in values  # HOST is None

    # Test items()
    items = dict(schema.items())
    assert items["ENGINE"] == "django.db.backends.postgresql"
    assert items["NAME"] == "mydb"
    assert items["HOST"] is None

    # Test conversion to dict
    # dict(schema) now includes None values
    d = dict(schema)
    assert "HOST" in d
    assert d["HOST"] is None

    # schema.to_dict() still excludes None values (by design in BaseSchema)
    assert "HOST" not in schema.to_dict()
    assert dict(schema) != schema.to_dict()


def test_schema_mutable_mapping():
    """Test that schemas support mutation (MutableMapping)."""
    schema = DatabaseSchema(
        ENGINE="django.db.backends.postgresql",
        NAME="mydb",
    )

    # Test __setitem__ on existing field
    schema["USER"] = "new_user"
    assert schema.USER == "new_user"
    assert schema["USER"] == "new_user"
    assert "USER" in schema

    # Test __setitem__ on new ad-hoc field
    schema["NEW_FIELD"] = 123
    assert schema.NEW_FIELD == 123
    assert schema["NEW_FIELD"] == 123
    assert "NEW_FIELD" in schema

    # Test setdefault (provided by MutableMapping mixin)
    # 1. Key exists
    val = schema.setdefault("USER", "default_user")
    assert val == "new_user"
    assert schema.USER == "new_user"

    # 2. Key exists but is None (field default)
    # setdefault returns the existing value if key exists, even if None
    val = schema.setdefault("HOST", "localhost")
    assert val is None
    assert schema.HOST is None

    # We can explicitly set it
    schema["HOST"] = "localhost"
    assert schema.HOST == "localhost"

    # 3. Key does not exist (ad-hoc)
    val = schema.setdefault("ANOTHER_FIELD", "foo")

    assert val == "foo"
    assert schema.ANOTHER_FIELD == "foo"

    # Test __delitem__
    # 1. Delete field (sets to None)
    del schema["USER"]
    assert schema.USER is None
    assert "USER" in schema  # Field remains in schema keys, but value is None

    # 2. Delete ad-hoc field
    del schema["NEW_FIELD"]
    with pytest.raises(AttributeError):
        _ = schema.NEW_FIELD
    assert "NEW_FIELD" not in schema

    # Test update()
    schema.update({"PORT": 5432, "EXTRA": "bar"})
    assert schema.PORT == 5432
    assert schema.EXTRA == "bar"

    # Test iteration with new fields
    keys = list(schema.keys())
    assert "ENGINE" in keys
    assert "HOST" in keys
    assert "PORT" in keys
    assert "EXTRA" in keys
    assert "USER" in keys  # deleted (None) but still a field key
