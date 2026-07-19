<#
.SYNOPSIS
    一键部署脚本 - 本地模式
.DESCRIPTION
    自动部署设备信息动态管理系统（本地模式，不使用 Docker）
.NOTES
    需要手动安装 Python 3.11、Node.js 18、PostgreSQL、Redis
#>

param(
    [switch]$SkipInstall,
    [switch]$SkipDBInit,
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
  .\deploy-local.ps1                # 完整部署
  .\deploy-local.ps1 -SkipInstall   # 跳过依赖安装
  .\deploy-local.ps1 -SkipDBInit    # 跳过数据库初始化
  .\deploy-local.ps1 -Help           # 显示此帮助

注意:
  本地模式需要手动安装以下软件:
    - Python 3.11
    - Node.js 18
    - PostgreSQL 15
    - Redis
"@
    exit
}

Write-Output ""
Write-Info "========================================="
Write-Info "  设备信息动态管理系统 - 本地部署"
Write-Info "========================================="
Write-Output ""

# 检查 Python
Write-Info "检查 Python..."
try {
    $pythonVersion = python --version 2>&1
    Write-Success "Python 已安装: $pythonVersion"
} catch {
    Write-Error "Python 未安装！请先安装 Python 3.11+"
    Write-Output "下载地址: https://www.python.org/downloads/windows/"
    exit 1
}

# 检查 Node.js
Write-Info "检查 Node.js..."
try {
    $nodeVersion = node --version
    Write-Success "Node.js 已安装: $nodeVersion"
} catch {
    Write-Error "Node.js 未安装！请先安装 Node.js 18+"
    Write-Output "下载地址: https://nodejs.org/"
    exit 1
}

# 检查 PostgreSQL
Write-Info "检查 PostgreSQL..."
try {
    $psqlVersion = psql --version 2>&1
    Write-Success "PostgreSQL 已安装: $psqlVersion"
} catch {
    Write-Error "PostgreSQL 未安装！请先安装 PostgreSQL 15"
    Write-Output "下载地址: https://www.postgresql.org/download/windows/"
    exit 1
}

# 检查 Redis
Write-Info "检查 Redis..."
try {
    $redisPing = redis-cli ping 2>&1
    if ($redisPing -match "PONG") {
        Write-Success "Redis 已安装并运行"
    } else {
        throw "Redis not responding"
    }
} catch {
    Write-Warning "Redis 未运行，尝试启动..."
    Start-Process redis-server -ArgumentList "--daemonize yes" -NoNewWindow -Wait
    Start-Sleep -Seconds 2
    Write-Success "Redis 已启动"
}

# 安装 Python 依赖
if (-not $SkipInstall) {
    Write-Info "安装 Python 依赖..."
    Set-Location "$ProjectPath\backend"

    # 检查虚拟环境
    if (-not (Test-Path "venv")) {
        Write-Info "创建 Python 虚拟环境..."
        python -m venv venv
    }

    # 激活虚拟环境
    $venvActivate = "$ProjectPath\backend\venv\Scripts\Activate.ps1"
    & $venvActivate

    # 升级 pip
    Write-Info "升级 pip..."
    python -m pip install --upgrade pip

    # 安装依赖
    Write-Info "安装后端依赖（约需 5-10 分钟）..."
    pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
    if ($LASTEXITCODE -ne 0) {
        Write-Error "依赖安装失败！"
        exit 1
    }
    Write-Success "Python 依赖安装完成"
}

# 安装 Node.js 依赖
if (-not $SkipInstall) {
    Write-Info "安装 Node.js 依赖..."
    Set-Location "$ProjectPath\frontend"
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Error "前端依赖安装失败！"
        exit 1
    }
    Write-Success "Node.js 依赖安装完成"
}

# 初始化数据库
if (-not $SkipDBInit) {
    Write-Info "初始化数据库..."

    # 读取 .env 文件获取数据库配置
    $envContent = Get-Content "$ProjectPath\backend\.env" -Raw
    if ($envContent -match 'POSTGRES_USER=(\S+)') { $dbUser = $Matches[1] }
    if ($envContent -match 'POSTGRES_PASSWORD=(\S+)') { $dbPass = $Matches[1] }
    if ($envContent -match 'POSTGRES_DB=(\S+)') { $dbName = $Matches[1] }

    if (-not $dbUser) { $dbUser = "postgres" }
    if (-not $dbPass) { $dbPass = "password" }
    if (-not $dbName) { $dbName = "equipment_db" }

    Write-Info "数据库配置: 用户=$dbUser, 数据库=$dbName"

    # 设置密码环境变量
    $env:PGPASSWORD = $dbPass

    # 检查数据库是否存在
    $dbExists = psql -U $dbUser -lqt 2>&1 | Select-String "\m$dbName\m"
    if (-not $dbExists) {
        Write-Info "创建数据库..."
        psql -U $dbUser -c "CREATE DATABASE $dbName;"
    } else {
        Write-Success "数据库已存在"
    }

    # 执行初始化脚本
    Write-Info "执行数据库初始化脚本..."
    psql -U $dbUser -d $dbName -f "$ProjectPath\backend\init.sql"
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "数据库初始化可能有问题，请检查"
    } else {
        Write-Success "数据库初始化完成"
    }
}

# 配置环境变量
Write-Info "检查环境变量配置..."
if (-not (Test-Path "$ProjectPath\backend\.env")) {
    Write-Warning ".env 文件不存在，从模板创建..."
    Copy-Item "$ProjectPath\backend\.env.example" "$ProjectPath\backend\.env"
    Write-Error "请编辑 backend\.env 文件，配置数据库密码！"
    Write-Output "文件路径: $ProjectPath\backend\.env"
    exit 1
}

# 显示配置信息
Write-Output ""
Write-Info "========================================="
Write-Success "  部署准备完成！"
Write-Info "========================================="
Write-Output ""
Write-Info "下一步:"
Write-Output "  运行 .\start-system.ps1 启动所有服务"
Write-Output ""
Write-Info "详细配置请查看: LOCAL_DEPLOYMENT_GUIDE.md"
Write-Output ""
