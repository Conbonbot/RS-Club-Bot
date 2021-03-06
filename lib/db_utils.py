"""Database utilities."""
from typing import List

import logging
import os

import sqlite3

# TODO: Centralize settings in a settings lib.
DB_FILE = os.getenv('DB_FILE') or 'rsqueue.sqlite'

LOGGER = logging.getLogger(__name__)


def _dict_factory(cursor, row):
    """Dictionary factory for sqlite rows."""
    result = {}
    for idx, col in enumerate(cursor.description):
        result[col[0]] = row[idx]
    return result


class Database:
    """Wrapper class to simplify usage by providing pre-set queries and handing 'with' statements."""

    class Connector:
        """Interface for querying Sqlite3."""
        def __init__(self, file, **kwargs):
            """Initialize DB settings."""
            self.file = file
            self.kwargs = kwargs

        def __enter__(self):
            self.conn = sqlite3.connect(self.file)
            self.conn.row_factory = _dict_factory
            self.cursor = self.conn.cursor()
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            """Rollback changes if an exception is found."""
            if exc_tb is None:
                self.conn.rollback()
            else:
                self.conn.commit()
            self.cursor.close()
            self.conn.close()

    @staticmethod
    def run_query(query) -> List[dict]:
        """Runs SQLite3 database query.

        Arguments:
            query: The query to run.

        Returns:
            results: The results of the query.
        """
        LOGGER.debug(f'QUERY | {query}')
        with Database.Connector(DB_FILE) as db:
            db.cursor.execute(query)
            results = db.cursor.fetchall()
        if results:
            LOGGER.debug(f'RESULT | {results}')
        return results


def create_tables(tables):
    """Creates the specified tables if they don't exist.

    Arguments:
        tables: The tables to create.
    """
    for table in tables:
        Database.run_query(f'CREATE TABLE IF NOT EXISTS {table}')


def players_in_queue(queue: int) -> int:
    """Query the database and return the number of players in a specific RS queue."""
    query_result = Database.run_query(f'SELECT amount FROM main WHERE level={queue}')
    return len(query_result) + 1
