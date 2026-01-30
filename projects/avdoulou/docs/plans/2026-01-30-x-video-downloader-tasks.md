# X 视频下载 Telegram Bot 实现计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**目标：** 构建一个 Telegram Bot，用户发送 X (Twitter) 推文链接后，Bot 解析并返回视频的直链供用户下载。

**架构：** 单体架构，使用 python-telegram-bot 接收 Telegram 消息，yt-dlp 解析 X 视频链接，返回直链给用户。

**技术栈：** Python 3.12+, python-telegram-bot 21.0, yt-dlp 2024.12.6, Pydantic 2.10, Docker

---

## 项目初始化

### Task 1: 创建项目目录结构

**Files:**
- Create: `handlers/__init__.py`
- Create: `handlers/link_handler.py`
- Create: `handlers/message_handler.py`
- Create: `utils/__init__.py`
- Create: `utils/formatter.py`
- Create: `utils/validators.py`
- Create: `tests/__init__.py`
- Create: `tests/test_link_handler.py`
- Create: `tests/test_validators.py`
- Create: `tests/test_formatter.py`
- Create: `.env.example`
- Create: `.gitignore`

**Step 1: 创建目录结构**

```bash
mkdir -p handlers utils tests
touch handlers/__init__.py utils/__init__.py tests/__init__.py
touch handlers/link_handler.py handlers/message_handler.py
touch utils/formatter.py utils/validators.py
touch tests/test_link_handler.py tests/test_validators.py tests/test_formatter.py
touch .env.example .gitignore requirements.txt Dockerfile docker-compose.yml README.md bot.py config.py
```

**Step 2: 验证目录创建成功**

```bash
ls -la
```

预期输出：看到所有创建的文件和目录

**Step 3: 提交**

```bash
git add -A
git commit -m "chore: create project directory structure"
```

---

### Task 2: 配置依赖和基础文件

**Files:**
- Modify: `requirements.txt`
- Modify: `.gitignore`
- Modify: `.env.example`
- Modify: `README.md`

**Step 1: 写入 requirements.txt**

```text
python-telegram-bot==21.0
yt-dlp==2024.12.6
pydantic==2.10.4
pydantic-settings==2.6.1
pytest==8.3.4
pytest-asyncio==0.24.0
pytest-mock==3.14.0
```

**Step 2: 写入 .gitignore**

```text
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Environment
.env

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
```

**Step 3: 写入 .env.example**

```text
# Telegram Bot Token (从 @BotFather 获取)
BOT_TOKEN=your_bot_token_here

# 日志级别: DEBUG, INFO, WARNING, ERROR
LOG_LEVEL=INFO

# 速率限制: 每用户每分钟请求数
RATE_LIMIT_PER_MINUTE=5
```

**Step 4: 写入 README.md**

```markdown
# X 视频下载 Telegram Bot

一个简单的 Telegram Bot，用于下载 X (Twitter) 视频直链。

## 功能

- 发送 X 推文链接，获取视频直链
- 自动选择最高画质
- 简单易用

## 部署

\`\`\`bash
# 复制配置文件
cp .env.example .env

# 编辑 .env，填入你的 BOT_TOKEN

# Docker 部署
docker-compose up -d
\`\`\`

## 使用

1. 在 Telegram 中找到 @BotFather 创建 Bot
2. 获取 Bot Token
3. 部署此 Bot
4. 向 Bot 发送 X 推文链接

## 项目结构

\`\`\`
bot.py                 # Bot 入口
config.py              # 配置管理
handlers/              # 消息处理器
utils/                 # 工具函数
tests/                 # 测试
\`\`\`
```

**Step 5: 提交**

```bash
git add requirements.txt .gitignore .env.example README.md
git commit -m "chore: add dependencies and base configuration"
```

---

## 配置管理

### Task 3: 实现配置管理

**Files:**
- Create: `config.py`
- Create: `tests/test_config.py`

**Step 1: 写入失败的测试**

```python
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
```

