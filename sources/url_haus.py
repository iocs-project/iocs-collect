from io import StringIO

import polars as pl
import psycopg2
import requests
from db_utils.util.logger import logger

from sources.base import SourceBase
from src_type import SrcType


class URLHaus(SourceBase):
    src_type: SrcType = SrcType.URL

    def __init__(self, conn: psycopg2.extensions.connection):
        super().__init__(conn)

    def parse(self) -> pl.DataFrame:
        logger.info(f"Fetching data from URLHaus at {self.url}")

        if self.url is None:
            raise ValueError("URL must not be None")

        try:
            response = requests.get(self.url, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to fetch data from URLHaus: {e}")

        lines = response.text.splitlines()

        if len(lines) == 0:
            return pl.DataFrame(schema={"url": pl.Utf8})

        # Find the last header line (starts with #) which contains the actual CSV header
        header_line_index = None
        for i, line in enumerate(lines):
            if line.startswith("#") and "id,dateadded,url" in line:
                header_line_index = i
                break

        if header_line_index is None:
            raise ValueError("CSV header not found in URLHaus data.")

        csv_lines = lines[header_line_index:]
        csv_content = "\n".join(csv_lines)

        try:
            df = pl.read_csv(StringIO(csv_content), quote_char='"')
        except Exception as e:
            raise RuntimeError(f"Failed to parse CSV from URLHaus: {e}")

        logger.info(f"Parsed {len(df)} rows from URLHaus.")
        return df
