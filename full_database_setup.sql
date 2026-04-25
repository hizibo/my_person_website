-- 创建数据库
CREATE DATABASE IF NOT EXISTS my_website DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE my_website;

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

-- 初始化工具数据
INSERT INTO sys_tool (tool_id, name, icon, category, description, route, backend_path, status, sort) VALUES
('xmind2case', 'XMind 转测试用例', '🧪', '测试工具', '将 XMind 思维导图一键转换为标准测试用例，支持 Excel 导出', '/tools/xmind', '/api/tool/xmind/parse', 'online', 1),
('json-format', 'JSON 格式化', '📋', '开发工具', 'JSON 数据格式化、压缩、校验', '/tools/json', '/api/tool/json', 'online', 2),
('mock-server', 'Mock 服务器', '🎭', '开发工具', '快速搭建本地 Mock 服务', '/tools/mock', '/api/tool/mock', 'dev', 3),
('db-client', '数据库客户端', '💾', '开发工具', '轻量级数据库查询工具', '/tools/db', '/api/tool/db', 'dev', 4);

-- 使用记录表（可选）
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

-- 计划表（我的计划）
CREATE TABLE IF NOT EXISTS plan (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL COMMENT '计划标题',
    description TEXT COMMENT '计划描述',
    progress INT DEFAULT 0 COMMENT '进度(0-100)',
    status VARCHAR(16) DEFAULT 'active' COMMENT '状态: active/completed/cancelled',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_status (status),
    INDEX idx_create_time (create_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='计划表';

-- 初始化一些示例计划
INSERT INTO plan (title, description, progress, status) VALUES
('完成个人网站开发', '搭建完整的个人网站，包括前端和后端', 80, 'active'),
('学习 Vue 3 高级特性', '深入学习 Composition API、状态管理等', 60, 'active'),
('Spring Boot 项目实战', '开发一个完整的 Spring Boot 微服务项目', 30, 'active'),
('准备软件测试面试', '复习测试理论、算法、项目经验', 50, 'active');

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

-- 初始化默认分类
INSERT INTO my_website.note_category (id, name, parent_id, sort, create_time, update_time) VALUES (1030, '拾人牙慧', 1018, 0, '2026-04-23 22:22:30', '2026-04-23 22:22:30');
INSERT INTO my_website.note_category (id, name, parent_id, sort, create_time, update_time) VALUES (1002, '测试理论', 1001, 1, '2026-04-23 22:06:06', '2026-04-23 22:06:06');
INSERT INTO my_website.note_category (id, name, parent_id, sort, create_time, update_time) VALUES (1019, 'Java', 1029, 1, '2026-04-23 22:06:06', '2026-04-23 22:16:55');
INSERT INTO my_website.note_category (id, name, parent_id, sort, create_time, update_time) VALUES (1017, '方法论', 1018, 1, '2026-04-23 22:06:06', '2026-04-23 22:14:48');
INSERT INTO my_website.note_category (id, name, parent_id, sort, create_time, update_time) VALUES (1014, 'AI前沿', 1028, 1, '2026-04-23 22:06:06', '2026-04-23 22:16:14');
INSERT INTO my_website.note_category (id, name, parent_id, sort, create_time, update_time) VALUES (1007, '接口自动化', 1027, 1, '2026-04-23 22:06:06', '2026-04-23 22:11:57');
INSERT INTO my_website.note_category (id, name, parent_id, sort, create_time, update_time) VALUES (1001, '测试基础', 0, 1, '2026-04-23 22:06:06', '2026-04-23 22:06:06');
INSERT INTO my_website.note_category (id, name, parent_id, sort, create_time, update_time) VALUES (1003, '数据库', 1001, 2, '2026-04-23 22:06:06', '2026-04-23 22:06:06');
INSERT INTO my_website.note_category (id, name, parent_id, sort, create_time, update_time) VALUES (1027, '进阶技能', 0, 2, '2026-04-23 22:10:58', '2026-04-23 22:13:02');
INSERT INTO my_website.note_category (id, name, parent_id, sort, create_time, update_time) VALUES (1020, 'Python', 1029, 2, '2026-04-23 22:06:06', '2026-04-23 22:17:01');
INSERT INTO my_website.note_category (id, name, parent_id, sort, create_time, update_time) VALUES (1015, '测试交流', 1028, 2, '2026-04-23 22:06:06', '2026-04-23 22:19:45');
INSERT INTO my_website.note_category (id, name, parent_id, sort, create_time, update_time) VALUES (1008, 'UI自动化', 1027, 2, '2026-04-23 22:06:06', '2026-04-23 22:12:03');
INSERT INTO my_website.note_category (id, name, parent_id, sort, create_time, update_time) VALUES (1028, '行业动态', 0, 3, '2026-04-23 22:15:47', '2026-04-23 22:20:13');
INSERT INTO my_website.note_category (id, name, parent_id, sort, create_time, update_time) VALUES (1009, '中间件', 1027, 3, '2026-04-23 22:06:06', '2026-04-23 22:12:12');
INSERT INTO my_website.note_category (id, name, parent_id, sort, create_time, update_time) VALUES (1004, '环境搭建', 1001, 3, '2026-04-23 22:06:06', '2026-04-23 22:06:06');
INSERT INTO my_website.note_category (id, name, parent_id, sort, create_time, update_time) VALUES (1021, 'sql', 1029, 3, '2026-04-23 22:06:06', '2026-04-23 22:21:03');
INSERT INTO my_website.note_category (id, name, parent_id, sort, create_time, update_time) VALUES (1022, 'Liunx', 1029, 4, '2026-04-23 22:06:06', '2026-04-23 22:21:10');
INSERT INTO my_website.note_category (id, name, parent_id, sort, create_time, update_time) VALUES (1010, '前端项目', 1027, 4, '2026-04-23 22:06:06', '2026-04-23 22:12:28');
INSERT INTO my_website.note_category (id, name, parent_id, sort, create_time, update_time) VALUES (1018, '个人随笔', 0, 4, '2026-04-23 22:06:06', '2026-04-23 22:20:18');
INSERT INTO my_website.note_category (id, name, parent_id, sort, create_time, update_time) VALUES (1005, '工具使用', 1001, 4, '2026-04-23 22:06:06', '2026-04-23 22:06:06');
INSERT INTO my_website.note_category (id, name, parent_id, sort, create_time, update_time) VALUES (1006, '实战总结', 1001, 5, '2026-04-23 22:06:06', '2026-04-23 22:06:06');
INSERT INTO my_website.note_category (id, name, parent_id, sort, create_time, update_time) VALUES (1023, 'Vue', 1029, 5, '2026-04-23 22:06:06', '2026-04-23 22:17:32');
INSERT INTO my_website.note_category (id, name, parent_id, sort, create_time, update_time) VALUES (1011, 'Java项目', 1027, 5, '2026-04-23 22:06:06', '2026-04-23 22:11:35');
INSERT INTO my_website.note_category (id, name, parent_id, sort, create_time, update_time) VALUES (1029, '知识总结', 0, 5, '2026-04-23 22:16:49', '2026-04-23 22:21:27');
INSERT INTO my_website.note_category (id, name, parent_id, sort, create_time, update_time) VALUES (1012, 'Python项目', 1027, 6, '2026-04-23 22:06:06', '2026-04-23 22:12:47');
INSERT INTO my_website.note_category (id, name, parent_id, sort, create_time, update_time) VALUES (1024, 'Git', 1029, 6, '2026-04-23 22:06:06', '2026-04-23 22:17:43');
INSERT INTO my_website.note_category (id, name, parent_id, sort, create_time, update_time) VALUES (1025, 'Docker', 1029, 7, '2026-04-23 22:06:06', '2026-04-23 22:17:53');
INSERT INTO my_website.note_category (id, name, parent_id, sort, create_time, update_time) VALUES (1013, '测试平台', 1027, 7, '2026-04-23 22:06:06', '2026-04-23 22:14:24');
INSERT INTO my_website.note_category (id, name, parent_id, sort, create_time, update_time) VALUES (1026, 'Redis', 1029, 8, '2026-04-23 22:06:06', '2026-04-23 22:18:02');

# -- 授权 root 用户可以从任意主机访问
# CREATE USER IF NOT EXISTS 'root'@'%' IDENTIFIED BY 'root';
# GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;
# ALTER USER 'root'@'%' IDENTIFIED WITH mysql_native_password BY 'root';
# FLUSH PRIVILEGES;
