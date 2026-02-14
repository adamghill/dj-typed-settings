import argparse
import ast
import inspect
import json
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

URL = "https://raw.githubusercontent.com/django/django/main/django/conf/global_settings.py"
OUTPUT_FILE = Path(__file__).parent.parent / "src" / "dj_typed_settings" / "schema.py"
DEFAULTS_OUTPUT_FILE = Path(__file__).parent.parent / "src" / "dj_typed_settings" / "defaults.py"

# Manual overrides for settings that inference can't handle perfectly (e.g., None defaults)
TYPE_OVERRIDES = {
    "STATIC_ROOT": "str | Path | None",
    "STATIC_URL": "str | None",
    "MEDIA_ROOT": "str | Path | None",
    "MEDIA_URL": "str | None",
    "FORCE_SCRIPT_NAME": "str | None",
    "WSGI_APPLICATION": "str | None",
    "ASGI_APPLICATION": "str | None",
    "LANGUAGE_COOKIE_AGE": "int | None",
    "LANGUAGE_COOKIE_DOMAIN": "str | None",
    "LANGUAGE_COOKIE_SAMESITE": "str | None",
    "SECURE_SSL_HOST": "str | None",
    "LOGOUT_REDIRECT_URL": "str | None",
    "FORMAT_MODULE_PATH": "str | None",
    "FILE_UPLOAD_TEMP_DIR": "str | Path | None",
    "FILE_UPLOAD_DIRECTORY_PERMISSIONS": "int | None",
    "SESSION_FILE_PATH": "str | Path | None",
    "CSRF_COOKIE_DOMAIN": "str | None",
    "EMAIL_TIMEOUT": "int | None",
    "EMAIL_SSL_CERTFILE": "str | None",
    "EMAIL_SSL_KEYFILE": "str | None",
    "SECURE_PROXY_SSL_HEADER": "tuple | list | None",
    "MANAGERS": "list[tuple[str, str]] | tuple[tuple[str, str], ...]",
    "ADMINS": "list[tuple[str, str]] | tuple[tuple[str, str], ...]",
    "DATABASES": "dict[str, dict[str, Any]]",
    "CACHES": "dict[str, dict[str, Any]]",
    "TEMPLATES": "list[dict[str, Any]] | tuple[dict[str, Any], ...]",
    "AUTH_PASSWORD_VALIDATORS": "list[dict[str, Any]] | tuple[dict[str, Any], ...]",
    "INSTALLED_APPS": "list[str] | tuple[str, ...]",
    "MIDDLEWARE": "list[str] | tuple[str, ...]",
    "AUTHENTICATION_BACKENDS": "list[str] | tuple[str, ...]",
    "STATICFILES_DIRS": "list[str] | tuple[str, ...]",
}

REQUIRED_SETTINGS = ["SECRET_KEY"]

