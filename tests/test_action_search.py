from unittest.mock import MagicMock

import pytest
from InquirerPy.validator import ValidationError

from actions.search import classify_input, not_empty_validator, search


@pytest.mark.parametrize(
    "input_value, expected",
    [
        ("192.168.0.1", "ip"),
        ("8.8.8.8", "ip"),
        ("http://example.com", "url"),
        ("malicious.site", "url"),
    ],
)
def test_classify_input(input_value, expected):
    assert classify_input(input_value) == expected


def test_search_executes_ip_query():
    conn = MagicMock()
    cursor = MagicMock()
    conn.cursor.return_value = cursor
    cursor.fetchall.return_value = [(1, "8.8.8.8", "URLHaus", "2025-05-11 11:24:30.410682+00")]

    result = search(conn, "8.8.8.8")

    cursor.execute.assert_called_once_with(
        "SELECT id, ip, sou.name, created_at FROM ips JOIN sources sou ON (ips.source_id = sou.id) WHERE ip = %s",
        ("8.8.8.8",),
    )
    assert result == [(1, "8.8.8.8", "URLHaus", "2025-05-11 11:24:30.410682+00")]


def test_search_executes_url_query():
    conn = MagicMock()
    cursor = MagicMock()
    conn.cursor.return_value = cursor
    cursor.fetchall.return_value = [(1, "http://evil.com")]

    result = search(conn, "http://evil.com")

    cursor.execute.assert_called_once()
    assert "FROM links" in cursor.execute.call_args[0][0]
    assert result == [(1, "http://evil.com")]


def test_not_empty_validator_passes():
    assert not_empty_validator("abc") is True


def test_not_empty_validator_raises():
    with pytest.raises(ValidationError):
        not_empty_validator("   ")
