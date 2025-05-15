from unittest.mock import MagicMock, patch

from actions.update import update_data


def test_update_data_calls_parse_and_store():
    mock_conn = MagicMock()
    mock_source_instance = MagicMock()
    mock_source_instance.parse.return_value = "parsed_data"

    mock_source_class = MagicMock(return_value=mock_source_instance)

    source_registry = {"ExampleSource": mock_source_class}

    update_data(source_registry, "ExampleSource", mock_conn)

    mock_source_class.assert_called_once_with(mock_conn)
    mock_source_instance.parse.assert_called_once()
    mock_source_instance.store.assert_called_once_with("parsed_data")


@patch("actions.update.logger")
def test_update_data_logs_warning_if_source_missing(mock_logger):
    mock_conn = MagicMock()
    source_registry = {}

    update_data(source_registry, "MissingSource", mock_conn)

    mock_logger.warning.assert_called_once_with("Source 'MissingSource' not found in registry.")
