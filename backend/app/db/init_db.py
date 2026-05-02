from app.db.base import Base
from app.db.session import engine

# Import models so SQLAlchemy registers them before create_all.
from app.models import Meeting, Setting  # noqa: F401


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
