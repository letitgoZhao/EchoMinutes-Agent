from pydantic import BaseModel


class NoteResponse(BaseModel):
    markdown: str
