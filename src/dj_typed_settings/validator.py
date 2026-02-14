import logging
from dataclasses import MISSING, fields
from difflib import get_close_matches
from typing import Any, Union, get_args, get_origin, get_type_hints

from django.conf import settings
from django.core.checks import Error

from dj_typed_settings.schema import (
    AuthPasswordValidatorSchema,
    CacheSchema,
    DatabaseSchema,
    SettingsSchema,
    TemplateSchema,
)

logger = logging.getLogger(__name__)


def validate_type(value: Any, type_hint: Any, field_name: str) -> None:
    """
    Validates a value against a type hint at runtime. Supports basic types, List, Dict, Union, and Optional.
    """

    origin = get_origin(type_hint)
    args = get_args(type_hint)

    # Handle Optional[T] which is Union[T, NoneType]
    if origin is Union:
        # Check if value matches ANY of the args
        is_valid = False
        for arg in args:
            try:
                validate_type(value, arg, field_name)
                is_valid = True
                break
            except TypeError:
                continue

        if not is_valid:
            valid_types = [arg.__name__ if hasattr(arg, "__name__") else str(arg) for arg in args]
            valid_types = [t for t in valid_types if t != "NoneType"]

            if len(valid_types) > 1:
                expected = f"{', '.join(valid_types[:-1])} or {valid_types[-1]}"
            else:
                expected = valid_types[0]

            raise TypeError(f"If '{field_name}' is specified, it must be a {expected}, but got {type(value).__name__}")
        return

    # Handle List[T]
    if origin is list:
        if not isinstance(value, list):
            raise TypeError(f"'{field_name}' must be list, got {type(value).__name__}")

        # Validate list items if type args are provided
        if args and len(args) > 0:
            expected_item_type = args[0]
            # Check if items are dicts when expected
            if expected_item_type is dict or get_origin(expected_item_type) is dict:
                for i, item in enumerate(value):
                    if not isinstance(item, dict):
                        raise TypeError(f"'{field_name}[{i}]' must be a dict, got {type(item).__name__}")
        return

    # Handle Tuple[T, ...]
    if origin is tuple:
        if not isinstance(value, tuple):
            raise TypeError(f"'{field_name}' must be tuple, got {type(value).__name__}")
        # Note: We don't validate tuple items as strictly since tuple type hints can be complex
        return

    # Handle Dict[K, V]
    if origin is dict:
        if not isinstance(value, dict):
            raise TypeError(f"'{field_name}' must be a dict, got {type(value).__name__}")

        # Validate dict values if type args are provided
        if args and len(args) > 1:
            expected_value_type = args[1]
            # Check if values are dicts when expected
            if expected_value_type is dict or get_origin(expected_value_type) is dict:
                for key, val in value.items():
                    if not isinstance(val, dict):
                        raise TypeError(f"'{field_name}[{key!r}]' must be a dict, got {type(val).__name__}")
        return

    # Handle Any
    if type_hint is Any:
        return

    # Handle Simple Types (int, str, bool, etc.)
    if isinstance(type_hint, type):
        if not isinstance(value, type_hint):
            raise TypeError(f"'{field_name}' must be {type_hint.__name__}, got {type(value).__name__}")
        return


def validate_nested_database(db_name: str, db_config: dict[str, Any], ignore_errors: list[str]) -> list[str]:
    """
    Validate a database configuration against DatabaseSchema.

    Returns a list of error messages.
    """
    errors = []

    # Check if entire database should be ignored
    if f"DATABASES.{db_name}" in ignore_errors:
        return errors

    # Get valid keys from DatabaseSchema
    valid_keys = {f.name for f in fields(DatabaseSchema)}
    hints = get_type_hints(DatabaseSchema)
    schema_fields = {f.name: f for f in fields(DatabaseSchema)}

    # Check for invalid keys
    for key in db_config.keys():
        dotted_path = f"DATABASES.{db_name}.{key}"

        # Skip if this specific key is ignored
        if dotted_path in ignore_errors:
            continue

        if key not in valid_keys:
            error_msg = f"Invalid key '{key}' in DATABASES['{db_name}']."

            # Suggest similar keys if any are found
            suggestions = get_close_matches(key, valid_keys, n=3, cutoff=0.6)
            if suggestions:
                error_msg += f" Did you mean: {', '.join(suggestions)}?"
            else:
                error_msg += f" Valid keys are: {', '.join(sorted(valid_keys))}"

            errors.append(error_msg)

    # Validate required fields and types for non-ignored keys
    for field_name, type_hint in hints.items():
        dotted_path = f"DATABASES.{db_name}.{field_name}"

        # Skip if this specific key is ignored
        if dotted_path in ignore_errors:
            continue

        if field_name not in db_config:
            f = schema_fields.get(field_name)
            if f.default is MISSING and f.default_factory is MISSING:
                errors.append(f"Missing required key '{field_name}' in DATABASES['{db_name}']")
            continue

        value = db_config[field_name]
        try:
            validate_type(value, type_hint, f"DATABASES.{db_name}.{field_name}")
        except TypeError as e:
            errors.append(str(e))

    return errors


