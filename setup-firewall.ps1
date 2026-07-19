<#
.SYNOPSIS
    配置防火墙规则 - 允许局域网访问
.DESCRIPTION
    自动配置 Windows 防火墙，开放设备管理系统所需的端口
#>

param(
    [switch]$Remove,
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
  .\setup-firewall.ps1           # 配置防火墙规则
  .\setup-firewall.ps1 -Remove   # 删除防火墙规则
  .\setup-firewall.ps1 -Help      # 显示此帮助

说明:
  此脚本会创建以下防火墙规则:
    - 设备管理系统-前端: 开放 5173 端口（前端）
    - 设备管理系统-后端: 开放 8000 端口（后端 API）
    - 设备管理系统-数据库: 可选，开放 5432 端口
"@
    exit
}

# 需要管理员权限
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Error "需要管理员权限！"
    Write-Output "请右键点击 PowerShell 选择 '以管理员身份运行'"
    exit 1
}

Write-Output ""
Write-Info "========================================="
Write-Info "  防火墙配置"
Write-Info "========================================="
Write-Output ""

$rules = @(
    @{
        Name = "设备管理系统-前端"
        Port = 5173
        Description = "设备管理系统前端开发服务器"
    },
    @{
        Name = "设备管理系统-后端"
        Port = 8000
        Description = "设备管理系统后端 API"
    },
    @{
        Name = "设备管理系统-数据库"
        Port = 5432
        Description = "PostgreSQL 数据库（可选）"
    }
)

if ($Remove) {
    # 删除规则
    Write-Info "删除防火墙规则..."
    foreach ($rule in $rules) {
        $existingRule = Get-NetFirewallRule -DisplayName $rule.Name -ErrorAction SilentlyContinue
        if ($existingRule) {
            Remove-NetFirewallRule -DisplayName $rule.Name
            Write-Success "已删除: $($rule.Name)"
        } else {
            Write-Info "规则不存在: $($rule.Name)"
        }
    }
    Write-Success "防火墙规则已删除"
} else {
    # 添加规则
    Write-Info "配置防火墙规则..."
    foreach ($rule in $rules) {
        $existingRule = Get-NetFirewallRule -DisplayName $rule.Name -ErrorAction SilentlyContinue
        if ($existingRule) {
            Write-Info "规则已存在: $($rule.Name)，跳过"
        } else {
            New-NetFirewallRule -DisplayName $rule.Name -Direction Inbound -Protocol TCP -LocalPort $rule.Port -Action Allow -Description $rule.Description | Out-Null
            Write-Success "已添加: $($rule.Name) (端口 $($rule.Port))"
        }
    }
    Write-Success "防火墙配置完成"
}

Write-Output ""
Write-Info "查看规则: Get-NetFirewallRule -DisplayName '设备管理系统*'"
Write-Output ""
