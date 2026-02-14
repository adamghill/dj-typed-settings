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

Add to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    ...,
    "dj_typed_settings",  # required for runtime type checking
]
```

## Features

There are multiple features to help you write better Django settings. they are all optional and opt-in, so you can use as much or as little as you want.

### Runtime type checking

Ensures your `settings.py` values match the expected types (e.g., `DEBUG` must be `bool`, `TEMPLATES` must be `list`). Also catches typos and invalid keys in complex settings like `DATABASES`, `CACHES`, and `TEMPLATES`.

This will run a system checks when you run `python manage.py runserver` or `python manage.py check` and raise an error if any setting is the incorrect type.

```{note}
To skip, runtime type checking altogether, remove `"dj_typed_settings"` from `INSTALLED_APPS`.

To skip particular settings, add them to `TYPED_SETTINGS_IGNORE_ERRORS` as detailed in the [Configuration](#configuration) section.
```

### Autocomplete when editing settings

Provides IDE autocomplete when editing settings.py.

```python
# settings.py

from dj_typed_settings.defaults import *  # noqa: F403

DEBUG = True  # IDE autocomplete works here when hovering over "DEBUG"
```

The `*` import uses default values from Django's `global_settings.py` (with additional generated types and docstrings) as the base and allows you to override them. This provides the IDE the information needed to give you autocomplete in the editor.

#### Typed dictionaries

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

## Automatically fix setting variable types

`dj-typed-settings` can also automatically fix up setting variable types. This can be helpful when using the standard library `os.getenv()` which always returns a string.

```python
# settings.py

from os import getenv
from dj_typed_settings import fixup_types

DEBUG = getenv("DEBUG")
...

fixup_types(globals())  # this will fix up all variables when called at the end of the file
```

`fixup_types()` converts all default Django setting variables to the expected type when possible. Supported types:

- `bool` from `"True"`, `"true"`, `"False"`, `"false"`, `"1"`, `"0"`
- `int` from `"123"`
- `float` from `"123.45"`
- `list` from `"1,2,3"` (comma separated)

### Configuration

You can ignore specific validation errors in your `settings.py`:

```python
TYPED_SETTINGS_IGNORE_ERRORS = [
    "DEBUG",  # Ignore type errors for DEBUG
    "DATABASES.default.ENGINE",  # Ignore specific nested key
]
```

## Goals

- Stay as close to "normal" Django settings.py usage as possible
- No dependencies outside of the Python standard library
- No runtime performance impact (other than the optional system check)

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

