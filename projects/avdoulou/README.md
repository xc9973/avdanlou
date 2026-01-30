# X 视频下载 Telegram Bot

一个简单的 Telegram Bot，用于下载 X (Twitter) 视频直链。

## 功能

- 发送 X 推文链接，获取视频直链
- 自动选择最高画质
- 简单易用

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

## 项目结构

```
bot.py                 # Bot 入口
config.py              # 配置管理
handlers/              # 消息处理器
utils/                 # 工具函数
tests/                 # 测试
```
