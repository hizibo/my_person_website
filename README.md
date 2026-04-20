# 🌐 我的网站

个人网站平台，持续建设实用功能。

## 🚀 快速启动

### 方式一：Docker 一键启动（推荐）

```bash
# 启动所有服务（MySQL + 后端 + Python服务 + 前端）
docker-compose up -d

# 查看日志
docker-compose logs -f
```

### 方式二：本地开发启动

**1. 启动 MySQL**
```bash
docker run -d --name website-mysql \
  -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=my_website \
  -p 3306:3306 \
  mysql:8.0 \
  --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci
```

**2. 启动 Python 服务**
```bash
cd python-services
pip install -r requirements.txt
uvicorn xmind_parser.main:app --reload --port 8001
```

**3. 启动 Spring Boot 后端**
```bash
cd backend
mvn spring-boot:run
```

**4. 启动 Vue 前端**
```bash
cd frontend
npm install
npm run dev
```

访问 http://localhost:5173

## 📁 项目结构

```
my-website/
├── frontend/          # Vue 3 前端
│   ├── src/
│   │   ├── views/    # 页面组件
│   │   │   ├── plan/Plan.vue          # 我的计划
│   │   │   ├── notes/Notes.vue        # 我的笔记
│   │   │   ├── website/Website.vue    # 网站管理
│   │   │   └── tools/                 # 工具集
│   │   └── router/
│   └── package.json
│
├── backend/           # Spring Boot 后端
│   ├── src/main/java/com/toolbox/
│   │   ├── controller/   # 接口
│   │   ├── service/      # 业务逻辑
│   │   ├── entity/       # 数据模型
│   │   └── mapper/       # 数据访问
│   ├── src/main/resources/db/migration/  # Flyway 数据库迁移脚本
│   └── pom.xml
│
├── python-services/   # Python 微服务
│   ├── xmind_parser/  # XMind 解析服务
│   │   └── main.py
│   └── requirements.txt
│
└── docker-compose.yml  # 容器编排
```

## 🗄️ 数据库迁移

项目使用 Flyway 管理数据库版本，迁移脚本位于 `backend/src/main/resources/db/migration/`。

- 首次启动自动执行所有迁移
- 后续更新只需新增迁移脚本（如 `V3__add_new_table.sql`）
- **不再每次部署重建表结构**

## 🧪 XMind 转测试用例

上传 `.xmind` 文件，自动转换为标准测试用例，支持 Excel 导出。

## ➕ 添加新功能

添加新功能只需 3 步：

**1. 后端添加 Controller**
```java
// backend/src/main/java/com/toolbox/controller/新功能Controller.java
@RestController
@RequestMapping("/api/新功能")
public class NewFeatureController {
    // 实现业务逻辑
}
```

**2. 前端添加页面**
```vue
// frontend/src/views/新功能/NewFeature.vue
<template>...</template>
```

**3. 注册路由**
```js
// frontend/src/router/index.js
{ path: '/new-feature', component: () => import('@/views/新功能/NewFeature.vue') }
```

**4. 数据库迁移**（如需新表）
```sql
-- backend/src/main/resources/db/migration/V3__add_new_table.sql
CREATE TABLE IF NOT EXISTS ...
```

## 🔧 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + Vite + Element Plus |
| 后端 | Spring Boot 3 + MyBatis-Plus + Flyway |
| 数据库 | MySQL 8 |
| Python服务 | FastAPI |
| 部署 | Docker + Docker Compose |

## 📝 开发说明

- 前端端口: 5173
- 后端端口: 8080
- Python服务端口: 8001
- MySQL端口: 3306

接口文档（后端启动后访问）:
http://localhost:8080/doc
