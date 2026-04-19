#!/bin/bash
# my-toolbox 部署脚本
# 日期: 2026-04-20
# 功能: 自动部署前端和后端服务

set -e

PROJECT_DIR="/opt/my-toolbox"
BACKUP_DIR="/opt/my-toolbox-backups"

echo "========================================"
echo "my-toolbox 自动部署脚本"
echo "========================================"

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份当前版本
if [ -d "$PROJECT_DIR" ]; then
    BACKUP_NAME="my-toolbox-$(date +%Y%m%d-%H%M%S).tar.gz"
    echo "正在备份当前版本..."
    tar -czf "$BACKUP_DIR/$BACKUP_NAME" -C "$(dirname $PROJECT_DIR)" "$(basename $PROJECT_DIR)" 2>/dev/null || true
    echo "备份完成: $BACKUP_DIR/$BACKUP_NAME"
fi

# 进入项目目录
cd $PROJECT_DIR

# 拉取最新代码
echo "正在拉取最新代码..."
git pull origin main || git pull origin master

# 构建前端
echo "正在构建前端..."
cd frontend
npm install
npm run build

# 重启服务
echo "正在重启服务..."
cd $PROJECT_DIR
docker compose down
docker compose up -d --build

# 等待服务启动
echo "等待服务启动..."
sleep 10

# 检查服务状态
echo "检查服务状态..."
docker compose ps

echo "========================================"
echo "部署完成！"
echo "访问地址: http://175.178.98.241"
echo "========================================"
