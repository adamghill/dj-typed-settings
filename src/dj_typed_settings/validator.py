import logging
import types
from dataclasses import MISSING, dataclass, fields
from difflib import get_close_matches
from typing import Any, Union, get_args, get_origin, get_type_hints

from django.conf import settings
from django.core.checks import Error

from dj_typed_settings.schema import (
    BaseSchema,
    SettingsSchema,
)

logger = logging.getLogger(__name__)


class SettingsError(ValueError):
    """Base class for settings validation errors."""

    def __init__(self, message: str, *, code: str = "E001", is_base_type_error: bool = False):
        super().__init__(message)
        self.code = code
        self.is_base_type_error = is_base_type_error


def is_ignored(path: str, ignore_errors: list[str]) -> bool:
    """Check if a path or any of its parents are in the ignore list."""
    if not path or not ignore_errors:
        return False
    if path in ignore_errors:
        return True
    parts = path.split(".")
    for i in range(1, len(parts)):
        if ".".join(parts[:i]) in ignore_errors:
            return True
    return False


def format_type(t: Any) -> str:
    """Format a type hint as a string for error messages."""
    if t is Any:
        return "Any"
    if str(t) == "<class 'NoneType'>":
        return "None"

    # Handle GenericAlias like list[str]
    if get_origin(t) is not None:
        return (
            str(t)
            .replace("pathlib.", "")
            .replace("typing.", "")
            .replace("dj_typed_settings.schema.", "")
            .replace("dj_typed_settings.validator.", "")
        )

    if hasattr(t, "__name__"):
        return t.__name__

    return (
        str(t)
        .replace("pathlib.", "")
        .replace("typing.", "")
        .replace("dj_typed_settings.schema.", "")
        .replace("dj_typed_settings.validator.", "")
    )


