package com.toolbox.controller;

import com.toolbox.common.Result;
import com.toolbox.entity.Plan;
import com.toolbox.service.PlanService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/plan")
@Tag(name = "计划管理")
@CrossOrigin(origins = "*")
public class PlanController {

    @Autowired
    private PlanService planService;

    @GetMapping("/list")
    @Operation(summary = "获取计划列表")
    public Result<List<Plan>> list() {
        List<Plan> plans = planService.getAllPlans();
        return Result.success(plans);
    }

    @PostMapping("/add")
    @Operation(summary = "新增计划")
    public Result<Boolean> add(@RequestBody Plan plan) {
        boolean success = planService.addPlan(plan);
        return success ? Result.success(true) : Result.error("添加失败");
    }

    @PutMapping("/update")
    @Operation(summary = "更新计划")
    public Result<Boolean> update(@RequestBody Plan plan) {
        if (plan.getId() == null) {
            return Result.error("ID不能为空");
        }
        boolean success = planService.updatePlan(plan);
        return success ? Result.success(true) : Result.error("更新失败");
    }

    @DeleteMapping("/delete/{id}")
    @Operation(summary = "删除计划")
    public Result<Boolean> delete(@PathVariable Long id) {
        boolean success = planService.deletePlan(id);
        return success ? Result.success(true) : Result.error("删除失败");
    }
}