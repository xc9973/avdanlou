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


def test_config_get_twitter_cookie_file_none(monkeypatch):
    """测试未配置 cookie 时返回 None"""
    monkeypatch.setenv("BOT_TOKEN", "test_token")
    monkeypatch.setenv("TWITTER_COOKIE", "")

    from config import Config
    config = Config()
    result = config.get_twitter_cookie_file()
    assert result is None


def test_config_get_twitter_cookie_file_valid(monkeypatch):
    """测试有效 cookie 字符串解析"""
    monkeypatch.setenv("BOT_TOKEN", "test_token")
    monkeypatch.setenv("TWITTER_COOKIE", "auth_token=abc123; ct0=xyz789")

    from config import Config
    config = Config()
    cookie_file = config.get_twitter_cookie_file()

    assert cookie_file is not None
    assert "avdoulou_" in cookie_file
    assert "_twitter_cookies.txt" in cookie_file
    assert os.path.exists(cookie_file)

    # 验证文件内容
    with open(cookie_file, 'r') as f:
        content = f.read()
        assert "auth_token\tabc123" in content
        assert "ct0\txyz789" in content
        assert ".x.com" in content

    # 清理
    os.remove(cookie_file)


def test_config_get_twitter_cookie_file_unique_names(monkeypatch):
    """测试每次调用生成唯一文件名"""
    monkeypatch.setenv("BOT_TOKEN", "test_token")
    monkeypatch.setenv("TWITTER_COOKIE", "auth_token=abc123")

    from config import Config
    config = Config()

    cookie_file1 = config.get_twitter_cookie_file()
    cookie_file2 = config.get_twitter_cookie_file()

    assert cookie_file1 != cookie_file2

    # 清理
    os.remove(cookie_file1)
    os.remove(cookie_file2)


def test_config_get_twitter_cookie_file_skip_empty(monkeypatch):
    """测试跳过空 name 或 value 的 cookie"""
    monkeypatch.setenv("BOT_TOKEN", "test_token")
    monkeypatch.setenv("TWITTER_COOKIE", "auth_token=abc123; =empty; name_only=; ; ct0=xyz789")

    from config import Config
    config = Config()
    cookie_file = config.get_twitter_cookie_file()

    assert cookie_file is not None

    with open(cookie_file, 'r') as f:
        content = f.read()
        # 应该只包含有效的 cookie
        assert "auth_token\tabc123" in content
        assert "ct0\txyz789" in content
        # 不包含空 name 或 value
        assert "\t\t" not in content  # 空值会产生连续的 tab

    # 清理
    os.remove(cookie_file)


def test_config_get_allowed_user_ids(monkeypatch):
    """测试获取允许的用户 ID 列表"""
    monkeypatch.setenv("BOT_TOKEN", "test_token")
    monkeypatch.setenv("ALLOWED_USER_IDS", "123,456,789")

    from config import Config
    config = Config()
    allowed = config.get_allowed_user_ids()
    assert allowed == {123, 456, 789}


def test_config_is_user_allowed(monkeypatch):
    """测试用户白名单检查"""
    monkeypatch.setenv("BOT_TOKEN", "test_token")
    monkeypatch.setenv("ALLOWED_USER_IDS", "123,456,789")

    from config import Config
    config = Config()
    assert config.is_user_allowed(123) is True
    assert config.is_user_allowed(999) is False


def test_config_is_user_allowed_empty_whitelist(monkeypatch):
    """测试空白名单时拒绝所有用户"""
    monkeypatch.setenv("BOT_TOKEN", "test_token")
    monkeypatch.setenv("ALLOWED_USER_IDS", "")

    from config import Config
    config = Config()
    assert config.is_user_allowed(123) is False
