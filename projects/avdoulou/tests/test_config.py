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


def test_config_invalid_rate_limit(monkeypatch):
    """测试 rate_limit 负数验证"""
    monkeypatch.setenv("BOT_TOKEN", "test_token")
    monkeypatch.setenv("RATE_LIMIT_PER_MINUTE", "-1")

    from config import Config
    with pytest.raises(ValidationError):
        Config()


def test_config_invalid_log_level(monkeypatch):
    """测试无效日志级别"""
    monkeypatch.setenv("BOT_TOKEN", "test_token")
    monkeypatch.setenv("LOG_LEVEL", "INVALID")

    from config import Config
    with pytest.raises(ValidationError):
        Config()


def test_config_case_insensitive(monkeypatch):
    """测试环境变量大小写不敏感"""
    monkeypatch.setenv("bot_token", "test_token")  # 小写
    monkeypatch.setenv("log_level", "debug")       # 小写

    from config import Config
    config = Config()
    assert config.bot_token == "test_token"
    assert config.log_level == "DEBUG"


def test_config_rate_limit_zero(monkeypatch):
    """测试 rate_limit 为 0 时验证"""
    monkeypatch.setenv("BOT_TOKEN", "test_token")
    monkeypatch.setenv("RATE_LIMIT_PER_MINUTE", "0")

    from config import Config
    with pytest.raises(ValidationError):
        Config()


def test_config_log_level_normalization(monkeypatch):
    """测试日志级别自动转为大写"""
    monkeypatch.setenv("BOT_TOKEN", "test_token")
    monkeypatch.setenv("LOG_LEVEL", "warning")

    from config import Config
    config = Config()
    assert config.log_level == "WARNING"
