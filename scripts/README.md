# 项目脚本集合

本目录包含项目所有的可执行脚本，按平台和用途分类。

## 目录结构

```
scripts/
├── README.md              # 本文件
├── windows/              # Windows 本地开发脚本
│   ├── start-local.ps1   # 本地一键启动（MySQL + Python + Spring Boot + Vue）
│   └── stop-local.ps1    # 停止本地所有服务
├── linux/                # Linux 服务器脚本
│   ├── start-jenkins.sh # Jenkins 容器启动（已优化内存配置）
│   ├── clean-jenkins.sh # Jenkins 清理脚本（磁盘/内存优化）
│   └── deploy.sh         # 自动化部署脚本（备份+构建+重启）
└── utils/                # 工具脚本（预留）
```

## 使用说明

### Windows 本地开发

```powershell
# 启动所有本地服务
.\scripts\windows\start-local.ps1

# 停止所有本地服务
.\scripts\windows\stop-local.ps1
```

**依赖：**
- Docker Desktop（用于 MySQL 容器）
- Maven（用于 Spring Boot）
- Python 3（用于 Python 服务）
- Node.js / npm（用于 Vue 前端）

### Linux 服务器

```bash
# 启动 Jenkins（优化版）
bash scripts/linux/start-jenkins.sh

# 清理 Jenkins（磁盘/内存）
bash scripts/linux/clean-jenkins.sh
```

**服务器环境要求：**
- Docker
- Bash shell

## 脚本详情

| 脚本 | 平台 | 功能 |
|------|------|------|
| start-local.ps1 | Windows | 本地开发一键启动 |
| stop-local.ps1 | Windows | 停止本地服务 |
| start-jenkins.sh | Linux | Jenkins 容器启动（1G内存+G1GC） |
| clean-jenkins.sh | Linux | Jenkins 清理（workspace/构建历史/Maven仓库） |
| deploy.sh | Linux | 自动化部署（备份+构建+重启） |

## 更新日志

- 2026-05-13: 添加 start-jenkins.sh（Jenkins 内存优化启动脚本）
- 2026-05-13: 添加 deploy.sh（自动化部署脚本）
- 2026-04-23: 添加 clean-jenkins.sh（Jenkins 清理脚本）
- 2026-04-20: 初始版本