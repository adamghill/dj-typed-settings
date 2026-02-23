# Changelog

## 0.3.1

- Allow `str` or `Path` for database `NAME` for sqlite.

## 0.3.0

- Add `load_env()` to load .env files.
- Add `parse_db_url()` and `parse_cache_url()` to parse database and cache URLs.
- Add schema for Task settings.
- Validate fields that are `str | int` are actually digits.
- Add Literal types for `TEMPLATE.BACKEND`, `DATABASE.ENGINE`, `CACHE.BACKEND`, and `AUTH_PASSWORD_VALIDATOR.NAME`.

## 0.2.0

- Better support for Python 3.10 and 3.11.

## 0.1.0

- Initial release.
- `fixup_types()` to automatically fix up setting variable types.
- Django system check to validate settings.
- `defaults` for IDE autocomplete.
- `DATABASE`, `CACHES`, `TEMPLATE`, and `AUTH_PASSWORD_VALIDATOR` to handle dictionary settings.
- `dj_typed_settings.conf.settings` for typed access to settings.
