<#
.SYNOPSIS
    快速诊断脚本 - 检查局域网访问能力
.DESCRIPTION
    快速诊断系统是否可以从局域网访问
#>

param(
    [switch]$Fix,
    [switch]$Help
)

if ($Help) {
    Write-Output @"
使用说明:
  .\test-lan-access.ps1           # 测试局域网访问
  .\test-lan-access.ps1 -Fix      # 自动修复问题
  .\test-lan-access.ps1 -Help      # 显示此帮助
"@
    exit
}

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Output ""
Write-Info "========================================="
Write-Info "  局域网访问诊断"
Write-Info "========================================="
Write-Output ""

# 检查管理员权限
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
$isAdmin = $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Warning "建议以管理员身份运行此脚本"
    Write-Output ""
}

# 1. 获取本机 IP
Write-Info "1. 检查本机 IP..."
$localIP = Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -notlike "127.*" -and $_.IPAddress -ne "169.254.*" } | Select-Object -First 1 -ExpandProperty IPAddress

if ($localIP) {
    Write-Success "本机 IP: $localIP"
} else {
    Write-Error "未找到本机 IP！请检查网络连接"
    exit 1
}
Write-Output ""

# 2. 检查端口监听
Write-Info "2. 检查服务端口..."

$ports = @(
    @{ Port = 5173; Name = "前端"; Expected = "frontend" },
    @{ Port = 8000; Name = "后端 API"; Expected = "backend" }
)

foreach ($portInfo in $ports) {
    $connection = Get-NetTCPConnection -LocalPort $portInfo.Port -ErrorAction SilentlyContinue
    if ($connection) {
        Write-Success "$($portInfo.Name) 正在监听端口 $($portInfo.Port)"

        # 检查监听的 IP
        $listeningAddress = $connection.LocalAddress
        if ($listeningAddress -eq "0.0.0.0") {
            Write-Success "  → 监听所有接口（包括局域网）"
        } elseif ($listeningAddress -eq "127.0.0.1") {
            Write-Error "  → 仅监听本地回环（局域网无法访问）"
        } else {
            Write-Info "  → 监听 $listeningAddress"
        }
    } else {
        Write-Warning "$($portInfo.Name) 未在端口 $($portInfo.Port) 运行"
    }
}
Write-Output ""

# 3. 检查防火墙
Write-Info "3. 检查防火墙规则..."
$firewallRules = @("设备管理系统-前端", "设备管理系统-后端")
foreach ($ruleName in $firewallRules) {
    $rule = Get-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue
    if ($rule) {
        Write-Success "防火墙规则存在: $ruleName"
    } else {
        Write-Warning "防火墙规则不存在: $ruleName"

        if ($Fix -and $isAdmin) {
            Write-Info "自动修复: 创建防火墙规则..."
            if ($ruleName -match "前端") {
                New-NetFirewallRule -DisplayName $ruleName -Direction Inbound -Protocol TCP -LocalPort 5173 -Action Allow | Out-Null
            } else {
                New-NetFirewallRule -DisplayName $ruleName -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow | Out-Null
            }
            Write-Success "已创建规则: $ruleName"
        } elseif (-not $isAdmin) {
            Write-Info "需要管理员权限才能修复（使用 -Fix 参数）"
        }
    }
}
Write-Output ""

# 4. 测试网络连通性
Write-Info "4. 测试本地访问..."
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5173" -TimeoutSec 3 -UseBasicParsing -ErrorAction Stop
    Write-Success "本地访问正常 (HTTP $($response.StatusCode))"
} catch {
    Write-Warning "本地访问测试失败（服务可能未启动）"
}
Write-Output ""

# 5. 检查网络发现
Write-Info "5. 检查网络发现..."
$networkProfile = Get-NetConnectionProfile -ErrorAction SilentlyContinue
if ($networkProfile) {
    Write-Info "网络类型: $($networkProfile.NetworkCategory)"

    # 检查网络发现是否启用
    $registryPath = "HKLM:\SYSTEM\CurrentControlSet\Services\FDResPub\Parameters"
    $networkDiscoveryEnabled = Get-ItemProperty -Path $registryPath -Name "Start" -ErrorAction SilentlyContinue
    if ($networkDiscoveryEnabled.Start -eq 2) {
        Write-Success "网络发现已启用"
    } else {
        Write-Warning "网络发现可能未启用"
    }
}
Write-Output ""

# 6. 提供访问地址
Write-Info "6. 局域网访问地址:"
Write-Output "  前端: http://${localIP}:5173"
Write-Output "  API:  http://${localIP}:8000"
Write-Output "  API文档: http://${localIP}:8000/docs"
Write-Output ""

# 7. 排查建议
Write-Info "7. 排查建议:"

$issues = @()
if (-not (Get-NetTCPConnection -LocalPort 5173 -ErrorAction SilentlyContinue)) {
    $issues += "服务未启动（运行 .\start-system.ps1）"
}
if (-not (Get-NetFirewallRule -DisplayName "设备管理系统-前端" -ErrorAction SilentlyContinue)) {
    $issues += "防火墙规则缺失（运行 .\setup-firewall.ps1）"
}

if ($issues.Count -eq 0) {
    Write-Success "未发现明显问题"
    Write-Info ""
    Write-Info "如果局域网仍无法访问:"
    Write-Output "  1. 确认其他设备和本机在同一局域网"
    Write-Output "  2. 检查路由器是否隔离设备（AP 隔离）"
    Write-Output "  3. 检查 Windows 防火墙其他规则"
    Write-Output "  4. 在浏览器访问 http://${localIP}:5173 测试"
} else {
    Write-Warning "发现以下问题:"
    foreach ($issue in $issues) {
        Write-Output "  - $issue"
    }

    if ($Fix) {
        Write-Info ""
        Write-Info "使用 -Fix 参数尝试自动修复"
    }
}
Write-Output ""
