#!/bin/bash
# Jenkins 清理脚本 - 适用于低资源服务器
# 用法: bash /opt/scripts/clean-jenkins.sh

set -e

echo "=========================================="
echo "Jenkins 清理脚本 - $(date)"
echo "=========================================="

# Jenkins 容器名称
JENKINS_CONTAINER="jenkins"
JENKINS_HOME="/var/jenkins_home"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查磁盘空间
echo -e "\n${YELLOW}[1/6] 检查磁盘空间...${NC}"
df -h /
echo ""

# 清理 Docker 未使用资源（最激进）
echo -e "${YELLOW}[2/6] 清理 Docker 未使用资源...${NC}"
echo "清理停止的容器..."
docker container prune -f

echo "清理未使用的镜像（保留最近构建的）..."
docker image prune -a -f --filter "until=24h"

echo "清理未使用的卷..."
docker volume prune -f

echo "清理构建缓存..."
docker builder prune -f --filter "until=24h"

echo "清理网络..."
docker network prune -f

# 清理 Jenkins workspace
echo -e "\n${YELLOW}[3/6] 清理 Jenkins workspace...${NC}"
docker exec $JENKINS_CONTAINER bash -c '
    cd /var/jenkins_home/workspace
    # 保留最新的构建目录，删除旧的
    for job in */; do
        if [ -d "$job" ]; then
            # 只保留最近的 1 个构建
            builds=$(ls -dt "$job"* 2>/dev/null | head -n 1)
            if [ -n "$builds" ]; then
                ls -dt "$job"* 2>/dev/null | grep -v "^$builds$" | xargs rm -rf 2>/dev/null || true
            fi
        fi
    done
    echo "Workspace 清理完成"
'

# 清理 Jenkins 构建历史
echo -e "\n${YELLOW}[4/6] 清理 Jenkins 构建历史...${NC}"
docker exec $JENKINS_CONTAINER bash -c '
    cd /var/jenkins_home/jobs
    for job in */; do
        if [ -d "${job}builds" ]; then
            cd "${job}builds"
            # 只保留最近 3 次构建
            builds_to_keep=$(ls -dt [0-9]* 2>/dev/null | head -n 3)
            if [ -n "$builds_to_keep" ]; then
                ls -dt [0-9]* 2>/dev/null | grep -v -E "^($(echo "$builds_to_keep" | tr "\n" "|"))$" | xargs rm -rf 2>/dev/null || true
            fi
            cd /var/jenkins_home/jobs
        fi
    done
    echo "构建历史清理完成"
'

# 清理 Jenkins 临时文件和日志
echo -e "\n${YELLOW}[5/6] 清理 Jenkins 临时文件...${NC}"
docker exec $JENKINS_CONTAINER bash -c '
    # 清理临时文件
    rm -rf /var/jenkins_home/tmp/* 2>/dev/null || true
    
    # 清理缓存
    rm -rf /var/jenkins_home/cache/* 2>/dev/null || true
    
    # 截断日志文件（保留最后 100 行）
    find /var/jenkins_home/logs -name "*.log" -exec sh -c "tail -n 100 \"\$1\" > \"\$1.tmp\" && mv \"\$1.tmp\" \"\$1\"" _ {} \; 2>/dev/null || true
    
    # 清理旧的 agent jar
    find /var/jenkins_home -name "agent.jar" -mtime +7 -delete 2>/dev/null || true
    
    echo "临时文件清理完成"
'

# 清理 Maven 本地仓库中的旧快照
echo -e "\n${YELLOW}[6/6] 清理 Maven 本地仓库...${NC}"
docker exec $JENKINS_CONTAINER bash -c '
    if [ -d /root/.m2/repository ]; then
        # 删除超过 30 天未访问的 SNAPSHOT
        find /root/.m2/repository -name "*-SNAPSHOT*" -type d -atime +30 -exec rm -rf {} \; 2>/dev/null || true
        echo "Maven 仓库清理完成"
    fi
'

# 重启 Jenkins 释放内存
echo -e "\n${RED}清理完成！${NC}"
echo -e "${YELLOW}是否重启 Jenkins 容器以释放内存？(y/n)${NC}"
read -t 5 -n 1 restart_jenkins
if [[ "$restart_jenkins" == "y" || "$restart_jenkins" == "Y" ]]; then
    echo -e "\n重启 Jenkins..."
    docker restart $JENKINS_CONTAINER
    echo -e "${GREEN}Jenkins 已重启${NC}"
fi

# 显示清理后的磁盘空间
echo -e "\n${GREEN}=========================================="
echo "清理后磁盘空间:"
echo "==========================================${NC}"
df -h /

echo -e "\n${GREEN}Docker 磁盘使用情况:${NC}"
docker system df

echo -e "\n${GREEN}清理完成！$(date)${NC}"
