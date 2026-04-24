# MySQL 性能优化与索引原理

> 来源：综合整理自 CSDN、知乎、菜鸟教程等技术文章  
> 整理日期：2026-04-25

---

## 一、索引基础

### 1. 什么是索引？

**索引（Index）** 是帮助 MySQL 高效获取数据的数据结构，它就像书籍的目录一样，可以快速定位到需要的内容。

**创建索引**：
```sql
-- 创建普通索引
CREATE INDEX index_name ON table_name (column_name);

-- 创建唯一索引
CREATE UNIQUE INDEX index_name ON table_name (column_name);

-- 创建组合索引
CREATE INDEX index_name ON table_name (col1, col2, col3);
```

### 2. 为什么需要索引？

| 场景 | 无索引 | 有索引 |
|------|--------|--------|
| 数据量 | 小表(<1000行) | 大表(>10000行) |
| 查询类型 | 全表扫描 | 精确查找、范围查询 |
| 性能影响 | 线性增长 O(n) | 对数增长 O(log n) |

### 3. 索引的代价

- **存储空间**：索引需要额外的磁盘空间
- **维护成本**：INSERT、UPDATE、DELETE 操作需要维护索引
- **优化器选择**：错误的索引可能导致性能下降

---

## 二、索引数据结构

### 1. B+Tree 索引

**B+Tree 是 MySQL 中最常用的索引数据结构**。

**B+Tree vs B-Tree**：

| 特性 | B-Tree | B+Tree |
|------|--------|--------|
| 数据存储 | 所有节点都存储数据 | 只有叶子节点存储数据 |
| 查询效率 | 不稳定 | 稳定，总是 O(log n) |
| 范围查询 | 需要中序遍历 | 叶子节点链表直接遍历 |
| 空间利用率 | 较低 | 较高 |

**B+Tree 特点**：
- 非叶子节点只存储键值，不存储数据
- 所有叶子节点通过指针连接，形成有序链表
- 适合范围查询和排序

### 2. Hash 索引

**特点**：
- 基于哈希表实现，查询效率 O(1)
- 只支持等值查询（=、IN）
- 不支持范围查询和排序
- Memory 引擎支持，InnoDB 的自适应哈希索引

### 3. 索引类型对比

| 索引类型 | 存储引擎 | 特点 | 适用场景 |
|----------|----------|------|----------|
| **B+Tree** | InnoDB/MyISAM | 支持范围查询、排序 | 大多数场景 |
| **Hash** | Memory | 等值查询快 | 等值查询 |
| **Full-text** | MyISAM/InnoDB 5.6+ | 全文检索 | 文本搜索 |
| **R-Tree** | MyISAM | 空间数据索引 | 地理信息 |

---

## 三、MySQL 索引分类

### 1. 按数据结构分类

- **B+Tree 索引**：最常用的索引类型
- **Hash 索引**：仅用于 Memory 引擎
- **Full-text 索引**：全文索引

### 2. 按物理存储分类

**聚簇索引（Clustered Index）**：
- InnoDB 的主键索引
- 叶子节点存储完整的数据行
- 一个表只能有一个聚簇索引
- 数据按主键顺序存储

**非聚簇索引（Secondary Index）**：
- 叶子节点存储主键值
- 查询时需要回表（根据主键查找数据）
- 一个表可以有多个非聚簇索引

### 3. 按功能分类

| 索引类型 | 说明 | 语法 |
|----------|------|------|
| **主键索引** | 唯一标识每行记录 | PRIMARY KEY |
| **唯一索引** | 保证列值唯一 | UNIQUE INDEX |
| **普通索引** | 加速查询 | INDEX |
| **组合索引** | 多列组合索引 | INDEX (a, b, c) |
| **前缀索引** | 列的前缀索引 | INDEX (col(10)) |
| **覆盖索引** | 查询字段都在索引中 | - |

---

## 四、索引设计原则

### 1. 适合创建索引的列

- 频繁作为查询条件的列（WHERE、JOIN、ORDER BY）
- 区分度高的列（唯一值多）
- 外键列
- 经常需要排序的列

### 2. 不适合创建索引的列

- 区分度低的列（如性别、状态）
- 频繁更新的列
- 小表（数据量 < 1000）
- 很少作为查询条件的列

### 3. 组合索引设计原则

**最左前缀原则**：
```sql
-- 创建组合索引 (a, b, c)
CREATE INDEX idx_abc ON table_name (a, b, c);

-- 可以使用索引的查询
WHERE a = 1
WHERE a = 1 AND b = 2
WHERE a = 1 AND b = 2 AND c = 3
WHERE a = 1 AND c = 3  -- 只使用 a

-- 不能使用索引的查询
WHERE b = 2
WHERE b = 2 AND c = 3
WHERE c = 3
```

**设计建议**：
- 区分度高的列放在前面
- 查询频率高的列放在前面
- 避免冗余索引

---

## 五、SQL 优化

### 1. EXPLAIN 分析

```sql
EXPLAIN SELECT * FROM users WHERE id = 1;
```

**关键字段解读**：

| 字段 | 说明 | 优化建议 |
|------|------|----------|
| **type** | 访问类型 | system > const > eq_ref > ref > range > index > ALL |
| **possible_keys** | 可能使用的索引 | - |
| **key** | 实际使用的索引 | 为 NULL 表示未使用索引 |
| **rows** | 扫描行数 | 越小越好 |
| **Extra** | 额外信息 | 避免 Using filesort、Using temporary |

