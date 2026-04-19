package com.toolbox.controller;

import com.toolbox.common.Result;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.web.bind.annotation.*;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/website")
@Tag(name = "网站管理")
@CrossOrigin(origins = "*")
public class WebsiteController {

    @GetMapping("/list")
    @Operation(summary = "获取网站列表")
    public Result<List<Map<String, Object>>> list() {
        List<Map<String, Object>> websites = new ArrayList<>();
        // 模拟数据
        websites.add(Map.of(
                "id", 1,
                "name", "个人博客",
                "url", "https://blog.example.com",
                "description", "技术博客，分享开发心得",
                "status", "在线"
        ));
        websites.add(Map.of(
                "id", 2,
                "name", "项目作品集",
                "url", "https://portfolio.example.com",
                "description", "展示个人项目作品",
                "status", "在线"
        ));
        websites.add(Map.of(
                "id", 3,
                "name", "工具平台",
                "url", "https://tools.example.com",
                "description", "在线工具集合",
                "status", "开发中"
        ));
        return Result.success(websites);
    }
}