import os

import polars as pl
import psycopg2

from actions.store import db_store
from src_type import SrcType


class SourceBase:
    src_type: SrcType = SrcType.URL

    def __init__(self, conn: psycopg2.extensions.connection):
        self.name = self.__class__.__name__
        self.url = os.getenv(self.name)
        self.conn = conn
        self.id = self._fetch_source_id()
        self.src_type = self.__class__.src_type

    def parse(self) -> pl.DataFrame:
        """This method must be implemented in a subclass to return a Polars DataFrame."""
        raise NotImplementedError("Subclasses must implement the `parse` method.")

    def store(self, df: pl.DataFrame):
        """Store parsed data in the database using shared db_store logic."""
        db_store(self.id, self.name, self.conn, self.src_type, df)

    def _fetch_source_id(self) -> int:
        """Retrieve the source ID from the `sources` table based on the source name."""
        query = "SELECT id FROM sources WHERE name = %s"
        try:
            with self.conn.cursor() as cur:
                cur.execute(query, (self.name,))
                result = cur.fetchone()
                if result:
                    return result[0]
                raise ValueError(f"Source <{self.name}> was not found in the database.")
        except Exception as e:
            raise ValueError(f"Error while retrieving source ID: {e}")
