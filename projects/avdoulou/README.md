# X 媒体下载 Telegram Bot

一个简单的 Telegram Bot，用于下载 X (Twitter) 视频和图片。

## 功能

- 📹 自动下载推文中的视频
- 🖼️ 批量下载推文中的图片（最多10张）
- 🔗 视频超过 50MB 返回直链
- 👤 用户白名单保护
- 🎨 自动选择最高画质

## 环境要求

- Python 3.10 或更高版本
- Docker（可选）

## 部署

```bash
# 复制配置文件
cp .env.example .env

# 编辑 .env，填入你的 BOT_TOKEN 和白名单用户 ID
nano .env

# Docker 部署
docker compose up -d
```

## 使用

1. 在 Telegram 中找到 @BotFather 创建 Bot
2. 获取 Bot Token
3. 获取你的 Telegram User ID（发送消息给 @userinfobot）
4. 配置 `.env` 文件
5. 部署此 Bot
6. 向 Bot 发送 X 推文链接

## 本地开发

### 安装依赖

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac

# 安装依赖
pip install -r requirements.txt
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行测试并显示覆盖率
pytest --cov=. --cov-report=html
```

### 运行 Bot

```bash
# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的 BOT_TOKEN 和 ALLOWED_USER_IDS

# 运行 Bot
python bot.py
```

### 命令行工具

```bash
# 只获取直链
python cli.py "https://x.com/user/status/123456"

# 下载到本地
python cli.py "https://x.com/user/status/123456" --download
```

## 项目结构

```
bot.py                 # Bot 入口
config.py              # 配置管理
cli.py                 # 命令行工具
handlers/              # 消息处理器
utils/                 # 工具函数
tests/                 # 测试
```
