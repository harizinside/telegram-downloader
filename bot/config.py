from pathlib import Path
from typing import Optional

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_LOCAL_API_BASE_URL = "http://telegram-bot-api:8081"
_CLOUD_API_BASE_URL = "https://api.telegram.org"
_CLOUD_MAX_VIDEO_SIZE_MB = 45  # safety margin under Telegram's cloud 50MB upload limit
_LOCAL_MAX_VIDEO_SIZE_MB = 1950  # safety margin under the local server's 2GB limit


class Settings(BaseSettings):
    bot_token: str
    # Only consumed by the telegram-bot-api sidecar, but the bot reads them
    # too so it can decide, on its own, which API base URL and size limit to use.
    telegram_api_id: Optional[str] = None
    telegram_api_hash: Optional[str] = None
    telegram_api_base_url: Optional[str] = None  # auto-derived below if left unset
    download_dir: Path = Path("/data/downloads")
    max_concurrent_downloads: int = 2
    download_timeout_seconds: float = 600
    max_video_size_mb: Optional[int] = None  # auto-derived below if left unset

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def uses_local_api_server(self) -> bool:
        return bool(self.telegram_api_id and self.telegram_api_hash)

    @model_validator(mode="after")
    def _apply_derived_defaults(self) -> "Settings":
        if not self.telegram_api_base_url:
            self.telegram_api_base_url = (
                _LOCAL_API_BASE_URL if self.uses_local_api_server else _CLOUD_API_BASE_URL
            )
        if self.max_video_size_mb is None:
            self.max_video_size_mb = (
                _LOCAL_MAX_VIDEO_SIZE_MB if self.uses_local_api_server else _CLOUD_MAX_VIDEO_SIZE_MB
            )
        return self