def validate_type(
    value: Any,
    type_hint: Any,
    error_path: str,
    ignore_path: str | None = None,
    ignore_errors: list[str] | None = None,
) -> None:
    """
    Validates a value against a type hint at runtime. Supports basic types, List, Dict, Union, and Optional.
    Also supports recursive validation of BaseSchema subclasses.
    """

    if ignore_path is None:
        ignore_path = error_path
    if ignore_errors is None:
        ignore_errors = []

    origin = get_origin(type_hint)
    args = get_args(type_hint)

    # Handle Any
    if type_hint is Any:
        return

    # Handle Optional[T] which is Union[T, NoneType] or T | None
    if origin is Union or (hasattr(types, "UnionType") and origin is types.UnionType):
        # Check if value matches ANY of the args
        type_errors = []
        value_errors = []

        for arg in args:
            try:
                validate_type(value, arg, error_path, ignore_path, ignore_errors)
                return
            except (TypeError, ValueError) as e:
                if isinstance(e, SettingsError) and not e.is_base_type_error:
                    value_errors.append(e)
                else:
                    type_errors.append(e)

        if value_errors:
            # If we have value errors, it means the type matched but the content didn't
            raise value_errors[0]

        valid_types = [format_type(arg) for arg in args if str(arg) != "<class 'NoneType'>"]

        if len(valid_types) > 1:
            expected = f"{', '.join(valid_types[:-1])} or {valid_types[-1]}"
        else:
            expected = valid_types[0]

        raise SettingsError(
            f"If '{error_path}' is specified, it must be a {expected}, but got {type(value).__name__}",
            code="E003",
            is_base_type_error=True,
        )

    # Handle List[T]
    if origin is list:
        if not isinstance(value, list):
            raise SettingsError(
                f"'{error_path}' must be list, got {type(value).__name__}", code="E003", is_base_type_error=True
            )

        # Validate list items if type args are provided
        if args and len(args) > 0:
            expected_item_type = args[0]
            for i, item in enumerate(value):
                try:
                    validate_type(item, expected_item_type, f"{error_path}[{i}]", f"{ignore_path}.{i}", ignore_errors)
                except (TypeError, ValueError) as e:
                    # If we are inside a container, any error in items is effectively a value error for the container
                    raise SettingsError(str(e), code=getattr(e, "code", "E003"), is_base_type_error=False) from e
        return

    # Handle Tuple[T, ...]
    if origin is tuple:
        if not isinstance(value, tuple):
            raise SettingsError(
                f"'{error_path}' must be tuple, got {type(value).__name__}", code="E003", is_base_type_error=True
            )

        # Validate tuple items if type args are provided
        if args:
            # Handle Tuple[T, ...]
            if len(args) == 2 and args[1] is Ellipsis:  # noqa: PLR2004
                expected_item_type = args[0]
                for i, item in enumerate(value):
                    try:
                        validate_type(
                            item, expected_item_type, f"{error_path}[{i}]", f"{ignore_path}.{i}", ignore_errors
                        )
                    except (TypeError, ValueError) as e:
                        raise SettingsError(str(e), code=getattr(e, "code", "E003"), is_base_type_error=False) from e
            # Handle fixed-size Tuple[T1, T2, ...]
            elif len(args) == len(value):
                for i, (item, expected_item_type) in enumerate(zip(value, args, strict=False)):
                    try:
                        validate_type(
                            item, expected_item_type, f"{error_path}[{i}]", f"{ignore_path}.{i}", ignore_errors
                        )
                    except (TypeError, ValueError) as e:
                        raise SettingsError(str(e), code=getattr(e, "code", "E003"), is_base_type_error=False) from e
            elif len(args) != len(value):
                raise SettingsError(
                    f"'{error_path}' must have {len(args)} items, got {len(value)}",
                    code="E003",
                    is_base_type_error=False,
                )

        return

    # Handle Dict[K, V]
    if origin is dict:
        if not isinstance(value, dict):
            raise SettingsError(
                f"'{error_path}' must be a dict, got {type(value).__name__}", code="E003", is_base_type_error=True
            )

        # Validate dict values if type args are provided (ignoring keys for now as they are usually str)
        if args and len(args) > 1:
            expected_value_type = args[1]
            for key, val in value.items():
                key_repr = f"'{key}'" if isinstance(key, str) else repr(key)
                try:
                    validate_type(
                        val, expected_value_type, f"{error_path}[{key_repr}]", f"{ignore_path}.{key}", ignore_errors
                    )
                except (TypeError, ValueError) as e:
                    raise SettingsError(str(e), code=getattr(e, "code", "E003"), is_base_type_error=False) from e
        return

    # Handle BaseSchema subclasses (recursive validation)
    if isinstance(type_hint, type) and issubclass(type_hint, BaseSchema):
        if not isinstance(value, dict):
            raise SettingsError(
                f"'{error_path}' must be a dict, got {type(value).__name__}", code="E003", is_base_type_error=True
            )
        # Note: We use validate_data_against_schema here to get full validation including unknown keys
        validate_data_against_schema(
            value, type_hint, ignore_errors=ignore_errors, error_path=error_path, ignore_path=ignore_path
        )
        return

    # Handle Simple Types (int, str, bool, etc.)
    if isinstance(type_hint, type):
        if not isinstance(value, type_hint):
            expected = format_type(type_hint)
            raise SettingsError(
                f"'{error_path}' must be {expected}, got {type(value).__name__}", code="E003", is_base_type_error=True
            )
        return


@dataclass
class SettingsValidationError(ValueError):
    """Exception raised when settings validation fails, containing multiple specific errors."""

    errors: list[SettingsError]

    def __str__(self):
        return "\n".join(str(e) for e in self.errors)


