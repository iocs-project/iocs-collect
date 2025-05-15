import psycopg2
from db_utils.util.logger import logger
from InquirerPy import inquirer

from actions.search import search_menu
from actions.update import update_data_menu


def show_main_menu(conn: psycopg2.extensions.connection) -> None:
    while True:
        action = inquirer.select(
            message="Select an action:",
            choices=[
                "Update data",
                "Search data",
                "Exit",
            ],
            default="Search data",
        ).execute()

        if action == "Update data":
            update_data_menu(conn)
        elif action == "Search data":
            search_menu(conn)
        elif action == "Exit":
            confirm_exit = inquirer.confirm(
                message="Are you sure you want to exit?",
                default=True,
            ).execute()

            if confirm_exit:
                logger.info("👋 Exiting the application.")
                conn.close()
                break
