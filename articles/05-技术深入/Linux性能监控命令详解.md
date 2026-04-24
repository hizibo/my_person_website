# Linux 性能监控命令详解

> 来源：综合整理自 Worktile、PHP中文网、深度开源等技术文章  
> 整理日期：2026-04-25

---

## 一、top 命令

### 1. 基本用法

```bash
# 启动 top
top

# 常用快捷键
P  # 按 CPU 使用率排序
M  # 按内存使用率排序
T  # 按时间排序
1  # 显示每个 CPU 核心的使用情况
q  # 退出
h  # 帮助
```

### 2. 输出解析

```
top - 10:03:40 up 30 days, 23:31,  1 user,  load average: 0.00, 0.01, 0.00
Tasks: 332 total,   1 running, 251 sleeping,   0 stopped,   0 zombie
%Cpu(s):  0.0 us,  0.3 sy,  0.0 ni, 99.7 id,  0.0 wa,  0.0 hi,  0.0 si,  0.0 st
MiB Mem :   7810.4 total,   1423.2 free,   3124.8 used,   3262.4 buff/cache
MiB Swap:   2048.0 total,   2048.0 free,      0.0 used.   4234.1 avail Mem

  PID USER      PR  NI    VIRT    RES    SHR S  %CPU  %MEM     TIME+ COMMAND
 1234 root      20   0  234567  12345   6789 S   0.3   0.2   0:01.23 nginx
```

**第一行 - 系统信息**：
- `10:03:40`：当前时间
- `up 30 days, 23:31`：系统运行时间
- `1 user`：登录用户数
- `load average: 0.00, 0.01, 0.00`：1/5/15 分钟平均负载

**第二行 - 任务信息**：
- `332 total`：总进程数
- `1 running`：运行中进程
- `251 sleeping`：睡眠进程
- `0 stopped`：停止进程
- `0 zombie`：僵尸进程

**第三行 - CPU 信息**：
- `us`：用户空间占用
- `sy`：系统空间占用
- `ni`：nice 优先级调整
- `id`：空闲 CPU
- `wa`：IO 等待
- `hi`：硬件中断
- `si`：软件中断
- `st`：虚拟机偷取时间

**第四、五行 - 内存信息**：
- `total`：总内存
- `free`：空闲内存
- `used`：已用内存
- `buff/cache`：缓存
- `avail Mem`：可用内存

### 3. 高级用法

```bash
# 指定刷新间隔（3秒）
top -d 3

# 指定显示进程数
top -n 5

# 显示指定用户的进程
top -u username

# 保存到文件
top -b -n 1 > top.log
```

---

## 二、vmstat 命令

### 1. 基本用法

```bash
# 安装 sysstat（如未安装）
sudo apt-get install sysstat  # Ubuntu/Debian
sudo yum install sysstat       # CentOS/RHEL

# 基本用法
vmstat 1 10  # 每秒采样一次，共10次
```

### 2. 输出解析

```
procs -----------memory---------- ---swap-- -----io---- -system-- ------cpu-----
 r  b   swpd   free   buff  cache   si   so    bi    bo   in   cs us sy id wa st
 1  0      0 810420  97380 706280    0    0   115     4   89   79  1  6 90  3  0
```

**进程 (procs)**：
- `r`：运行队列中的进程数（等待 CPU）
- `b`：不可中断睡眠的进程数（等待 IO）

**内存 (memory)**：
- `swpd`：使用的虚拟内存（KB）
- `free`：空闲内存（KB）
- `buff`：缓冲区（KB）
- `cache`：缓存（KB）

**交换 (swap)**：
- `si`：每秒从磁盘读入内存的大小
- `so`：每秒从内存写入磁盘的大小

**IO (io)**：
- `bi`：每秒读取的块数
- `bo`：每秒写入的块数

**系统 (system)**：
- `in`：每秒中断数
- `cs`：每秒上下文切换数

