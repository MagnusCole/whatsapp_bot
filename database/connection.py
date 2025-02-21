from drizzle_orm import PostgresDatabase
from drizzle_orm.pg_core import create_engine
from contextlib import contextmanager
from typing import Generator

class DatabaseManager:
    def __init__(self, connection_string: str):
        self.engine = create_engine(connection_string)
        self.db = PostgresDatabase(self.engine)

    @contextmanager
    def get_session(self) -> Generator[PostgresDatabase, None, None]:
        try:
            yield self.db
        except Exception as e:
            raise e