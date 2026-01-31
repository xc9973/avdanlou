# config.py
"""配置管理模块。

使用 Pydantic Settings 管理应用配置，支持从环境变量和 .env 文件加载。

环境变量:
    BOT_TOKEN: Telegram Bot 令牌（必填）
    LOG_LEVEL: 日志级别，默认 INFO
    RATE_LIMIT_PER_MINUTE: 每分钟请求限制，默认 5
    ALLOWED_USER_IDS: 允许使用 Bot 的 Telegram 用户 ID，逗号分隔（必填）
    TWITTER_COOKIE: Twitter/X Cookie，用于访问 18+ 内容（可选）
    TWITTER_PROXY_URL: Cloudflare Worker 代理 URL（可选）
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator


class Config(BaseSettings):
    """Bot 配置"""

    bot_token: str
    log_level: str = "INFO"
    rate_limit_per_minute: int = 5
    allowed_user_ids: str = ""  # 逗号分隔的用户 ID 列表
    twitter_cookie: str = ""  # Twitter/X Cookie（Netscape 格式）
    twitter_proxy_url: str = ""  # Cloudflare Worker 代理 URL

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

    def get_allowed_user_ids(self) -> set[int]:
        """获取允许的用户 ID 列表"""
        if not self.allowed_user_ids.strip():
            return set()
        try:
            return set(int(uid.strip()) for uid in self.allowed_user_ids.split(",") if uid.strip())
        except ValueError:
            return set()

    def is_user_allowed(self, user_id: int) -> bool:
        """检查用户是否在白名单中"""
        allowed = self.get_allowed_user_ids()
        return user_id in allowed

    def get_twitter_cookie_file(self) -> str | None:
        """获取 Twitter Cookie 文件路径

        如果配置了 cookie 内容，会创建临时文件并返回路径
        """
        if not self.twitter_cookie.strip():
            return None

        import tempfile
        import os

        # 创建临时 cookie 文件（Netscape 格式）
        temp_dir = tempfile.gettempdir()
        cookie_file = os.path.join(temp_dir, "twitter_cookies.txt")

        # 解析 cookie 字符串并转换成 Netscape 格式
        # 输入格式: auth_token=xxx; ct0=xxx; twid=xxx
        # 输出格式: 每行一个 cookie，tab 分隔 7 个字段
        cookies = self.twitter_cookie.strip().split(';')

        with open(cookie_file, 'w') as f:
            for cookie in cookies:
                cookie = cookie.strip()
                if '=' in cookie:
                    name, value = cookie.split('=', 1)
                    # Netscape 格式: domain \t path \t secure \t expiration \t name \t value
                    f.write(f".x.com\tTRUE\t/\tTRUE\t0\t{name}\t{value}\n")

        return cookie_file

    def use_proxy(self) -> bool:
        """检查是否配置了代理"""
        return bool(self.twitter_proxy_url.strip())
