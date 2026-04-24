# Git 高级用法与分支管理

> 来源：综合整理自 Worktile、CSDN 等技术文章  
> 整理日期：2026-04-25

---

## 一、Git 基础回顾

### 1. 常用基础命令

```bash
# 克隆仓库
git clone https://github.com/user/repo.git

# 查看状态
git status

# 添加文件到暂存区
git add filename
git add .  # 添加所有修改

# 提交更改
git commit -m "提交信息"

# 推送到远程
git push origin main

# 拉取更新
git pull origin main
```

### 2. 配置设置

```bash
# 全局配置
git config --global user.name "Your Name"
git config --global user.email "your@email.com"

# 查看配置
git config --list

# 设置默认编辑器
git config --global core.editor "vim"

# 设置别名
git config --global alias.st status
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.ci commit
```

---

## 二、分支管理

### 1. 基础分支操作

```bash
# 查看分支
git branch              # 本地分支
git branch -r           # 远程分支
git branch -a           # 所有分支

# 创建分支
git branch feature-branch

# 切换分支
git checkout feature-branch

# 创建并切换分支（快捷方式）
git checkout -b feature-branch

# 重命名分支
git branch -m old-name new-name

# 删除分支
git branch -d feature-branch      # 已合并的分支
git branch -D feature-branch      # 强制删除

# 删除远程分支
git push origin --delete feature-branch
```

### 2. 分支合并

```bash
# 切换到目标分支
git checkout main

# 合并分支
git merge feature-branch

# 合并时创建合并提交（保留历史）
git merge --no-ff feature-branch

# 取消合并
git merge --abort
```

### 3. 变基（Rebase）

```bash
# 将当前分支变基到 main
git checkout feature-branch
git rebase main

# 交互式变基（修改提交历史）
git rebase -i HEAD~3

# 常用交互式命令：
# p, pick = 使用提交
# r, reword = 使用提交，但修改提交信息
# e, edit = 使用提交，但停止修改
# s, squash = 使用提交，但合并到前一个提交
# d, drop = 删除提交

# 继续变基（解决冲突后）
git rebase --continue

# 跳过当前提交
git rebase --skip

# 取消变基
git rebase --abort
```

---

## 三、Git 工作流

### 1. Git Flow 工作流

```
main (生产分支)
  ↑
develop (开发分支)
  ↑
feature/* (功能分支)
  ↑
release/* (发布分支)
  ↑
hotfix/* (热修复分支)
```

**分支说明**：

