#!/bin/bash
# my-website 自动化部署脚本
# 日期: 2026-05-13
# 功能: 增量部署（默认）或全量部署
# 用法:
#   bash scripts/linux/deploy.sh          # 增量部署（git pull + 重建变更服务）
#   bash scripts/linux/deploy.sh --full   # 全量部署（备份 + 重建所有服务）

set -e

PROJECT_DIR="/opt/my-toolbox"
BACKUP_DIR="/opt/my-toolbox-backups"
FULL_MODE=false

# 解析参数
if [[ "$1" == "--full" ]]; then
    FULL_MODE=true
fi

echo "=========================================="
echo "my-website 部署脚本 ($([ "$FULL_MODE" = true ] && echo '全量' || echo '增量'))"
echo "=========================================="

cd $PROJECT_DIR

# 拉取最新代码
echo "[1/4] 拉取最新代码..."
git fetch origin
BEFORE=$(git rev-parse HEAD)
git pull origin main
AFTER=$(git rev-parse HEAD)

if [ "$BEFORE" = "$AFTER" ] && [ "$FULL_MODE" = false ]; then
    echo "代码无变更，跳过部署。"
    exit 0
fi

if [ "$FULL_MODE" = true ]; then
    # 全量部署：备份 + 重建所有
    echo "[2/4] 全量部署：备份当前版本..."
    mkdir -p $BACKUP_DIR
    BACKUP_NAME="my-website-$(date +%Y%m%d-%H%M%S).tar.gz"
    tar -czf "$BACKUP_DIR/$BACKUP_NAME" \
        --exclude='node_modules' \
        --exclude='.git' \
        -C "$(dirname $PROJECT_DIR)" "$(basename $PROJECT_DIR)" 2>/dev/null || true
    echo "备份完成: $BACKUP_DIR/$BACKUP_NAME"

    echo "[3/4] 重建所有服务..."
    docker compose down
    docker compose up -d --build
else
    # 增量部署：检测变更的服务，只重建变更的
    echo "[2/4] 增量部署：检测变更..."
    CHANGED=$(git diff --name-only $BEFORE $AFTER)

    REBUILD_BACKEND=false
    REBUILD_FRONTEND=false
    REBUILD_PYTHON=false
    RESTART_MYSQL=false

    if echo "$CHANGED" | grep -q "backend/"; then REBUILD_BACKEND=true; fi
    if echo "$CHANGED" | grep -q "frontend/"; then REBUILD_FRONTEND=true; fi
    if echo "$CHANGED" | grep -q "python-services/"; then REBUILD_PYTHON=true; fi
    if echo "$CHANGED" | grep -q "mysql-optimizations\|docker-compose"; then RESTART_MYSQL=true; fi

    echo "变更文件:"
    echo "$CHANGED"
    echo ""
    echo "重建计划: 后端=$REBUILD_BACKEND 前端=$REBUILD_FRONTEND Python=$REBUILD_PYTHON MySQL=$RESTART_MYSQL"

    echo "[3/4] 重建变更服务..."
    if [ "$REBUILD_BACKEND" = true ] || [ "$REBUILD_FRONTEND" = true ]; then
        docker compose up -d --build backend frontend
    fi
    if [ "$REBUILD_PYTHON" = true ]; then
        docker compose up -d --build python-tools
    fi
    if [ "$RESTART_MYSQL" = true ]; then
        docker compose up -d --build mysql
    fi
    # 如果没有任何特定服务变更但有其他文件变更，重建所有
    if [ "$REBUILD_BACKEND" = false ] && [ "$REBUILD_FRONTEND" = false ] && [ "$REBUILD_PYTHON" = false ] && [ "$RESTART_MYSQL" = false ]; then
        docker compose up -d --build
    fi
fi

# 等待服务启动
echo "[4/4] 等待服务启动..."
sleep 15

# 检查服务状态
echo ""
echo "=========================================="
echo "部署完成！"
echo "=========================================="
docker compose ps
echo ""
echo "访问地址: http://175.178.98.241"
echo "=========================================="