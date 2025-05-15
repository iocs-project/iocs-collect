import re
from typing import List, Literal, Tuple

import psycopg2
from db_utils.util.logger import logger
from InquirerPy import inquirer
from InquirerPy.validator import ValidationError


def classify_input(value: str) -> Literal["ip", "url"]:
    ip_pattern = re.compile(r"^(?:\d{1,3}\.){3}\d{1,3}$")
    return "ip" if ip_pattern.match(value) else "url"


def search(conn: psycopg2.extensions.connection, input_value: str) -> List[Tuple[int, str, str, str]]:
    input_type = classify_input(input_value)
    cursor = conn.cursor()

    if input_type == "ip":
        cursor.execute(
            "SELECT id, ip, sou.name, created_at FROM ips JOIN sources sou ON (ips.source_id = sou.id) WHERE ip = %s",
            (input_value,),
        )
    elif input_type == "url":
        cursor.execute(
            "SELECT id, url, sou.name, created_at "
            "FROM links lin "
            "JOIN sources sou ON lin.source_id = sou.id WHERE url=%s",
            (input_value,),
        )
    else:
        logger.info("Invalid input — must be an IP or URL.")
        return []

    return cursor.fetchall()


def not_empty_validator(result: str) -> bool:
    if not result.strip():
        raise ValidationError(message="Please enter at least one character.")
    return True


def search_menu(conn: psycopg2.extensions.connection) -> None:
    term = inquirer.text(message="Enter an IP or URL to search:", validate=not_empty_validator).execute()

    results: List[Tuple[int, str, str, str]] = search(conn, term)

    if results:

        for data in results:
            logger.info(f"ID: {data[0]}")
            logger.info(f"URL: {data[1]}")
            logger.info(f"Source name: {data[2]}")
            logger.info(f"Created At: {data[3]}")
    else:
        logger.info("No results found.")

    input("\nPress Enter to return to the main menu.")