| 分支 | 用途 | 生命周期 |
|------|------|----------|
| **main** | 生产环境代码，保持稳定 | 永久 |
| **develop** | 开发主分支，集成最新功能 | 永久 |
| **feature/*** | 开发新功能 | 从 develop 创建，合并后删除 |
| **release/*** | 准备发布，测试和修复 | 从 develop 创建，合并后删除 |
| **hotfix/*** | 生产环境紧急修复 | 从 main 创建，合并后删除 |

**Git Flow 命令**：

```bash
# 初始化 Git Flow
git flow init

# 创建功能分支
git flow feature start my-feature

# 完成功能分支
git flow feature finish my-feature

# 创建发布分支
git flow release start 1.0.0

# 完成发布分支
git flow release finish 1.0.0

# 创建热修复分支
git flow hotfix start fix-bug

# 完成热修复分支
git flow hotfix finish fix-bug
```

### 2. GitHub Flow 工作流

简化版工作流，适合持续部署：

```
main 分支（始终可部署）
  ↑
feature-branch（功能分支）
```

**流程**：
1. 从 main 创建功能分支
2. 在功能分支上开发
3. 提交 Pull Request
4. 代码审查和讨论
5. 合并到 main
6. 自动部署

### 3. GitLab Flow 工作流

结合 Git Flow 和 GitHub Flow 的优点：

```
production（生产分支）
  ↑
pre-production（预发布分支）
  ↑
main（主分支）
  ↑
feature/*（功能分支）
```

---

## 四、高级操作

### 1. 储藏（Stash）

```bash
# 储藏当前修改
git stash

# 储藏并添加说明
git stash save "工作进度保存"

# 查看储藏列表
git stash list

# 应用最近储藏
git stash apply

# 应用指定储藏
git stash apply stash@{2}

# 应用并删除储藏
git stash pop

# 删除储藏
git stash drop stash@{0}

# 清空所有储藏
git stash clear

# 从储藏创建分支
git stash branch new-branch stash@{0}
```

### 2. 撤销操作

```bash
# 撤销工作区的修改
git checkout -- filename

# 撤销暂存区的修改
git reset HEAD filename

# 撤销最后一次提交（保留修改）
git reset --soft HEAD~1

# 撤销最后一次提交（丢弃修改）
git reset --hard HEAD~1

# 查看 reflog（操作历史）
git reflog

# 恢复到指定状态
git reset --hard HEAD@{2}
```

### 3. 提交修改

```bash
# 修改最后一次提交
git commit --amend

# 修改最后一次提交（不修改信息）
git commit --amend --no-edit

# 修改提交作者
git commit --amend --author="New Name <new@email.com>"
```

### 4. Cherry-pick

```bash
# 将指定提交应用到当前分支
git cherry-pick commit-hash

# Cherry-pick 多个提交
git cherry-pick hash1 hash2

# Cherry-pick 一个范围
git cherry-pick hash1^..hash2
```

### 5. 子模块（Submodule）

```bash
# 添加子模块
git submodule add https://github.com/user/repo.git path/to/submodule

# 克隆包含子模块的仓库
git clone --recursive https://github.com/user/repo.git

# 初始化子模块
git submodule update --init --recursive

# 更新子模块
git submodule update --recursive
```

---

## 五、远程仓库操作

### 1. 远程仓库管理

```bash
# 查看远程仓库
git remote -v

# 添加远程仓库
git remote add origin https://github.com/user/repo.git

# 修改远程仓库地址
git remote set-url origin https://new-url.git

# 删除远程仓库
git remote remove origin

# 重命名远程仓库
git remote rename old-name new-name
```

### 2. 获取和推送

```bash
# 获取远程更新（不合并）
git fetch origin

# 获取所有远程分支
git fetch --all

# 拉取并合并
git pull origin main

# 拉取使用变基
git pull --rebase origin main

# 推送到远程
git push origin main

# 强制推送（谨慎使用）
git push -f origin main

# 推送所有分支
git push --all origin

# 推送标签
git push origin tag-name

# 推送所有标签
git push origin --tags
```

### 3. 跟踪远程分支

```bash
# 建立本地分支与远程分支的关联
git branch --set-upstream-to=origin/main main

# 创建本地分支并跟踪远程分支
git checkout -b feature-branch origin/feature-branch

# 删除远程分支的跟踪
git branch --unset-upstream
```

---

## 六、标签管理

```bash
# 创建轻量标签
git tag v1.0.0

# 创建附注标签
git tag -a v1.0.0 -m "版本 1.0.0"

# 查看标签
git tag
git tag -l "v1.*"

# 查看标签详情
git show v1.0.0

# 推送标签到远程
git push origin v1.0.0

# 推送所有标签
git push origin --tags

# 删除本地标签
git tag -d v1.0.0

# 删除远程标签
git push origin --delete v1.0.0

# 检出标签（创建分支）
git checkout -b version1 v1.0.0
```

---

## 七、日志和查看

### 1. 查看提交历史

```bash
# 基本日志
git log

# 简洁格式
git log --oneline

# 图形化显示
git log --graph --oneline --all

# 查看文件修改历史
git log -p filename

# 查看某人的提交
git log --author="username"

# 查看最近 N 次提交
git log -5

# 查看文件修改统计
git log --stat

# 查看某行代码的修改历史
git blame filename
```

### 2. 查看差异

```bash
# 查看工作区与暂存区的差异
git diff

# 查看暂存区与最新提交的差异
git diff --cached
git diff --staged

# 查看指定文件的差异
git diff filename

# 查看两次提交之间的差异
git diff commit1 commit2

# 查看分支之间的差异
git diff main feature-branch
```

---

## 八、最佳实践

### 1. 提交规范

**Commit Message 格式**：
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Type 类型**：
- **feat**: 新功能
- **fix**: 修复 bug
- **docs**: 文档修改
- **style**: 代码格式修改（不影响功能）
- **refactor**: 代码重构
- **test**: 测试相关
- **chore**: 构建过程或辅助工具的变动

**示例**：
```
feat(user): 添加用户登录功能

- 实现 JWT 认证
- 添加登录页面
- 集成短信验证码

Closes #123
```

### 2. 分支命名规范

```
feature/user-login       # 功能分支
bugfix/login-error       # Bug 修复分支
hotfix/security-patch    # 热修复分支
release/v1.0.0           # 发布分支
docs/api-update          # 文档分支
```

### 3. 协作流程

1. **更新代码**：`git pull origin main`
2. **创建分支**：`git checkout -b feature/xxx`
3. **提交更改**：`git commit -m "xxx"`
4. **推送分支**：`git push origin feature/xxx`
5. **创建 Pull Request**
6. **代码审查**
7. **合并分支**
8. **删除分支**

---

## 九、常见问题

### Q1: 合并冲突怎么解决？
**A**: 
```bash
# 1. 查看冲突文件
git status

# 2. 手动编辑冲突文件，解决冲突

# 3. 标记为已解决
git add filename

# 4. 完成合并
git commit -m "解决合并冲突"
```

### Q2: 误删分支怎么恢复？
**A**: 
```bash
# 查看 reflog 找到分支的 commit
git reflog

# 创建分支恢复
git checkout -b branch-name commit-hash
```

### Q3: 如何忽略已跟踪的文件？
**A**: 
```bash
# 1. 添加到 .gitignore

# 2. 从暂存区移除，但保留文件
git rm --cached filename

# 3. 提交更改
git commit -m "停止跟踪文件"
```

---

## 十、参考链接

- [Git 分支管理与工作流实践 - CSDN](https://blog.csdn.net/Lee_3S/article/details/147264849)
- [Git 之三 - 分支管理 - Clay 的技术空间](https://www.techgrow.cn/posts/501d8c1.html)
- [Git 官方文档](https://git-scm.com/doc)
- [Git Flow 工作流](https://nvie.com/posts/a-successful-git-branching-model/)
