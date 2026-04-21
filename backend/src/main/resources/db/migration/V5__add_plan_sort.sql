-- =============================================
-- V5: plan 表新增 sort 字段
-- =============================================

-- 新增 sort 字段，默认值 0
ALTER TABLE plan ADD COLUMN sort INT DEFAULT 0 COMMENT '排序';

-- 索引（排序查询优化）
CREATE INDEX idx_plan_sort ON plan(sort);

-- 给现有数据设置合理的 sort 值（按 id 顺序）
SET @rank = 0;
UPDATE plan SET sort = (@rank := @rank + 1) WHERE 1=1;