package com.toolbox.controller;

import com.toolbox.common.Result;
import com.toolbox.entity.User;
import com.toolbox.service.UserService;
import com.toolbox.util.JwtUtil;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/auth")
@Tag(name = "认证管理")
@CrossOrigin(origins = "*")
public class AuthController {

    @Autowired
    private UserService userService;

    @Autowired
    private PasswordEncoder passwordEncoder;

    @Autowired
    private JwtUtil jwtUtil;

    @PostMapping("/login")
    @Operation(summary = "用户登录")
    public Result<Map<String, Object>> login(@RequestBody Map<String, String> body) {
        String username = body.get("username");
        String password = body.get("password");

        if (username == null || password == null) {
            return Result.error("用户名和密码不能为空");
        }

        User user = userService.findByUsername(username);
        if (user == null || !passwordEncoder.matches(password, user.getPassword())) {
            return Result.error("用户名或密码错误");
        }

        String token = jwtUtil.generateToken(username);
        Map<String, Object> data = new HashMap<>();
        data.put("token", token);
        data.put("username", username);
        // admin 用户拥有所有权限，permissions 返回 "all"
        data.put("permissions", "admin".equals(username) ? "all" : (user.getPermissions() != null ? user.getPermissions() : ""));
        return Result.success(data);
    }

    @GetMapping("/check")
    @Operation(summary = "校验Token是否有效")
    public Result<Map<String, Object>> check(@RequestHeader(value = "Authorization", required = false) String authHeader) {
        if (authHeader != null && authHeader.startsWith("Bearer ")) {
            String token = authHeader.substring(7);
            if (jwtUtil.validateToken(token)) {
                String username = jwtUtil.getUsernameFromToken(token);
                User user = userService.findByUsername(username);
                Map<String, Object> data = new HashMap<>();
                data.put("username", username);
                data.put("permissions", "admin".equals(username) ? "all" : (user != null && user.getPermissions() != null ? user.getPermissions() : ""));
                return Result.success(data);
            }
        }
        return Result.error(401, "未登录或Token已过期");
    }
}
