# Docker 容器化部署入门

> 来源：综合整理自马哥教育、CSDN 等技术文章  
> 整理日期：2026-04-25

---

## 一、Docker 简介

### 1. 什么是 Docker？

**Docker** 是一个开源的容器化平台，可以让开发者打包应用及其依赖到一个可移植的容器中，然后发布到任何流行的 Linux 或 Windows 机器上。

### 2. 核心概念

| 概念 | 说明 | 类比 |
|------|------|------|
| **镜像 (Image)** | 只读模板，包含应用代码、运行时环境和配置 | 类（Class） |
| **容器 (Container)** | 镜像的运行实例，拥有独立文件系统和网络 | 对象（Object） |
| **Dockerfile** | 文本文件，定义镜像构建步骤 | 构建脚本 |
| **仓库 (Registry)** | 存储和分发镜像的服务 | 应用商店 |

### 3. Docker vs 虚拟机

| 特性 | Docker 容器 | 虚拟机 |
|------|-------------|--------|
| **启动速度** | 秒级 | 分钟级 |
| **资源占用** | 轻量（MB） | 重量级（GB） |
| **性能** | 接近原生 | 有性能损耗 |
| **隔离性** | 进程级隔离 | 系统级隔离 |
| **部署密度** | 单机可部署数百个 | 单机通常十几个 |

---

## 二、Docker 安装

### 1. Ubuntu 安装

```bash
# 更新包索引
sudo apt-get update

# 安装依赖
sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common

# 添加 Docker 官方 GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# 添加 Docker 软件源
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 安装 Docker
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io

# 启动 Docker
sudo systemctl start docker
sudo systemctl enable docker

# 验证安装
docker --version
docker run hello-world
```

### 2. CentOS 安装

```bash
# 安装依赖
sudo yum install -y yum-utils device-mapper-persistent-data lvm2

# 添加软件源
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

# 安装 Docker
sudo yum install -y docker-ce docker-ce-cli containerd.io

# 启动 Docker
sudo systemctl start docker
sudo systemctl enable docker
```

### 3. 配置国内镜像源

```bash
# 创建/编辑配置文件
sudo mkdir -p /etc/docker
sudo tee /etc/docker/daemon.json <<-'EOF'
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com"
  ]
}
EOF

# 重启 Docker
sudo systemctl daemon-reload
sudo systemctl restart docker
```

---

## 三、Docker 基础命令

### 1. 镜像操作

```bash
# 搜索镜像
docker search nginx

# 拉取镜像
docker pull nginx:latest
docker pull nginx:1.21

# 查看本地镜像
docker images

# 删除镜像
docker rmi nginx:latest
docker rmi image_id

# 查看镜像历史
docker history nginx:latest

# 导出镜像
docker save -o nginx.tar nginx:latest

# 导入镜像
docker load -i nginx.tar
```

### 2. 容器操作

```bash
# 运行容器
docker run -d -p 80:80 --name my-nginx nginx:latest

# 参数说明：
# -d: 后台运行
# -p: 端口映射（主机端口:容器端口）
# --name: 指定容器名称
# -v: 挂载卷
# -e: 设置环境变量

# 查看运行中的容器
docker ps

# 查看所有容器（包括停止的）
docker ps -a

# 启动/停止/重启容器
docker start my-nginx
docker stop my-nginx
docker restart my-nginx

# 进入容器
docker exec -it my-nginx /bin/bash

# 查看容器日志
docker logs my-nginx
docker logs -f my-nginx  # 实时查看

# 复制文件
docker cp my-nginx:/etc/nginx/nginx.conf ./
docker cp ./index.html my-nginx:/usr/share/nginx/html/

# 删除容器
docker rm my-nginx
docker rm -f my-nginx  # 强制删除运行中的容器

# 清理已停止的容器
docker container prune
```

### 3. 数据卷操作

```bash
# 创建数据卷
docker volume create my-data

# 查看数据卷
docker volume ls

# 查看数据卷详情
docker volume inspect my-data

# 删除数据卷
docker volume rm my-data

# 使用数据卷运行容器
docker run -d -v my-data:/data nginx:latest
```

---

## 四、Dockerfile 编写

### 1. Dockerfile 指令

| 指令 | 说明 | 示例 |
|------|------|------|
| **FROM** | 基础镜像 | `FROM python:3.9-slim` |
| **WORKDIR** | 工作目录 | `WORKDIR /app` |
| **COPY** | 复制文件 | `COPY . /app` |
| **ADD** | 复制文件（支持URL、自动解压） | `ADD https://... /app/` |
| **RUN** | 执行命令 | `RUN pip install -r requirements.txt` |
| **CMD** | 容器启动命令 | `CMD ["python", "app.py"]` |
| **ENTRYPOINT** | 容器启动入口 | `ENTRYPOINT ["python"]` |
| **ENV** | 环境变量 | `ENV PORT=8080` |
| **EXPOSE** | 暴露端口 | `EXPOSE 8080` |
| **VOLUME** | 挂载点 | `VOLUME ["/data"]` |