**Step 2: 运行测试验证失败**

```bash
python -m pytest tests/test_config.py -v
```

预期输出：`ModuleNotFoundError: No module named 'config'`

**Step 3: 实现配置类**

```python
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
```

**Step 4: 运行测试验证通过**

```bash
python -m pytest tests/test_config.py -v
```

预期输出：所有测试通过

**Step 5: 提交**

```bash
git add config.py tests/test_config.py
git commit -m "feat: add configuration management with Pydantic"
```

---

## 链接验证

### Task 4: 实现 X 链接验证

**Files:**
- Create: `utils/validators.py`
- Create: `tests/test_validators.py`

**Step 1: 写入失败的测试**

```python
# tests/test_validators.py
import pytest
from utils.validators import is_x_video_url, extract_tweet_id


def test_valid_x_url():
    """测试有效的 X 链接"""
    assert is_x_video_url("https://x.com/user/status/123456789") is True
    assert is_x_video_url("https://twitter.com/user/status/123456789") is True
    assert is_x_video_url("https://x.com/user/status/123456789/video/1") is True


def test_invalid_x_url():
    """测试无效的链接"""
    assert is_x_video_url("https://youtube.com/watch?v=123") is False
    assert is_x_video_url("https://example.com") is False
    assert is_x_video_url("not a url") is False
    assert is_x_video_url("https://x.com/home") is False


def test_extract_tweet_id():
    """测试提取推文 ID"""
    assert extract_tweet_id("https://x.com/user/status/123456789") == "123456789"
    assert extract_tweet_id("https://twitter.com/user/status/987654321") == "987654321"
    assert extract_tweet_id("https://x.com/user/status/123456789/video/1") == "123456789"


def test_extract_tweet_id_invalid():
    """测试无效链接返回 None"""
    assert extract_tweet_id("https://youtube.com/watch?v=123") is None
    assert extract_tweet_id("not a url") is None
```

**Step 2: 运行测试验证失败**

```bash
python -m pytest tests/test_validators.py -v
```

预期输出：`ModuleNotFoundError: No module named 'utils'` 或 `ImportError`

**Step 3: 实现验证函数**

```python
# utils/validators.py
import re
from urllib.parse import urlparse


def is_x_video_url(url: str) -> bool:
    """验证是否为 X/Twitter 推文链接"""
    if not url:
        return False

    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()

        # 检查域名
        if domain not in ["x.com", "twitter.com", "www.x.com", "www.twitter.com"]:
            return False

        # 检查路径是否包含 /status/
        return "/status/" in parsed.path
    except Exception:
        return False


def extract_tweet_id(url: str) -> str | None:
    """从 X 链接中提取推文 ID"""
    if not is_x_video_url(url):
        return None

    try:
        # 匹配 /status/ 后面的数字
        match = re.search(r"/status/(\d+)", url)
        if match:
            return match.group(1)
    except Exception:
        pass

    return None
```

**Step 4: 运行测试验证通过**

```bash
python -m pytest tests/test_validators.py -v
```

预期输出：所有测试通过

**Step 5: 提交**

```bash
git add utils/validators.py tests/test_validators.py
git commit -m "feat: add X/Twitter URL validation"
```

---

## 视频解析

### Task 5: 实现视频链接解析

**Files:**
- Create: `handlers/link_handler.py`
- Create: `tests/test_link_handler.py`

**Step 1: 写入失败的测试**

