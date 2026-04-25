-- V8: 为 admin_user 表添加 permissions 字段
-- permissions 存储用户拥有的菜单权限，逗号分隔（如 "plan,notes,website,permission"）
-- admin 用户不依赖此字段，默认拥有所有权限
ALTER TABLE admin_user ADD COLUMN permissions VARCHAR(500) DEFAULT '' AFTER password;
