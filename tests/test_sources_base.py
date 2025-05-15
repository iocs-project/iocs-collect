from unittest.mock import MagicMock, patch

import polars as pl
import pytest

from sources.base import SourceBase
from src_type import SrcType


@patch("sources.base.os.getenv", return_value="http://example.com")
def test_source_base_initialization(mock_getenv):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = [42]
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    class DummySource(SourceBase):
        src_type = SrcType.URL

    source = DummySource(mock_conn)

    assert source.name == "DummySource"
    assert source.url == "http://example.com"
    assert source.conn == mock_conn
    assert source.id == 42
    assert source.src_type == SrcType.URL
    mock_getenv.assert_called_once_with("DummySource")


def test_source_base_fetch_source_id_value_error():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    class DummySource(SourceBase):
        src_type = SrcType.IP

    with pytest.raises(
        ValueError, match="Error while retrieving source ID: Source <DummySource> was not found in the database."
    ):
        DummySource(mock_conn)


@patch("sources.base.db_store")
def test_source_base_store_calls_db_store(mock_db_store):
    mock_conn = MagicMock()

    class DummySource(SourceBase):
        src_type = SrcType.URL

    instance = DummySource(mock_conn)
    instance.id = 42
    df = pl.DataFrame({"url": ["http://test.com"]})

    instance.store(df)
    mock_db_store.assert_called_once_with(42, "DummySource", mock_conn, SrcType.URL, df)


def test_source_base_parse_raises_not_implemented():
    mock_conn = MagicMock()

    class DummySource(SourceBase):
        src_type = SrcType.URL

    instance = DummySource(mock_conn)
    with pytest.raises(NotImplementedError):
        instance.parse()