def validate_nested_cache(cache_name: str, cache_config: dict[str, Any], ignore_errors: list[str]) -> list[str]:
    """
    Validate a cache configuration against CacheSchema.

    Returns a list of error messages.
    """
    errors = []

    # Check if entire cache should be ignored
    if f"CACHES.{cache_name}" in ignore_errors:
        return errors

    # Get valid keys from CacheSchema
    valid_keys = {f.name for f in fields(CacheSchema)}
    hints = get_type_hints(CacheSchema)
    schema_fields = {f.name: f for f in fields(CacheSchema)}

    # Check for invalid keys
    for key in cache_config.keys():
        dotted_path = f"CACHES.{cache_name}.{key}"

        # Skip if this specific key is ignored
        if dotted_path in ignore_errors:
            continue

        if key not in valid_keys:
            error_msg = f"Invalid key '{key}' in CACHES['{cache_name}']"

            # Suggest similar keys if any are found
            suggestions = get_close_matches(key, valid_keys, n=3, cutoff=0.6)
            if suggestions:
                error_msg += f". Did you mean: {', '.join(suggestions)}?"
            else:
                error_msg += f". Valid keys are: {', '.join(sorted(valid_keys))}"

            errors.append(error_msg)

    # Validate required fields and types for non-ignored keys
    for field_name, type_hint in hints.items():
        dotted_path = f"CACHES.{cache_name}.{field_name}"

        # Skip if this specific key is ignored
        if dotted_path in ignore_errors:
            continue

        if field_name not in cache_config:
            f = schema_fields.get(field_name)
            if f.default is MISSING and f.default_factory is MISSING:
                errors.append(f"Missing required key '{field_name}' in CACHES['{cache_name}']")
            continue

        value = cache_config[field_name]
        try:
            validate_type(value, type_hint, f"CACHES.{cache_name}.{field_name}")
        except TypeError as e:
            errors.append(str(e))

    return errors


def validate_nested_template(index: int, template_config: dict[str, Any], ignore_errors: list[str]) -> list[str]:
    """
    Validate a template configuration against TemplateSchema.

    Returns a list of error messages.
    """
    errors = []

    # Check if entire template should be ignored
    if f"TEMPLATES.{index}" in ignore_errors:
        return errors

    # Get valid keys from TemplateSchema
    valid_keys = {f.name for f in fields(TemplateSchema)}
    hints = get_type_hints(TemplateSchema)
    schema_fields = {f.name: f for f in fields(TemplateSchema)}

    # Check for invalid keys
    for key in template_config.keys():
        dotted_path = f"TEMPLATES.{index}.{key}"

        # Skip if this specific key is ignored
        if dotted_path in ignore_errors:
            continue

        if key not in valid_keys:
            error_msg = f"Invalid key '{key}' in TEMPLATES[{index}]."

            # Suggest similar keys if any are found
            suggestions = get_close_matches(key, valid_keys, n=3, cutoff=0.6)
            if suggestions:
                error_msg += f" Did you mean: {', '.join(suggestions)}?"
            else:
                error_msg += f" Valid keys are: {', '.join(sorted(valid_keys))}"

            errors.append(error_msg)

    # Validate required fields and types for non-ignored keys
    for field_name, type_hint in hints.items():
        dotted_path = f"TEMPLATES.{index}.{field_name}"

        # Skip if this specific key is ignored
        if dotted_path in ignore_errors:
            continue

        if field_name not in template_config:
            f = schema_fields.get(field_name)
            if f.default is MISSING and f.default_factory is MISSING:
                errors.append(f"Missing required key '{field_name}' in TEMPLATES[{index}]")
            continue

        value = template_config[field_name]
        try:
            validate_type(value, type_hint, f"TEMPLATES.{index}.{field_name}")
        except TypeError as e:
            errors.append(str(e))

    return errors


