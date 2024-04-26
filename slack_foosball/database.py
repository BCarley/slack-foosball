from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from slack_foosball.models import Base


def get_engine(file_name: str):
    return create_engine(f"sqlite+pysqlite:///{file_name}", echo=True)


def init_db(file_name: str):
    """Simple file init for sqlite, erasing all previously loaded data."""
    engine = get_engine(file_name)
    Base.metadata.create_all(engine)


class DBManager:
    def __init__(self, *, file_name: str = "games.db", engine=None):
        self.file_name = file_name
        if engine is None:
            engine = get_engine(file_name=file_name)

        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        self.db = SessionLocal()

    @contextmanager
    def __call__(self):
        yield self.db
        self.db.close()


def get_db():
    """
    Get a tenanted DB session

    Yields:
        Tenanted Session object
    """
    manager = DBManager()
    yield manager
