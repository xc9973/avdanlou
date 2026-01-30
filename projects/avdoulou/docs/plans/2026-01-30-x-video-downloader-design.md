# X 视频下载 Telegram Bot 设计文档

## 概述

一个基于 Telegram 的 X (Twitter) 视频下载 Bot。用户发送 X 推文链接，Bot 解析并返回视频的直链，用户点击即可直接下载。

## 功能范围

| 功能 | 状态 |
|------|------|
| X 视频解析与直链返回 | ✅ |
| 默认最高画质 | ✅ |
| 链接验证与错误处理 | ✅ |
| 图片下载 | ❌ |
| 推文文字获取 | ❌ |
| 私密/登录内容 | ❌ |

## 架构设计

### 整体架构

```
┌─────────┐      ┌──────────┐      ┌─────────┐
│  用户   │ ──►  │ Telegram │ ──►  │   Bot   │
└─────────┘      └──────────┘      └────┬────┘
                                           │
                                           ▼
                                    ┌─────────────┐
                                    │  yt-dlp     │
                                    └──────┬──────┘
                                           │
                                           ▼
                                    ┌─────────────┐
                                    │ 返回视频直链│
                                    └─────────────┘
```

### 技术栈

- **语言**: Python 3.12+
- **Bot 框架**: `python-telegram-bot` (PTB)
- **视频解析**: `yt-dlp`
- **运行方式**: Docker + docker-compose

## 组件设计

### 1. 主应用 (`bot.py`)

Bot 入口，负责：
- 初始化 Telegram Bot
- 注册命令处理器
- 启动长轮询或 Webhook

### 2. 配置管理 (`config.py`)

使用 Pydantic 管理配置：
- `BOT_TOKEN`: Telegram Bot Token
- `LOG_LEVEL`: 日志级别
- `RATE_LIMIT`: 速率限制（每用户每分钟请求数）

### 3. 链接处理器 (`link_handler.py`)

核心业务逻辑：

```python
class XVideoLinkHandler:
    async def process(self, url: str) -> Result:
        # 1. 验证是否为 X/Twitter 链接
        # 2. 调用 yt-dlp 解析
        # 3. 提取最高画质视频 URL
        # 4. 返回结果
```

### 4. 消息处理器 (`message_handler.py`)

处理 Telegram 消息：
- `/start` - 欢迎消息和使用说明
- `/help` - 帮助信息
- 链接消息 - 触发视频解析

### 5. 输出格式化 (`formatter.py`)

格式化返回消息：
- 成功：视频标题 + 直链 + 时长 + 分辨率
- 错误：友好的错误提示

## 数据流

### 正常流程

```
1. 用户发送 X 链接
   ↓
2. Bot 接收消息，验证链接格式
   ↓
3. 调用 yt-dlp 解析
   ↓
4. 提取最高画质视频 URL
   ↓
5. 格式化回复消息
   ↓
6. 发送给用户
```

### 错误处理

| 错误类型 | 处理方式 |
|----------|----------|
| 无效链接格式 | 提示用户发送有效的 X 推文链接 |
| 链接中无视频 | 提示该推文不包含视频 |
| yt-dlp 解析失败 | 提示解析失败，可能是私密内容或链接失效 |
| 网络超时 | 提示稍后重试 |
| 速率限制 | 提示用户稍后再试 |

## 项目结构

```
x-video-downloader/
├── bot.py                 # Bot 入口
├── config.py              # 配置管理
├── handlers/
│   ├── __init__.py
│   ├── link_handler.py    # 链接处理逻辑
│   └── message_handler.py # Telegram 消息处理
├── utils/
│   ├── __init__.py
│   ├── formatter.py       # 消息格式化
│   └── validators.py      # 链接验证
├── tests/
│   ├── test_link_handler.py
│   └── test_validators.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## 依赖项

```
python-telegram-bot==21.0
yt-dlp==2024.12.6
pydantic==2.10.4
pydantic-settings==2.6.1
```

## 安全考虑

1. **输入验证** - 严格验证 URL 格式，防止注入攻击
2. **速率限制** - 防止滥用，每个用户每分钟限制 N 次请求
3. **日志脱敏** - 不记录完整的用户聊天内容
4. **错误信息** - 不暴露内部实现细节

## 测试策略

### 单元测试
- 链接验证函数
- 消息格式化函数
- yt-dlp 解析结果的解析逻辑

### 集成测试
- 使用测试 Bot Token 测试完整流程
- Mock yt-dlp 响应

### 测试用例
| 场景 | 预期结果 |
|------|----------|
| 正常 X 视频链接 | 返回视频直链 |
| 无视频的推文 | 提示无视频 |
| 无效链接 | 提示链接格式错误 |
| 私密推文 | 提示无法访问 |
| 空消息 | 忽略或提示 |

## 部署方案

### 本地开发

```bash
pip install -r requirements.txt
export BOT_TOKEN="your_token"
python bot.py
```

### Docker 部署

```bash
docker-compose up -d
```

### 服务器要求

- CPU: 1 核心以上
- 内存: 512MB 以上
- 存储: 无需存储（无状态）
- 网络: 需访问 Telegram API 和 X/Twitter

## 后续扩展可能性

1. 支持 YouTube 视频
2. 添加图片下载功能
3. 支持用户选择清晰度
4. 服务器下载后转发文件
5. 支持批量下载
6. 添加下载历史记录

## 实现优先级

| 优先级 | 任务 |
|--------|------|
| P0 | 基础 Bot 框架 + /start 命令 |
| P0 | 链接验证 + yt-dlp 集成 |
| P0 | 返回视频直链 |
| P1 | 错误处理完善 |
| P1 | 单元测试 |
| P2 | Docker 部署配置 |
| P2 | 速率限制 |
