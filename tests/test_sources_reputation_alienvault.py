import os
from unittest.mock import MagicMock, patch

import pytest
import requests

from sources.reputation_alienvault import ReputationAlienvault


@pytest.fixture
def mock_conn():
    # Create a mock connection for the tests
    return MagicMock()


@pytest.fixture
def mock_response():
    # Create a mock response for the requests.get call
    mock_response = MagicMock()
    return mock_response


@patch.dict(os.environ, {"ReputationAlienvault": "http://test.url"})
def test_parse_success(mock_conn, mock_response):
    # Prepare mock response
    mock_response.text = "192.168.0.1\n# comment\n10.0.0.1\n"
    mock_response.status_code = 200

    with patch("requests.get", return_value=mock_response):
        reputation_alienvault = ReputationAlienvault(mock_conn)

        df = reputation_alienvault.parse()

        # Assert that the dataframe contains the expected IPs
        assert df.shape[0] == 2  # We expect 2 IPs
        assert "ip" in df.columns  # Column 'ip' should be present
        assert "192.168.0.1" in df["ip"].to_list()
        assert "10.0.0.1" in df["ip"].to_list()


@patch.dict(os.environ, {"ReputationAlienvault": "http://test.url"})
def test_parse_no_ips(mock_conn, mock_response):
    # Prepare mock response with no valid IPs
    mock_response.text = "# comment\n"
    mock_response.status_code = 200

    with patch("requests.get", return_value=mock_response):
        reputation_alienvault = ReputationAlienvault(mock_conn)

        df = reputation_alienvault.parse()

        # Assert that the dataframe is empty
        assert df.shape[0] == 0  # No IPs, so no rows
        assert "ip" in df.columns


@patch.dict(os.environ, {"ReputationAlienvault": "http://test.url"})
def test_parse_request_exception(mock_conn, mock_response):
    # Simulate a request exception (e.g., connection timeout)
    with patch("requests.get", side_effect=requests.RequestException("Connection error")):
        reputation_alienvault = ReputationAlienvault(mock_conn)

        # Call the method and check that it raises a RuntimeError
        with pytest.raises(RuntimeError):
            reputation_alienvault.parse()


@patch.dict(os.environ, {"ReputationAlienvault": "http://test.url"})
def test_parse_empty_response(mock_conn, mock_response):
    # Prepare an empty response
    mock_response.text = ""
    mock_response.status_code = 200

    with patch("requests.get", return_value=mock_response):
        reputation_alienvault = ReputationAlienvault(mock_conn)

        df = reputation_alienvault.parse()

        # Assert that the dataframe is empty
        assert df.shape[0] == 0  # No rows should be present
        assert "ip" in df.columns
