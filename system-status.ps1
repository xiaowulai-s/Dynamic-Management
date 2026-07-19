<#
.SYNOPSIS
    查看系统状态 - Docker 模式
.DESCRIPTION
    查看设备信息动态管理系统的运行状态
#>

param([switch]$Help)

if ($Help) {
    Write-Output "查看系统运行状态"
    exit
}

Write-Output ""
Write-Info "========================================="
Write-Info "  系统状态"
Write-Info "========================================="
Write-Output ""

# 检查 Docker
try {
    docker --version | Out-Null
} catch {
    Write-Error "Docker 未安装或未启动！"
    exit 1
}

# 服务状态
Write-Info "服务状态:"
docker-compose ps
Write-Output ""

# 资源使用情况
Write-Info "资源使用情况:"
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
Write-Output ""

# 日志统计
Write-Info "最近的日志:"
Write-Output "使用 'docker-compose logs -f [service-name]' 查看详细日志"
Write-Output ""

# 获取本机 IP
$localIP = Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -notlike "127.*" } | Select-Object -First 1 -ExpandProperty IPAddress

Write-Info "访问地址:"
Write-Output "  本机: http://localhost:5173"
Write-Output "  局域网: http://${localIP}:5173"
Write-Output ""