```python
# tests/test_link_handler.py
import pytest
from handlers.link_handler import LinkHandler, VideoInfo
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
async def test_parse_x_video_success():
    """测试成功解析 X 视频"""
    handler = LinkHandler()

    mock_result = {
        "url": "https://video.twimg.com/test.mp4",
        "title": "Test Video",
        "duration": 60,
        "width": 1920,
        "height": 1080,
    }

    with patch.object(handler, "_extract_video_info", AsyncMock(return_value=mock_result)):
        result = await handler.parse_x_video("https://x.com/user/status/123456789")

        assert result.url == "https://video.twimg.com/test.mp4"
        assert result.title == "Test Video"
        assert result.duration == 60
        assert result.width == 1920
        assert result.height == 1080


@pytest.mark.asyncio
async def test_parse_x_video_no_video():
    """测试推文无视频"""
    handler = LinkHandler()

    with patch.object(handler, "_extract_video_info", AsyncMock(return_value=None)):
        result = await handler.parse_x_video("https://x.com/user/status/123456789")

        assert result is None


@pytest.mark.asyncio
async def test_parse_x_video_invalid_url():
    """测试无效 URL"""
    handler = LinkHandler()
    result = await handler.parse_x_video("https://youtube.com/watch?v=123")

    assert result is None
```

**Step 2: 运行测试验证失败**

```bash
python -m pytest tests/test_link_handler.py -v
```

预期输出：模块或类不存在

**Step 3: 实现链接处理器**

```python
# handlers/link_handler.py
import yt_dlp
from dataclasses import dataclass
from utils.validators import is_x_video_url


@dataclass
class VideoInfo:
    """视频信息"""
    url: str
    title: str
    duration: int
    width: int
    height: int


class LinkHandler:
    """链接处理器"""

    async def parse_x_video(self, url: str) -> VideoInfo | None:
        """解析 X 视频链接，返回视频信息"""
        if not is_x_video_url(url):
            return None

        video_data = await self._extract_video_info(url)
        if not video_data:
            return None

        return VideoInfo(
            url=video_data["url"],
            title=video_data.get("title", "Unknown"),
            duration=video_data.get("duration", 0),
            width=video_data.get("width", 0),
            height=video_data.get("height", 0),
        )

    async def _extract_video_info(self, url: str) -> dict | None:
        """使用 yt-dlp 提取视频信息"""
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": False,
            "format": "best",  # 选择最佳质量
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

                if not info:
                    return None

                # 获取视频 URL
                video_url = info.get("url")
                if not video_url:
                    # 尝试从 formats 中获取
                    formats = info.get("formats", [])
                    if formats:
                        video_url = formats[-1].get("url")  # 通常最后一个是最佳质量

                if not video_url:
                    return None

                return {
                    "url": video_url,
                    "title": info.get("title", "Unknown"),
                    "duration": info.get("duration", 0),
                    "width": info.get("width", 0),
                    "height": info.get("height", 0),
                }
        except Exception as e:
            print(f"Error extracting video info: {e}")
            return None
```

**Step 4: 运行测试验证通过**

```bash
python -m pytest tests/test_link_handler.py -v
```

预期输出：所有测试通过

**Step 5: 提交**

```bash
git add handlers/link_handler.py tests/test_link_handler.py
git commit -m "feat: add X video link parsing with yt-dlp"
```

---

## 消息格式化

### Task 6: 实现回复消息格式化

**Files:**
- Create: `utils/formatter.py`
- Create: `tests/test_formatter.py`

**Step 1: 写入失败的测试**

```python
# tests/test_formatter.py
import pytest
from utils.formatter import format_success_message, format_error_message
from handlers.link_handler import VideoInfo


def test_format_success_message():
    """测试成功消息格式化"""
    video = VideoInfo(
        url="https://video.twimg.com/test.mp4",
        title="Test Video Title",
        duration=120,
        width=1920,
        height=1080,
    )

    message = format_success_message(video)

    assert "Test Video Title" in message
    assert "https://video.twimg.com/test.mp4" in message
    assert "2:00" in message or "120" in message
    assert "1920x1080" in message


def test_format_error_message_no_video():
    """测试无视频错误消息"""
    message = format_error_message("no_video")

    assert "视频" in message or "video" in message.lower()


def test_format_error_message_parse_failed():
    """测试解析失败错误消息"""
    message = format_error_message("parse_failed")

    assert "解析" in message or "失败" in message or "error" in message.lower()


def test_format_error_message_invalid_url():
    """测试无效链接错误消息"""
    message = format_error_message("invalid_url")

    assert "链接" in message or "url" in message.lower()
```

