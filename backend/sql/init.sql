-- 创建数据库
CREATE DATABASE IF NOT EXISTS my_toolbox DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE my_toolbox;

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
