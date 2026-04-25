package com.toolbox.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.toolbox.entity.User;
import com.toolbox.mapper.UserMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class UserService {

    @Autowired
    private UserMapper userMapper;

    @Autowired
    private PasswordEncoder passwordEncoder;

    public User findByUsername(String username) {
        return userMapper.selectOne(
            new LambdaQueryWrapper<User>().eq(User::getUsername, username)
        );
    }

    public List<User> findAll() {
        return userMapper.selectList(null);
    }

    public User findById(Long id) {
        return userMapper.selectById(id);
    }

    /**
     * 新增用户（密码自动 BCrypt 加密）
     */
    public User createUser(String username, String password, String permissions) {
        User user = new User();
        user.setUsername(username);
        user.setPassword(passwordEncoder.encode(password));
        user.setPermissions(permissions != null ? permissions : "");
        userMapper.insert(user);
        return user;
    }

    /**
     * 更新用户信息（密码、权限）
     */
    public User updateUser(Long id, String password, String permissions) {
        User user = userMapper.selectById(id);
        if (user == null) return null;
        if (password != null && !password.isEmpty()) {
            user.setPassword(passwordEncoder.encode(password));
        }
        if (permissions != null) {
            user.setPermissions(permissions);
        }
        userMapper.updateById(user);
        return user;
    }

    /**
     * 删除用户（禁止删除 admin）
     */
    public boolean deleteUser(Long id) {
        User user = userMapper.selectById(id);
        if (user == null || "admin".equals(user.getUsername())) {
            return false;
        }
        userMapper.deleteById(id);
        return true;
    }

    /**
     * 检查用户名是否已存在
     */
    public boolean existsByUsername(String username) {
        return userMapper.selectOne(
            new LambdaQueryWrapper<User>().eq(User::getUsername, username)
        ) != null;
    }
}
