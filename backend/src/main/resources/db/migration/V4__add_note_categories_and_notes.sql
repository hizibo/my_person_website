-- =============================================
-- V4: 新增笔记分类和技术文章
-- 分类：AI前沿、部署实战、源码学习
-- =============================================

-- 新增分类
INSERT INTO note_category (name, parent_id, sort) VALUES
('AI前沿', 0, 4),
('部署实战', 0, 5),
('源码学习', 0, 6);

-- =============================================
-- AI前沿分类下的笔记
-- =============================================

SET @cat_ai = (SELECT id FROM note_category WHERE name = 'AI前沿' LIMIT 1);

INSERT INTO note (category_id, title, summary, tags, content) VALUES
(@cat_ai, 'GPT-5 技术原理深度解析', '全面解析GPT-5的核心架构创新、训练方法和能力跃升', 'AI,GPT,NLP', '<p><strong>GPT-5 核心升级点</strong></p><ul><li>多模态原生融合：不再是外挂decoder，而是从预训练阶段就统一建模文本、图像、音频</li><li>百万级上下文窗口：原生支持100万token的上下文理解</li><li>自我博弈强化学习：在安全框架内实现持续的自我能力提升</li></ul><p><strong>架构创新</strong></p><p>稀疏MoE与稠密注意力的混合架构，在不同层自适应选择计算路径，大幅提升推理效率。</p>'),
(@cat_ai, 'Claude 3.5 vs GPT-4o 深度对比', '从架构、训练数据、能力边界等多个维度对比两大顶级模型', 'AI,Claude,GPT,对比', '<p><strong>上下文处理</strong></p><p>Claude 3.5 Sontext支持20万token上下文，在长文档分析任务中明显优于GPT-4o的12.8万token限制。</p><p><strong>代码能力</strong></p><p>GPT-4o在代码生成速度上更快，Claude 3.5在复杂代码理解和debug上略胜一筹。</p><p><strong>指令遵循</strong></p><p>Claude 3.5的Haiku子模型在指令遵循 benchmark上刷新了SOTA，领先GPT-4o约12%。</p>'),
(@cat_ai, 'RAG系统优化实践指南', '从检索质量、Embedding模型选择、混合检索策略提升RAG效果', 'AI,RAG,向量检索', '<p><strong>检索质量优化</strong></p><ul><li>使用BGE-M3或E5-Mistral等多语言Embedding模型</li><li>对文档进行智能分块：递归字符分割 + 重叠窗口</li><li>添加Query Expansion，提升召回率</li></ul><p><strong>混合检索策略</strong></p><p>BM25 + 向量检索的RRF融合，在多数benchmark上优于单一检索方式。</p>');

-- =============================================
-- 部署实战分类下的笔记
-- =============================================

SET @cat_deploy = (SELECT id FROM note_category WHERE name = '部署实战' LIMIT 1);

INSERT INTO note (category_id, title, summary, tags, content) VALUES
(@cat_deploy, 'Docker容器化最佳实践', '从零构建生产级Docker镜像，包括多阶段构建、安全加固、资源限制', 'Docker,容器,DevOps', '<p><strong>多阶段构建示例</strong></p><pre><code>FROM maven:3.9 AS build\nWORKDIR /app\nCOPY pom.xml .\nRUN mvn dependency:go-offline\nCOPY src ./src\nRUN mvn package -DskipTests\n\nFROM openjdk:17-slim\nCOPY --from=build /app/target/*.jar app.jar\nEXPOSE 8080\nENTRYPOINT [&quot;java&quot;, &quot;-jar&quot;, &quot;-Xmx256m&quot;, &quot;app.jar&quot;]</code></pre><p><strong>安全加固</strong></p><ul><li>使用非root用户运行：<code>USER nonroot:nonroot</code></li><li>只读文件系统：<code>--read-only</code></li><li>禁用特权模式</li></ul>'),
(@cat_deploy, 'Kubernetes生产环境集群规划', '生产K8s集群的节点规划、网络方案、存储选型和高可用设计', 'Kubernetes,K8s,运维', '<p><strong>节点规划建议</strong></p><ul><li>etcd集群：3节点独立，最低2核4G SSD</li><li>Master节点：3节点，4核8G</li><li>Worker节点：根据业务量，16核64G起步</li></ul><p><strong>网络方案</strong></p><p>Cilium + eBPF是当前性能最优方案，相比Calico提升20-30%网络吞吐量。</p>'),
(@cat_deploy, 'Nginx反向代理与负载均衡配置', '生产环境Nginx配置实战：SSL终结、动静分离、健康检查', 'Nginx,运维,反向代理', '<p><strong>核心配置片段</strong></p><pre><code>upstream backend {\n    least_conn;\n    server 192.168.1.10:8080 max_fails=3 fail_timeout=30s;\n    server 192.168.1.11:8080 max_fails=3 fail_timeout=30s;\n    keepalive 32;\n}\n\nserver {\n    listen 443 ssl http2;\n    ssl_certificate /etc/ssl/certs/server.crt;\n    ssl_certificate_key /etc/ssl/private/server.key;\n    ssl_protocols TLSv1.2 TLSv1.3;\n    \n    location /api/ {\n        proxy_pass http://backend;\n        proxy_set_header Host $host;\n        proxy_set_header X-Real-IP $remote_addr;\n    }\n}</code></pre>');

