<#
.SYNOPSIS
    配置 Docker 镜像源
.DESCRIPTION
    配置 Docker 使用国内镜像源加速下载
.NOTES
    需要 Docker Desktop 已安装
#>

param(
    [switch]$Reset,
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
  .\setup-docker-mirror.ps1        # 配置国内镜像源
  .\setup-docker-mirror.ps1 -Reset # 恢复默认设置
  .\setup-docker-mirror.ps1 -Help   # 显示此帮助
"@
    exit
}

Write-Output ""
Write-Info "========================================="
Write-Info "  Docker 镜像源配置"
Write-Info "========================================="
Write-Output ""

# 检查 Docker
Write-Info "检查 Docker..."
try {
    docker --version | Out-Null
    Write-Success "Docker 已安装"
} catch {
    Write-Error "Docker 未安装或未运行"
    exit 1
}

# 查找 Docker Desktop 配置文件
Write-Info "查找 Docker Desktop 配置文件..."

$possiblePaths = @(
    "$env:APPDATA\Docker\settings-store.json",
    "C:\ProgramData\Docker\config\daemon.json",
    "$env:USERPROFILE\AppData\Roaming\Docker\settings-store.json"
)

$configFile = $null
foreach ($path in $possiblePaths) {
    if (Test-Path $path) {
        $configFile = $path
        Write-Success "找到配置文件: $path"
        break
    }
}

if (-not $configFile) {
    Write-Warning "未找到 Docker Desktop 配置文件"
    Write-Info "请使用 Docker Desktop 界面手动配置："
    Write-Output "  1. 打开 Docker Desktop"
    Write-Output "  2. Settings → Docker Engine"
    Write-Output "  3. 添加 registry-mirrors 配置"
    Write-Output ""
    Write-Info "推荐使用以下镜像源："
    Write-Output @"
{
  "registry-mirrors": [
    "https://docker.m.daocloud.io",
    "https://docker.1ms.run",
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com"
  ]
}
"@
    exit 0
}

# 读取配置
Write-Info "读取当前配置..."
try {
    $config = Get-Content $configFile -Raw | ConvertFrom-Json
} catch {
    Write-Warning "配置文件格式错误，创建新配置..."
    $config = @{}
}

if ($Reset) {
    # 恢复默认设置
    Write-Info "恢复默认设置..."
    if ($config.registry-mirrors) {
        $config.PSObject.Properties.Remove("registry-mirrors")
        Write-Success "已删除镜像源配置"
    } else {
        Write-Info "没有镜像源配置需要删除"
    }
} else {
    # 配置镜像源
    $mirrors = @(
        "https://docker.m.daocloud.io",
        "https://docker.1ms.run",
        "https://docker.xuanyuan.me",
        "https://docker.mirrors.ustc.edu.cn",
        "https://hub-mirror.c.163.com"
    )

    Write-Info "配置镜像源..."
    $config | Add-Member -NotePropertyName "registry-mirrors" -NotePropertyValue $mirrors -Force
    Write-Success "已配置 $(@($mirrors).Count) 个镜像源"
}

# 保存配置
Write-Info "保存配置..."
$config | ConvertTo-Json -Depth 10 | Set-Content $configFile -Encoding UTF8
Write-Success "配置已保存"

Write-Output ""
Write-Info "========================================="
Write-Success "  配置完成"
Write-Info "========================================="
Write-Output ""
Write-Info "请重启 Docker Desktop："
Write-Output "  1. 右键点击托盘区的 Docker 图标"
Write-Output "  2. 选择 'Quit Docker Desktop'"
Write-Output "  3. 从开始菜单重新启动 Docker Desktop"
Write-Output ""
Write-Info "重启后测试："
Write-Output "  docker pull hello-world"
Write-Output ""
