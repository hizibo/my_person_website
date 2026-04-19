# 个人网站项目本地一键启动脚本（Windows PowerShell） - 增强版
# 用途：在本地启动所有可用的服务（MySQL、Python、Spring Boot、Vue），方便调试
# 运行方式：右键选择“使用 PowerShell 运行”，或命令行执行：.\start-local.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   个人网站项目 - 本地调试启动脚本     " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 函数：检查命令是否存在
function Test-CommandExists($cmd) {
    $null = Get-Command $cmd -ErrorAction SilentlyContinue
    return $?
}

# 检查各命令是否存在
$dockerExists = Test-CommandExists "docker"
$mvnExists = Test-CommandExists "mvn"
$pythonExists = Test-CommandExists "python"
$npmExists = Test-CommandExists "npm"

$servicesStarted = @()
$servicesSkipped = @()

# 1. MySQL 容器（依赖 Docker）
if ($dockerExists) {
    # 检查 Docker 是否运行
    $dockerRunning = docker info 2>$null
    if (-not $dockerRunning) {
        Write-Host "[警告] Docker 未运行，跳过 MySQL 容器启动。" -ForegroundColor Yellow
        $servicesSkipped += "MySQL"
    } else {
        Write-Host "[1] 检查 MySQL 容器..." -ForegroundColor Yellow
        $mysqlContainer = docker ps -q -f name=toolbox-mysql
        if (-not $mysqlContainer) {
            Write-Host "   启动 MySQL 容器..." -ForegroundColor Gray
            docker run -d --name toolbox-mysql `
                -e MYSQL_ROOT_PASSWORD=root `
                -e MYSQL_DATABASE=my_toolbox `
                -p 3306:3306 `
                -v toolbox-mysql-data:/var/lib/mysql `
                mysql:8.0 `
                --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci
            Start-Sleep -Seconds 10  # 等待 MySQL 完全启动
            Write-Host "   MySQL 容器已启动。" -ForegroundColor Green
        } else {
            Write-Host "   MySQL 容器已在运行。" -ForegroundColor Green
        }
        $servicesStarted += "MySQL"
    }
} else {
    Write-Host "[警告] Docker 未安装，跳过 MySQL 容器启动。" -ForegroundColor Yellow
    $servicesSkipped += "MySQL"
}

# 2. Python 服务（依赖 Python）
if ($pythonExists) {
    Write-Host "[2] 启动 Python 服务 (端口 8001)..." -ForegroundColor Yellow
    $pythonPidFile = "$env:TEMP\personal-website-python.pid"
    Start-Process -WindowStyle Normal -FilePath "python" -ArgumentList "-m uvicorn xmind_parser.main:app --reload --port 8001" -WorkingDirectory "python-services" -PassThru | Select-Object -ExpandProperty Id | Out-File $pythonPidFile
    Write-Host "   Python 服务已启动 (PID: $(Get-Content $pythonPidFile))。" -ForegroundColor Green
    $servicesStarted += "Python"
} else {
    Write-Host "[警告] Python 未安装，跳过 Python 服务启动。" -ForegroundColor Yellow
    $servicesSkipped += "Python"
}

# 3. Spring Boot 后端（依赖 Maven）
if ($mvnExists) {
    Write-Host "[3] 启动 Spring Boot 后端 (端口 8080)..." -ForegroundColor Yellow
    $javaPidFile = "$env:TEMP\personal-website-java.pid"
    Start-Process -WindowStyle Normal -FilePath "mvn" -ArgumentList "spring-boot:run" -WorkingDirectory "backend" -PassThru | Select-Object -ExpandProperty Id | Out-File $javaPidFile
    Write-Host "   Spring Boot 后端已启动 (PID: $(Get-Content $javaPidFile))。" -ForegroundColor Green
    $servicesStarted += "Spring Boot"
} else {
    Write-Host "[警告] Maven 未安装，跳过 Spring Boot 后端启动。" -ForegroundColor Yellow
    $servicesSkipped += "Spring Boot"
}

