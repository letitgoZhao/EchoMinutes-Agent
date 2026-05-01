from functools import cached_property
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    version: str = "0.1.0"
    env: str = Field(default="development", alias="ECHOMINUTES_ENV")
    api_host: str = Field(default="127.0.0.1", alias="ECHOMINUTES_API_HOST")
    api_port: int = Field(default=8765, alias="ECHOMINUTES_API_PORT")
    workspace_dir_raw: str = Field(default="./workspace.local", alias="ECHOMINUTES_WORKSPACE_DIR")
    dashscope_api_key: str = Field(default="", alias="DASHSCOPE_API_KEY")
    dashscope_base_url: str = Field(
        default="https://dashscope.aliyuncs.com/compatible-mode/v1",
        alias="DASHSCOPE_BASE_URL",
    )
    dashscope_model: str = Field(default="qwen-plus", alias="DASHSCOPE_MODEL")

    @cached_property
    def workspace_dir(self) -> Path:
        path = Path(self.workspace_dir_raw)
        if not path.is_absolute():
            path = ROOT_DIR / path
        return path

    @cached_property
    def database_url(self) -> str:
        db_path = self.workspace_dir / "echominutes.sqlite3"
        return f"sqlite:///{db_path.as_posix()}"

    @property
    def cors_origins(self) -> list[str]:
        return [
            "http://127.0.0.1:5173",
            "http://localhost:5173",
        ]

    @property
    def has_dashscope_api_key(self) -> bool:
        key = self.dashscope_api_key.strip()
        return bool(key and key != "sk-<your_api_key>")


settings = Settings()
