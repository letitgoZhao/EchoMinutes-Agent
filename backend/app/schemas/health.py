from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    ok: bool
    version: str
    workspace_dir: str = Field(serialization_alias="workspaceDir")
