import polars as pl
import psycopg2
import requests
from db_utils.util.logger import logger

from sources.base import SourceBase
from src_type import SrcType


class OpenPhish(SourceBase):
    src_type: SrcType = SrcType.URL

    def __init__(self, conn: psycopg2.extensions.connection):
        super().__init__(conn)

    def parse(self) -> pl.DataFrame:
        logger.info(f"Fetching data from OpenPhish at {self.url}")

        if self.url is None:
            raise ValueError("URL must not be None")

        try:
            response = requests.get(self.url, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to fetch data from OpenPhish: {e}")

        lines = response.text.splitlines()
        # Filter out comments or empty lines
        urls = [line.strip() for line in lines if line.strip() and not line.startswith("#")]

        if not urls:
            logger.warning("No valid URLs found in OpenPhish feed.")
            return pl.DataFrame(schema={"url": pl.Utf8})  # empty df with schema

        df = pl.DataFrame({"url": urls})
        logger.info(f"Parsed {len(df)} URLs from OpenPhish.")
        return df
