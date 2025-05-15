import psycopg2
from db_utils.util.logger import logger
from InquirerPy import inquirer

from sources.open_phish import OpenPhish
from sources.reputation_alienvault import ReputationAlienvault
from sources.url_haus import URLHaus


def update_data(source_registry: dict, selected_source: str, conn: psycopg2.extensions.connection) -> None:
    if selected_source in source_registry:
        source_class = source_registry[selected_source]
        source_instance = source_class(conn)
        data = source_instance.parse()
        source_instance.store(data)
    else:
        logger.warning(f"Source '{selected_source}' not found in registry.")


def update_data_menu(conn: psycopg2.extensions.connection) -> None:
    source_classes = [URLHaus, ReputationAlienvault, OpenPhish]
    source_registry = {cls(conn).name: cls for cls in source_classes}

    choices = list(source_registry.keys()) + ["All sources", "Back"]

    selected = inquirer.select(
        message="Which source do you want to update data from?",
        choices=choices,
        default="All sources",
    ).execute()

    if selected == "Back":
        return

    logger.info(f"\nUpdating data from: {selected}\n")

    if selected == "All sources":
        for source_name in source_registry.keys():
            update_data(source_registry, source_name, conn)
    else:
        update_data(source_registry, selected, conn)

    input("\nPress Enter to return to the main menu.")
