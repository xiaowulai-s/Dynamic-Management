<#
.SYNOPSIS
    一键部署脚本 - Docker 模式
.DESCRIPTION
    自动部署设备信息动态管理系统（Docker 模式）
.NOTES
    需要先安装 Docker Desktop
#>

param(
    [switch]$SkipBuild,
    [switch]$SkipInit,
    [switch]$Help
)

# 设置控制台编码
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

# 项目路径
$ProjectPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectPath

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

# 显示帮助
if ($Help) {
    Write-Output @"
使用说明:
  .\deploy-docker.ps1              # 完整部署（构建镜像+启动）
  .\deploy-docker.ps1 -SkipBuild   # 跳过构建，直接启动
  .\deploy-docker.ps1 -Help         # 显示此帮助

示例:
  .\deploy-docker.ps1               # 首次部署
  .\deploy-docker.ps1 -SkipBuild    # 代码更新后重启
"@
    exit
}

Write-Output ""
Write-Info "========================================="
Write-Info "  设备信息动态管理系统 - Docker 部署"
Write-Info "========================================="
Write-Output ""

# 检查 Docker
Write-Info "检查 Docker 环境..."
try {
    $dockerVersion = docker --version
    Write-Success "Docker 已安装: $dockerVersion"
} catch {
    Write-Error "Docker 未安装或未启动！"
    Write-Output "请先安装 Docker Desktop: https://www.docker.com/products/docker-desktop/"
    exit 1
}

try {
    $composeVersion = docker-compose --version
    Write-Success "Docker Compose 已安装: $composeVersion"
} catch {
    Write-Error "Docker Compose 未安装！"
    exit 1
}

# 检查 Docker 服务状态
Write-Info "检查 Docker 服务状态..."
try {
    docker info 2>$null | Out-Null
    Write-Success "Docker 服务运行正常"
} catch {
    Write-Error "Docker 服务未启动！请启动 Docker Desktop。"
    exit 1
}

# 停止旧服务
Write-Info "停止旧服务..."
docker-compose down 2>$null | Out-Null

# 构建镜像
if (-not $SkipBuild) {
    Write-Info "构建 Docker 镜像（首次约需 10-15 分钟）..."
    docker-compose build --no-cache
    if ($LASTEXITCODE -ne 0) {
        Write-Error "镜像构建失败！"
        exit 1
    }
    Write-Success "镜像构建完成"
} else {
    Write-Info "跳过构建步骤"
}

# 启动服务
Write-Info "启动所有服务..."
docker-compose up -d

if ($LASTEXITCODE -ne 0) {
    Write-Error "服务启动失败！"
    exit 1
}

Write-Success "服务启动成功"
Write-Output ""

# 等待服务启动
Write-Info "等待服务初始化..."
Start-Sleep -Seconds 10

# 检查服务状态
Write-Info "检查服务状态..."
$services = docker-compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
Write-Output $services

# 检查数据库是否就绪
Write-Info "等待数据库就绪..."
$maxRetries = 30
$retry = 0
$dbReady = $false

while ($retry -lt $maxRetries -and -not $dbReady) {
    try {
        $result = docker exec equipment-postgres pg_isready -U postgres 2>&1
        if ($LASTEXITCODE -eq 0) {
            $dbReady = $true
            Write-Success "数据库就绪"
        }
    } catch {}

    if (-not $dbReady) {
        Write-Info "数据库初始化中... ($($retry + 1)/$maxRetries)"
        Start-Sleep -Seconds 2
        $retry++
    }
}

if (-not $dbReady) {
    Write-Warning "数据库初始化超时，但服务可能仍在启动中"
}

# 显示访问信息
Write-Output ""
Write-Info "========================================="
Write-Success "  部署完成！"
Write-Info "========================================="
Write-Output ""

# 获取本机 IP
$localIP = Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -notlike "127.*" } | Select-Object -First 1 -ExpandProperty IPAddress

Write-Output "访问地址:"
Write-Output "  本机访问:  http://localhost:5173"
Write-Output "  局域网访问: http://${localIP}:5173"
Write-Output ""
Write-Output "API 文档:"
Write-Output "  本机: http://localhost:8000/docs"
Write-Output "  局域网: http://${localIP}:8000/docs"
Write-Output ""
Write-Output "默认账号:"
Write-Output "  超级管理员: root / root123"
Write-Output "  管理员: admin / admin123"
Write-Output ""

Write-Info "常用命令:"
Write-Output "  查看状态: docker-compose ps"
Write-Output "  查看日志: docker-compose logs -f"
Write-Output "  停止服务: docker-compose down"
Write-Output "  重启服务: docker-compose restart"
Write-Output ""

Write-Info "详细文档请查看: LOCAL_DEPLOYMENT_GUIDE.md"
Write-Output ""