**Step 2: 运行测试验证失败**

```bash
python -m pytest tests/test_formatter.py -v
```

预期输出：模块不存在

**Step 3: 实现格式化函数**

```python
# utils/formatter.py
from handlers.link_handler import VideoInfo


def format_success_message(video: VideoInfo) -> str:
    """格式化成功消息"""
    # 格式化时长
    minutes = video.duration // 60
    seconds = video.duration % 60
    duration_str = f"{minutes}:{seconds:02d}"

    # 格式化分辨率
    resolution = f"{video.width}x{video.height}" if video.width and video.height else "未知"

    return f"""🎬 *{video.title}*

⏱ 时长: {duration_str}
📐 分辨率: {resolution}

🔗 [点击下载视频]({video.url})"""


def format_error_message(error_type: str) -> str:
    """格式化错误消息"""
    messages = {
        "invalid_url": "❌ 请发送有效的 X (Twitter) 推文链接",
        "no_video": "❌ 该推文不包含视频",
        "parse_failed": "❌ 解析失败，可能是私密内容或链接已失效",
        "rate_limit": "⚠️ 请求过于频繁，请稍后再试",
    }

    return messages.get(error_type, "❌ 发生未知错误")
```

**Step 4: 运行测试验证通过**

```bash
python -m pytest tests/test_formatter.py -v
```

预期输出：所有测试通过

**Step 5: 提交**

```bash
git add utils/formatter.py tests/test_formatter.py
git commit -m "feat: add message formatting utilities"
```

---

## Telegram Bot 消息处理

### Task 7: 实现 Telegram 消息处理器

**Files:**
- Create: `handlers/message_handler.py`

**Step 1: 创建消息处理器**

```python
# handlers/message_handler.py
from telegram import Update
from telegram.ext import ContextTypes
from handlers.link_handler import LinkHandler
from utils.validators import is_x_video_url
from utils.formatter import format_success_message, format_error_message


class MessageHandler:
    """Telegram 消息处理器"""

    def __init__(self):
        self.link_handler = LinkHandler()

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """处理 /start 命令"""
        welcome_message = """👋 欢迎！我是 X 视频下载 Bot

使用方法：
1. 发送 X (Twitter) 推文链接
2. 我会解析并返回视频直链
3. 点击链接即可下载

支持的链接格式：
• https://x.com/user/status/123456
• https://twitter.com/user/status/123456"""

        await update.message.reply_text(welcome_message)

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """处理 /help 命令"""
        help_message = """📖 使用帮助

发送 X (Twitter) 推文链接，我会返回视频的直链。

注意事项：
• 只支持公开推文
• 私密推文无法解析
• 自动选择最高画质

如有问题请联系管理员。"""

        await update.message.reply_text(help_message)

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """处理普通消息"""
        # 获取消息文本
        text = update.message.text

        if not text:
            return

        # 检查是否为 X 链接
        if not is_x_video_url(text):
            await update.message.reply_text(format_error_message("invalid_url"))
            return

        # 发送处理中消息
        processing_msg = await update.message.reply_text("⏳ 正在解析...")

        try:
            # 解析视频
            video_info = await self.link_handler.parse_x_video(text)

            # 删除处理中消息
            await processing_msg.delete()

            if video_info:
                # 发送结果
                await update.message.reply_text(
                    format_success_message(video_info),
                    parse_mode="Markdown"
                )
            else:
                await update.message.reply_text(format_error_message("no_video"))

        except Exception as e:
            await processing_msg.delete()
            await update.message.reply_text(format_error_message("parse_failed"))
            print(f"Error: {e}")
```

**Step 2: 验证文件创建成功**

```bash
cat handlers/message_handler.py
```

预期输出：看到上面的代码

**Step 3: 提交**

```bash
git add handlers/message_handler.py
git commit -m "feat: add Telegram message handler"
```

---

## Bot 主程序

