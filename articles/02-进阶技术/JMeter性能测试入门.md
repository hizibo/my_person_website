# JMeter 性能测试入门

> 来源：综合整理自 CSDN、白月黑羽、川石教育等技术文章  
> 整理日期：2026-04-25

---

## 一、JMeter 简介

**Apache JMeter** 是一款开源的性能测试工具，主要用于：
- Web 网站性能测试
- API 接口压力测试
- 数据库性能测试
- 消息队列性能测试

**核心特点**：
- 支持多种协议（HTTP/HTTPS、FTP、JDBC、JMS 等）
- 可视化图形界面
- 支持分布式压测
- 丰富的插件生态

---

## 二、环境搭建

### 1. 安装 JDK

JMeter 基于 Java 开发，需要先安装 JDK。

> **建议版本**：JDK 8 或 JDK 11（JDK 17 可能有兼容问题）

### 2. 下载 JMeter

1. 访问 Apache 官网：https://jmeter.apache.org/
2. 下载 Binaries 版本的 zip 包
3. 解压到本地目录，如 `D:\tools\apache-jmeter-5.x.x`

### 3. 启动 JMeter

**Windows**：
```bash
cd apache-jmeter-5.x.x\bin
jmeter.bat
```

**Mac/Linux**：
```bash
cd apache-jmeter-5.x.x/bin
sh jmeter.sh
```

### 4. 设置中文界面

菜单栏：`Options` → `Choose Language` → `Chinese (Simplified)`

---

## 三、核心概念

### 1. 测试计划 (Test Plan)
JMeter 测试的顶层容器，所有测试组件都在测试计划下组织。

### 2. 线程组 (Thread Group)
模拟并发用户的核心组件：
- **线程数**：虚拟用户数（并发数）
- **Ramp-Up 时间**：启动所有线程所需时间
- **循环次数**：每个线程发送请求的次数

### 3. 取样器 (Sampler)
发送具体请求的组件：
- HTTP 请求
- JDBC 请求
- FTP 请求
- JMS 请求

### 4. 监听器 (Listener)
查看测试结果：
- 查看结果树
- 聚合报告
- 图形结果

### 5. 断言 (Assertion)
验证响应结果是否符合预期。

### 6. 配置元件 (Config Element)
配置请求参数：
- HTTP 请求默认值
- HTTP Cookie 管理器
- HTTP 信息头管理器

---

## 四、HTTP 接口压测实战

### 步骤 1：创建测试计划

1. 右键点击「测试计划」
2. 选择「添加」→「线程（用户）」→「线程组」

### 步骤 2：配置线程组

| 参数 | 说明 | 示例值 |
|------|------|--------|
| 线程数 | 并发用户数 | 100 |
| Ramp-Up 时间 | 启动时间（秒） | 10 |
| 循环次数 | 每个线程执行次数 | 10 |

**计算**：100 线程 × 10 循环 = 1000 次请求，在 10 秒内启动完成

### 步骤 3：添加 HTTP 请求

1. 右键点击「线程组」
2. 选择「添加」→「取样器」→「HTTP 请求」

**配置参数**：
- **协议**：http 或 https
- **服务器名称或 IP**：目标服务器地址
- **端口号**：服务端口号
- **方法**：GET / POST / PUT / DELETE
- **路径**：接口路径
- **参数**：请求参数（GET）或请求体数据（POST）

### 步骤 4：添加 HTTP 信息头管理器

1. 右键点击「HTTP 请求」
2. 选择「添加」→「配置元件」→「HTTP 信息头管理器」

**常用请求头**：
```
Content-Type: application/json
Authorization: Bearer your_token
```

### 步骤 5：添加监听器

1. 右键点击「线程组」
2. 选择「添加」→「监听器」

**推荐监听器**：
- **查看结果树**：查看每个请求的详细响应
- **聚合报告**：查看整体性能指标
- **图形结果**：实时查看响应时间曲线

### 步骤 6：运行测试

点击工具栏的绿色「启动」按钮运行测试。

---

## 五、聚合报告指标解读

