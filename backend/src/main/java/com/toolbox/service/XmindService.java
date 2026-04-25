package com.toolbox.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.*;

@Service
public class XmindService {

    private static final Logger log = LoggerFactory.getLogger(XmindService.class);

    // 识别计数器（每个解析请求独立）
    private int recognizedCount = 0;
    private int convertedCount = 0;

    @Value("${python.xmind.url:http://python-tools:8001/xmind/parse-xmind-base64}")
    private String pythonUrl;

    /**
     * 解析XMind文件
     * 返回包含 cases 列表和转换统计的 Map
     */
    public Map<String, Object> parseXmind(byte[] fileContent) {
        // 重置计数器
        recognizedCount = 0;
        convertedCount = 0;

        try {
            // 尝试调用Python服务
            RestTemplate restTemplate = new RestTemplate();
            org.springframework.http.HttpHeaders headers = new org.springframework.http.HttpHeaders();
            headers.set("Content-Type", "application/octet-stream");

            java.util.Base64.Encoder encoder = java.util.Base64.getEncoder();
            String encoded = encoder.encodeToString(fileContent);

            Map<String, String> body = new HashMap<>();
            body.put("file", encoded);

            org.springframework.http.HttpEntity<Map<String, String>> request =
                new org.springframework.http.HttpEntity<>(body, headers);

            var response = restTemplate.postForEntity(pythonUrl, request, Map.class);

            if (response.getStatusCode().value() == 200 && response.getBody() != null) {
                return response.getBody();
            }
        } catch (Exception e) {
            log.warn("Python服务不可用，使用Java原生解析: {}", e.getMessage());
        }

        // 降级：使用Java原生ZIP解析
        return parseXmindNatively(fileContent);
    }

    /**
     * Java原生解析XMind（ZIP格式）
     */
    private Map<String, Object> parseXmindNatively(byte[] fileContent) {
        Map<String, Object> result = new HashMap<>();
        List<Map<String, Object>> cases = new ArrayList<>();
        Map<String, Object> mindmap = new HashMap<>();

        try (java.io.ByteArrayInputStream bais = new java.io.ByteArrayInputStream(fileContent);
             java.util.zip.ZipInputStream zis = new java.util.zip.ZipInputStream(bais)) {

            java.util.zip.ZipEntry entry;
            String jsonContent = null;

            while ((entry = zis.getNextEntry()) != null) {
                if (entry.getName().equals("content.json") || entry.getName().endsWith("/content.json")) {
                    jsonContent = new String(zis.readAllBytes(), java.nio.charset.StandardCharsets.UTF_8);
                    break;
                }
                zis.closeEntry();
            }

            if (jsonContent != null) {
                ObjectMapper mapper = new ObjectMapper();
                Object parsed = mapper.readValue(jsonContent, Object.class);
                mindmap.put("raw", parsed);

                // XMind content.json 是 sheet 数组: [{ "rootTopic": {...} }, ...]
                if (parsed instanceof List) {
                    for (Object sheet : (List<?>) parsed) {
                        cases.addAll(extractCasesFromParsed(sheet, new ArrayList<>()));
                    }
                } else {
                    cases = extractCasesFromParsed(parsed, new ArrayList<>());
                }
            }
        } catch (Exception e) {
            log.error("原生解析失败: ", e);
        }

        result.put("cases", cases);
        result.put("mindmap", mindmap);
        // 转换统计
        result.put("recognizedCount", recognizedCount);
        result.put("convertedCount", convertedCount);
        return result;
    }

