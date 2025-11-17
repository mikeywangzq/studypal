# 数据库索引详解

## 什么是索引？

索引是一种特殊的数据结构，用于快速定位和访问数据库表中的数据。类似于书籍的目录，可以快速找到需要的内容。

## 索引的类型

### 1. B-Tree 索引

最常用的索引类型，适用于大多数场景。

**特点**:
- 平衡树结构
- 所有叶子节点在同一层
- 支持范围查询
- 时间复杂度 O(log n)

**适用场景**:
- 等值查询: `WHERE id = 100`
- 范围查询: `WHERE age BETWEEN 20 AND 30`
- 排序: `ORDER BY name`
- 模糊匹配: `WHERE name LIKE 'abc%'` (前缀匹配)

**示例**:
```sql
CREATE INDEX idx_user_name ON users(name);
```

### 2. Hash 索引

基于哈希表实现。

**特点**:
- 等值查询非常快 O(1)
- 不支持范围查询
- 不支持排序
- Memory 引擎默认使用

**适用场景**:
- 精确匹配: `WHERE id = 100`

**示例**:
```sql
CREATE INDEX idx_user_email USING HASH ON users(email);
```

### 3. 全文索引 (Full-Text Index)

用于文本搜索。

**特点**:
- 支持自然语言搜索
- 支持布尔搜索
- 只能用于 CHAR, VARCHAR, TEXT 类型

**适用场景**:
- 文章内容搜索
- 产品描述搜索

**示例**:
```sql
CREATE FULLTEXT INDEX idx_article_content ON articles(content);

-- 使用全文索引
SELECT * FROM articles
WHERE MATCH(content) AGAINST('数据库索引');
```

### 4. 空间索引 (Spatial Index)

用于地理空间数据。

**特点**:
- 基于 R-Tree
- 支持几何类型数据

**示例**:
```sql
CREATE SPATIAL INDEX idx_location ON places(coordinates);
```

## 索引的实现

### B+Tree 结构

```
                [50, 100]
               /    |    \
              /     |     \
         [20,30] [60,80] [110,120]
          /  \    /  \     /   \
       [data][data][data][data][data][data]
```

**特点**:
- 非叶子节点只存储键值
- 叶子节点存储数据（或指向数据的指针）
- 叶子节点之间有链表连接

**优势**:
- 范围查询效率高
- 所有查询都访问到叶子节点，IO次数稳定

### MySQL InnoDB 的索引

```python
# 聚簇索引（Clustered Index）
# 数据行和主键存储在一起
Primary Key: id -> [id, name, age, email] (完整行数据)

# 二级索引（Secondary Index）
# 索引键 + 主键
Index on name: name -> [name, id] -> 通过id查聚簇索引获取完整数据
```

## 创建索引

### 单列索引
```sql
CREATE INDEX idx_name ON table_name(column_name);
```

### 复合索引（多列索引）
```sql
CREATE INDEX idx_name_age ON users(name, age);
```

**最左前缀原则**:
```sql
-- 可以使用索引
SELECT * FROM users WHERE name = 'Alice';
SELECT * FROM users WHERE name = 'Alice' AND age = 25;

-- 不能使用索引
SELECT * FROM users WHERE age = 25;
```

### 唯一索引
```sql
CREATE UNIQUE INDEX idx_email ON users(email);
```

### 主键索引
```sql
ALTER TABLE users ADD PRIMARY KEY (id);
```

## 查看索引

```sql
-- 查看表的所有索引
SHOW INDEX FROM users;

-- 查看执行计划
EXPLAIN SELECT * FROM users WHERE name = 'Alice';
```

## 何时使用索引

### 应该创建索引的情况

1. **WHERE 子句中频繁查询的列**
```sql
-- name 列应该建索引
SELECT * FROM users WHERE name = 'Alice';
```

2. **JOIN 连接的列**
```sql
-- user_id 应该建索引
SELECT * FROM orders o
JOIN users u ON o.user_id = u.id;
```

3. **ORDER BY 排序的列**
```sql
-- created_at 应该建索引
SELECT * FROM posts ORDER BY created_at DESC;
```

4. **GROUP BY 分组的列**
```sql
-- status 应该建索引
SELECT status, COUNT(*) FROM orders
GROUP BY status;
```

5. **频繁作为查询返回的列**
- 可以考虑覆盖索引

### 不应该创建索引的情况

1. **数据量很小的表** (几百行)
2. **频繁更新的列**
   - 每次更新都要维护索引
3. **区分度很低的列**
   - 如性别字段（只有男/女）
   - 建议：区分度 < 10% 不建索引
4. **很少查询的列**

## 索引优化技巧

### 1. 覆盖索引

索引包含查询需要的所有列，不需要回表。