| 指标 | 说明 | 参考标准 |
|------|------|----------|
| **样本数** | 总请求数 | - |
| **平均值** | 平均响应时间 | < 500ms |
| **中位数** | 响应时间中位数 | < 500ms |
| **90% 百分位** | 90% 请求的响应时间 | < 1s |
| **95% 百分位** | 95% 请求的响应时间 | < 2s |
| **99% 百分位** | 99% 请求的响应时间 | < 3s |
| **最小值/最大值** | 最短/最长响应时间 | - |
| **错误率** | 失败请求占比 | < 0.1% |
| **吞吐量** | 每秒处理请求数 (TPS) | 越高越好 |
| **接收/发送 KB/sec** | 网络带宽 | - |

---

## 六、高级功能

### 1. 参数化测试

**CSV 数据文件设置**：
1. 准备 CSV 文件，包含测试数据
2. 右键「线程组」→「添加」→「配置元件」→「CSV Data Set Config」
3. 配置文件路径和变量名
4. 在 HTTP 请求中使用 `${变量名}` 引用

### 2. 断言验证

**响应断言**：
1. 右键「HTTP 请求」→「添加」→「断言」→「响应断言」
2. 配置要验证的响应内容

**JSON 断言**：
1. 右键「HTTP 请求」→「添加」→「断言」→「JSON 断言」
2. 使用 JSON Path 提取和验证字段

### 3. 关联处理

**正则表达式提取器**：
1. 右键「HTTP 请求」→「添加」→「后置处理器」→「正则表达式提取器」
2. 提取响应中的动态值（如 token）
3. 在后续请求中使用 `${变量名}` 引用

**JSON 提取器**：
```
JSON Path 表达式: $.data.token
变量名: token
```

### 4. 插件安装

**安装插件管理器**：
1. 下载 `plugins-manager.jar`
2. 放入 `lib/ext` 目录
3. 重启 JMeter

**推荐插件**：
- **3 Basic Graphs**：实时 TPS 和响应时间图表
- **PerfMon Metrics Collector**：服务器性能监控
- **Custom Thread Groups**：阶梯加压线程组

---

## 七、分布式压测

### 1. 架构

```
控制机 (Master)  ---->  负载机 1 (Slave)
                    ---->  负载机 2 (Slave)
                    ---->  负载机 N (Slave)
```

### 2. 负载机配置

1. 编辑 `bin/jmeter.properties`：
```properties
server_port=1099
server.rmi.localport=1099
```

2. 启动负载机：
```bash
jmeter-server.bat  # Windows
./jmeter-server    # Linux/Mac
```

### 3. 控制机配置

编辑 `bin/jmeter.properties`：
```properties
remote_hosts=192.168.1.101:1099,192.168.1.102:1099
```

### 4. 运行分布式测试

菜单栏：`运行` → `远程启动` → 选择负载机

---

## 八、最佳实践

### 1. 测试计划设计原则
- 线程组之间保持独立
- 合理使用配置元件减少重复配置
- 添加必要的断言验证结果

### 2. 压测执行原则
- 从低并发开始，逐步增加压力
- 关注系统资源使用情况（CPU、内存、IO）
- 记录每次测试的配置和结果

### 3. 结果分析原则
- 重点关注 90%、95%、99% 百分位响应时间
- 错误率必须控制在可接受范围内
- 吞吐量达到瓶颈时停止加压

---

## 九、常见问题

### Q1: JMeter 启动报错 Java 版本问题？
**A**: 确保安装 JDK 8 或 JDK 11，并配置好 JAVA_HOME 环境变量。

### Q2: 中文显示乱码？
**A**: 
1. 修改 `bin/jmeter.properties`：
```properties
sampleresult.default.encoding=UTF-8
```
2. HTTP 请求添加 Content-Type: application/json;charset=UTF-8

### Q3: 高并发时 JMeter 内存不足？
**A**: 修改 `bin/jmeter.bat` 中的 JVM 参数：
```bash
set HEAP=-Xms2g -Xmx8g
```

---

## 十、参考链接

- [使用 JMeter 进行系统性能压测教程 - CSDN](https://blog.csdn.net/qq_43622031/article/details/126389414)
- [JMeter 压测详解 - 今日头条](https://www.toutiao.com/article/7415795512995103258/)
- [JMeter 快速上手 - 白月黑羽](https://www.byhy.net/etc/loadtest/jmeter/01/)
- [JMeter 压力测试怎么做 - 川石教育](http://www.chuansinfo.com/itzixun/2643.html)
