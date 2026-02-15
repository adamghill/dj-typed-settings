## Features

### Runtime type checking

```python
# settings.py
INSTALLED_APPS = [
    ...,
    "dj_typed_settings",  # required for runtime type checking
]
```

### Autocomplete when editing settings

```python
# settings.py
from dj_typed_settings.defaults import *  # noqa: F403

DEBUG = True  # IDE autocomplete works here when hovering over "DEBUG"
```

#### Typed dictionaries

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

### Autocomplete when using settings

```python
# views.py
from dj_typed_settings.conf import settings

def index(request):
    if settings.DEBUG:  # Autocomplete in the IDE works here
        return HttpResponse("debug")

    return HttpResponse("production")
```

### Automatically fix setting variable types

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

### Load .env file

```python
from dj_typed_settings import load_env

load_env()  # Loads .env into os.environ
```

### Parse database and cache URLs

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
