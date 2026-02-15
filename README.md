# dj-typed-settings

Type checking and IDE autocomplete for Django settings to improve the developer experience.

## Installation

```bash
uv add dj-typed-settings
```

OR

```bash
pip install dj-typed-settings
```

## Goals

- Stay as close to "normal" Django settings.py usage as possible
- No dependencies outside of the Python standard library
- No runtime performance impact (other than the optional system check)

## Features

There are multiple features to help you write better Django settings. They are all optional and opt-in, so you can use as much or as little as you want.

### Runtime type checking

Ensures your `settings.py` values match the expected types (e.g., `DEBUG` must be `bool`, `TEMPLATES` must be `list`). Also catches typos and invalid keys in complex settings like `DATABASES`, `CACHES`, and `TEMPLATES`.

```python
# settings.py
INSTALLED_APPS = [
    ...,
    "dj_typed_settings",  # required for runtime type checking
]
```

This will run a system check when you run `python manage.py runserver` or `python manage.py check` and raise an error if any setting is the incorrect type.

#### Configuration

You can ignore specific validation errors in your `settings.py`:

```python
TYPED_SETTINGS_IGNORE_ERRORS = [
    "DEBUG",  # Ignore type errors for DEBUG
    "DATABASES.default.ENGINE",  # Ignore specific nested key
]
```

### Autocomplete when editing settings

Provides IDE autocomplete when editing settings.py.

```python
# settings.py
from dj_typed_settings.defaults import *  # noqa: F403

DEBUG = True  # IDE autocomplete works here when hovering over "DEBUG"
```

The `*` import uses default values from Django's `global_settings.py` (with additional generated types and docstrings) as the base and allows you to override them. This provides the IDE the information needed to give you autocomplete in the editor.

### Typed dictionaries

There are a number of complex settings that are normally dictionaries. `dj-typed-settings` provides helper methods that mimic the structure of the dictionary, but provide a better autocomplete experience.

```python
# settings.py
from dj_typed_settings import DATABASES

DATABASES = {
    "default": DATABASE(
        ENGINE="django.db.backends.sqlite3",
        NAME="db.sqlite3",
    )
}
```

The available methods are:

- `AUTH_PASSWORD_VALIDATOR`
- `CACHE`
- `DATABASE`
- `TEMPLATE`

### Autocomplete when using settings

Provides IDE autocomplete when using settings in other Python code.

```python
# views.py
from dj_typed_settings.conf import settings

def index(request):
    if settings.DEBUG:  # Autocomplete in the IDE works here
        return HttpResponse("debug")

    return HttpResponse("production")
```

This is a drop-in replacement for `from django.conf import settings` which provides type hints to the IDE for standard Django settings.

```{note}
For third-party or custom settings, it works exactly like `django.conf.settings`, i.e. provides no additional type hints. However, it will still return the setting as expected.
```

### Automatically cast setting variable types

`dj-typed-settings` can also automatically fix up setting variable types. This can be helpful when using the standard library `os.getenv()` which always returns a string.

```bash
# .env
DEBUG=True
```

```python
# settings.py
from os import getenv
from dj_typed_settings import fix_types

DEBUG = getenv("DEBUG")  # this would be a string at runtime, i.e. DEBUG = "True"
...

fix_types(globals())  # this will fix up all variables when called at the end of the file
```

`fix_types()` converts all default Django setting variables to the expected type when possible. Supported types:

- `bool` from `"True"`, `"true"`, `"False"`, `"false"`, `"1"`, `"0"`
- `int` from `"123"`
- `float` from `"123.45"`
- `list` from `"1,2,3"` (comma separated)

### Load .env file

`dj-typed-settings` can parse `.env` files. It supports shell-style quoting, comments, and line continuations.

```{note}
The support is not quite as robust as `python-dotenv`, for example it doesn't support nested quotes or environment variable expansion. However, it should work for most common use cases. If your `.env` file is complex, you may want to use `python-dotenv` instead.
```

```python
from dj_typed_settings import load_env

load_env()  # Loads .env into os.environ
```

`load_env()` can also take a path to a `.env` file:

```python
load_env(".env")
```

`load_env()` will recursively go up the directory tree until it finds a `.env` file or a directory with a `manage.py` file.

### Parse database and cache URLs

`dj-typed-settings` can parse database and cache URLs into the expected setting dictionaries.

```python
from os import getenv
from dj_typed_settings import parse_db_url, parse_cache_url

DATABASES = {
    "default": parse_db_url(getenv("DATABASE_URL"))
}

CACHES = {
    "default": parse_cache_url(getenv("CACHE_URL"))
}
```

## Acknowledgments

There are a lot of Django settings libraries. Here are a few I use or looked at recently:

- [django-configurations](https://github.com/jazzband/django-configurations)
- [Dynaconf](https://www.dynaconf.com/django/)
- [python-decouple](https://github.com/HBNetwork/python-decouple)
- [dj-settings](https://github.com/spapanik/dj_settings)
- [django-typed-settings](https://pypi.org/project/django-typed-settings/)
- [django-settings-json](https://pypi.org/project/django-settings-json/)
- [normalized-django-settings](https://github.com/irvingleonard/normalized-django-settings)

There are also a lot of libraries which get settings from the environment, which is a slightly different use case, but is related.

- [django-environ](https://github.com/joke2k/django-environ)
- [python-dotenv](https://github.com/theskumar/python-dotenv)
- [environs](https://github.com/sloria/environs)
- [django-settings-env](https://github.com/deeprave/django-settings-env)

## Credits

- [poethepoet](https://github.com/nat-n/poethepoet) (adapted .env parser)
- [django-environ](https://github.com/joke2k/django-environ) (adapted database/cache URL parser)
