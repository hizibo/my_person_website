# Redis 核心知识点总结

> 整理日期：2026-04-25  
> 适用：面试复习、技术深入

---

## 一、Redis 基础

### 1. 什么是 Redis？

**Redis**（Remote Dictionary Server）是一个开源的、基于内存的高性能键值对数据库。

**核心特点**：
- **内存存储**：读写速度极快（10万+ QPS）
- **数据结构丰富**：String、Hash、List、Set、Sorted Set 等
- **持久化支持**：RDB 快照、AOF 日志
- **高可用**：主从复制、哨兵模式、集群模式
- **单线程模型**：避免锁竞争，简化设计

---

### 2. 数据类型及应用场景

| 数据类型 | 说明 | 应用场景 |
|----------|------|----------|
| **String** | 字符串、整数、浮点数 | 缓存、计数器、分布式锁 |
| **Hash** | 键值对集合 | 对象存储、用户信息 |
| **List** | 双向链表 | 消息队列、时间线 |
| **Set** | 无序唯一集合 | 标签、共同好友、去重 |
| **Sorted Set** | 有序集合 | 排行榜、延迟队列 |
| **Bitmap** | 位图 | 用户签到、在线统计 |
| **HyperLogLog** | 基数统计 | UV 统计 |
| **Geo** | 地理位置 | 附近的人、位置服务 |
| **Stream** | 日志型数据结构 | 消息队列（Kafka 替代） |

---

### 3. 常用命令速查

**String**：
```bash
SET key value           # 设置值
GET key                 # 获取值
INCR key                # 自增
DECR key                # 自减
SETEX key seconds value # 设置并指定过期时间
```

**Hash**：
```bash
HSET key field value    # 设置字段值
HGET key field          # 获取字段值
HGETALL key             # 获取所有字段
HDEL key field          # 删除字段
```

**List**：
```bash
LPUSH key value         # 左侧插入
RPUSH key value         # 右侧插入
LPOP key                # 左侧弹出
RPOP key                # 右侧弹出
LRANGE key 0 -1         # 获取所有元素
```

**Set**：
```bash
SADD key member         # 添加成员
SMEMBERS key            # 获取所有成员
SISMEMBER key member    # 判断成员是否存在
SINTER key1 key2        # 交集
SUNION key1 key2        # 并集
```

**Sorted Set**：
```bash
ZADD key score member   # 添加成员（带分数）
ZRANGE key 0 -1         # 按分数升序获取
ZREVRANGE key 0 -1      # 按分数降序获取
ZREM key member         # 删除成员
```

---

## 二、持久化机制

### 1. RDB（Redis Database）

**原理**：定时将内存数据快照保存到磁盘

**触发方式**：
- 手动：`SAVE`（阻塞）、`BGSAVE`（后台）
- 自动：配置 `save 900 1`（900秒内1次修改）

**优点**：
- 文件紧凑，适合备份
- 恢复速度快
- 对性能影响小

**缺点**：
- 可能丢失最后一次快照后的数据

---

### 2. AOF（Append Only File）

**原理**：将每个写操作追加到日志文件

**同步策略**：
- `always`：每次写入都同步（最安全，最慢）
- `everysec`：每秒同步（默认，平衡）
- `no`：由操作系统决定（最快，最不安全）

**优点**：
- 数据安全性高，最多丢失1秒数据
- 日志可读，便于分析

**缺点**：
- 文件体积大
- 恢复速度慢
- 性能开销较大

---

### 3. 混合持久化（Redis 4.0+）

**原理**：AOF 文件前半部分是 RDB 快照，后半部分是 AOF 日志

**优点**：
- 结合 RDB 快速恢复和 AOF 低数据丢失
- 推荐生产环境使用

---

## 三、高可用架构

### 1. 主从复制（Replication）

**架构**：
```
Master（主） ----> Slave1（从）
            ----> Slave2（从）
```

**复制过程**：
1. 从节点发送 SYNC 命令
2. 主节点执行 BGSAVE 生成 RDB
3. 主节点发送 RDB 给从节点
4. 主节点持续发送写命令到从节点

