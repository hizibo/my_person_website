# 🧰 我的工具箱

个人工具平台，持续上架实用小工具。

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
docker run -d --name toolbox-mysql \
  -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=my_toolbox \
  -p 3306:3306 \
  mysql:8.0 \
  --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci
```

**2. 初始化数据库**
```bash
mysql -uroot -proot -h127.0.0.1 < backend/sql/init.sql
```

**3. 启动 Python 服务**
```bash
cd python-services
pip install -r requirements.txt
uvicorn xmind_parser.main:app --reload --port 8001
```

**4. 启动 Spring Boot 后端**
```bash
cd backend
mvn spring-boot:run
```

**5. 启动 Vue 前端**
```bash
cd frontend
npm install
npm run dev
```

访问 http://localhost:5173

## 📁 项目结构

```
my-toolbox/
├── frontend/          # Vue 3 前端
│   ├── src/
│   │   ├── views/    # 页面组件
│   │   │   ├── Home.vue           # 首页（工具列表）
│   │   │   └── tools/
│   │   │       └── XmindTool.vue  # XMind工具
│   │   └── router/
│   └── package.json
│
├── backend/           # Spring Boot 后端
│   ├── src/main/java/com/toolbox/
│   │   ├── controller/   # 接口
│   │   ├── service/      # 业务逻辑
│   │   ├── entity/       # 数据模型
│   │   └── mapper/       # 数据访问
│   ├── sql/
│   │   └── init.sql      # 数据库初始化
│   └── pom.xml
│
├── python-services/   # Python 微服务
│   ├── xmind_parser/  # XMind 解析服务
│   │   └── main.py
│   └── requirements.txt
│
└── docker-compose.yml  # 容器编排
```

## 🧪 XMind 转测试用例

上传 `.xmind` 文件，自动转换为标准测试用例，支持 Excel 导出。

## ➕ 添加新工具

添加新工具只需 3 步：

**1. 后端添加 Controller**
```java
// backend/src/main/java/com/toolbox/controller/新工具Controller.java
@RestController
@RequestMapping("/api/tool/新工具")
public class NewToolController {
    // 实现业务逻辑
}
```

**2. 前端添加页面**
```vue
// frontend/src/views/tools/NewTool.vue
<template>...</template>
```

**3. 注册路由**
```js
// frontend/src/router/index.js
{ path: '/tools/new', component: () => import('@/views/tools/NewTool.vue') }
```

**4. 数据库添加记录**（可选）
```sql
INSERT INTO sys_tool (tool_id, name, ...) VALUES ('new_tool', '新工具', ...);
```

## 🔧 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + Vite + Element Plus |
| 后端 | Spring Boot 3 + MyBatis-Plus |
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