**CPU**：
- `us`：用户时间
- `sy`：系统时间
- `id`：空闲时间
- `wa`：等待 IO 时间
- `st`：虚拟机偷取时间

### 3. 常用场景

```bash
# 查看内存使用情况
vmstat -s

# 查看活跃内存和非活跃内存
vmstat -a

# 查看磁盘统计
vmstat -d

# 查看 fork 统计
vmstat -f
```

---

## 三、iostat 命令

### 1. 基本用法

```bash
# 基本用法
iostat -d -k 1 10  # 每秒显示磁盘IO，共10次

# 显示 CPU 和磁盘信息
iostat -c -d 1

# 显示详细信息
iostat -x 1
```

### 2. 输出解析

```
Device            r/s     w/s     rkB/s     wkB/s   rrqm/s   wrqm/s  %rrqm  %wrqm r_await w_await aqu-sz rareq-sz wareq-sz  svctm  %util
sda              0.50    2.30     12.40     45.60     0.10     1.20  16.67  34.29    2.40    3.10   0.01    24.80    19.83   0.80   0.22
```

**关键指标**：
- `r/s`：每秒读取次数
- `w/s`：每秒写入次数
- `rkB/s`：每秒读取数据量（KB）
- `wkB/s`：每秒写入数据量（KB）
- `r_await`：读请求平均等待时间（ms）
- `w_await`：写请求平均等待时间（ms）
- `%util`：设备利用率（接近100%表示饱和）

### 3. 常用场景

```bash
# 监控指定磁盘
iostat -x sda 1

# 查看 CPU 统计
iostat -c 1

# 显示时间戳
iostat -t 1
```

---

## 四、其他常用命令

### 1. free - 内存使用情况

```bash
# 以人类可读格式显示
free -h

# 以 MB 显示
free -m

# 显示详细信息
free -l

# 持续监控
free -s 3  # 每3秒刷新
```

**输出解析**：
```
              total        used        free      shared  buff/cache   available
Mem:           7.6G        3.0G        1.4G        256M        3.2G        4.1G
Swap:          2.0G          0B        2.0G
```

### 2. df - 磁盘空间

```bash
# 以人类可读格式显示
df -h

# 显示文件系统类型
df -T

# 显示 inode 信息
df -i

# 只显示本地文件系统
df -l
```

### 3. du - 目录大小

```bash
# 查看当前目录大小
du -sh

# 查看指定目录大小
du -sh /var/log

# 查看当前目录下各子目录大小
du -h --max-depth=1

# 排序显示最大的目录
du -h --max-depth=1 | sort -hr
```

### 4. netstat / ss - 网络连接

```bash
# 查看所有连接
netstat -an

# 查看监听端口
netstat -tlnp

# 查看 TCP 连接状态统计
netstat -nat | awk '{print $6}' | sort | uniq -c | sort -rn

# 使用 ss（更快）
ss -tlnp  # 查看监听端口
ss -s     # 统计信息
ss -tan   # 所有 TCP 连接
```

### 5. ps - 进程查看

```bash
# 查看所有进程
ps aux

# 查看指定用户的进程
ps -u username

# 查看进程树
ps auxf

# 按 CPU 排序
ps aux --sort=-%cpu | head -10

# 按内存排序
ps aux --sort=-%mem | head -10

# 查看线程
ps -eLf
```

### 6. sar - 系统活动报告

```bash
# 安装 sysstat
sudo apt-get install sysstat

# 查看 CPU
sar -u 1 10

# 查看内存
sar -r 1 10

# 查看 IO
sar -b 1 10

# 查看网络
sar -n DEV 1 10

# 查看历史数据
sar -u -f /var/log/sysstat/sa01
```

### 7. pidstat - 进程统计

```bash
# 查看所有进程的 CPU
pidstat 1 10

# 查看指定进程
pidstat -p 1234 1

# 查看内存统计
pidstat -r 1

# 查看 IO 统计
pidstat -d 1
```

### 8. lsof - 打开的文件