# 4. Vue 前端（依赖 npm）
if ($npmExists) {
    Write-Host "[4] 启动 Vue 前端 (端口 5173)..." -ForegroundColor Yellow
    $vuePidFile = "$env:TEMP\personal-website-vue.pid"
    Start-Process -WindowStyle Normal -FilePath "npm" -ArgumentList "run dev" -WorkingDirectory "frontend" -PassThru | Select-Object -ExpandProperty Id | Out-File $vuePidFile
    Write-Host "   Vue 前端已启动 (PID: $(Get-Content $vuePidFile))。" -ForegroundColor Green
    $servicesStarted += "Vue"
} else {
    Write-Host "[警告] npm 未安装，跳过 Vue 前端启动。" -ForegroundColor Yellow
    $servicesSkipped += "Vue"
}

# 汇总信息
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
if ($servicesStarted.Count -gt 0) {
    Write-Host "           部分服务启动完成             " -ForegroundColor Green
} else {
    Write-Host "           没有服务被启动               " -ForegroundColor Red
}
Write-Host "========================================" -ForegroundColor Cyan
if ($servicesStarted.Count -gt 0) {
    Write-Host "已启动的服务：" -ForegroundColor White
    foreach ($svc in $servicesStarted) {
        Write-Host "  ✓ $svc" -ForegroundColor Green
    }
}
if ($servicesSkipped.Count -gt 0) {
    Write-Host "跳过的服务：" -ForegroundColor White
    foreach ($svc in $servicesSkipped) {
        Write-Host "  ✗ $svc" -ForegroundColor Yellow
    }
}
Write-Host ""
Write-Host "服务访问地址：" -ForegroundColor White
if ($servicesStarted -contains "Vue") {
    Write-Host "  前端页面:  http://localhost:5173" -ForegroundColor Yellow
}
if ($servicesStarted -contains "Spring Boot") {
    Write-Host "  后端 API:  http://localhost:8080" -ForegroundColor Yellow
}
if ($servicesStarted -contains "Python") {
    Write-Host "  Python服务: http://localhost:8001" -ForegroundColor Yellow
}
if ($servicesStarted -contains "MySQL") {
    Write-Host "  数据库:    localhost:3306 (用户 root / 密码 root)" -ForegroundColor Yellow
}
if ($servicesStarted.Count -eq 0) {
    Write-Host "  无服务运行。" -ForegroundColor Gray
}
Write-Host ""
if ($servicesSkipped.Count -gt 0) {
    Write-Host "缺失的依赖：" -ForegroundColor White
    if (-not $dockerExists) { Write-Host "  - Docker Desktop (用于 MySQL)" -ForegroundColor Gray }
    if (-not $mvnExists) { Write-Host "  - Maven (用于 Spring Boot 后端)" -ForegroundColor Gray }
    if (-not $pythonExists) { Write-Host "  - Python 3 (用于 Python 服务)" -ForegroundColor Gray }
    if (-not $npmExists) { Write-Host "  - Node.js / npm (用于 Vue 前端)" -ForegroundColor Gray }
    Write-Host ""
    Write-Host "安装建议：" -ForegroundColor White
    Write-Host "  1. Docker Desktop: 下载 https://www.docker.com/products/docker-desktop/" -ForegroundColor Gray
    Write-Host "  2. Maven: 使用 Chocolatey (choco install maven) 或手动安装" -ForegroundColor Gray
    Write-Host "  3. Python 3: 从官网下载安装包" -ForegroundColor Gray
    Write-Host "  4. Node.js: 下载包含 npm 的安装包" -ForegroundColor Gray
}
Write-Host ""
Write-Host "停止服务：" -ForegroundColor White
Write-Host "  关闭所有服务:  .\stop-local.ps1" -ForegroundColor Gray
Write-Host "  或手动关闭对应的 PowerShell 窗口。" -ForegroundColor Gray
Write-Host "========================================" -ForegroundColor Cyan