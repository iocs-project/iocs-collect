from db_utils.config.config import Config
from db_utils.connect import connect
from dotenv import load_dotenv

from menu import show_main_menu

if __name__ == "__main__":
    load_dotenv()
    config = Config()
    conn = connect(config)
    show_main_menu(conn)