```sql
-- 创建覆盖索引
CREATE INDEX idx_name_age_email ON users(name, age, email);

-- 查询可以只访问索引
SELECT name, age, email FROM users WHERE name = 'Alice';
```

### 2. 索引下推 (Index Condition Pushdown)

MySQL 5.6+ 支持，将部分过滤条件下推到存储引擎层。

```sql
-- age 的过滤可以在索引层完成
SELECT * FROM users
WHERE name LIKE 'A%' AND age > 20;
```

### 3. 前缀索引

对于长字符串列，只索引前几个字符。

```sql
-- 只索引 email 的前 10 个字符
CREATE INDEX idx_email_prefix ON users(email(10));
```

**选择合适的前缀长度**:
```sql
-- 计算区分度
SELECT
  COUNT(DISTINCT LEFT(email, 5)) / COUNT(*) AS prefix_5,
  COUNT(DISTINCT LEFT(email, 10)) / COUNT(*) AS prefix_10,
  COUNT(DISTINCT LEFT(email, 15)) / COUNT(*) AS prefix_15,
  COUNT(DISTINCT email) / COUNT(*) AS full_column
FROM users;
```

### 4. 索引合并

MySQL 可以同时使用多个索引。

```sql
-- 可能同时使用 idx_name 和 idx_age
SELECT * FROM users
WHERE name = 'Alice' OR age = 25;
```

## 索引失效的情况

### 1. 使用函数或计算
```sql
-- 不走索引
SELECT * FROM users WHERE YEAR(created_at) = 2024;

-- 应该改为
SELECT * FROM users
WHERE created_at BETWEEN '2024-01-01' AND '2024-12-31';
```

### 2. 类型不匹配
```sql
-- id 是整数，但用字符串查询
SELECT * FROM users WHERE id = '100';  -- 不走索引
SELECT * FROM users WHERE id = 100;    -- 走索引
```

### 3. 使用 NOT、!=、<>
```sql
-- 不走索引
SELECT * FROM users WHERE status != 'active';

-- 可以改为
SELECT * FROM users WHERE status IN ('pending', 'inactive');
```

### 4. LIKE 以通配符开头
```sql
-- 不走索引
SELECT * FROM users WHERE name LIKE '%alice';

-- 走索引
SELECT * FROM users WHERE name LIKE 'alice%';
```

### 5. OR 条件中有未建索引的列
```sql
-- 如果 age 没有索引，整个查询不走索引
SELECT * FROM users WHERE name = 'Alice' OR age = 25;
```

## 索引监控和维护

### 查看索引使用情况
```sql
-- 查看索引统计信息
SELECT * FROM sys.schema_unused_indexes;

-- 查看索引大小
SELECT
  table_name,
  index_name,
  ROUND(stat_value * @@innodb_page_size / 1024 / 1024, 2) AS 'Size (MB)'
FROM mysql.innodb_index_stats
WHERE stat_name = 'size';
```

### 重建索引
```sql
-- 删除并重建索引
ALTER TABLE users DROP INDEX idx_name, ADD INDEX idx_name(name);

-- 或使用 OPTIMIZE TABLE
OPTIMIZE TABLE users;
```

## 实际案例

### 案例 1: 慢查询优化

**问题**: 查询慢
```sql
SELECT * FROM orders
WHERE user_id = 100 AND status = 'pending'
ORDER BY created_at DESC
LIMIT 10;
```

**分析**: 没有合适的索引

**解决**: 创建复合索引
```sql
CREATE INDEX idx_user_status_created
ON orders(user_id, status, created_at);
```

### 案例 2: 覆盖索引优化

**问题**: 需要回表
```sql
SELECT id, name, email FROM users WHERE name = 'Alice';
```

**解决**: 创建覆盖索引
```sql
CREATE INDEX idx_name_email ON users(name, email);
-- 查询只需访问索引，不需要回表
```

## 常见面试题

**Q1: 为什么 InnoDB 使用 B+Tree 而不是 B-Tree？**

A:
- B+Tree 所有数据都在叶子节点，非叶子节点只存键值，一个节点能存更多键
- 叶子节点之间有链表，范围查询更高效
- 查询性能稳定，都需要访问到叶子节点

**Q2: 聚簇索引和非聚簇索引的区别？**

A:
- 聚簇索引：数据行和索引存在一起（InnoDB 的主键）
- 非聚簇索引：索引和数据分开存储（MyISAM）
- 聚簇索引决定数据在磁盘上的物理顺序

**Q3: 什么是回表？如何避免？**

A:
- 回表：通过二级索引找到主键，再通过主键查数据
- 避免：使用覆盖索引，让二级索引包含所有需要的列

**Q4: 索引越多越好吗？**

A:
- 不是！
- 索引占用空间
- 写操作（INSERT、UPDATE、DELETE）需要维护索引
- 建议：根据实际查询需求创建索引
