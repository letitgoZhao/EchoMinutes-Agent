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
