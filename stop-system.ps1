<#
.SYNOPSIS
    停止系统 - Docker 模式
.DESCRIPTION
    停止设备信息动态管理系统（Docker 模式）
#>

param(
    [switch]$RemoveData,
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
  .\stop-system.ps1           # 停止系统（保留数据）
  .\stop-system.ps1 -RemoveData  # 停止并删除所有数据
  .\stop-system.ps1 -Help         # 显示此帮助

警告:
  -RemoveData 参数将删除所有数据，包括数据库、上传文件等！
  此操作不可恢复！
"@
    exit
}

Write-Output ""
Write-Info "========================================="
Write-Info "  停止设备信息动态管理系统"
Write-Info "========================================="
Write-Output ""

# 检查 Docker
try {
    docker --version | Out-Null
} catch {
    Write-Error "Docker 未安装或未启动！"
    exit 1
}

# 检查服务是否运行
$runningServices = docker-compose ps --services --filter "status=running" 2>$null
if (-not $runningServices) {
    Write-Warning "系统未运行"
    exit 0
}

# 确认操作
if ($RemoveData) {
    Write-Warning "警告: 此操作将删除所有数据，包括："
    Write-Output "  - 数据库数据"
    Write-Output "  - 上传文件"
    Write-Output "  - Redis 数据"
    Write-Output ""
    $confirmation = Read-Host "确定要继续吗？输入 'YES' 确认"

    if ($confirmation -ne 'YES') {
        Write-Info "操作已取消"
        exit 0
    }

    Write-Info "停止服务并删除数据..."
    docker-compose down -v
    Write-Success "已停止并删除所有数据"
} else {
    Write-Info "停止服务（保留数据）..."
    docker-compose down
    Write-Success "服务已停止，数据已保留"
}

Write-Output ""
Write-Info "使用 .\start-system.ps1 重新启动系统"
Write-Output ""