-- =============================================
-- 源码学习分类下的笔记
-- =============================================

SET @cat_source = (SELECT id FROM note_category WHERE name = '源码学习' LIMIT 1);

INSERT INTO note (category_id, title, summary, tags, content) VALUES
(@cat_source, 'Vue3响应式系统源码解析', '深入理解Vue3的Proxy-based响应式原理，从ref到reactive的实现链路', 'Vue3,源码,JavaScript', '<p><strong>响应式核心链路</strong></p><ol><li><code>ref()</code>创建一个包装对象，持有<code>.value</code></li><li>通过<code>createReactiveObject()</code>生成Proxy</li><li>getter中收集依赖到<code>targetMap</code>（WeakMap）</li><li>setter中触发<code>triggerEffects</code>遍历更新</li></ol><p><strong>关键数据结构</strong></p><pre><code>const targetMap = new WeakMap&lt;Object, Map&lt;string | symbol, Set&lt;ReactiveEffect&gt;&gt;&gt;()</code></pre><p>这是整个响应式系统的依赖图，外层WeakMap按target寻址，内层Map按key寻址，Set存储所有依赖该属性的Effect。</p>'),
(@cat_source, 'Spring Boot自动配置原理', '从@EnableAutoConfiguration到Condition条件装配的完整流程', 'Spring,Java,源码', '<p><strong>自动配置触发链路</strong></p><ul><li><code>@EnableAutoConfiguration</code> → <code>AutoConfigurationImportSelector</code></li><li>读取<code>META-INF/spring.factories</code>或<code>META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports</code></li><li>按<code>@Conditional</code>条件过滤可用的配置类</li><li>通过<code>AutoConfigurationSorter</code>解析<code>@AutoConfigureBefore/After</code>确定加载顺序</li></ul><p><strong>条件装配</strong></p><p>最常用的是<code>@ConditionalOnClass</code>——当classpath中存在指定类时才生效，这也是Spring Boot智能判断用户引入了什么依赖的核心机制。</p>'),
(@cat_source, 'MyBatis-Plus核心原理与插件机制', '理解MyBatis-Plus的ID生成器、逻辑删除、分页插件的执行流程', 'MyBatis,Java,ORM', '<p><strong>分页插件原理</strong></p><p>MyBatis-Plus的<code>PaginationInnerInterceptor</code>在SQL执行前判断是否需要分页：</p><ol><li>先执行<code>SELECT COUNT(*)</code>获取总数</li><li>然后在原SQL外包裹分页子查询：<code>SELECT * FROM (...) AS t LIMIT x OFFSET y</code></li></ol><p><strong>ID生成器</strong></p><p><code>IdentifierGenerator</code>接口支持多种策略：</p><ul><li>Snowflake（默认）：时间戳 + 机器ID + 序列号</li><li>Redis：基于Redis INCR原子操作</li><li>自定义：实现接口注入Spring容器即可</li></ul>');
