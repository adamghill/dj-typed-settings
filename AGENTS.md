# dj-typed-settings Developer Guide

## System Overview

`dj-typed-settings` is a Django library that provides static and runtime type safety for settings. It is designed to be a drop-in enhancement for `django.conf.settings`.

## Core Architecture

### 1. Schema Generation (`schema.py`)
- **Source of Truth**: `src/dj_typed_settings/schema.py` defines the expected structure of all settings.
- **Generation**: This file is **generated** by `scripts/generate_schema.py`. It should rarely be edited manually.
- **Structure**:
  - `BaseSchema`: Inherits `MutableMapping` to allow dictionary-like access (essential for Django compatibility).
  - `SettingsSchema`: A large dataclass representing the root `settings.py`.
  - Sub-schemas: `DatabaseSchema`, `CacheSchema`, `TemplateSchema`, `AuthPasswordValidatorSchema`, `TaskSchema`.

### 2. Runtime Validation (`validator.py`)
- **Mechanism**: specific Django system checks are registered to validate settings at startup.
- **Validation Logic**:
  - `validate_data_against_schema`: Recursively checks a dict against a `BaseSchema` subclass.
  - `validate_type`: Supports `Union`, `List`, `Tuple`, `Dict`, and recursive schemas.
  - **Error Handling**: Collects all errors and raises `SettingsValidationError` or reports them as Django `checks.Error`.
- **Type Coercion**: `fix_types()` and `cast_to_type()` handle environment variable conversion (strings to bool/int/list/float).
  - `bool`: "true"/"1" -> True, "false"/"0" -> False (case-insensitive).
  - `list`: Splits by comma (default delimiter).

### 3. Environment & Parsing
- **`.env` Loader** (`env.py`):
  - `load_env()`: Custom parser (not `python-dotenv`). Supports shell-style quoting (single/double) and comments.
  - **Upward Search**: recurses parents until `.env` or `manage.py` is found.
- **URL Parsers** (`env_parser.py`):
  - `parse_database_url()`: Supports `postgres`, `postgresql`, `psql`, `mysql`, `sqlite` (including `:memory:`), `oracle`.
  - `parse_cache_url()`: Supports `redis`, `rediss`, `memcache`, `pymemcache`, `dbcache`, `dummycache`, `locmemcache`, `filecache`.

### 4. Developer Experience (`conf.py` & `alias.py`)
- **`conf.settings`**: Wraps `django.conf.settings` but types it as `SettingsSchema` for IDEs.
- **Aliases**: `DATABASE()`, `CACHE()`, etc. in `alias.py` are helper functions that use `Annotated` arguments to provide inline documentation and validation for complex dictionary configs.

## Key Files Map

| File | Purpose |
|------|---------|
| `schema.py` | Definitive type definitions (generated). |
| `validator.py` | Runtime type checking logic. |
| `env.py` | `.env` file reading and parsing. |
| `env_parser.py` | `DATABASE_URL` and `CACHE_URL` parsing. |
| `defaults.py` | Stubs/Defaults for `from ...defaults import *` pattern. |
| `scripts/generate_schema.py` | Generator script for `schema.py` and `defaults.py`. |

## Development Rules

1. **Schema Changes**: Do not edit `schema.py` directly. Modify `scripts/generate_schema.py` and run it.
2. **Type Checking**: Use `ty` (or `mypy`) to ensure internal type safety.
3. **Linting**: Conforms to `ruff` standards (Google-style docstrings).

## Common Patterns

### Fixing Types
The `fix_types(globals())` call at the end of `settings.py` is crucial for users relying on `os.getenv`. It iterates over `SettingsSchema` fields and coercively casts matching global variables.

### Ignore List
Users can bypass validation using `TYPED_SETTINGS_IGNORE_ERRORS` (list of strings). The validator checks this list (supporting nested paths like `DATABASES.default.ENGINE`) before raising errors.

## Commands

### Schema Generation
To regenerate `src/dj_typed_settings/schema.py` and `src/dj_typed_settings/defaults.py`:

```bash
uv run scripts/generate_schema.py
```

This reads from the installed Django version. To use a specific version from a URL:

```bash
uv run scripts/generate_schema.py --url https://raw.githubusercontent.com/django/django/stable/4.2.x/django/conf/global_settings.py
```