# Manual overrides for default values
# We store RAW values here. The generator will use repr() to write them to defaults.py
DEFAULTS_OVERRIDES = {
    "LANGUAGES": [
        ("af", "Afrikaans"),
        ("ar", "Arabic"),
        ("ar-dz", "Algerian Arabic"),
        ("ast", "Asturian"),
        ("az", "Azerbaijani"),
        ("bg", "Bulgarian"),
        ("be", "Belarusian"),
        ("bn", "Bengali"),
        ("br", "Breton"),
        ("bs", "Bosnian"),
        ("ca", "Catalan"),
        ("ckb", "Central Kurdish (Sorani)"),
        ("cs", "Czech"),
        ("cy", "Welsh"),
        ("da", "Danish"),
        ("de", "German"),
        ("dsb", "Lower Sorbian"),
        ("el", "Greek"),
        ("en", "English"),
        ("en-au", "Australian English"),
        ("en-gb", "British English"),
        ("eo", "Esperanto"),
        ("es", "Spanish"),
        ("es-ar", "Argentinian Spanish"),
        ("es-co", "Colombian Spanish"),
        ("es-mx", "Mexican Spanish"),
        ("es-ni", "Nicaraguan Spanish"),
        ("es-ve", "Venezuelan Spanish"),
        ("et", "Estonian"),
        ("eu", "Basque"),
        ("fa", "Persian"),
        ("fi", "Finnish"),
        ("fr", "French"),
        ("fy", "Frisian"),
        ("ga", "Irish"),
        ("gd", "Scottish Gaelic"),
        ("gl", "Galician"),
        ("he", "Hebrew"),
        ("hi", "Hindi"),
        ("hr", "Croatian"),
        ("hsb", "Upper Sorbian"),
        ("hu", "Hungarian"),
        ("hy", "Armenian"),
        ("ia", "Interlingua"),
        ("id", "Indonesian"),
        ("ig", "Igbo"),
        ("io", "Ido"),
        ("is", "Icelandic"),
        ("it", "Italian"),
        ("ja", "Japanese"),
        ("ka", "Georgian"),
        ("kab", "Kabyle"),
        ("kk", "Kazakh"),
        ("km", "Khmer"),
        ("kn", "Kannada"),
        ("ko", "Korean"),
        ("ky", "Kyrgyz"),
        ("lb", "Luxembourgish"),
        ("lt", "Lithuanian"),
        ("lv", "Latvian"),
        ("mk", "Macedonian"),
        ("ml", "Malayalam"),
        ("mn", "Mongolian"),
        ("mr", "Marathi"),
        ("ms", "Malay"),
        ("my", "Burmese"),
        ("nb", "Norwegian Bokmål"),
        ("ne", "Nepali"),
        ("nl", "Dutch"),
        ("nn", "Norwegian Nynorsk"),
        ("os", "Ossetic"),
        ("pa", "Punjabi"),
        ("pl", "Polish"),
        ("pt", "Portuguese"),
        ("pt-br", "Brazilian Portuguese"),
        ("ro", "Romanian"),
        ("ru", "Russian"),
        ("sk", "Slovak"),
        ("sl", "Slovenian"),
        ("sq", "Albanian"),
        ("sr", "Serbian"),
        ("sr-latn", "Serbian Latin"),
        ("sv", "Swedish"),
        ("sw", "Swahili"),
        ("ta", "Tamil"),
        ("te", "Telugu"),
        ("tg", "Tajik"),
        ("th", "Thai"),
        ("tk", "Turkmen"),
        ("tr", "Turkish"),
        ("tt", "Tatar"),
        ("udm", "Udmurt"),
        ("ug", "Uyghur"),
        ("uk", "Ukrainian"),
        ("ur", "Urdu"),
        ("uz", "Uzbek"),
        ("vi", "Vietnamese"),
        ("zh-hans", "Simplified Chinese"),
        ("zh-hant", "Traditional Chinese"),
    ],
}


# Manual overrides for docstrings when they are missing or poor in the source
DOCSTRING_OVERRIDES = {
    "DEBUG": """
A boolean that turns on/off debug mode.
""".strip(),
    "LANGUAGES": """
A list of all available languages. The list is a list of two-tuples in the
format (language code, language name) - for example, ('ja', 'Japanese').
This setting is used to determine which languages are available for language
selection.
""".strip(),
}


def infer_type(node):
    if isinstance(node, ast.Constant):
        if node.value is None:
            return "Any | None"
        return type(node.value).__name__
    elif isinstance(node, ast.List):
        return "list | tuple"
    elif isinstance(node, ast.Dict):
        return "dict"
    elif isinstance(node, ast.Tuple):
        return "tuple | list"
    elif isinstance(node, ast.Name):
        if node.id in ["True", "False"]:
            return "bool"
    elif isinstance(node, (ast.BinOp, ast.UnaryOp)):
        try:
            val = eval(compile(ast.Expression(node), "", "eval"))  # noqa: S307
            return type(val).__name__
        except:  # noqa: E722
            return "Any"
    return "Any"