def validate_nested_auth_password_validator(
    index: int, validator_config: dict[str, Any], ignore_errors: list[str]
) -> list[str]:
    """
    Validate a password validator configuration against AuthPasswordValidatorSchema.

    Returns a list of error messages.
    """
    errors = []

    # Check if entire validator should be ignored
    if f"AUTH_PASSWORD_VALIDATORS.{index}" in ignore_errors:
        return errors

    # Get valid keys from AuthPasswordValidatorSchema
    valid_keys = {f.name for f in fields(AuthPasswordValidatorSchema)}
    hints = get_type_hints(AuthPasswordValidatorSchema)
    schema_fields = {f.name: f for f in fields(AuthPasswordValidatorSchema)}

    # Check for invalid keys
    for key in validator_config.keys():
        dotted_path = f"AUTH_PASSWORD_VALIDATORS.{index}.{key}"

        # Skip if this specific key is ignored
        if dotted_path in ignore_errors:
            continue

        if key not in valid_keys:
            error_msg = f"Invalid key '{key}' in AUTH_PASSWORD_VALIDATORS[{index}]."

            # Suggest similar keys if any are found
            suggestions = get_close_matches(key, valid_keys, n=3, cutoff=0.6)
            if suggestions:
                error_msg += f" Did you mean: {', '.join(suggestions)}?"
            else:
                error_msg += f" Valid keys are: {', '.join(sorted(valid_keys))}"

            errors.append(error_msg)

    # Validate required fields and types for non-ignored keys
    for field_name, type_hint in hints.items():
        dotted_path = f"AUTH_PASSWORD_VALIDATORS.{index}.{field_name}"

        # Skip if this specific key is ignored
        if dotted_path in ignore_errors:
            continue

        if field_name not in validator_config:
            f = schema_fields.get(field_name)
            if f.default is MISSING and f.default_factory is MISSING:
                errors.append(f"Missing required key '{field_name}' in AUTH_PASSWORD_VALIDATORS[{index}]")
            continue

        value = validator_config[field_name]
        try:
            validate_type(value, type_hint, f"AUTH_PASSWORD_VALIDATORS.{index}.{field_name}")
        except TypeError as e:
            errors.append(str(e))

    return errors