**作用**：
- 数据冗余
- 读写分离（读多写少场景）
- 故障恢复基础

---

### 2. 哨兵模式（Sentinel）

**功能**：
- **监控**：监控主从节点状态
- **通知**：故障时通知管理员
- **自动故障转移**：主节点故障时自动选举新主节点
- **配置提供者**：客户端通过哨兵获取主节点地址

**架构**：
```
        Sentinel1
           |
    Sentinel2 - Sentinel3
           |
    Master <----> Slave
```

**故障转移流程**：
1. 哨兵检测到主节点主观下线
2. 多个哨兵确认客观下线
3. 选举领头哨兵
4. 从从节点中选举新主节点
5. 通知其他从节点切换主节点
6. 通知客户端更新主节点地址

---

### 3. 集群模式（Cluster）

**特点**：
- 数据分片存储（16384 个槽位）
- 支持水平扩展
- 自动故障转移

**架构**：
```
MasterA(0-5460)    MasterB(5461-10922)    MasterC(10923-16383)
    |                      |                       |
SlaveA                 SlaveB                  SlaveC
```

**数据路由**：
- `CRC16(key) % 16384` 计算槽位
- 客户端缓存槽位到节点的映射
- MOVED 重定向处理槽位迁移

---

## 四、缓存问题与解决方案

### 1. 缓存穿透

**问题**：查询不存在的数据，每次都穿透到数据库

**解决**：
- 布隆过滤器预判
- 缓存空值（设置短过期时间）

---

### 2. 缓存击穿

**问题**：热点 key 过期瞬间，大量请求打到数据库

**解决**：
- 互斥锁（只有一个线程去加载数据）
- 逻辑过期（不设置 TTL，通过逻辑时间判断）
- 热点 key 永不过期

---

### 3. 缓存雪崩

**问题**：大量 key 同时过期，数据库压力剧增

**解决**：
- 过期时间加随机值
- 多级缓存
- 熔断降级
- 提前预热

---

## 五、Redis 与测试

### 1. 测试场景

| 场景 | 测试要点 |
|------|----------|
| **缓存功能** | 命中/未命中逻辑、过期策略 |
| **并发安全** | 分布式锁、原子操作 |
| **性能测试** | QPS、延迟、内存使用 |
| **高可用** | 主从切换、故障恢复 |
| **数据一致性** | 缓存与数据库一致性 |

### 2. 分布式锁实现

```python
import redis
import time
import uuid

class RedisLock:
    def __init__(self, redis_client, lock_key, expire_time=30):
        self.redis = redis_client
        self.lock_key = f"lock:{lock_key}"
        self.expire_time = expire_time
        self.identifier = str(uuid.uuid4())
    
    def acquire(self):
        """获取锁"""
        end_time = time.time() + self.expire_time
        while time.time() < end_time:
            if self.redis.set(self.lock_key, self.identifier, 
                              nx=True, ex=self.expire_time):
                return True
            time.sleep(0.1)
        return False
    
    def release(self):
        """释放锁（使用 Lua 脚本保证原子性）"""
        lua_script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        self.redis.eval(lua_script, 1, self.lock_key, self.identifier)
```

---

## 六、面试常见问题

### Q1: Redis 为什么这么快？
**A**: 
1. 纯内存操作
2. 单线程避免上下文切换和锁竞争
3. IO 多路复用（epoll）
4. 高效的数据结构

### Q2: Redis 是单线程还是多线程？
**A**: 
- Redis 6.0 之前：完全单线程
- Redis 6.0+：网络 IO 多线程，命令执行单线程

### Q3: 如何保证缓存与数据库一致性？
**A**: 
- 先更新数据库，再删除缓存（Cache Aside）
- 延迟双删策略
- 监听 Binlog 异步更新缓存

### Q4: Redis 内存满了怎么办？
**A**: 
- 设置内存上限 `maxmemory`
- 配置淘汰策略（LRU/LFU/TTL）
- 数据分片或扩容

---

## 七、参考资源

- [Redis 官方文档](https://redis.io/documentation)
- [Redis 设计与实现](http://redisbook.com/)
- [Redis 深度历险](https://juejin.cn/book/6844733724618129422)