def extract_default_value(node):
    """Extract the default value from an AST node as a Python literal string."""
    if isinstance(node, ast.Constant):
        value = node.value
        if value is None:
            return "None"
        elif isinstance(value, str):
            return json.dumps(value)
        elif isinstance(value, (int, float, bool)):
            return str(value)
        return None
    elif isinstance(node, ast.List):
        if len(node.elts) == 0:
            return "[]"
        try:
            elements = []
            for elt in node.elts:
                if isinstance(elt, ast.Constant):
                    if isinstance(elt.value, str):
                        elements.append(json.dumps(elt.value))
                    else:
                        elements.append(repr(elt.value))
                elif isinstance(elt, ast.Tuple):
                    return None
                else:
                    return None
            return "[" + ", ".join(elements) + "]"
        except:  # noqa: E722
            return None
    elif isinstance(node, ast.Dict):
        if len(node.keys) == 0:
            return "{}"
        return None
    elif isinstance(node, ast.Tuple):
        if len(node.elts) == 0:
            return "()"
        return None
    elif isinstance(node, ast.Name):
        if node.id in ["True", "False"]:
            return node.id
        return None
    return None


def get_autocomplete_type(type_hint: str, has_default: bool) -> str:
    """Convert validation type to stricter autocomplete type."""
    if not has_default:
        return type_hint
    if " | None" in type_hint:
        type_hint = type_hint.replace(" | None", "")
    return type_hint


def extract_docstring(lines, lineno):
    """Extract comments preceding the assignment as a docstring."""
    comments = []
    # Look backwards from the line before assignment
    idx = lineno - 2  # lineno is 1-indexed

    # First, skip backwards over blank lines to find the *end* of the comment block
    while idx >= 0:
        if lines[idx].strip():
            break
        idx -= 1

    while idx >= 0:
        line = lines[idx].strip()
        if not line:
            if comments:  # Stop at blank line if we have comments (paragraph break)
                break
            idx -= 1
            continue

        if line.startswith("#"):
            # Check if this is a section header or separator to ignore
            # e.g. "####", "CORE    #"
            clean_line = line.replace("#", "").strip()
            if not clean_line or set(clean_line) == {"-"}:
                # Skip purely decorative lines like "#######" or "# ------- #"
                # If we already have comments, we probably hit the top of the block, so stop?
                # No, sometimes headers are *above* the docstring.
                # But usually headers are above the *setting*.
                # If we see a header line, we should probably stop if we already have content?
                # Or skip it if we don't?

                # If we encounter a section header, that divides this setting from previous ones.
                break

            # If the line ends with a bunch of #s, it's likely a header frame
            if line.rstrip().endswith("####") or line.rstrip().endswith(" #"):
                # Likely "CORE             #" style header
                break

            # Clean up the comment delimiter
            content = line.lstrip("#").strip()
            if content:
                comments.insert(0, content)
            idx -= 1
        else:
            break  # Stop at non-comment line

    if not comments:
        return None

    return "\n".join(comments)


