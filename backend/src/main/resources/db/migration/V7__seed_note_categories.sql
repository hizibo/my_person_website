-- =============================================
-- 预制分类数据（安全插入，存在则跳过）
-- 使用 INSERT IGNORE 避免重复插入
-- =============================================

-- ========== 一级分类：测试基础 ==========
INSERT IGNORE INTO note_category (id, name, parent_id, sort) VALUES
(1001, '测试基础', 0, 1);

INSERT IGNORE INTO note_category (name, parent_id, sort) VALUES
('测试理论', 1001, 1),
('数据库', 1001, 2),
('环境搭建', 1001, 3),
('工具使用', 1001, 4),
('实战总结', 1001, 5);

-- ========== 一级分类：进阶技术 ==========
INSERT IGNORE INTO note_category (id, name, parent_id, sort) VALUES
(1002, '进阶技术', 0, 2);

INSERT IGNORE INTO note_category (name, parent_id, sort) VALUES
('接口自动化', 1002, 1),
('UI自动化', 1002, 2),
('中间件', 1002, 3),
('前端项目', 1002, 4),
('Java项目', 1002, 5),
('Python项目', 1002, 6),
('测试平台', 1002, 7);

-- ========== 一级分类：行业动态 ==========
INSERT IGNORE INTO note_category (id, name, parent_id, sort) VALUES
(1003, '行业动态', 0, 3);

INSERT IGNORE INTO note_category (name, parent_id, sort) VALUES
('AI前沿', 1003, 1),
('技术交流', 1003, 2),
('趋势分析', 1003, 3);

-- ========== 一级分类：个人笔记 ==========
INSERT IGNORE INTO note_category (id, name, parent_id, sort) VALUES
(1004, '个人笔记', 0, 4);

INSERT IGNORE INTO note_category (name, parent_id, sort) VALUES
('方法论', 1004, 1),
('个人随笔', 1004, 2);

-- ========== 一级分类：技术笔记 ==========
INSERT IGNORE INTO note_category (id, name, parent_id, sort) VALUES
(1005, '技术笔记', 0, 5);

INSERT IGNORE INTO note_category (name, parent_id, sort) VALUES
('Java', 1005, 1),
('Python', 1005, 2),
('数据库', 1005, 3),
('操作系统', 1005, 4),
('Vue', 1005, 5),
('Git', 1005, 6),
('Docker', 1005, 7),
('Redis', 1005, 8);