### Task 8: 实现 Bot 主程序

**Files:**
- Create: `bot.py`

**Step 1: 创建 Bot 主程序**

```python
# bot.py
import logging
from telegram.ext import Application
from config import Config
from handlers.message_handler import MessageHandler


def setup_logging(log_level: str):
    """配置日志"""
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=getattr(logging, log_level.upper()),
    )


def main():
    """启动 Bot"""
    # 加载配置
    config = Config()

    # 配置日志
    setup_logging(config.log_level)

    # 创建应用
    application = Application.builder().token(config.bot_token).build()

    # 创建消息处理器
    message_handler = MessageHandler()

    # 注册处理器
    application.add_handler("telegram.ext.CommandHandler("start", message_handler.start_command))
    application.add_handler("telegram.ext.CommandHandler("help", message_handler.help_command))
    application.add_handler("telegram.ext.MessageHandler("telegram.ext.filters.TEXT & ~telegram.ext.filters.COMMAND, message_handler.handle_message))

    # 启动 Bot
    print("Bot 启动中...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
```

**Step 2: 修复导入问题（更新 bot.py）**

```python
# bot.py - 修正后的版本
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters, Update
from config import Config
from handlers.message_handler import MessageHandler as MsgHandler


def setup_logging(log_level: str):
    """配置日志"""
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=getattr(logging, log_level.upper()),
    )


def main():
    """启动 Bot"""
    # 加载配置
    config = Config()

    # 配置日志
    setup_logging(config.log_level)

    # 创建应用
    application = Application.builder().token(config.bot_token).build()

    # 创建消息处理器
    msg_handler = MsgHandler()

    # 注册处理器
    application.add_handler(CommandHandler("start", msg_handler.start_command))
    application.add_handler(CommandHandler("help", msg_handler.help_command))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, msg_handler.handle_message)
    )

    # 启动 Bot
    print("Bot 启动中...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
```

**Step 3: 验证文件**

```bash
cat bot.py
```

预期输出：看到修正后的代码

**Step 4: 提交**

```bash
git add bot.py
git commit -m "feat: add main bot application"
```

---

## Docker 部署

### Task 9: 创建 Docker 配置

**Files:**
- Create: `Dockerfile`
- Create: `docker-compose.yml`

**Step 1: 创建 Dockerfile**

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# 安装系统依赖（yt-dlp 可能需要 ffmpeg）
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 运行 Bot
CMD ["python", "bot.py"]
```

**Step 2: 创建 docker-compose.yml**

```yaml
version: '3.8'

services:
  bot:
    build: .
    restart: unless-stopped
    env_file:
      - .env
    environment:
      - TZ=Asia/Shanghai
```

**Step 3: 验证文件**

```bash
cat Dockerfile docker-compose.yml
```

预期输出：看到两个文件的内容

**Step 4: 提交**

```bash
git add Dockerfile docker-compose.yml
git commit -m "feat: add Docker deployment configuration"
```

---

## 完整测试

### Task 10: 运行完整测试套件

**Step 1: 安装依赖**

```bash
pip install -r requirements.txt
```

**Step 2: 运行所有测试**

```bash
python -m pytest tests/ -v
```

预期输出：所有测试通过

**Step 3: 测试本地运行**

```bash
# 设置测试 Token
export BOT_TOKEN="your_test_token"

# 启动 Bot
python bot.py
```

预期输出：Bot 启动成功

**Step 4: 提交**

```bash
git add .
git commit -m "test: ensure all tests pass"
```

---

## 实现完成检查清单

- [ ] 所有测试通过
- [ ] Bot 可以启动
- [ ] /start 命令返回欢迎消息
- [ ] 发送 X 链接可以解析并返回视频直链
- [ ] 发送无效链接返回错误提示
- [ ] Docker 部署正常工作

## 下一步

实现完成后，可以考虑：
1. 添加速率限制
2. 添加更多错误处理
3. 添加日志记录
4. 支持更多平台（YouTube 等）
