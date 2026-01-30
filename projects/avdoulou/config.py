# config.py
"""配置管理模块。

使用 Pydantic Settings 管理应用配置，支持从环境变量和 .env 文件加载。

环境变量:
    BOT_TOKEN: Telegram Bot 令牌（必填）
    LOG_LEVEL: 日志级别，默认 INFO
    RATE_LIMIT_PER_MINUTE: 每分钟请求限制，默认 5
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator


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

    @field_validator("rate_limit_per_minute")
    @classmethod
    def validate_rate_limit(cls, v: int) -> int:
        if v < 1:
            raise ValueError("rate_limit_per_minute must be at least 1")
        return v

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in valid_levels:
            raise ValueError(f"log_level must be one of {valid_levels}")
        return v.upper()