```bash
# 查看指定端口被哪个进程占用
lsof -i :8080

# 查看指定进程打开的文件
lsof -p 1234

# 查看指定用户打开的文件
lsof -u username

# 查看指定目录被哪些进程使用
lsof /path/to/dir
```

---

## 五、综合监控工具

### 1. htop（交互式 top）

```bash
# 安装
sudo apt-get install htop

# 启动
htop
```

**特点**：
- 彩色界面
- 支持鼠标操作
- 可以滚动查看进程
- 支持进程树显示

### 2. nmon

```bash
# 安装
sudo apt-get install nmon

# 启动
nmon

# 常用快捷键
c  # CPU
m  # 内存
d  # 磁盘
n  # 网络
q  # 退出
```

### 3. glances

```bash
# 安装
sudo apt-get install glances

# 启动
glances

# Web 模式
glances -w
```

---

## 六、性能问题排查流程

### 1. CPU 问题排查

```bash
# 1. 查看整体负载
top
uptime

# 2. 查看 CPU 使用详情
mpstat -P ALL 1

# 3. 查看高 CPU 进程
ps aux --sort=-%cpu | head -10

# 4. 查看进程线程
pidstat -u -p PID 1
```

### 2. 内存问题排查

```bash
# 1. 查看内存使用
free -h
vmstat 1

# 2. 查看高内存进程
ps aux --sort=-%mem | head -10

# 3. 查看内存详细使用
pidstat -r 1

# 4. 查看缓存和缓冲区
slabtop
cat /proc/meminfo
```

### 3. IO 问题排查

```bash
# 1. 查看磁盘 IO
iostat -x 1

# 2. 查看进程 IO
pidstat -d 1

# 3. 查看 IO 详情
iotop

# 4. 查看文件系统缓存
cat /proc/slabinfo
```

### 4. 网络问题排查

```bash
# 1. 查看网络连接
ss -tan
netstat -tan

# 2. 查看网络流量
iftop
nethogs

# 3. 查看网络统计
sar -n DEV 1

# 4. 抓包分析
tcpdump -i eth0
```

---

## 七、常用监控脚本

### 1. 系统资源监控脚本

```bash
#!/bin/bash
# monitor.sh - 系统资源监控

echo "=== 系统资源监控 ==="
echo "时间: $(date)"
echo ""

echo "=== CPU 负载 ==="
uptime
echo ""

echo "=== 内存使用 ==="
free -h
echo ""

echo "=== 磁盘使用 ==="
df -h
echo ""

echo "=== 磁盘 IO ==="
iostat -x 1 1
echo ""

echo "=== 网络连接 ==="
ss -s
echo ""

echo "=== 高 CPU 进程 TOP 5 ==="
ps aux --sort=-%cpu | head -6
echo ""

echo "=== 高内存进程 TOP 5 ==="
ps aux --sort=-%mem | head -6
```

### 2. 性能数据收集

```bash
#!/bin/bash
# collect.sh - 收集性能数据

OUTPUT_DIR="/var/log/perf/$(date +%Y%m%d)"
mkdir -p $OUTPUT_DIR

# 收集 top 数据
top -b -n 1 > $OUTPUT_DIR/top.log

# 收集 vmstat
vmstat 1 60 > $OUTPUT_DIR/vmstat.log &

# 收集 iostat
iostat -x 1 60 > $OUTPUT_DIR/iostat.log &

echo "数据收集开始，保存在 $OUTPUT_DIR"
```

---

## 八、参考链接

- [Linux 性能监控命令 - Worktile](https://worktile.com/kb/ask/291551.html)
- [Linux 监控 top 命令 - Worktile](https://worktile.com/kb/ask/309975.html)
- [Linux 进程监控方法 - PHP中文网](https://m.php.cn/faq/1303453.html)
- [监控 Linux 性能的 18 个命令行工具 - 深度开源](http://www.open-open.com/lib/view/open1392684857866.html)
