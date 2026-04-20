# my-website 部署说明

## 部署方式

### 方式一：Jenkins 自动部署（推荐）

Jenkins 已配置好自动部署 Pipeline，每次 push 到 GitHub 后会自动触发部署。

- Jenkins 地址: http://175.178.98.241:8088
- 账号密码: admin / admin
- Job 名称: my-toolbox-deploy

### 方式二：手动部署

#### 1. 本地提交代码

```bash
cd C:\Users\zhaoz\.qclaw\workspace\my-toolbox
git add .
git commit -m "更新功能"
git push
```

#### 2. 服务器执行部署脚本

```bash
ssh root@175.178.98.241
cd /opt/my-toolbox/archive/scripts
chmod +x deploy.sh
./deploy.sh
```

### 方式三：本地打包上传

如果 Git 或 Jenkins 不可用，可以使用本地打包方式：

```bash
# 1. 本地构建
cd C:\Users\zhaoz\.qclaw\workspace\my-toolbox\frontend
npm run build

# 2. 打包项目（排除 node_modules）
cd C:\Users\zhaoz\.qclaw\workspace\my-toolbox
# 使用 PowerShell 打包
Compress-Archive -Path backend,frontend\dist,python-services,docker-compose.yml,archive -DestinationPath my-website.zip -Force

# 3. 上传到服务器并解压
scp my-website.zip root@175.178.98.241:/tmp/
ssh root@175.178.98.241 "cd /opt && rm -rf my-toolbox && unzip -o /tmp/my-website.zip -d my-toolbox && cd my-toolbox && docker compose up -d --build"
```

## 本次更新内容

**日期**: 2026-04-20

### 项目重命名

1. **my-toolbox → my-website**
   - 项目名称、数据库、容器名全部更新
   - README.md 重写

### 功能更新

1. **数据库迁移改为 Flyway 增量模式**
   - 引入 Flyway 管理数据库版本
   - 迁移脚本位于 backend/src/main/resources/db/migration/
   - 不再每次部署重建表结构

2. **笔记页分类展开/收起功能**
   - 分类树支持展开/收起切换
   - 头部增加全部展开/收起按钮
   - 默认展开所有分类

3. **计划页搜索复用新增框**
   - 搜索和新增合并为一行
   - 删除额外的搜索栏
   - 搜索按钮放在添加按钮后面

4. **清理冗余代码**
   - 删除 NotesController.java（模拟数据，已被 NoteController 替代）
   - 删除旧的 init.sql（由 Flyway 接管）

### 修改的文件

- `backend/pom.xml` - 添加 Flyway 依赖，更新项目名
- `backend/src/main/resources/application.yml` - 数据库名、Flyway 配置
- `backend/src/main/resources/db/migration/V1__init_schema.sql` - Flyway 初始迁移
- `backend/src/main/resources/db/migration/V2__rename_project.sql` - 改名记录
- `backend/sql/init_database.sql` - Docker 初始化脚本
- `backend/src/main/java/com/toolbox/WebsiteApplication.java` - 主类重命名
- `frontend/package.json` - 项目名更新
- `frontend/src/views/notes/Notes.vue` - 分类展开/收起
- `frontend/src/views/plan/Plan.vue` - 搜索复用新增框
- `frontend/src/views/Home.vue` - 标题更新
- `docker-compose.yml` - 容器名、数据库名
- `README.md` - 项目说明重写

## 服务器信息

- IP: 175.178.98.241
- 用户: root
- 密码: zzb12345678#
- 项目路径: /opt/my-toolbox
- Jenkins 端口: 8088
