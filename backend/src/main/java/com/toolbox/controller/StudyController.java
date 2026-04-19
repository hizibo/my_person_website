package com.toolbox.controller;

import com.toolbox.common.Result;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.web.bind.annotation.*;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/study")
@Tag(name = "学习管理")
@CrossOrigin(origins = "*")
public class StudyController {

    @GetMapping("/list")
    @Operation(summary = "获取学习列表")
    public Result<List<Map<String, Object>>> list() {
        List<Map<String, Object>> studies = new ArrayList<>();
        // 模拟数据
        studies.add(Map.of(
                "id", 1,
                "title", "Spring Boot 入门",
                "category", "后端",
                "progress", 80,
                "lastUpdate", "2026-04-18"
        ));
        studies.add(Map.of(
                "id", 2,
                "title", "Vue 3 高级特性",
                "category", "前端",
                "progress", 60,
                "lastUpdate", "2026-04-17"
        ));
        studies.add(Map.of(
                "id", 3,
                "title", "MySQL 性能优化",
                "category", "数据库",
                "progress", 30,
                "lastUpdate", "2026-04-15"
        ));
        return Result.success(studies);
    }
}