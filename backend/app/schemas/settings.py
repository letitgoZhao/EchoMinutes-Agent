from pydantic import BaseModel, Field


class AppSettings(BaseModel):
    api_host: str = Field(serialization_alias="apiHost")
    api_port: int = Field(serialization_alias="apiPort")
    workspace_dir: str = Field(serialization_alias="workspaceDir")
    transcription_provider: str = Field(serialization_alias="transcriptionProvider")
    asr_ready: bool = Field(serialization_alias="asrReady")
    dashscope_base_url: str = Field(serialization_alias="dashscopeBaseUrl")
    dashscope_model: str = Field(serialization_alias="dashscopeModel")
    dashscope_asr_base_url: str = Field(serialization_alias="dashscopeAsrBaseUrl")
    dashscope_asr_model: str = Field(serialization_alias="dashscopeAsrModel")
    has_dashscope_api_key: bool = Field(serialization_alias="hasDashscopeApiKey")
    ffmpeg_available: bool = Field(serialization_alias="ffmpegAvailable")
    ffmpeg_path: str | None = Field(serialization_alias="ffmpegPath")


class AppSettingsUpdate(BaseModel):
    workspace_dir: str | None = None
    dashscope_base_url: str | None = None
    dashscope_model: str | None = None