def generate_schema(url=None):
    content = ""

    if url:
        print(f"Downloading from {url}...")
        try:
            with urllib.request.urlopen(url) as response:
                content = response.read().decode("utf-8")
        except Exception as e:
            print(f"Error downloading from {url}: {e}")
            sys.exit(1)
    else:
        print("Attempting to read from installed Django version...")
        try:
            from django.conf import global_settings

            content = inspect.getsource(global_settings)
            print(f"Successfully read global_settings from {global_settings.__file__}")
        except ImportError:
            print("Error: Django is not installed in the current environment.")
            print("Please install Django or provide a URL using --url.")
            sys.exit(1)
        except Exception as e:
            print(f"Error reading installed Django settings: {e}")
            sys.exit(1)

    source_lines = content.splitlines()
    tree = ast.parse(content)

    non_default_fields = []
    default_fields = []
    defaults_file_fields = []  # Fields for defaults.py
    seen = set()

    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id.isupper():
                    name = target.id
                    if name in seen:
                        continue
                    seen.add(name)

                    type_hint = TYPE_OVERRIDES.get(name)
                    inferred = infer_type(node.value)

                    if not type_hint:
                        type_hint = inferred

                    has_default = True
                    default_val = "None"
                    actual_default = extract_default_value(node.value)

                    # Extract docstring from comments
                    docstring = DOCSTRING_OVERRIDES.get(name) or extract_docstring(source_lines, node.lineno)

                    if name in REQUIRED_SETTINGS:
                        has_default = False

                    # Collect for defaults.py
                    autocomplete_type = get_autocomplete_type(type_hint, has_default)

                    # Check manual override
                    manual_val = DEFAULTS_OVERRIDES.get(name)

                    def format_value(v):
                        if isinstance(v, str):
                            return json.dumps(v)
                        if isinstance(v, list):
                            return "[" + ", ".join(format_value(x) for x in v) + "]"
                        if isinstance(v, tuple):
                            return "(" + ", ".join(format_value(x) for x in v) + ")"
                        if isinstance(v, dict):
                            return (
                                "{" + ", ".join(f"{json.dumps(k)}: {format_value(val)}" for k, val in v.items()) + "}"
                            )
                        return repr(v)

                    final_val = None
                    if manual_val is not None:
                        # Use custom formatter to ensure double quotes
                        final_val = format_value(manual_val)
                    elif actual_default:
                        final_val = actual_default
                    elif has_default:
                        # Fallback for complex defaults
                        if "list" in type_hint or "tuple" in type_hint:
                            final_val = "[]"
                        elif "dict" in type_hint:
                            final_val = "{}"
                        else:
                            final_val = "None"
                    else:
                        final_val = '""'  # Default for required fields

                    defaults_file_fields.append((name, autocomplete_type, final_val, docstring))

                    # Logic for SettingsSchema (validation) - No change needed here for docstrings
                    # ...

                    # Logic for SettingsSchema (validation)
                    if "list" in type_hint or "tuple" in type_hint:
                        default_val = "field(default_factory=list)"
                    elif "dict" in type_hint:
                        default_val = "field(default_factory=dict)"
                    else:
                        # If we have a concrete default (not None), use strict type
                        if has_default and final_val not in ("None", "[]", "{}", "()"):
                            default_val = final_val
                        else:
                            if "None" not in type_hint and type_hint != "Any":
                                type_hint = f"{type_hint} | None"
                            default_val = "None"

                    field_line = f"    {name}: {type_hint}"
                    if has_default:
                        field_line += f" = {default_val}"

                    if docstring:
                        safe_doc = docstring.replace('"""', '\\"\\"\\"')
                        # Indent docstring
                        indented_doc = "\n    ".join(safe_doc.splitlines())
                        field_line += f'\n    r"""\n    {indented_doc}\n    """'

                    if has_default:
                        default_fields.append(field_line)
                    else:
                        non_default_fields.append(field_line)

    # Generate validation schema (existing)
    lines = [
        '"""',
        f"Generated by scripts/generate_schema.py on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "DO NOT EDIT MANUALLY - use the generator script to update.",
        '"""',
        "from dataclasses import asdict, dataclass, field",
        "from pathlib import Path",
        "from typing import Any",
        "",
        "",
        "@dataclass",
        "class BaseSchema:",
        "    def to_dict(self) -> dict[str, Any]:",
        "        # Exclude None values",
        "        return {k: v for k, v in asdict(self).items() if v is not None}",
        "",
        "",
        "@dataclass",
        "class TemplateSchema(BaseSchema):",
        "    BACKEND: str",
        '    """',
        "    The template backend to use.",
        '    """',
        "    DIRS: list[str] = field(default_factory=list)",
        '    """',
        "    Directories where the engine should look for template source files, in search order.",
        '    """',
        "    APP_DIRS: bool = False",
        '    """',
        "    Whether the engine should look for template source files inside installed applications.",
        '    """',
        "    OPTIONS: dict[str, Any] = field(default_factory=dict)",
        '    """',
        "    Extra parameters to pass to the template backend.",
        '    """',
        "    NAME: str | None = None",
        '    """',
        "    The alias for this particular template engine.",
        '    """',
        "",
        "",
        "@dataclass",
        "class DatabaseSchema(BaseSchema):",
        "    ENGINE: str",
        '    """',
        "    The database backend to use.",
        '    """',
        "    NAME: str",
        '    """',
        "    The name of the database to use.",
        '    """',
        "    USER: str | None = None",
        '    """',
        "    The username to use when connecting to the database.",
        '    """',
        "    PASSWORD: str | None = None",
        '    """',
        "    The password to use when connecting to the database.",
        '    """',
        "    HOST: str | None = None",
        '    """',
        "    Which host to use when connecting to the database.",
        '    """',
        "    PORT: str | int | None = None",
        '    """',
        "    The port to use when connecting to the database.",
        '    """',
        "    ATOMIC_REQUESTS: bool = False",
        '    """',
        "    Set this to True to wrap each view in a transaction on this database.",
        '    """',
        "    AUTOCOMMIT: bool = True",
        '    """',
        "    Set this to False if you want to disable Django's transaction management and implement your own.",
        '    """',
        "    CONN_MAX_AGE: int = 0",
        '    """',
        "    The lifetime of a database connection, as an integer of seconds.",
        '    """',
        "    OPTIONS: dict[str, Any] = field(default_factory=dict)",
        '    """',
        "    Extra parameters to use when connecting to the database.",
        '    """',
        "    TIME_ZONE: str | None = None",
        '    """',
        "    A string representing the time zone for this database connection or None.",
        '    """',
        "    TEST: dict[str, Any] = field(default_factory=dict)",
        '    """',
        "    A dictionary of settings for test databases.",
        '    """',
        "    CONN_HEALTH_CHECKS: bool = False",
        '    """',
        "    If set to True, existing persistent database connections will be health checked before they are reused.",
        '    """',
        "",
        "",
        "@dataclass",
        "class CacheSchema(BaseSchema):",
        "    BACKEND: str",
        '    """',
        "    The cache backend to use.",
        '    """',
        "    LOCATION: str | None = None",
        '    """',
        "    The location of the cache to use.",
        '    """',
        "    TIMEOUT: int | None = None",
        '    """',
        "    The number of seconds before a cache entry is considered stale.",
        '    """',
        "    OPTIONS: dict[str, Any] = field(default_factory=dict)",
        '    """',
        "    Extra parameters to pass to the cache backend.",
        '    """',
        "    KEY_PREFIX: str | None = None",
        '    """',
        "    A string that will be automatically included (prepended by default) to all cache keys used by the Django server.",
        '    """',
        "    KEY_FUNCTION: str | None = None",
        '    """',
        "    A string containing a dotted path to a function (or any callable) that defines how to compose a prefix, version and key into a final cache key.",
        '    """',
        "    VERSION: int | None = None",
        '    """',
        "    The default version number for cache keys generated by the Django server.",
        '    """',
        "",
        "",
        "@dataclass",
        "class AuthPasswordValidatorSchema(BaseSchema):",
        "    NAME: str",
        '    """',
        "    The dotted path to the password validator class.",
        '    """',
        "    OPTIONS: dict[str, Any] = field(default_factory=dict)",
        '    """',
        "    Optional parameters for the password validator.",
        '    """',
        "",
        "",
        "@dataclass",
        "class SettingsSchema(BaseSchema):",
    ]

    lines.extend(non_default_fields)
    lines.extend(default_fields)

    with open(OUTPUT_FILE, "w") as f:
        f.write("\n".join(lines) + "\n")

    print(f"Schema generated successfully at {OUTPUT_FILE}")

    # Generate defaults file
    generate_defaults_file(defaults_file_fields)


def generate_defaults_file(settings_fields):
    """Generate defaults.py with explicit assignments."""
    lines = [
        '"""',
        "Django settings defaults.",
        "Import this module using `from dj_typed_settings.defaults import *` in settings.py",
        "to get IDE autocomplete and Django's actual default values.",
        "",
        f"Generated by scripts/generate_schema.py on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "DO NOT EDIT MANUALLY - use the generator script to update.",
        '"""',
        "from pathlib import Path",
        "from typing import Any",
        "",
    ]

    for name, type_hint, value, docstring in settings_fields:
        lines.append(f"{name}: {type_hint} = {value}")
        if docstring:
            # Use triple quotes for multi-line or single-line docstrings
            # Indent if needed? No, module level variables don't need indent
            # Escape quotes?
            safe_doc = docstring.replace('"""', '\\"\\"\\"')
            lines.append(f'r"""\n{safe_doc}\n"""')
        lines.append("")  # Spacer

    DEFAULTS_OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DEFAULTS_OUTPUT_FILE, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"Defaults file generated at {DEFAULTS_OUTPUT_FILE}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Django settings schema.")
    parser.add_argument("--url", help="URL to download global_settings.py from", default=None)
    args = parser.parse_args()

    generate_schema(url=args.url)
