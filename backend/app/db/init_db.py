from sqlalchemy import inspect, text

from app.db.base import Base
from app.db.session import engine

# Import models so SQLAlchemy registers them before create_all.
from app.models import (  # noqa: F401
    ExportRecord,
    Meeting,
    NoteRecord,
    ProcessingTask,
    Setting,
    TranscriptSegmentRecord,
)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    _upgrade_sqlite_schema()


def _upgrade_sqlite_schema() -> None:
    if engine.dialect.name != "sqlite":
        return

    inspector = inspect(engine)
    table_names = inspector.get_table_names()
    if "meetings" not in table_names:
        return

    meeting_columns = {column["name"] for column in inspector.get_columns("meetings")}
    if "deleted_at" in meeting_columns:
        return

    with engine.begin() as connection:
        connection.execute(text("ALTER TABLE meetings ADD COLUMN deleted_at DATETIME"))