### 2. Python 应用示例

```dockerfile
# 使用官方 Python 基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 5000

# 启动命令
CMD ["python", "app.py"]
```

### 3. Node.js 应用示例

```dockerfile
# 使用官方 Node 基础镜像
FROM node:14-alpine

# 设置工作目录
WORKDIR /app

# 复制 package.json
COPY package*.json ./

# 安装依赖
RUN npm install

# 复制项目文件
COPY . .

# 暴露端口
EXPOSE 3000

# 启动命令
CMD ["npm", "start"]
```

### 4. 多阶段构建（优化镜像大小）

```dockerfile
# 构建阶段
FROM node:14-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# 运行阶段
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

---

## 五、Docker Compose

### 1. 什么是 Docker Compose？

Docker Compose 是一个用于定义和运行多容器 Docker 应用的工具，使用 YAML 文件配置应用服务。

### 2. docker-compose.yml 示例

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - .:/app
    environment:
      - FLASK_ENV=development
      - DATABASE_URL=mysql://user:pass@db:3306/mydb
    depends_on:
      - db
    networks:
      - my-network

  db:
    image: mysql:8.0
    environment:
      - MYSQL_ROOT_PASSWORD=rootpass
      - MYSQL_DATABASE=mydb
      - MYSQL_USER=user
      - MYSQL_PASSWORD=pass
    volumes:
      - db-data:/var/lib/mysql
    ports:
      - "3306:3306"
    networks:
      - my-network

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
    networks:
      - my-network

volumes:
  db-data:

networks:
  my-network:
    driver: bridge
```

### 3. Docker Compose 命令

```bash
# 启动所有服务
docker-compose up

# 后台启动
docker-compose up -d

# 构建并启动
docker-compose up --build

# 停止服务
docker-compose down

# 停止并删除卷
docker-compose down -v

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs
docker-compose logs -f web

# 执行命令
docker-compose exec web bash

# 重启服务
docker-compose restart

# 拉取最新镜像
docker-compose pull
```

---

## 六、实战案例

### 1. 部署 Web 应用

```bash
# 1. 创建项目目录
mkdir my-web-app && cd my-web-app

# 2. 创建 Dockerfile
cat > Dockerfile << 'EOF'
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
EOF

# 3. 创建 docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'
services:
  web:
    build: .
    ports:
      - "5000:5000"
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - web
EOF

# 4. 启动应用
docker-compose up -d
```

### 2. 数据持久化

```yaml
version: '3.8'
services:
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: password
    volumes:
      # 命名卷持久化
      - mysql_data:/var/lib/mysql
      # 挂载配置文件
      - ./my.cnf:/etc/mysql/my.cnf
      # 挂载初始化脚本
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "3306:3306"

volumes:
  mysql_data:
```

---

## 七、最佳实践

### 1. 镜像优化

- 使用轻量级基础镜像（alpine、slim）
- 多阶段构建减少镜像大小
- 合并 RUN 指令减少层数
- 使用 .dockerignore 排除不需要的文件

```dockerfile
# .dockerignore
node_modules
.git
.env
*.md
```

### 2. 安全实践

- 不以 root 用户运行应用
- 及时更新基础镜像
- 扫描镜像漏洞
- 限制容器资源

```dockerfile
# 使用非 root 用户
FROM node:14-alpine
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nextjs -u 1001
USER nextjs
```

### 3. 日志管理

```bash
# 查看容器日志
docker logs container_name

# 限制日志大小（daemon.json）
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

---

## 八、常见问题

### Q1: 容器无法启动？
**A**: 
- 查看日志：`docker logs container_name`
- 检查端口冲突
- 检查挂载路径是否正确

### Q2: 镜像拉取失败？
**A**: 
- 配置国内镜像源
- 检查网络连接
- 使用代理

### Q3: 如何进入已停止的容器？
**A**: 
```bash
# 提交容器为新镜像
docker commit container_id my-image

# 运行新镜像并进入
docker run -it my-image /bin/bash
```

---

## 九、参考链接

- [Docker 入门指南 - 马哥教育](https://www.magedu.com/wenzhang/linux/7063.html)
- [使用 Docker 构建容器化应用 - 马哥教育](https://www.magedu.com/wenzhang/linux/31211.html)
- [Docker 容器化部署流程 - CSDN](https://blog.csdn.net/2501_92488950/article/details/148817054)
- [Docker 官方文档](https://docs.docker.com/)
