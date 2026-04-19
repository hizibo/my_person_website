package com.toolbox.controller;

import com.toolbox.common.Result;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.web.bind.annotation.*;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/notes")
@Tag(name = "笔记管理")
@CrossOrigin(origins = "*")
public class NotesController {

    @GetMapping("/list")
    @Operation(summary = "获取笔记列表")
    public Result<List<Map<String, Object>>> list() {
        List<Map<String, Object>> notes = new ArrayList<>();
        // 模拟数据
        notes.add(Map.of(
                "id", 1,
                "title", "Spring Boot 注解大全",
                "content", "详细记录了 Spring Boot 各种注解的使用方法和场景",
                "tags", "Spring,Java",
                "createTime", "2026-04-18"
        ));
        notes.add(Map.of(
                "id", 2,
                "title", "Vue 3 组合式 API 实践",
                "content", "对比选项式 API，总结了组合式 API 的最佳实践",
                "tags", "Vue,前端",
                "createTime", "2026-04-17"
        ));
        notes.add(Map.of(
                "id", 3,
                "title", "MySQL 索引优化原则",
                "content", "总结了索引设计原则、常见误区以及优化案例",
                "tags", "数据库,MySQL",
                "createTime", "2026-04-15"
        ));
        return Result.success(notes);
    }
}