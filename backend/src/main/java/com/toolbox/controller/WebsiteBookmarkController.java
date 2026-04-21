package com.toolbox.controller;

import com.toolbox.common.Result;
import com.toolbox.entity.WebsiteBookmark;
import com.toolbox.service.WebsiteBookmarkService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/website-bookmark")
@Tag(name = "网站收藏管理")
@CrossOrigin(origins = "*")
public class WebsiteBookmarkController {

    @Autowired
    private WebsiteBookmarkService websiteBookmarkService;

    @GetMapping("/list")
    @Operation(summary = "获取网站列表")
    public Result<List<WebsiteBookmark>> list() {
        List<WebsiteBookmark> bookmarks = websiteBookmarkService.getAllBookmarks();
        return Result.success(bookmarks);
    }

    @PostMapping("/add")
    @Operation(summary = "新增网站")
    public Result<Boolean> add(@RequestBody WebsiteBookmark bookmark) {
        if (bookmark.getName() == null || bookmark.getName().trim().isEmpty()) {
            return Result.error("网站名称不能为空");
        }
        if (bookmark.getUrl() == null || bookmark.getUrl().trim().isEmpty()) {
            return Result.error("网站地址不能为空");
        }
        boolean success = websiteBookmarkService.addBookmark(bookmark);
        return success ? Result.success(true) : Result.error("添加失败");
    }

    @PutMapping("/update")
    @Operation(summary = "更新网站")
    public Result<Boolean> update(@RequestBody WebsiteBookmark bookmark) {
        if (bookmark.getId() == null) {
            return Result.error("ID不能为空");
        }
        boolean success = websiteBookmarkService.updateBookmark(bookmark);
        return success ? Result.success(true) : Result.error("更新失败");
    }

    @DeleteMapping("/delete/{id}")
    @Operation(summary = "删除网站")
    public Result<Boolean> delete(@PathVariable Long id) {
        boolean success = websiteBookmarkService.deleteBookmark(id);
        return success ? Result.success(true) : Result.error("删除失败");
    }

    @GetMapping("/search")
    @Operation(summary = "搜索网站")
    public Result<List<WebsiteBookmark>> search(@RequestParam String keyword) {
        List<WebsiteBookmark> bookmarks = websiteBookmarkService.searchBookmarks(keyword);
        return Result.success(bookmarks);
    }
}
