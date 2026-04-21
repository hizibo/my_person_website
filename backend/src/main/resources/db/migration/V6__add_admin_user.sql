-- V6: 添加用户表和管理员账号
CREATE TABLE IF NOT EXISTS admin_user (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 插入默认管理员账号 admin/zhaozibo (BCrypt加密)
INSERT IGNORE INTO admin_user (username, password) VALUES ('admin', '$2b$10$JUc00382oEBLkMOtw7ZiAe.2lEzxSXFmNqxPVoHAnaTi64PtKUoku');
