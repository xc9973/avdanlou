# config.py
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """Bot 配置"""

    bot_token: str
    log_level: str = "INFO"
    rate_limit_per_minute: int = 5

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
