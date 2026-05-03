from datetime import datetime

from pydantic import BaseModel


class LogEntryResponse(BaseModel):
    timestamp: datetime
    level: str
    message: str
