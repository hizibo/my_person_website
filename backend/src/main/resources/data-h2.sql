-- H2 初始化数据
INSERT INTO tools (id, name, description, icon, path, status, sort_order) VALUES
(1, 'XMind转测试用例', '将XMind思维导图转换为标准测试用例格式', 'file-text', '/tools/xmind', 1, 1),
(2, 'JSON格式化', 'JSON数据格式化、压缩、校验工具', 'code', '/tools/json', 1, 2),
(3, '正则测试', '正则表达式在线测试工具', 'search', '/tools/regex', 1, 3);
