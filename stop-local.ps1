# 个人网站项目本地服务停止脚本
# 用途：停止由 start-local.ps1 启动的所有服务
# 运行方式：右键选择“使用 PowerShell 运行”，或命令行执行：.\stop-local.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   个人网站项目 - 停止所有服务         " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 停止 Vue 前端
$vuePidFile = "$env:TEMP\personal-website-vue.pid"
if (Test-Path $vuePidFile) {
    $pid = Get-Content $vuePidFile
    Write-Host "[1/4] 停止 Vue 前端 (PID: $pid)..." -ForegroundColor Yellow
    Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
    Remove-Item $vuePidFile -Force
    Write-Host "   Vue 前端已停止。" -ForegroundColor Green
} else {
    Write-Host "[1/4] Vue 前端未运行。" -ForegroundColor Gray
}

# 停止 Spring Boot 后端
$javaPidFile = "$env:TEMP\personal-website-java.pid"
if (Test-Path $javaPidFile) {
    $pid = Get-Content $javaPidFile
    Write-Host "[2/4] 停止 Spring Boot 后端 (PID: $pid)..." -ForegroundColor Yellow
    Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
    Remove-Item $javaPidFile -Force
    Write-Host "   Spring Boot 后端已停止。" -ForegroundColor Green
} else {
    Write-Host "[2/4] Spring Boot 后端未运行。" -ForegroundColor Gray
}

# 停止 Python 服务
$pythonPidFile = "$env:TEMP\personal-website-python.pid"
if (Test-Path $pythonPidFile) {
    $pid = Get-Content $pythonPidFile
    Write-Host "[3/4] 停止 Python 服务 (PID: $pid)..." -ForegroundColor Yellow
    Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
    Remove-Item $pythonPidFile -Force
    Write-Host "   Python 服务已停止。" -ForegroundColor Green
} else {
    Write-Host "[3/4] Python 服务未运行。" -ForegroundColor Gray
}

# 停止 MySQL 容器（可选，默认保留）
Write-Host "[4/4] MySQL 容器..." -ForegroundColor Yellow
Write-Host "   容器默认保留，如需停止请执行: docker stop toolbox-mysql" -ForegroundColor Gray
Write-Host "   如需删除容器: docker rm -f toolbox-mysql" -ForegroundColor Gray

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "           所有服务已停止               " -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan