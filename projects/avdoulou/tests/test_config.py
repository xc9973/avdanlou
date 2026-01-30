# tests/test_config.py
import os
from pydantic import ValidationError
import pytest


def test_config_loads_from_env(monkeypatch):
    """测试从环境变量加载配置"""
    monkeypatch.setenv("BOT_TOKEN", "test_token_123")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("RATE_LIMIT_PER_MINUTE", "10")

    from config import Config
    config = Config()

    assert config.bot_token == "test_token_123"
    assert config.log_level == "DEBUG"
    assert config.rate_limit_per_minute == 10


def test_config_defaults(monkeypatch):
    """测试默认值"""
    monkeypatch.setenv("BOT_TOKEN", "test_token")
    # 不设置其他环境变量

    from config import Config
    config = Config()

    assert config.log_level == "INFO"
    assert config.rate_limit_per_minute == 5


def test_config_missing_bot_token(monkeypatch):
    """测试缺少 BOT_TOKEN 时抛出错误"""
    monkeypatch.delenv("BOT_TOKEN", raising=False)

    from config import Config
    with pytest.raises(ValidationError):
        Config()
