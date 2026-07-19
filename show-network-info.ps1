<#
.SYNOPSIS
    查看本机局域网 IP 和端口信息
.DESCRIPTION
    显示本机 IP 地址和系统端口监听状态
#>

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Output ""
Write-Info "========================================="
Write-Info "  网络信息"
Write-Info "========================================="
Write-Output ""

# 1. IP 地址
Write-Info "1. 本机 IP 地址:"
$adapters = Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -notlike "127.*" -and $_.IPAddress -ne "169.254.*" -and $_.PrefixOrigin -ne "WellKnown" }

foreach ($adapter in $adapters) {
    Write-Output "  接口: $($adapter.InterfaceAlias)"
    Write-Output "  IP: $($adapter.IPAddress)"
    Write-Output "  子网: $($adapter.PrefixLength) 位"
    Write-Output ""

    # 计算子网范围
    $ipParts = $adapter.IPAddress.Split('.')
    $prefixLength = $adapter.PrefixLength

    if ($prefixLength -le 24) {
        $subnet = "$($ipParts[0]).$($ipParts[1]).$($ipParts[2]).0/24"
    } else {
        $subnet = "$($adapter.IPAddress)/$prefixLength"
    }

    Write-Info "  局域网地址范围: $subnet"
    Write-Output ""
}

# 2. 端口监听
Write-Info "2. 系统端口监听状态:"

$ports = @(
    @{ Port = 5173; Name = "前端"; Protocol = "HTTP" },
    @{ Port = 8000; Name = "后端 API"; Protocol = "HTTP" },
    @{ Port = 5432; Name = "PostgreSQL"; Protocol = "TCP" },
    @{ Port = 6379; Name = "Redis"; Protocol = "TCP" }
)

foreach ($portInfo in $ports) {
    $connection = Get-NetTCPConnection -LocalPort $portInfo.Port -ErrorAction SilentlyContinue
    if ($connection) {
        $address = $connection.LocalAddress
        $state = $connection.State

        if ($address -eq "0.0.0.0") {
            Write-Success "$($portInfo.Name) - 端口 $($portInfo.Port) ($($portInfo.Protocol)): 监听所有接口"
        } else {
            Write-Info "$($portInfo.Name) - 端口 $($portInfo.Port) ($($portInfo.Protocol)): 监听 $address"
        }
    } else {
        Write-Warning "$($portInfo.Name) - 端口 $($portInfo.Port) ($($portInfo.Protocol)): 未监听"
    }
}
Write-Output ""

# 3. 访问地址
Write-Info "3. 访问地址:"
$localIP = Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -notlike "127.*" } | Select-Object -First 1 -ExpandProperty IPAddress
Write-Output "  本机访问:"
Write-Output "    前端: http://localhost:5173"
Write-Output "    API:  http://localhost:8000"
Write-Output ""
Write-Output "  局域网访问（其他设备）:"
Write-Output "    前端: http://${localIP}:5173"
Write-Output "    API:  http://${localIP}:8000"
Write-Output ""
Write-Info "  请确保:"
Write-Output "    1. 其他设备与本机在同一局域网"
Write-Output "    2. 防火墙已开放相应端口（运行 .\setup-firewall.ps1）"
Write-Output "    3. 服务已启动（运行 .\start-system.ps1）"
Write-Output ""
