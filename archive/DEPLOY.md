# my-toolbox 部署说明

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
Compress-Archive -Path backend,frontend\dist,python-services,docker-compose.yml,archive -DestinationPath my-toolbox.zip -Force

# 3. 上传到服务器并解压
scp my-toolbox.zip root@175.178.98.241:/tmp/
ssh root@175.178.98.241 "cd /opt && rm -rf my-toolbox && unzip -o /tmp/my-toolbox.zip -d my-toolbox && cd my-toolbox && docker compose up -d --build"
```

## 本次更新内容

**日期**: 2026-04-20

### 功能更新

1. **补充说明提示图标**
   - 在计划页和笔记页标题旁添加小 i 图标
   - 鼠标悬停显示详细功能说明

2. **搜索功能完善**
   - 计划页新增搜索功能（支持搜索标题和描述）
   - 笔记页搜索功能优化（支持搜索标题、内容、标签）
   - 添加搜索图标和清除按钮

3. **富文本编辑器优化**
   - 编辑器默认高度从 400px 增加到 600px
   - 提供更好的编辑体验

4. **双击查看笔记**
   - 在笔记列表中双击任意行可快速打开编辑
   - 提升操作效率

### 修改的文件

- `frontend/src/views/plan/Plan.vue` - 添加搜索功能和提示图标
- `frontend/src/views/notes/Notes.vue` - 完善搜索、双击编辑、编辑器高度调整
- `archive/scripts/deploy.sh` - 部署脚本
- `archive/DEPLOY.md` - 部署说明文档

## 服务器信息

- IP: 175.178.98.241
- 用户: root
- 密码: zzb12345678#
- 项目路径: /opt/my-toolbox
- Jenkins 端口: 8088
