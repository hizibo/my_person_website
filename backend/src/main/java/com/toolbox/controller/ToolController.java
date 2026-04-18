package com.toolbox.controller;

import com.toolbox.common.Result;
import com.toolbox.entity.Tool;
import com.toolbox.service.ToolService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/tool")
@Tag(name = "工具管理")
@CrossOrigin(origins = "*")
public class ToolController {

    @Autowired
    private ToolService toolService;

    @GetMapping("/list")
    @Operation(summary = "获取工具列表")
    public Result<List<Tool>> list() {
        List<Tool> tools = toolService.getOnlineTools();
        return Result.success(tools);
    }

    @GetMapping("/all")
    @Operation(summary = "获取所有工具（含未上线）")
    public Result<List<Tool>> all() {
        return Result.success(toolService.getAllTools());
    }

    @PostMapping("/add")
    @Operation(summary = "添加工具")
    public Result<String> add(@RequestBody Tool tool) {
        boolean success = toolService.addTool(tool);
        return success ? Result.success("添加成功") : Result.error("添加失败");
    }

    @PutMapping("/update")
    @Operation(summary = "更新工具")
    public Result<String> update(@RequestBody Tool tool) {
        boolean success = toolService.updateTool(tool);
        return success ? Result.success("更新成功") : Result.error("更新失败");
    }

    @GetMapping("/info")
    @Operation(summary = "获取工具信息")
    public Result<Tool> info(@RequestParam String toolId) {
        return Result.success(null);
    }
}
