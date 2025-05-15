import polars as pl
import psycopg2
from db_utils.util.logger import logger

from src_type import SrcType


def db_store(
    source_id: int, source_name: str, conn: psycopg2.extensions.connection, src_type: SrcType, df: pl.DataFrame
) -> None:
    if df.is_empty():
        logger.info(f"Source <{source_name}> returned no data.")
        return

    insert_query = ""
    rows = []

    if src_type == SrcType.URL:
        rows = [(row["url"], source_id) for row in df.iter_rows(named=True)]
        insert_query = """
            INSERT INTO links (url, source_id)
            VALUES (%s, %s)
            ON CONFLICT (url) DO NOTHING;
        """
    elif src_type == SrcType.IP:
        rows = [(row["ip"], source_id) for row in df.iter_rows(named=True)]
        insert_query = """
            INSERT INTO ips (ip, source_id)
            VALUES (%s, %s)
            ON CONFLICT (ip) DO NOTHING;
        """
    else:
        raise ValueError(f"Unsupported source type: {src_type}")

    try:
        with conn.cursor() as cur:
            cur.executemany(insert_query, rows)
            conn.commit()
            logger.info(f"Inserted {cur.rowcount} new rows into the database.")
    except Exception as e:
        raise RuntimeError(f"Error during storing data for source <{source_name}>: {e}")
