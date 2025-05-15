from unittest.mock import MagicMock, patch

from menu import show_main_menu


@patch("menu.inquirer")
@patch("menu.update_data_menu")
@patch("menu.search_menu")
def test_show_main_menu_exit(mock_search_menu, mock_update_menu, mock_inquirer):
    # Nastavení výběrů: nejdřív "Exit", pak potvrzení True
    mock_inquirer.select.return_value.execute.return_value = "Exit"
    mock_inquirer.confirm.return_value.execute.return_value = True

    # Mock DB connection
    mock_conn = MagicMock()

    show_main_menu(mock_conn)

    # We expect the connection to be closed.
    mock_conn.close.assert_called_once()
    # The menu should only be run once, without calling any other functions
    mock_search_menu.assert_not_called()
    mock_update_menu.assert_not_called()


@patch("menu.inquirer")
@patch("menu.update_data_menu")
def test_show_main_menu_update(mock_update_menu, mock_inquirer):
    # We set the response "Update data", then "Exit"
    mock_inquirer.select.side_effect = [MagicMock(execute=lambda: "Update data"), MagicMock(execute=lambda: "Exit")]
    mock_inquirer.confirm.return_value.execute.return_value = True

    mock_conn = MagicMock()
    show_main_menu(mock_conn)

    mock_update_menu.assert_called_once()
    mock_conn.close.assert_called_once()


@patch("menu.inquirer")
@patch("menu.search_menu")
def test_show_main_menu_search(mock_search_menu, mock_inquirer):
    # We set the answer "Search data", then "Exit"
    mock_inquirer.select.side_effect = [MagicMock(execute=lambda: "Search data"), MagicMock(execute=lambda: "Exit")]
    mock_inquirer.confirm.return_value.execute.return_value = True

    mock_conn = MagicMock()
    show_main_menu(mock_conn)

    # We expect search_menu to be called
    mock_search_menu.assert_called_once()
    mock_conn.close.assert_called_once()


@patch("menu.inquirer")
@patch("menu.update_data_menu")
def test_show_main_menu_update_then_exit(mock_update_menu, mock_inquirer):
    # Set responses for "Update data", then "Exit"
    mock_inquirer.select.side_effect = [MagicMock(execute=lambda: "Update data"), MagicMock(execute=lambda: "Exit")]
    mock_inquirer.confirm.return_value.execute.return_value = True

    mock_conn = MagicMock()
    show_main_menu(mock_conn)

    # We expect update_data_menu to be called and the connection to be closed
    mock_update_menu.assert_called_once()
    mock_conn.close.assert_called_once()


@patch("menu.inquirer")
@patch("menu.search_menu")
def test_show_main_menu_repeated_search_then_exit(mock_search_menu, mock_inquirer):
    # Setting up repeated selection of "Search data" and then "Exit"
    mock_inquirer.select.side_effect = [
        MagicMock(execute=lambda: "Search data"),
        MagicMock(execute=lambda: "Search data"),
        MagicMock(execute=lambda: "Exit"),
    ]
    mock_inquirer.confirm.return_value.execute.return_value = True

    mock_conn = MagicMock()
    show_main_menu(mock_conn)

    # We expect search_menu to be called twice
    assert mock_search_menu.call_count == 2
    mock_conn.close.assert_called_once()
