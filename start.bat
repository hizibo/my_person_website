@echo off
chcp 65001 >nul
echo ========================================
echo     我的工具箱 - Windows 启动脚本
echo ========================================
echo.

:: 检查 Docker
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到 Docker，请先安装 Docker Desktop
    pause
    exit /b 1
)

echo [1/3] 启动 MySQL...
docker run -d --name toolbox-mysql ^
  -e MYSQL_ROOT_PASSWORD=root ^
  -e MYSQL_DATABASE=my_toolbox ^
  -p 3306:3306 ^
  -v toolbox-mysql-data:/var/lib/mysql ^
  mysql:8.0 ^
  --character-set-server=utf8mb4 ^
  --collation-server=utf8mb4_unicode_ci

echo [2/3] 初始化数据库...
timeout /t 15 /nobreak >nul
mysql -uroot -proot -h127.0.0.1 --default-character-set=utf8mb4 < backend\sql\init.sql 2>nul
if %errorlevel% equ 0 (
    echo       数据库初始化完成
) else (
    echo       数据库已存在，跳过初始化
)

echo [3/3] 启动完成！
echo.
echo ========================================
echo   服务已启动：
echo   - 数据库: localhost:3306
echo   - 后端:   localhost:8080  (需手动启动)
echo   - 前端:   localhost:5173  (需手动启动)
echo   - Python: localhost:8001  (需手动启动)
echo ========================================
echo.
echo 下一步：
echo   1. 启动后端:  cd backend ^&^& mvn spring-boot:run
echo   2. 启动Python: cd python-services ^&^& uvicorn xmind_parser.main:app --port 8001
echo   3. 启动前端:  cd frontend ^&^& npm run dev
echo.
pause
