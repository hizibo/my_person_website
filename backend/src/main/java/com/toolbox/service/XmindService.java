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

    @Value("${python.xmind.url:http://python-tools:8001/xmind/parse-xmind-base64}")
    private String pythonUrl;

    /**
     * 解析XMind文件
     * 如果Python服务不可用，使用Java原生解析
     */
    public Map<String, Object> parseXmind(byte[] fileContent) {
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

                // 提取测试用例
                cases = extractCasesFromParsed(parsed, new ArrayList<>());
            }
        } catch (Exception e) {
            log.error("原生解析失败: ", e);
        }

        result.put("cases", cases);
        result.put("mindmap", mindmap);
        return result;
    }

    /**
     * 从解析结果中递归提取测试用例
     */
    @SuppressWarnings("unchecked")
    private List<Map<String, Object>> extractCasesFromParsed(Object node, List<String> path) {
        List<Map<String, Object>> cases = new ArrayList<>();
        if (node == null) return cases;

        Map<String, Object> map = null;
        List<Map<String, Object>> children = new ArrayList<>();

        if (node instanceof Map) {
            map = (Map<String, Object>) node;
            String title = (String) map.get("title");

            if (title != null && !title.isEmpty()) {
                path = new ArrayList<>(path);
                path.add(title);
            }

            Object topicsObj = map.get("topics");
            if (topicsObj instanceof List) {
                children = (List<Map<String, Object>>) topicsObj;
            }
        }

        if (children.isEmpty()) {
            // 叶子节点 = 测试用例
            if (!path.isEmpty()) {
                Map<String, Object> testCase = buildTestCase(path);
                cases.add(testCase);
            }
        } else {
            for (Object child : children) {
                cases.addAll(extractCasesFromParsed(child, path));
            }
        }

        return cases;
    }

    /**
     * 根据路径构建测试用例
     */
    private Map<String, Object> buildTestCase(List<String> path) {
        Map<String, Object> tc = new LinkedHashMap<>();
        int size = path.size();

        tc.put("module", size >= 1 ? path.get(0) : "");
        tc.put("feature", size >= 2 ? path.get(1) : "");
        tc.put("caseName", size >= 3 ? path.get(size - 1) : (size >= 1 ? path.get(0) : "未命名"));

        StringBuilder steps = new StringBuilder();
        for (int i = 2; i < path.size(); i++) {
            if (steps.length() > 0) steps.append(" -> ");
            steps.append(path.get(i));
        }
        tc.put("precondition", "无");
        tc.put("steps", steps.length() > 0 ? steps.toString() : "根据需求文档执行测试");
        tc.put("expected", "功能运行正常，符合预期结果");

        // 根据深度推断优先级
        tc.put("priority", size <= 2 ? "P0" : (size == 3 ? "P1" : "P2"));

        return tc;
    }
}
