# 服务器部署指南

## 快速部署

### 1. 准备 .env 文件

```bash
# .env 文件配置示例
TWITTER_COOKIE=auth_token=xxx; ct0=xxx; twid=xxx
LOG_LEVEL=INFO
```

### 2. 部署到服务器

```bash
# 使用自动部署脚本
./scripts/deploy.sh root@your-server.com
```

### 3. 手动部署

```bash
# 1. 上传文件到服务器
scp -r . root@your-server.com:/opt/avdoulou/

# 2. SSH 登录服务器
ssh root@your-server.com

# 3. 进入项目目录
cd /opt/avdoulou

# 4. 启动服务
docker-compose up -d
```

## 服务管理

```bash
# 查看日志
docker-compose logs -f

# 重启服务
docker-compose restart

# 停止服务
docker-compose down

# 查看状态
docker-compose ps
```

## API 端点

| 端点 | 说明 |
|------|------|
| `GET /health` | 健康检查 |
| `GET /extract?url=链接` | 提取视频/图片 |
| `POST /parse` | 解析视频 (JSON Body) |

## iOS 快捷指令配置

```
API URL: http://你的服务器IP:58080/extract?url=
```

## 防火墙配置

```bash
# 开放 58080 端口
ufw allow 58080/tcp
```
