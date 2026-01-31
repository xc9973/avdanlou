#!/bin/bash
# 服务器部署脚本
# 使用方法: ./scripts/deploy.sh user@server.com

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 检查参数
if [ -z "$1" ]; then
    echo -e "${RED}错误: 请提供服务器地址${NC}"
    echo "使用方法: $0 user@server.com"
    exit 1
fi

SERVER=$1
PROJECT_NAME="avdoulou"
REMOTE_DIR="/opt/$PROJECT_NAME"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  X 视频解析 API - 服务器部署${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# 1. 检查本地文件
echo -e "${YELLOW}[1/6] 检查本地文件...${NC}"
if [ ! -f ".env" ]; then
    echo -e "${RED}错误: .env 文件不存在${NC}"
    echo "请先创建 .env 文件并配置必要的环境变量"
    exit 1
fi
echo -e "${GREEN}✓ .env 文件存在${NC}"

# 2. 创建服务器目录
echo -e "${YELLOW}[2/6] 创建服务器目录...${NC}"
ssh $SERVER "sudo mkdir -p $REMOTE_DIR && sudo chown \$USER:$REMOTE_DIR"
echo -e "${GREEN}✓ 服务器目录已创建: $REMOTE_DIR${NC}"

# 3. 上传文件
echo -e "${YELLOW}[3/6] 上传项目文件...${NC}"
rsync -av --progress \
    --exclude '.git' \
    --exclude '__pycache__' \
    --exclude '*.pyc' \
    --exclude '.pytest_cache' \
    --exclude 'Downloads' \
    --exclude '.DS_Store' \
    --exclude 'scripts/*.sh' \
    . $SERVER:$REMOTE_DIR/
echo -e "${GREEN}✓ 文件上传完成${NC}"

# 4. 安装 Docker（如果未安装）
echo -e "${YELLOW}[4/6] 检查 Docker...${NC}"
ssh $SERVER "command -v docker >/dev/null 2>&1 || { echo '安装 Docker...'; curl -fsSL https://get.docker.com | sh; }"
ssh $SERVER "command -v docker-compose >/dev/null 2>&1 || { echo '安装 docker-compose...'; sudo apt-get install -y docker-compose; }"
echo -e "${GREEN}✓ Docker 已就绪${NC}"

# 5. 构建并启动容器
echo -e "${YELLOW}[5/6] 启动服务...${NC}"
ssh $SERVER "cd $REMOTE_DIR && docker-compose down && docker-compose build && docker-compose up -d"
echo -e "${GREEN}✓ 服务已启动${NC}"

# 6. 检查服务状态
echo -e "${YELLOW}[6/6] 检查服务状态...${NC}"
sleep 3
ssh $SERVER "docker ps --filter 'name=avdoulou' --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'"
echo ""

# 获取服务器 IP
SERVER_IP=$(ssh $SERVER "curl -s ifconfig.me" || ssh $SERVER "hostname -I | awk '{print \$1}'")
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  部署完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "服务器信息:"
echo -e "  地址: ${GREEN}$SERVER${NC}"
echo -e "  IP: ${GREEN}$SERVER_IP${NC}"
echo -e "  项目目录: ${GREEN}$REMOTE_DIR${NC}"
echo ""
echo -e "API 端点:"
echo -e "  HTTP:  http://$SERVER_IP:58080"
echo -e "  健康检查: http://$SERVER_IP:58080/health"
echo ""
echo -e "iOS 快捷指令配置:"
echo -e "  API URL: http://$SERVER_IP:58080/extract?url="
echo ""
echo -e "管理命令:"
echo -e "  查看日志: ssh $SERVER 'cd $REMOTE_DIR && docker-compose logs -f'"
echo -e "  重启服务: ssh $SERVER 'cd $REMOTE_DIR && docker-compose restart'"
echo -e "  停止服务: ssh $SERVER 'cd $REMOTE_DIR && docker-compose down'"
echo ""