**type 类型说明**：
- **const**：主键或唯一索引等值查询
- **eq_ref**：JOIN 时主键或唯一索引关联
- **ref**：非唯一索引等值查询
- **range**：索引范围查询
- **index**：全索引扫描
- **ALL**：全表扫描（需优化）

### 2. 常见优化技巧

#### 避免 SELECT *
```sql
-- 不推荐
SELECT * FROM users WHERE age > 20;

-- 推荐
SELECT id, name, age FROM users WHERE age > 20;
```

#### 避免在索引列上使用函数
```sql
-- 不走索引
SELECT * FROM users WHERE YEAR(create_time) = 2024;

-- 走索引
SELECT * FROM users WHERE create_time >= '2024-01-01' AND create_time < '2025-01-01';
```

#### 避免隐式类型转换
```sql
-- 不走索引（字符串转数字）
SELECT * FROM users WHERE phone = 13800138000;

-- 走索引
SELECT * FROM users WHERE phone = '13800138000';
```

#### 使用覆盖索引
```sql
-- 创建覆盖索引
CREATE INDEX idx_name_age ON users(name, age);

-- 查询字段都在索引中，无需回表
SELECT name, age FROM users WHERE name = '张三';
```

#### 优化分页查询
```sql
-- 深度分页慢
SELECT * FROM users LIMIT 1000000, 10;

-- 优化：使用主键范围查询
SELECT * FROM users WHERE id > 1000000 LIMIT 10;

-- 或使用 JOIN
SELECT u.* FROM users u
JOIN (SELECT id FROM users LIMIT 1000000, 10) tmp ON u.id = tmp.id;
```

#### 优化 ORDER BY
```sql
-- 创建索引避免 filesort
CREATE INDEX idx_age ON users(age);

-- 使用索引排序
SELECT * FROM users ORDER BY age LIMIT 10;
```

---

## 六、索引失效场景

### 1. 违反最左前缀原则
```sql
-- 索引 (a, b, c)
WHERE b = 1 AND c = 2  -- 失效
```

### 2. 使用 OR 条件
```sql
-- 部分失效
WHERE a = 1 OR b = 2  -- 如果 b 没有索引，a 的索引也失效
```

### 3. 使用 != 或 <>
```sql
WHERE age != 20  -- 可能失效
```

### 4. 使用 IS NULL / IS NOT NULL
```sql
WHERE name IS NULL  -- 可能失效
```

### 5. LIKE 以 % 开头
```sql
WHERE name LIKE '%张%'  -- 失效
WHERE name LIKE '张%'   -- 有效
```

### 6. 对索引列进行计算
```sql
WHERE age + 1 = 20  -- 失效
WHERE age = 19      -- 有效
```

---

## 七、性能监控

### 1. 慢查询日志

```sql
-- 开启慢查询日志
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 2;  -- 超过2秒记录
SET GLOBAL slow_query_log_file = '/var/log/mysql/slow.log';
```

### 2. 查看执行频率

```sql
-- 查看 SQL 执行频率
SHOW GLOBAL STATUS LIKE 'Com_%';
SHOW GLOBAL STATUS LIKE 'Innodb_%';
```

### 3. 查看索引使用情况

```sql
-- 查看索引使用统计
SHOW GLOBAL STATUS LIKE 'Handler_read%';

-- Handler_read_key：使用索引读取行数
-- Handler_read_rnd_next：全表扫描或索引扫描行数
```

---

## 八、面试常见问题

### Q1: MySQL 为什么使用 B+Tree 而不是 B-Tree？
**A**: 
1. B+Tree 非叶子节点不存储数据，可以存储更多键值，树更矮，IO 次数更少
2. B+Tree 叶子节点形成有序链表，范围查询和排序更高效
3. B+Tree 查询性能更稳定，总是到叶子节点找到数据

### Q2: 聚簇索引和非聚簇索引的区别？
**A**: 
- **聚簇索引**：叶子节点存储完整数据行，数据按主键顺序存储，一个表只能有一个
- **非聚簇索引**：叶子节点存储主键值，查询需要回表，一个表可以有多个

### Q3: 什么情况下索引会失效？
**A**: 
- 违反最左前缀原则
- 使用函数或表达式
- 隐式类型转换
- LIKE 以 % 开头
- 使用 !=、<>、IS NULL
- OR 条件部分列无索引

### Q4: 如何优化慢 SQL？
**A**: 
1. 使用 EXPLAIN 分析执行计划
2. 添加合适的索引
3. 优化 SQL 写法（避免 SELECT *、使用覆盖索引等）
4. 优化表结构（字段类型、拆分大表）
5. 调整 MySQL 配置参数

---

## 九、参考链接

- [MySQL 面试指南：从索引原理到实战优化 - CSDN](https://blog.csdn.net/gitblog_00931/article/details/148504985)
- [MySQL 索引优化全攻略 - 菜鸟教程](http://www.runoob.com/w3cnote/mysql-index.html)
- [MySQL 优化&索引原理面试 - 知乎](https://zhuanlan.zhihu.com/p/378989779)
