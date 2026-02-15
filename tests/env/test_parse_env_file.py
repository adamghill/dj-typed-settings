import pytest

from dj_typed_settings.env import ParseError, parse_env_file


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
