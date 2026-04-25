package com.toolbox.controller;

import com.toolbox.common.Result;
import com.toolbox.entity.User;
import com.toolbox.service.UserService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/user")
@Tag(name = "用户权限管理")
public class UserController {

    @Autowired
    private UserService userService;

    @GetMapping("/list")
    @Operation(summary = "获取所有用户列表")
    public Result<List<Map<String, Object>>> list() {
        List<User> users = userService.findAll();
        // 返回时隐藏密码
        List<Map<String, Object>> result = users.stream().map(u -> {
            Map<String, Object> map = new java.util.LinkedHashMap<>();
            map.put("id", u.getId());
            map.put("username", u.getUsername());
            map.put("permissions", u.getPermissions() != null ? u.getPermissions() : "");
            map.put("createdAt", u.getCreatedAt());
            return map;
        }).collect(Collectors.toList());
        return Result.success(result);
    }

    @PostMapping("/add")
    @Operation(summary = "新增用户")
    public Result<Map<String, Object>> add(@RequestBody Map<String, String> body) {
        String username = body.get("username");
        String password = body.get("password");
        String permissions = body.get("permissions");

        if (username == null || username.trim().isEmpty()) {
            return Result.error("用户名不能为空");
        }
        if (password == null || password.trim().isEmpty()) {
            return Result.error("密码不能为空");
        }
        if ("admin".equalsIgnoreCase(username.trim())) {
            return Result.error("不允许创建 admin 用户");
        }
        if (userService.existsByUsername(username.trim())) {
            return Result.error("用户名已存在");
        }

        User user = userService.createUser(username.trim(), password, permissions != null ? permissions : "");
        Map<String, Object> data = new java.util.LinkedHashMap<>();
        data.put("id", user.getId());
        data.put("username", user.getUsername());
        data.put("permissions", user.getPermissions());
        return Result.success(data);
    }

    @PutMapping("/update")
    @Operation(summary = "更新用户信息（密码/权限）")
    public Result<String> update(@RequestBody Map<String, Object> body) {
        Object idObj = body.get("id");
        if (idObj == null) {
            return Result.error("用户ID不能为空");
        }
        Long id = Long.valueOf(idObj.toString());

        User user = userService.findById(id);
        if (user == null) {
            return Result.error("用户不存在");
        }
        if ("admin".equals(user.getUsername())) {
            return Result.error("不允许修改 admin 用户权限");
        }

        String password = (String) body.get("password");
        String permissions = (String) body.get("permissions");

        userService.updateUser(id, password, permissions);
        return Result.success("更新成功");
    }

    @DeleteMapping("/delete/{id}")
    @Operation(summary = "删除用户")
    public Result<String> delete(@PathVariable Long id) {
        User user = userService.findById(id);
        if (user == null) {
            return Result.error("用户不存在");
        }
        if ("admin".equals(user.getUsername())) {
            return Result.error("不允许删除 admin 用户");
        }
        userService.deleteUser(id);
        return Result.success("删除成功");
    }
}
