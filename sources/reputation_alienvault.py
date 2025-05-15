import polars as pl
import psycopg2
import requests
from db_utils.util.logger import logger

from sources.base import SourceBase
from src_type import SrcType


class ReputationAlienvault(SourceBase):
    src_type: SrcType = SrcType.IP

    def __init__(self, conn: psycopg2.extensions.connection):
        super().__init__(conn)

    def parse(self) -> pl.DataFrame:
        logger.info(f"Fetching data from Alienvault at {self.url}")

        if self.url is None:
            raise ValueError("URL must not be None")

        try:
            response = requests.get(self.url, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to fetch data from Alienvault: {e}")

        lines = response.text.splitlines()
        ips = [line.split("#", 1)[0].strip() for line in lines if line.strip() and not line.startswith("#")]

        if not ips:
            logger.warning("No valid IPs found in Alienvault feed.")
            return pl.DataFrame(schema={"ip": pl.Utf8})  # Empty DataFrame with schema

        df = pl.DataFrame({"ip": ips})
        logger.info(f"Parsed {len(df)} IPs from Alienvault.")
        return df
