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
