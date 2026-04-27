-- ============================================================
-- my_website 数据库完整初始化脚本
-- 合并 V1~V8 所有 Flyway 迁移 + 安全加固
-- 生成时间: 2026-04-28
-- ============================================================

-- 创建数据库
CREATE DATABASE IF NOT EXISTS my_website DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE my_website;

-- ============================================================
-- 表结构
-- ============================================================

-- 工具表
CREATE TABLE IF NOT EXISTS sys_tool (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    tool_id VARCHAR(64) NOT NULL UNIQUE COMMENT '工具唯一标识',
    name VARCHAR(128) NOT NULL COMMENT '工具名称',
    icon VARCHAR(32) DEFAULT '🔧' COMMENT '图标',
    category VARCHAR(64) DEFAULT '其他工具' COMMENT '分类',
    description VARCHAR(512) COMMENT '描述',
    route VARCHAR(128) COMMENT '前端路由',
    backend_path VARCHAR(256) COMMENT '后端接口路径',
    status VARCHAR(16) DEFAULT 'offline' COMMENT 'online/offline/dev',
    sort INT DEFAULT 0 COMMENT '排序',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_tool_id (tool_id),
    INDEX idx_status (status),
    INDEX idx_sort (sort)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='工具表';

-- 使用记录表
CREATE TABLE IF NOT EXISTS tool_usage_log (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    tool_id VARCHAR(64) NOT NULL COMMENT '工具ID',
    user_ip VARCHAR(64) COMMENT '用户IP',
    params TEXT COMMENT '请求参数',
    result_size INT DEFAULT 0 COMMENT '结果大小',
    duration_ms INT DEFAULT 0 COMMENT '耗时(ms)',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_tool_id (tool_id),
    INDEX idx_create_time (create_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='工具使用记录';

-- 计划表
CREATE TABLE IF NOT EXISTS plan (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL COMMENT '计划标题',
    description TEXT COMMENT '计划描述',
    progress INT DEFAULT 0 COMMENT '进度(0-100)',
    status VARCHAR(16) DEFAULT 'active' COMMENT '状态: active/completed/cancelled',
    sort INT DEFAULT 0 COMMENT '排序',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_status (status),
    INDEX idx_create_time (create_time),
    INDEX idx_plan_sort (sort)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='计划表';

-- 网站收藏表
CREATE TABLE IF NOT EXISTS website_bookmark (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL COMMENT '网站名称',
    url VARCHAR(1024) NOT NULL COMMENT '网站地址',
    account VARCHAR(255) DEFAULT NULL COMMENT '账号',
    password VARCHAR(255) DEFAULT NULL COMMENT '密码',
    description VARCHAR(512) DEFAULT NULL COMMENT '网站描述',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_create_time (create_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='网站收藏表';

-- 笔记分类表
CREATE TABLE IF NOT EXISTS note_category (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(128) NOT NULL COMMENT '分类名称',
    parent_id BIGINT DEFAULT 0 COMMENT '父分类ID，0表示根分类',
    sort INT DEFAULT 0 COMMENT '排序',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_parent_id (parent_id),
    INDEX idx_sort (sort)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='笔记分类表';

-- 笔记表
CREATE TABLE IF NOT EXISTS note (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    category_id BIGINT NOT NULL COMMENT '分类ID',
    title VARCHAR(255) NOT NULL COMMENT '笔记标题',
    content LONGTEXT COMMENT '笔记内容（HTML格式）',
    summary VARCHAR(512) COMMENT '摘要',
    tags VARCHAR(255) COMMENT '标签，逗号分隔',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_category_id (category_id),
    INDEX idx_create_time (create_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='笔记表';

-- 管理员用户表
CREATE TABLE IF NOT EXISTS admin_user (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    permissions VARCHAR(500) DEFAULT '' COMMENT '菜单权限，逗号分隔',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='管理员用户表';

-- Flyway 版本记录表（防止 Flyway 重复执行）
CREATE TABLE IF NOT EXISTS flyway_schema_history (
    installed_rank INT NOT NULL,
    version VARCHAR(50),
    description VARCHAR(200) NOT NULL,
    type VARCHAR(20) NOT NULL,
    script VARCHAR(1000) NOT NULL,
    checksum INT,
    installed_by VARCHAR(100) NOT NULL,
    installed_on TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    execution_time INT NOT NULL,
    success BOOL NOT NULL,
    PRIMARY KEY (installed_rank),
    INDEX idx_flyway_schema_history_s (success)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Flyway版本记录';

-- ============================================================
-- 初始数据
-- ============================================================

-- 工具数据
INSERT INTO sys_tool (tool_id, name, icon, category, description, route, backend_path, status, sort) VALUES
('xmind2case', 'XMind 转测试用例', '🧪', '测试工具', '将 XMind 思维导图一键转换为标准测试用例，支持 Excel 导出', '/tools/xmind', '/api/tool/xmind/parse', 'online', 1),
('json-format', 'JSON 格式化', '📋', '开发工具', 'JSON 数据格式化、压缩、校验', '/tools/json', '/api/tool/json', 'online', 2),
('mock-server', 'Mock 服务器', '🎭', '开发工具', '快速搭建本地 Mock 服务', '/tools/mock', '/api/tool/mock', 'dev', 3),
('db-client', '数据库客户端', '💾', '开发工具', '轻量级数据库查询工具', '/tools/db', '/api/tool/db', 'dev', 4);

-- 示例计划
INSERT INTO plan (title, description, progress, status, sort) VALUES
('完成个人网站开发', '搭建完整的个人网站，包括前端和后端', 80, 'active', 1),
('学习 Vue 3 高级特性', '深入学习 Composition API、状态管理等', 60, 'active', 2),
('Spring Boot 项目实战', '开发一个完整的 Spring Boot 微服务项目', 30, 'active', 3),
('准备软件测试面试', '复习测试理论、算法、项目经验', 50, 'active', 4);

-- 管理员账号 admin/zhaozibo (BCrypt加密)
INSERT INTO admin_user (username, password, permissions) VALUES ('admin', '$2b$10$JUc00382oEBLkMOtw7ZiAe.2lEzxSXFmNqxPVoHAnaTi64PtKUoku', '');

-- 一级分类：测试基础
INSERT INTO note_category (id, name, parent_id, sort) VALUES (1001, '测试基础', 0, 1);
INSERT INTO note_category (name, parent_id, sort) VALUES
('测试理论', 1001, 1), ('数据库', 1001, 2), ('环境搭建', 1001, 3), ('工具使用', 1001, 4), ('实战总结', 1001, 5);

-- 一级分类：进阶技术
INSERT INTO note_category (id, name, parent_id, sort) VALUES (1002, '进阶技术', 0, 2);
INSERT INTO note_category (name, parent_id, sort) VALUES
('接口自动化', 1002, 1), ('UI自动化', 1002, 2), ('中间件', 1002, 3), ('前端项目', 1002, 4),
('Java项目', 1002, 5), ('Python项目', 1002, 6), ('测试平台', 1002, 7);

-- 一级分类：行业动态
INSERT INTO note_category (id, name, parent_id, sort) VALUES (1003, '行业动态', 0, 3);
INSERT INTO note_category (name, parent_id, sort) VALUES
('AI前沿', 1003, 1), ('技术交流', 1003, 2), ('趋势分析', 1003, 3);

-- 一级分类：个人笔记
INSERT INTO note_category (id, name, parent_id, sort) VALUES (1004, '个人笔记', 0, 4);
INSERT INTO note_category (name, parent_id, sort) VALUES
('方法论', 1004, 1), ('个人随笔', 1004, 2);

-- 一级分类：技术笔记
INSERT INTO note_category (id, name, parent_id, sort) VALUES (1005, '技术笔记', 0, 5);
INSERT INTO note_category (name, parent_id, sort) VALUES
('Java', 1005, 1), ('Python', 1005, 2), ('数据库', 1005, 3), ('操作系统', 1005, 4),
('Vue', 1005, 5), ('Git', 1005, 6), ('Docker', 1005, 7), ('Redis', 1005, 8);

-- V4 笔记数据：AI前沿
SET @cat_ai = (SELECT id FROM note_category WHERE name = 'AI前沿' LIMIT 1);
INSERT INTO note (category_id, title, summary, tags, content) VALUES
(@cat_ai, 'GPT-5 技术原理深度解析', '全面解析GPT-5的核心架构创新、训练方法和能力跃升', 'AI,GPT,NLP', '<p><strong>GPT-5 核心升级点</strong></p><ul><li>多模态原生融合：不再是外挂decoder，而是从预训练阶段就统一建模文本、图像、音频</li><li>百万级上下文窗口：原生支持100万token的上下文理解</li><li>自我博弈强化学习：在安全框架内实现持续的自我能力提升</li></ul><p><strong>架构创新</strong></p><p>稀疏MoE与稠密注意力的混合架构，在不同层自适应选择计算路径，大幅提升推理效率。</p>'),
(@cat_ai, 'Claude 3.5 vs GPT-4o 深度对比', '从架构、训练数据、能力边界等多个维度对比两大顶级模型', 'AI,Claude,GPT,对比', '<p><strong>上下文处理</strong></p><p>Claude 3.5 Sontext支持20万token上下文，在长文档分析任务中明显优于GPT-4o的12.8万token限制。</p><p><strong>代码能力</strong></p><p>GPT-4o在代码生成速度上更快，Claude 3.5在复杂代码理解和debug上略胜一筹。</p><p><strong>指令遵循</strong></p><p>Claude 3.5的Haiku子模型在指令遵循 benchmark上刷新了SOTA，领先GPT-4o约12%。</p>'),
(@cat_ai, 'RAG系统优化实践指南', '从检索质量、Embedding模型选择、混合检索策略提升RAG效果', 'AI,RAG,向量检索', '<p><strong>检索质量优化</strong></p><ul><li>使用BGE-M3或E5-Mistral等多语言Embedding模型</li><li>对文档进行智能分块：递归字符分割 + 重叠窗口</li><li>添加Query Expansion，提升召回率</li></ul><p><strong>混合检索策略</strong></p><p>BM25 + 向量检索的RRF融合，在多数benchmark上优于单一检索方式。</p>');

-- V4 笔记数据：部署实战
SET @cat_deploy = (SELECT id FROM note_category WHERE name = '部署实战' LIMIT 1);
INSERT INTO note (category_id, title, summary, tags, content) VALUES
(@cat_deploy, 'Docker容器化最佳实践', '从零构建生产级Docker镜像，包括多阶段构建、安全加固、资源限制', 'Docker,容器,DevOps', '<p><strong>多阶段构建示例</strong></p><pre><code>FROM maven:3.9 AS build\nWORKDIR /app\nCOPY pom.xml .\nRUN mvn dependency:go-offline\nCOPY src ./src\nRUN mvn package -DskipTests\n\nFROM openjdk:17-slim\nCOPY --from=build /app/target/*.jar app.jar\nEXPOSE 8080\nENTRYPOINT [&quot;java&quot;, &quot;-jar&quot;, &quot;-Xmx256m&quot;, &quot;app.jar&quot;]</code></pre><p><strong>安全加固</strong></p><ul><li>使用非root用户运行：<code>USER nonroot:nonroot</code></li><li>只读文件系统：<code>--read-only</code></li><li>禁用特权模式</li></ul>'),
(@cat_deploy, 'Kubernetes生产环境集群规划', '生产K8s集群的节点规划、网络方案、存储选型和高可用设计', 'Kubernetes,K8s,运维', '<p><strong>节点规划建议</strong></p><ul><li>etcd集群：3节点独立，最低2核4G SSD</li><li>Master节点：3节点，4核8G</li><li>Worker节点：根据业务量，16核64G起步</li></ul><p><strong>网络方案</strong></p><p>Cilium + eBPF是当前性能最优方案，相比Calico提升20-30%网络吞吐量。</p>'),
(@cat_deploy, 'Nginx反向代理与负载均衡配置', '生产环境Nginx配置实战：SSL终结、动静分离、健康检查', 'Nginx,运维,反向代理', '<p><strong>核心配置片段</strong></p><pre><code>upstream backend {\n    least_conn;\n    server 192.168.1.10:8080 max_fails=3 fail_timeout=30s;\n    server 192.168.1.11:8080 max_fails=3 fail_timeout=30s;\n    keepalive 32;\n}\n\nserver {\n    listen 443 ssl http2;\n    ssl_certificate /etc/ssl/certs/server.crt;\n    ssl_certificate_key /etc/ssl/private/server.key;\n    ssl_protocols TLSv1.2 TLSv1.3;\n    \n    location /api/ {\n        proxy_pass http://backend;\n        proxy_set_header Host $host;\n        proxy_set_header X-Real-IP $remote_addr;\n    }\n}</code></pre>');

-- V4 笔记数据：源码学习
SET @cat_source = (SELECT id FROM note_category WHERE name = '源码学习' LIMIT 1);
INSERT INTO note (category_id, title, summary, tags, content) VALUES
(@cat_source, 'Vue3响应式系统源码解析', '深入理解Vue3的Proxy-based响应式原理，从ref到reactive的实现链路', 'Vue3,源码,JavaScript', '<p><strong>响应式核心链路</strong></p><ol><li><code>ref()</code>创建一个包装对象，持有<code>.value</code></li><li>通过<code>createReactiveObject()</code>生成Proxy</li><li>getter中收集依赖到<code>targetMap</code>（WeakMap）</li><li>setter中触发<code>triggerEffects</code>遍历更新</li></ol><p><strong>关键数据结构</strong></p><pre><code>const targetMap = new WeakMap&lt;Object, Map&lt;string | symbol, Set&lt;ReactiveEffect&gt;&gt;&gt;()</code></pre><p>这是整个响应式系统的依赖图，外层WeakMap按target寻址，内层Map按key寻址，Set存储所有依赖该属性的Effect。</p>'),
(@cat_source, 'Spring Boot自动配置原理', '从@EnableAutoConfiguration到Condition条件装配的完整流程', 'Spring,Java,源码', '<p><strong>自动配置触发链路</strong></p><ul><li><code>@EnableAutoConfiguration</code> → <code>AutoConfigurationImportSelector</code></li><li>读取<code>META-INF/spring.factories</code>或<code>META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports</code></li><li>按<code>@Conditional</code>条件过滤可用的配置类</li><li>通过<code>AutoConfigurationSorter</code>解析<code>@AutoConfigureBefore/After</code>确定加载顺序</li></ul><p><strong>条件装配</strong></p><p>最常用的是<code>@ConditionalOnClass</code>——当classpath中存在指定类时才生效，这也是Spring Boot智能判断用户引入了什么依赖的核心机制。</p>'),
(@cat_source, 'MyBatis-Plus核心原理与插件机制', '理解MyBatis-Plus的ID生成器、逻辑删除、分页插件的执行流程', 'MyBatis,Java,ORM', '<p><strong>分页插件原理</strong></p><p>MyBatis-Plus的<code>PaginationInnerInterceptor</code>在SQL执行前判断是否需要分页：</p><ol><li>先执行<code>SELECT COUNT(*)</code>获取总数</li><li>然后在原SQL外包裹分页子查询：<code>SELECT * FROM (...) AS t LIMIT x OFFSET y</code></li></ol><p><strong>ID生成器</strong></p><p><code>IdentifierGenerator</code>接口支持多种策略：</p><ul><li>Snowflake（默认）：时间戳 + 机器ID + 序列号</li><li>Redis：基于Redis INCR原子操作</li><li>自定义：实现接口注入Spring容器即可</li></ul>');

-- ============================================================
-- 安全加固
-- ============================================================

-- 删除勒索软件留下的数据库（如果存在）
DROP DATABASE IF EXISTS RECOVER_YOUR_DATA;

-- 删除 root@'%' 远程 root 账号，只保留 root@localhost
DELETE FROM mysql.user WHERE user='root' AND host='%';
FLUSH PRIVILEGES;
