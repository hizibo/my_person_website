package com.toolbox.controller;

import com.toolbox.common.Result;
import com.toolbox.entity.NoteCategory;
import com.toolbox.service.NoteCategoryService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController
@RequestMapping("/api/note/category")
@Tag(name = "笔记分类管理")
@CrossOrigin(origins = "*")
public class NoteCategoryController {

    @Autowired
    private NoteCategoryService noteCategoryService;

    @GetMapping("/list")
    @Operation(summary = "获取所有分类列表")
    public Result<List<NoteCategory>> list() {
        List<NoteCategory> categories = noteCategoryService.getAllCategories();
        return Result.success(categories);
    }

    @GetMapping("/root")
    @Operation(summary = "获取根分类")
    public Result<List<NoteCategory>> root() {
        List<NoteCategory> categories = noteCategoryService.getRootCategories();
        return Result.success(categories);
    }

    @GetMapping("/children/{parentId}")
    @Operation(summary = "根据父级ID获取子分类")
    public Result<List<NoteCategory>> children(@PathVariable Long parentId) {
        List<NoteCategory> categories = noteCategoryService.getChildrenCategories(parentId);
        return Result.success(categories);
    }

    @PostMapping("/add")
    @Operation(summary = "新增分类")
    public Result<Boolean> add(@RequestBody NoteCategory category) {
        boolean success = noteCategoryService.addCategory(category);
        return success ? Result.success(true) : Result.error("添加失败");
    }

    @PutMapping("/update")
    @Operation(summary = "更新分类")
    public Result<Boolean> update(@RequestBody NoteCategory category) {
        if (category.getId() == null) {
            return Result.error("ID不能为空");
        }
        boolean success = noteCategoryService.updateCategory(category);
        return success ? Result.success(true) : Result.error("更新失败");
    }

    @DeleteMapping("/delete/{id}")
    @Operation(summary = "删除分类")
    public Result<Boolean> delete(@PathVariable Long id) {
        boolean success = noteCategoryService.deleteCategory(id);
        return success ? Result.success(true) : Result.error("删除失败（存在子分类或笔记）");
    }
}