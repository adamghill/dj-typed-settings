from pathlib import Path
from typing import get_type_hints

from dj_typed_settings import defaults


def test_defaults_file_exists():
    """Test that defaults.py exists and can be imported."""
    defaults_path = Path(defaults.__file__)
    assert defaults_path.exists()
    assert defaults_path.name == "defaults.py"


def test_defaults_content():
    """Test that defaults.py contains expected settings and docstrings."""
    assert hasattr(defaults, "DEBUG")
    assert defaults.DEBUG is False

    assert hasattr(defaults, "SECRET_KEY")
    assert defaults.SECRET_KEY == ""  # Required setting default

    assert hasattr(defaults, "INSTALLED_APPS")
    assert isinstance(defaults.INSTALLED_APPS, list)

    # Check for docstrings (which are just comments in the file, but we can check if the file content has them)
    # Or just check that the variable is defined. Docstrings are not runtime accessible variables.
    pass


def test_defaults_docstrings_in_file():
    """Test that defaults.py file content includes docstrings."""
    with open(defaults.__file__) as f:
        content = f.read()

    assert '"""' in content
    assert "A boolean that turns on/off debug mode." in content


def test_defaults_type_hints_resolvable():
    """Test that all type hints in defaults.py are resolvable."""

    # This will raise a NameError if any type hint references an undefined name
    # (unless from __future__ import annotations is used, in which case it might still fail if evaluated)
    # Using get_type_hints(defaults) forces evaluation of the hints.
    hints = get_type_hints(defaults)

    assert "DEBUG" in hints
    assert hints["DEBUG"] is bool

    assert "DATABASES" in hints
    # DATABASES: dict[str, DatabaseSchema] = {}
    # The hint should be resolvable now
    assert "DatabaseSchema" in str(hints["DATABASES"])