def validate_data_against_schema(
    data: dict[str, Any],
    schema_cls: type[BaseSchema],
    ignore_errors: list[str] | None = None,
    error_path: str = "",
    ignore_path: str = "",
) -> None:
    """
    Validates a dictionary of data against a BaseSchema subclass.
    Supports recursive validation and checks for required fields and types.
    """
    hints = get_type_hints(schema_cls)
    errors: list[SettingsError] = []

    if ignore_errors is None:
        ignore_errors = []

    schema_fields = {f.name: f for f in fields(schema_cls)}

    for name, type_hint in hints.items():
        new_error_path = f"{error_path}.{name}" if error_path else name
        new_ignore_path = f"{ignore_path}.{name}" if ignore_path else name

        # Skip if this specific setting is ignored
        if is_ignored(new_ignore_path, ignore_errors):
            continue

        if name not in data:
            f = schema_fields.get(name)
            # If the field has no default value (default is MISSING)
            if f.default is MISSING and f.default_factory is MISSING:
                errors.append(SettingsError(f"Missing required setting: {new_error_path}", code="E002"))
            continue

        value = data[name]

        # Validate the type recursively
        try:
            validate_type(value, type_hint, new_error_path, new_ignore_path, ignore_errors)
        except (TypeError, ValueError) as e:
            if isinstance(e, SettingsError):
                errors.append(e)
            else:
                code = getattr(e, "code", "E003")
                errors.append(SettingsError(str(e), code=code))

    # Check for unknown settings (potential typos) - keep strict for nested
    valid_setting_names = set(hints.keys())
    for key in data.keys():
        new_ignore_path = f"{ignore_path}.{key}" if ignore_path else key

        # Skip if ignored
        if is_ignored(new_ignore_path, ignore_errors):
            continue

        # Skip private/magic attributes
        if key.startswith("_"):
            continue

        if key not in valid_setting_names:
            if not ignore_path:
                continue

            # Found an unknown setting in nested structure - suggest close matches
            error_prefix = f"Invalid key '{key}' in {error_path}"
            suggestions = get_close_matches(key, valid_setting_names, n=3, cutoff=0.6)
            if suggestions:
                error_msg = f"{error_prefix}. Did you mean: {', '.join(suggestions)}?"
            else:
                error_msg = f"{error_prefix}. Valid keys are: {', '.join(sorted(valid_setting_names))}"

            errors.append(SettingsError(error_msg, code="E001"))

    if errors:
        raise SettingsValidationError(errors)


# --- Integrations ---


def validate_settings_check(app_configs, **kwargs):  # noqa: ARG001
    errors = []
    logger.debug("Validating Settings...")

    try:
        current_settings = {key: getattr(settings, key) for key in dir(settings) if key.isupper()}
        ignore_errors = getattr(settings, "TYPED_SETTINGS_IGNORE_ERRORS", [])

        validate_data_against_schema(current_settings, SettingsSchema, ignore_errors=ignore_errors)
        logger.debug("✅ Settings are valid.")
    except SettingsValidationError as e:
        for err in e.errors:
            errors.append(
                Error(
                    str(err),
                    hint="Check your settings.py file.",
                    obj=settings,
                    id=f"dj_typed_settings.{err.code}",
                )
            )
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


def cast_to_type(value: Any, type_hint: Any, list_delimiter: str = ",") -> Any:
    """
    Attempts to cast a value to a given type hint.
    Primarily used for converting string-based settings (e.g. from environment variables).
    """
    if type_hint is Any:
        return value

    origin = get_origin(type_hint)
    args = get_args(type_hint)

    # Handle Optional[T] / Union[T, None] / T | None
    if origin is Union or (hasattr(types, "UnionType") and origin is types.UnionType):
        if value is None or (isinstance(value, str) and value.lower() == "none"):
            return None
        # Try casting to each type in the union (except NoneType)
        for arg in args:
            if str(arg) == "<class 'NoneType'>":
                continue
            try:
                return cast_to_type(value, arg, list_delimiter=list_delimiter)
            except (ValueError, TypeError):
                continue
        return value

    # Handle basic types if value is a string
    if isinstance(value, str):
        target_type = type_hint if origin is None else origin

        if target_type is bool:
            v = value.lower()
            if v in ("true", "1"):
                return True
            if v in ("false", "0"):
                return False
            return value

        if target_type is int:
            try:
                return int(value)
            except ValueError:
                return value

        if target_type is float:
            try:
                return float(value)
            except ValueError:
                return value

        if target_type is list:
            items = [item.strip() for item in value.split(list_delimiter)]
            if args:
                item_type = args[0]
                return [cast_to_type(item, item_type, list_delimiter=list_delimiter) for item in items]
            return items

    return value


def fix_types(settings_globals: dict[str, Any], list_delimiter: str = ",") -> None:
    """
    Iterates through the SettingsSchema fields and attempts to cast any matching
    values in settings_globals to the correct type.
    """
    hints = get_type_hints(SettingsSchema)

    for name, type_hint in hints.items():
        if name in settings_globals:
            current_value = settings_globals[name]
            new_value = cast_to_type(current_value, type_hint, list_delimiter=list_delimiter)
            if new_value != current_value:
                logger.debug(f"Fixed up {name}: {type(current_value).__name__} -> {type(new_value).__name__}")
                settings_globals[name] = new_value
