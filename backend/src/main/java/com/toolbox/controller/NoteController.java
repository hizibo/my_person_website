package com.toolbox.controller;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.toolbox.common.PageResult;
import com.toolbox.common.Result;
import com.toolbox.entity.Note;
import com.toolbox.service.NoteService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController
@RequestMapping("/api/note")
@Tag(name = "笔记管理")
@CrossOrigin(origins = "*")
public class NoteController {

    @Autowired
    private NoteService noteService;

    @GetMapping("/list")
    @Operation(summary = "获取所有笔记（分页）")
    public Result<PageResult<Note>> list(
            @RequestParam(defaultValue = "1") Integer page,
            @RequestParam(defaultValue = "10") Integer size) {
        PageResult<Note> result = noteService.getAllNotes(page, size);
        return Result.success(result);
    }

    @GetMapping("/category/{categoryId}")
    @Operation(summary = "根据分类ID获取笔记（分页）")
    public Result<PageResult<Note>> listByCategory(
            @PathVariable Long categoryId,
            @RequestParam(defaultValue = "1") Integer page,
            @RequestParam(defaultValue = "10") Integer size) {
        PageResult<Note> result = noteService.getNotesByCategoryId(categoryId, page, size);
        return Result.success(result);
    }

    @GetMapping("/category/{categoryId}/with-children")
    @Operation(summary = "根据分类ID获取笔记（含子分类，分页）")
    public Result<PageResult<Note>> listByCategoryWithChildren(
            @PathVariable Long categoryId,
            @RequestParam(defaultValue = "1") Integer page,
            @RequestParam(defaultValue = "10") Integer size) {
        PageResult<Note> result = noteService.getNotesByCategoryIdWithChildren(categoryId, page, size);
        return Result.success(result);
    }

    @GetMapping("/search")
    @Operation(summary = "搜索笔记（分页）")
    public Result<PageResult<Note>> search(
            @RequestParam String keyword,
            @RequestParam(defaultValue = "1") Integer page,
            @RequestParam(defaultValue = "10") Integer size) {
        PageResult<Note> result = noteService.searchNotes(keyword, page, size);
        return Result.success(result);
    }

    @GetMapping("/detail/{id}")
    @Operation(summary = "获取笔记详情")
    public Result<Note> detail(@PathVariable Long id) {
        Note note = noteService.getNoteById(id);
        return note != null ? Result.success(note) : Result.error("笔记不存在");
    }

    @PostMapping("/add")
    @Operation(summary = "新增笔记")
    public Result<Boolean> add(@RequestBody Note note) {
        boolean success = noteService.addNote(note);
        return success ? Result.success(true) : Result.error("添加失败");
    }

    @PutMapping("/update")
    @Operation(summary = "更新笔记")
    public Result<Boolean> update(@RequestBody Note note) {
        if (note.getId() == null) {
            return Result.error("ID不能为空");
        }
        boolean success = noteService.updateNote(note);
        return success ? Result.success(true) : Result.error("更新失败");
    }

    @DeleteMapping("/delete/{id}")
    @Operation(summary = "删除笔记")
    public Result<Boolean> delete(@PathVariable Long id) {
        boolean success = noteService.deleteNote(id);
        return success ? Result.success(true) : Result.error("删除失败");
    }
}
