<#
.SYNOPSIS
    启动系统 - Docker 模式
.DESCRIPTION
    启动设备信息动态管理系统（Docker 模式）
#>

param(
    [switch]$SkipBuild,
    [switch]$Help
)

# 设置控制台编码
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

# 颜色输出函数
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

function Write-Success($msg) { Write-ColorOutput Green "[✓] $msg" }
function Write-Error($msg) { Write-ColorOutput Red "[✗] $msg" }
function Write-Info($msg) { Write-ColorOutput Cyan "[ℹ] $msg" }
function Write-Warning($msg) { Write-ColorOutput Yellow "[⚠] $msg" }

if ($Help) {
    Write-Output @"
使用说明:
  .\start-system.ps1              # 启动系统
  .\start-system.ps1 -SkipBuild   # 跳过构建
  .\start-system.ps1 -Help         # 显示此帮助
"@
    exit
}

Write-Output ""
Write-Info "========================================="
Write-Info "  启动设备信息动态管理系统"
Write-Info "========================================="
Write-Output ""

# 检查 Docker
try {
    docker --version | Out-Null
} catch {
    Write-Error "Docker 未安装或未启动！"
    exit 1
}

# 检查服务状态
Write-Info "检查现有服务..."
$runningServices = docker-compose ps --services --filter "status=running" 2>$null

# 如果服务已经在运行，询问是否重启
if ($runningServices) {
    Write-Warning "系统已在运行中！"
    Write-Output ""
    $response = Read-Host "是否重启系统？(y/N)"
    if ($response -ne 'y' -and $response -ne 'Y') {
        Write-Info "取消操作"
        exit 0
    }
    Write-Info "停止旧服务..."
    docker-compose down
}

# 构建并启动
Write-Info "启动服务..."
if ($SkipBuild) {
    docker-compose up -d
} else {
    docker-compose up -d --build
}

if ($LASTEXITCODE -ne 0) {
    Write-Error "启动失败！"
    exit 1
}

Write-Success "服务启动成功"
Write-Output ""

# 等待服务就绪
Write-Info "等待服务初始化（约 10-15 秒）..."
Start-Sleep -Seconds 15

# 检查服务状态
Write-Info "检查服务状态..."
docker-compose ps

# 获取本机 IP
$localIP = Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -notlike "127.*" } | Select-Object -First 1 -ExpandProperty IPAddress

Write-Output ""
Write-Success "========================================="
Write-Success "  系统启动成功！"
Write-Success "========================================="
Write-Output ""
Write-Output "访问地址:"
Write-Output "  前端界面:  http://localhost:5173"
Write-Output "  局域网访问: http://${localIP}:5173"
Write-Output ""
Write-Output "API 文档:"
Write-Output "  http://localhost:8000/docs"
Write-Output ""
Write-Output "默认账号:"
Write-Output "  超级管理员: root / root123"
Write-Output "  管理员: admin / admin123"
Write-Output ""
Write-Info "提示: 使用 .\stop-system.ps1 停止系统"
Write-Output ""
