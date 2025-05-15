from unittest.mock import MagicMock, patch

import polars as pl
import pytest

from actions.store import db_store
from src_type import SrcType


@patch("actions.store.logger")
def test_db_store_empty_dataframe_logs(mock_logger):
    conn = MagicMock()
    df = pl.DataFrame(schema={"url": pl.Utf8})
    db_store(1, "TestSource", conn, SrcType.URL, df)
    mock_logger.info.assert_called_once_with("Source <TestSource> returned no data.")
    conn.cursor.assert_not_called()


def test_db_store_url_inserts_correct_query():
    conn = MagicMock()
    cursor = MagicMock()
    conn.cursor.return_value.__enter__.return_value = cursor

    df = pl.DataFrame({"url": ["http://evil.com", "http://phish.com"]})
    db_store(42, "URLHaus", conn, SrcType.URL, df)

    cursor.executemany.assert_called_once()
    args, _ = cursor.executemany.call_args
    query, rows = args
    assert "INSERT INTO links" in query
    assert rows == [("http://evil.com", 42), ("http://phish.com", 42)]
    conn.commit.assert_called_once()


def test_db_store_ip_inserts_correct_query():
    conn = MagicMock()
    cursor = MagicMock()
    conn.cursor.return_value.__enter__.return_value = cursor

    df = pl.DataFrame({"ip": ["8.8.8.8", "1.1.1.1"]})
    db_store(99, "AlienVault", conn, SrcType.IP, df)

    cursor.executemany.assert_called_once()
    args, _ = cursor.executemany.call_args
    query, rows = args
    assert "INSERT INTO ips" in query
    assert rows == [("8.8.8.8", 99), ("1.1.1.1", 99)]
    conn.commit.assert_called_once()


def test_db_store_unsupported_type_raises():
    conn = MagicMock()
    df = pl.DataFrame({"domain": ["bad.com"]})

    with pytest.raises(ValueError, match="'unsupported' is not a valid SrcType"):
        db_store(1, "Unsupported", conn, SrcType("unsupported"), df)


def test_db_store_database_error_raises():
    conn = MagicMock()
    cursor = MagicMock()
    conn.cursor.return_value.__enter__.return_value = cursor
    cursor.executemany.side_effect = Exception("db error")

    df = pl.DataFrame({"url": ["http://fail.com"]})
    with pytest.raises(RuntimeError, match="Error during storing data"):
        db_store(1, "BrokenSource", conn, SrcType.URL, df)
