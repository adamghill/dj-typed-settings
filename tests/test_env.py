import os

import pytest

from dj_typed_settings.env import ParseError, load_env, parse_env_file


def test_parse_simple():
    lines = ["KEY=VALUE\n", "FOO=BAR"]
    result = parse_env_file(lines)
    assert result == {"KEY": "VALUE", "FOO": "BAR"}


def test_parse_export():
    lines = ["export KEY=VALUE\n"]
    result = parse_env_file(lines)
    assert result == {"KEY": "VALUE"}


def test_parse_comments():
    lines = ["# Comment\n", "KEY=VALUE # Inline comment\n", "  # Another comment"]
    result = parse_env_file(lines)
    assert result == {"KEY": "VALUE"}


def test_parse_quotes():
    lines = ["SINGLE='single quoted'\n", 'DOUBLE="double quoted"\n', 'INNER_HASH="value with # hash"\n']
    result = parse_env_file(lines)
    assert result == {"SINGLE": "single quoted", "DOUBLE": "double quoted", "INNER_HASH": "value with # hash"}


def test_parse_escaping():
    lines = ['ESCAPED_QUOTE="quote \\" here"\n', 'ESCAPED_BACKSLASH="backslash \\\\ here"\n']
    result = parse_env_file(lines)
    assert result == {"ESCAPED_QUOTE": 'quote " here', "ESCAPED_BACKSLASH": "backslash \\ here"}


def test_parse_multiline_backslash():
    lines = ["MULTILINE=line1\\\n", "line2\\\n", "line3"]
    result = parse_env_file(lines)
    assert result == {"MULTILINE": "line1line2line3"}


def test_parse_error_expected_assignment():
    lines = ["INVALID_LINE\n"]
    with pytest.raises(ParseError, match="Expected"):
        parse_env_file(lines)


def test_parse_error_expected_assignment_operator():
    lines = ["KEY VALUE\n"]
    with pytest.raises(ParseError, match="Expected assignment operator"):
        parse_env_file(lines)


def test_parse_error_unmatched_quote():
    lines = ['KEY="unmatched\n']
    with pytest.raises(ParseError, match="Unmatched double quote"):
        parse_env_file(lines)


def test_load_env(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("LOADED_VAR=success\n")

    # Ensure it's not in environ
    if "LOADED_VAR" in os.environ:
        del os.environ["LOADED_VAR"]

    load_env(env_file)
    assert os.environ["LOADED_VAR"] == "success"

    # Test no override
    os.environ["LOADED_VAR"] = "original"
    load_env(env_file, override=False)
    assert os.environ["LOADED_VAR"] == "original"

    # Test override
    load_env(env_file, override=True)
    assert os.environ["LOADED_VAR"] == "success"


def test_load_env_nonexistent():
    # Should not raise error
    load_env("nonexistent_file")


def test_load_env_upward_search(tmp_path, monkeypatch):
    # Setup:
    # project/
    #   manage.py
    #   .env (target)
    #   app/
    #     (CWD here)

    project_dir = tmp_path / "project"
    project_dir.mkdir()
    (project_dir / "manage.py").touch()
    (project_dir / ".env").write_text("UPWARD_VAR=found\n")

    app_dir = project_dir / "app"
    app_dir.mkdir()

    monkeypatch.chdir(app_dir)

    if "UPWARD_VAR" in os.environ:
        del os.environ["UPWARD_VAR"]

    load_env()
    assert os.environ["UPWARD_VAR"] == "found"


def test_load_env_stops_at_manage_py(tmp_path, monkeypatch):
    # Setup:
    # project/
    #   .env (should NOT be found)
    #   subproject/
    #     manage.py
    #     app/
    #       (CWD here)

    project_dir = tmp_path / "project"
    project_dir.mkdir()
    (project_dir / ".env").write_text("DANGEROUS_VAR=wrong\n")

    subproject_dir = project_dir / "subproject"
    subproject_dir.mkdir()
    (subproject_dir / "manage.py").touch()

    app_dir = subproject_dir / "app"
    app_dir.mkdir()

    monkeypatch.chdir(app_dir)

    if "DANGEROUS_VAR" in os.environ:
        del os.environ["DANGEROUS_VAR"]

    load_env()
    assert "DANGEROUS_VAR" not in os.environ