    /**
     * 从解析结果中递归提取测试用例
     *
     * 层级结构约定：
     * - Level 1 (root) = 项目名称（不生成用例）
     * - Level 2        = 模块
     * - Level 3        = 预置条件
     * - Level 4        = 测试步骤
     * - Level 5+       = 预期结果
     *
     * 用例名 = 预置条件 _ 测试步骤 _ 预期结果（以下划线连接）
     * 识别到 Level 3 但结构不满足（缺少步骤或预期结果）时跳过该条
     */
    @SuppressWarnings("unchecked")
    private List<Map<String, Object>> extractCasesFromParsed(Object node, List<String> path) {
        List<Map<String, Object>> cases = new ArrayList<>();
        if (node == null) return cases;

        // 处理数组（递归展开）
        if (node instanceof List) {
            for (Object item : (List<?>) node) {
                cases.addAll(extractCasesFromParsed(item, path));
            }
            return cases;
        }

        if (!(node instanceof Map)) return cases;

        Map<String, Object> map = (Map<String, Object>) node;

        // 处理 sheet 的 rootTopic 结构
        if (map.containsKey("rootTopic")) {
            return extractCasesFromParsed(map.get("rootTopic"), path);
        }

        String title = (String) map.get("title");
        if (title != null && !title.isEmpty()) {
            path = new ArrayList<>(path);
            path.add(title);
        }

        // 获取子节点
        List<Map<String, Object>> children = extractTopics(map);

        if (children.isEmpty()) {
            // 叶子节点，判断是否满足用例结构
            // 至少需要 4 层才构成合法用例：项目(1) + 模块(2) + 预置条件(3) + 步骤(4)
            // 预期结果可以是第5层或更深
            if (!path.isEmpty()) {
                if (path.size() >= 3) {
                    // 识别到（至少有预置条件）
                    recognizedCount++;
                }
                Map<String, Object> testCase = buildTestCase(path);
                if (testCase != null) {
                    convertedCount++;
                    cases.add(testCase);
                }
            }
        } else {
            for (Object child : children) {
                cases.addAll(extractCasesFromParsed(child, path));
            }
        }

        return cases;
    }

    /**
     * 提取 topics 节点中的子主题列表
     * 兼容多种 XMind 格式
     */
    @SuppressWarnings("unchecked")
    private List<Map<String, Object>> extractTopics(Map<String, Object> map) {
        List<Map<String, Object>> children = new ArrayList<>();

        Object topicsObj = map.get("topics");
        if (topicsObj instanceof List) {
            children = (List<Map<String, Object>>) topicsObj;
        } else if (topicsObj instanceof Map) {
            // XMind Zen 格式: { "topics": { "attached": [...] } }
            Map<String, Object> topicsMap = (Map<String, Object>) topicsObj;
            if (topicsMap.containsKey("attached")) {
                Object attached = topicsMap.get("attached");
                if (attached instanceof List) {
                    children = (List<Map<String, Object>>) attached;
                }
            }
        }

        return children;
    }

    /**
     * 根据路径构建测试用例
     *
     * 层级映射（path 从 index 0 开始）：
     * - path[0] = Level 1 项目名称（不参与用例名拼接）
     * - path[1] = Level 2 模块
     * - path[2] = Level 3 预置条件
     * - path[3] = Level 4 测试步骤
     * - path[4+] = Level 5+ 预期结果（取最深一层，即 path 最后一项）
     *
     * 用例名 = 预置条件 _ 测试步骤 _ 预期结果
     *
     * @return null 表示结构不合法，应跳过
     */
    private Map<String, Object> buildTestCase(List<String> path) {
        // 至少需要 4 层：项目(1) + 模块(2) + 预置条件(3) + 步骤(4) = index 0~3
        if (path.size() < 4) {
            return null;
        }

        Map<String, Object> tc = new LinkedHashMap<>();

        String module    = path.get(1);             // 模块
        String prereq    = path.get(2);             // 预置条件
        String step     = path.get(3);             // 测试步骤
        String expected = path.get(path.size() - 1); // 预期结果（最深一层）

        tc.put("module",       module);
        tc.put("feature",      prereq);                 // 功能点 = 预置条件
        tc.put("caseName",     prereq + "_" + step + "_" + expected);
        tc.put("precondition", prereq);
        tc.put("steps",        step);
        tc.put("expected",     expected);

        // 优先级：层数越深优先级越低
        int depth = path.size() - 1; // 去掉根节点后的层数
        if (depth <= 3) {
            tc.put("priority", "P0");
        } else if (depth == 4) {
            tc.put("priority", "P1");
        } else {
            tc.put("priority", "P2");
        }

        return tc;
    }
}
