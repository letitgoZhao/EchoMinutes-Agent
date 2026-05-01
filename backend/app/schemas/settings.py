from pydantic import BaseModel, Field


class AppSettings(BaseModel):
    api_host: str = Field(serialization_alias="apiHost")
    api_port: int = Field(serialization_alias="apiPort")
    workspace_dir: str = Field(serialization_alias="workspaceDir")
    dashscope_base_url: str = Field(serialization_alias="dashscopeBaseUrl")
    dashscope_model: str = Field(serialization_alias="dashscopeModel")
    has_dashscope_api_key: bool = Field(serialization_alias="hasDashscopeApiKey")


class AppSettingsUpdate(BaseModel):
    workspace_dir: str | None = None
    dashscope_base_url: str | None = None
    dashscope_model: str | None = None