def validate_data_against_schema(data: dict[str, Any], schema_cls, ignore_errors: list[str] | None = None):
    hints = get_type_hints(schema_cls)
    errors = []

    if ignore_errors is None:
        ignore_errors = []

    # Check for required fields (fields without defaults)

    schema_fields = {f.name: f for f in fields(schema_cls)}

    for name, type_hint in hints.items():
        if name in ignore_errors:
            continue

        if name not in data:
            f = schema_fields.get(name)
            # If the field has no default value (default is MISSING)
            # Note: dataclasses._MISSING_TYPE is internal, but we can check default/default_factory

            if f.default is MISSING and f.default_factory is MISSING:
                errors.append(f"Missing required setting: {name}")

            continue

        value = data[name]

        # First validate the type (this catches issues like wrong types for list items/dict values)
        try:
            validate_type(value, type_hint, name)
        except TypeError as e:
            errors.append(str(e))
            continue  # Skip nested validation if type is wrong

        # Special handling for DATABASES - validate nested configs
        if name == "DATABASES" and isinstance(value, dict):
            for db_name, db_config in value.items():
                if isinstance(db_config, dict):
                    db_errors = validate_nested_database(db_name, db_config, ignore_errors)
                    errors.extend(db_errors)
            continue

        # Special handling for CACHES - validate nested configs
        if name == "CACHES" and isinstance(value, dict):
            for cache_name, cache_config in value.items():
                if isinstance(cache_config, dict):
                    cache_errors = validate_nested_cache(cache_name, cache_config, ignore_errors)
                    errors.extend(cache_errors)
            continue

        # Special handling for TEMPLATES - validate list items
        if name == "TEMPLATES" and isinstance(value, list):
            for index, template_config in enumerate(value):
                if isinstance(template_config, dict):
                    template_errors = validate_nested_template(index, template_config, ignore_errors)
                    errors.extend(template_errors)
            continue

        # Special handling for AUTH_PASSWORD_VALIDATORS - validate list items
        if name == "AUTH_PASSWORD_VALIDATORS" and isinstance(value, list):
            for index, validator_config in enumerate(value):
                if isinstance(validator_config, dict):
                    validator_errors = validate_nested_auth_password_validator(index, validator_config, ignore_errors)
                    errors.extend(validator_errors)
            continue

    # Check for unknown top-level settings (potential typos)
    valid_setting_names = set(hints.keys())
    for setting_name in data.keys():
        # Skip private/magic attributes and ignored settings
        if setting_name.startswith("_") or setting_name in ignore_errors:
            continue

        # Skip if it's a valid setting
        if setting_name in valid_setting_names:
            continue

        # Check if it's a common Django setting we don't validate
        common_unvalidated_settings = {
            "TYPED_SETTINGS_IGNORE_ERRORS",  # Our own setting
            "BASE_DIR",  # Common project setting
            "SITE_ID",  # Django sites framework
            "APPEND_SLASH",
            "PREPEND_WWW",
            "DEFAULT_AUTO_FIELD",
            "USE_THOUSAND_SEPARATOR",
            "NUMBER_GROUPING",
            "DECIMAL_SEPARATOR",
            "THOUSAND_SEPARATOR",
            "DATE_FORMAT",
            "DATETIME_FORMAT",
            "TIME_FORMAT",
            "SHORT_DATE_FORMAT",
            "SHORT_DATETIME_FORMAT",
            "FIRST_DAY_OF_WEEK",
            "DATE_INPUT_FORMATS",
            "TIME_INPUT_FORMATS",
            "DATETIME_INPUT_FORMATS",
            "YEAR_MONTH_FORMAT",
            "MONTH_DAY_FORMAT",
        }

        if setting_name in common_unvalidated_settings:
            continue

        # Found an unknown setting - ONLY suggest / error if we find a close match
        # This allows custom settings that aren't in the schema but catches typos
        suggestions = get_close_matches(setting_name, valid_setting_names, n=3, cutoff=0.6)
        if suggestions:
            error_msg = f"Unknown setting '{setting_name}'. Did you mean: {', '.join(suggestions)}?"
            # errors.append(error_msg)
            logger.debug(error_msg)

    if errors:
        raise ValueError("\n".join(errors))


# --- Integrations ---


def validate_settings_check(app_configs, **kwargs):
    errors = []
    logger.debug("Validating Settings...")

    try:
        current_settings = {key: getattr(settings, key) for key in dir(settings) if key.isupper()}
        ignore_errors = getattr(settings, "TYPED_SETTINGS_IGNORE_ERRORS", [])

        validate_data_against_schema(current_settings, SettingsSchema, ignore_errors=ignore_errors)
        logger.debug("✅ Settings are valid.")
    except Exception as e:
        errors.append(
            Error(
                f"Invalid Typed Setting: {e}",
                hint="Check your settings.py file.",
                obj=settings,
                id="dj_typed_settings.E001",
            )
        )

    return errors


def validate_settings(settings_module_globals: dict[str, Any]):
    logger.debug("Validating Settings...")

    try:
        clean_settings = {k: v for k, v in settings_module_globals.items() if not k.startswith("__")}
        ignore_errors = settings_module_globals.get("TYPED_SETTINGS_IGNORE_ERRORS", [])
        validate_data_against_schema(clean_settings, SettingsSchema, ignore_errors=ignore_errors)

        logger.debug("✅ Settings are valid.")
    except Exception as e:
        logger.error(f"❌ INVALID SETTINGS: {e}")
