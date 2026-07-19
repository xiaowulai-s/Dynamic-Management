<#
.SYNOPSIS
    系统诊断脚本
.DESCRIPTION
    检查系统环境和服务状态，诊断常见问题
#>

param([switch]$Help)

if ($Help) {
    Write-Output "诊断系统环境和服务状态"
    exit
}

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

Write-Output ""
Write-Info "========================================="
Write-Info "  系统诊断"
Write-Info "========================================="
Write-Output ""

# 1. 检查 Docker
Write-Info "1. 检查 Docker..."
try {
    $dockerVersion = docker --version
    Write-Success "Docker: $dockerVersion"

    $composeVersion = docker-compose --version
    Write-Success "Docker Compose: $composeVersion"

    # 检查 Docker 服务
    docker info 2>$null | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Docker 服务运行正常"
    } else {
        Write-Error "Docker 服务未运行"
    }
} catch {
    Write-Error "Docker 未安装"
}
Write-Output ""

# 2. 检查项目目录
Write-Info "2. 检查项目目录..."
$ProjectPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectPath

$requiredFiles = @(
    "docker-compose.yml",
    "backend\requirements.txt",
    "frontend\package.json",
    "backend\app\main.py"
)

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Success "找到: $file"
    } else {
        Write-Error "缺失: $file"
    }
}
Write-Output ""

# 3. 检查环境配置
Write-Info "3. 检查环境配置..."
if (Test-Path "backend\.env") {
    Write-Success ".env 文件存在"

    # 检查关键配置
    $envContent = Get-Content "backend\.env" -Raw
    if ($envContent -match 'HOST=0\.0\.0\.0') {
        Write-Success "HOST 配置正确（允许局域网访问）"
    } else {
        Write-Warning "HOST 可能未配置为 0.0.0.0"
    }
} else {
    Write-Error ".env 文件不存在，请从 .env.example 创建"
}
Write-Output ""

# 4. 检查防火墙
Write-Info "4. 检查防火墙规则..."
$firewallRules = @("设备管理系统-前端", "设备管理系统-后端", "设备管理系统-数据库")
foreach ($ruleName in $firewallRules) {
    $rule = Get-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue
    if ($rule) {
        Write-Success "防火墙规则存在: $ruleName"
    } else {
        Write-Warning "防火墙规则不存在: $ruleName"
    }
}
Write-Output ""

# 5. 检查网络
Write-Info "5. 检查网络配置..."
$localIP = Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -notlike "127.*" } | Select-Object -First 1 -ExpandProperty IPAddress
if ($localIP) {
    Write-Success "本机 IP: $localIP"
} else {
    Write-Error "未找到本机 IP 地址"
}

# 检查端口监听
$listeningPorts = @(5173, 8000)
foreach ($port in $listeningPorts) {
    $connection = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($connection) {
        Write-Success "端口 $port 正在监听"
    } else {
        Write-Warning "端口 $port 未监听"
    }
}
Write-Output ""

# 6. 检查 Docker 服务状态
Write-Info "6. 检查 Docker 服务状态..."
try {
    docker-compose ps | Out-Null
    $services = docker-compose ps --services --filter "status=running"
    if ($services) {
        Write-Success "运行中的服务:"
        $services | ForEach-Object { Write-Output "  - $_" }
    } else {
        Write-Warning "没有服务在运行"
    }
} catch {
    Write-Error "无法检查服务状态"
}
Write-Output ""

# 7. 检查磁盘空间
Write-Info "7. 检查磁盘空间..."
$drive = Get-PSDrive C -ErrorAction SilentlyContinue
if ($drive) {
    $freeGB = [math]::Round($drive.Free / 1GB, 2)
    $totalGB = [math]::Round(($drive.Used + $drive.Free) / 1GB, 2)
    $usedPercent = [math]::Round(($drive.Used / ($drive.Used + $drive.Free)) * 100, 1)

    if ($freeGB -gt 10) {
        Write-Success "磁盘空间: $freeGB GB 可用 / $totalGB GB 总计 ($usedPercent% 已使用)"
    } else {
        Write-Warning "磁盘空间不足: $freeGB GB 可用"
    }
}
Write-Output ""

# 8. 测试端口连通性
Write-Info "8. 测试端口连通性..."

# 测试本地访问
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5173" -TimeoutSec 3 -UseBasicParsing -ErrorAction Stop
    Write-Success "本地访问正常 (HTTP $($response.StatusCode))"
} catch {
    Write-Warning "本地访问测试失败（可能服务未启动）"
}

# 测试后端 API
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 3 -UseBasicParsing -ErrorAction Stop
    Write-Success "后端 API 正常 (HTTP $($response.StatusCode))"
} catch {
    Write-Warning "后端 API 测试失败（可能服务未启动）"
}
Write-Output ""

# 总结
Write-Info "========================================="
Write-Info "  诊断完成"
Write-Info "========================================="
Write-Output ""

Write-Info "建议操作:"
Write-Output "  1. 安装缺失的软件"
Write-Output "  2. 配置防火墙: .\setup-firewall.ps1"
Write-Output "  3. 启动系统: .\start-system.ps1"
Write-Output ""
