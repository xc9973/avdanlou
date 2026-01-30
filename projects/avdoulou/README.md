# X 视频下载 Telegram Bot

一个简单的 Telegram Bot，用于下载 X (Twitter) 视频直链。

## 功能

- 发送 X 推文链接，获取视频直链
- 自动选择最高画质
- 简单易用

## 环境要求

- Python 3.10 或更高版本

## 部署

```bash
# 复制配置文件
cp .env.example .env

# 编辑 .env，填入你的 BOT_TOKEN

# Docker 部署
docker-compose up -d
```

## 使用

1. 在 Telegram 中找到 @BotFather 创建 Bot
2. 获取 Bot Token
3. 部署此 Bot
4. 向 Bot 发送 X 推文链接

## 本地开发

### 安装依赖

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行测试并显示覆盖率
pytest --cov=. --cov-report=html

# 查看覆盖率报告
open htmlcov/index.html  # Mac
# 或在浏览器中打开 htmlcov/index.html
```

### 运行 Bot

```bash
# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的 BOT_TOKEN

# 运行 Bot
python bot.py
```

## 项目结构

```
bot.py                 # Bot 入口
config.py              # 配置管理
handlers/              # 消息处理器
utils/                 # 工具函数
tests/                 # 测试
```
