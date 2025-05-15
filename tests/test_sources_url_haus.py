import os
from unittest.mock import MagicMock, patch

import polars as pl
import pytest
import requests

from sources.url_haus import URLHaus
from src_type import SrcType


@pytest.fixture
def mock_connv2():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = [42]
    mock_conn = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    return mock_conn


@pytest.fixture
def mock_conn():
    # Create a mock connection for the tests
    return MagicMock()


@pytest.fixture
def mock_response():
    # Create a mock response for the requests.get call
    mock_response = MagicMock()
    return mock_response


@patch.dict(os.environ, {"URLHaus": "http://test.url"})
def test_parse_success(mock_conn, mock_response):
    # Prepare mock response with a valid CSV format
    mock_response.text = "# id,dateadded,url\n" "1,2025-05-10,http://example.com\n" "2,2025-05-11,http://test.com\n"
    mock_response.status_code = 200

    with patch("requests.get", return_value=mock_response):
        urlhaus = URLHaus(mock_conn)

        df = urlhaus.parse()

        # Assert that the dataframe contains the expected data
        assert df.shape[0] == 2  # We expect 2 rows
        assert "url" in df.columns  # Column 'url' should be present
        assert "http://example.com" in df["url"].to_list()
        assert "http://test.com" in df["url"].to_list()


@patch.dict(os.environ, {"URLHaus": "http://test.url"})
def test_parse_no_header(mock_conn, mock_response):
    # Prepare mock response with no valid CSV header
    mock_response.text = "# invalidheader\n" "1,2025-05-10,http://example.com\n" "2,2025-05-11,http://test.com\n"
    mock_response.status_code = 200

    with patch("requests.get", return_value=mock_response):
        urlhaus = URLHaus(mock_conn)

        # Call the method and check for a ValueError due to missing header
        with pytest.raises(ValueError, match="CSV header not found in URLHaus data."):
            urlhaus.parse()


@patch.dict(os.environ, {"URLHaus": "http://test.url"})
def test_parse_empty_response(mock_conn, mock_response):
    # Prepare an empty response
    mock_response.text = ""
    mock_response.status_code = 200

    with patch("requests.get", return_value=mock_response):
        urlhaus = URLHaus(mock_conn)

        df = urlhaus.parse()

        # Assert that the dataframe is empty
        assert df.shape[0] == 0  # No rows should be present
        assert "url" in df.columns


@patch.dict(os.environ, {"URLHaus": "http://test.url"})
def test_parse_request_exception(mock_conn, mock_response):
    # Simulate a request exception (e.g., connection timeout)
    with patch("requests.get", side_effect=requests.RequestException("Connection error")):
        urlhaus = URLHaus(mock_conn)

        # Call the method and check that it raises a RuntimeError
        with pytest.raises(RuntimeError, match="Failed to fetch data from URLHaus"):
            urlhaus.parse()


@patch("sources.url_haus.requests.get")
@patch("sources.base.db_store")
@patch.dict(os.environ, {"URLHaus": "http://test.url"})
def test_urlhaus_parse_and_store(mock_db_store, mock_get, mock_connv2):
    csv_data = """
# csv export
# id,dateadded,url
1,2025-05-10,http://malicious.example.com
""".strip()

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = csv_data
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    urlhaus = URLHaus(mock_connv2)
    df = urlhaus.parse()

    assert isinstance(df, pl.DataFrame)
    assert df.shape[0] == 1
    assert "url" in df.columns
    assert df["url"][0] == "http://malicious.example.com"

    urlhaus.store(df)

    mock_db_store.assert_called_once()
    args, _ = mock_db_store.call_args
    assert args[0] == 42
    assert args[1] == "URLHaus"
    assert args[2] == mock_connv2
    assert args[3] == SrcType.URL
    assert isinstance(args[4], pl.DataFrame)
