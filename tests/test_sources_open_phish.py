import os
from unittest.mock import MagicMock, patch

import pytest
import requests

from sources.open_phish import OpenPhish


@pytest.fixture
def mock_conn():
    # Create a mock connection for the tests
    return MagicMock()


@pytest.fixture
def mock_response():
    # Create a mock response for the requests.get call
    mock_response = MagicMock()
    return mock_response


@patch.dict(os.environ, {"OpenPhish": "http://test.url"})
def test_parse_success(mock_conn, mock_response):
    # Prepare mock response
    mock_response.text = "http://example.com\n# comment\nhttp://test.com\n"
    mock_response.status_code = 200

    with patch("requests.get", return_value=mock_response):
        openphish = OpenPhish(mock_conn)

        df = openphish.parse()

        # Assert that the dataframe contains the expected URLs
        assert df.shape[0] == 2  # We expect 2 URLs
        assert "url" in df.columns  # Column 'url' should be present
        assert "http://example.com" in df["url"].to_list()
        assert "http://test.com" in df["url"].to_list()


@patch.dict(os.environ, {"OpenPhish": "http://test.url"})
def test_parse_no_urls(mock_conn, mock_response):
    # Prepare mock response with no valid URLs
    mock_response.text = "# comment\n"
    mock_response.status_code = 200

    with patch("requests.get", return_value=mock_response):
        openphish = OpenPhish(mock_conn)

        df = openphish.parse()

        # Assert that the dataframe is empty
        assert df.shape[0] == 0  # No URLs, so no rows
        assert "url" in df.columns


@patch.dict(os.environ, {"OpenPhish": "http://test.url"})
def test_parse_request_exception(mock_conn, mock_response):
    # Simulate a request exception (e.g., connection timeout)
    with patch("requests.get", side_effect=requests.RequestException("Connection error")):
        openphish = OpenPhish(mock_conn)

        # Call the method and check that it raises a RuntimeError
        with pytest.raises(RuntimeError):
            openphish.parse()


@patch.dict(os.environ, {"OpenPhish": "http://test.url"})
def test_parse_empty_response(mock_conn, mock_response):
    # Prepare an empty response
    mock_response.text = ""
    mock_response.status_code = 200

    with patch("requests.get", return_value=mock_response):
        openphish = OpenPhish(mock_conn)

        df = openphish.parse()

        # Assert that the dataframe is empty
        assert df.shape[0] == 0  # No rows should be present
        assert "url" in df.columns
