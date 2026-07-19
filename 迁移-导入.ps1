# 迁移导入工具 - 设备信息动态管理系统
# 在【新服务器】运行，部署系统并导入数据
$ErrorActionPreference = 'Continue'
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  迁移导入工具 - 设备信息动态管理系统" -ForegroundColor Cyan
Write-Host "  在新服务器运行，部署系统并导入数据" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# 检查 Docker
$dockerInfo = docker info 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[错误] Docker 未运行！" -ForegroundColor Red
    Write-Host ""
    Write-Host "请先安装并启动 Docker Desktop for Windows:" -ForegroundColor White
    Write-Host "  1. 下载: https://www.docker.com/products/docker-desktop/" -ForegroundColor White
    Write-Host "  2. 安装后启动 Docker Desktop" -ForegroundColor White
    Write-Host "  3. 等待右下角 Docker 图标变为绿色（运行中）" -ForegroundColor White
    Write-Host "  4. 再次运行本脚本" -ForegroundColor White
    Write-Host ""
    Read-Host "按回车键退出"
    exit 1
}

Write-Host "[1/7] 检查项目文件..." -ForegroundColor Yellow
if (-not (Test-Path "docker-compose.yml")) {
    Write-Host "[错误] 未找到 docker-compose.yml，请确保在迁移包根目录运行本脚本" -ForegroundColor Red
    Read-Host "按回车键退出"
    exit 1
}
if (-not (Test-Path "data\equipment_db.dump")) {
    Write-Host "[错误] 未找到 data\equipment_db.dump，迁移包不完整" -ForegroundColor Red
    Read-Host "按回车键退出"
    exit 1
}
Write-Host "      文件检查通过"
Write-Host ""

Write-Host "[2/7] 构建 Docker 镜像并启动服务..." -ForegroundColor Yellow
Write-Host "      （首次启动需要拉取 postgres/redis/nginx 镜像，可能需要 5-15 分钟）"
Write-Host ""
docker compose up -d --build
if ($LASTEXITCODE -ne 0) {
    Write-Host "[错误] 服务启动失败，请检查上方错误信息" -ForegroundColor Red
    Read-Host "按回车键退出"
    exit 1
}
Write-Host ""

Write-Host "[3/7] 等待 PostgreSQL 就绪..." -ForegroundColor Yellow
$ready = $false
for ($i = 1; $i -le 30; $i++) {
    docker exec equipment-postgres pg_isready -U postgres 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        $ready = $true
        Write-Host "      PostgreSQL 已就绪"
        break
    }
    Write-Host "      等待中... $i/30"
    Start-Sleep -Seconds 2
}
if (-not $ready) {
    Write-Host "[错误] PostgreSQL 启动超时" -ForegroundColor Red
    Read-Host "按回车键退出"
    exit 1
}
Write-Host ""

Write-Host "[4/7] 导入数据库数据..." -ForegroundColor Yellow
Write-Host "      （先清空新库，再导入备份数据）"
# 终止现有连接
docker exec equipment-postgres psql -U postgres -d postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='equipment_db' AND pid <> pg_backend_pid();" 2>&1 | Out-Null
# 删除并重建数据库
docker exec equipment-postgres psql -U postgres -d postgres -c "DROP DATABASE IF EXISTS equipment_db;" 2>&1 | Out-Null
docker exec equipment-postgres psql -U postgres -d postgres -c "CREATE DATABASE equipment_db OWNER postgres;" 2>&1 | Out-Null
# 拷贝备份文件进容器并还原
docker cp "data\equipment_db.dump" equipment-postgres:/tmp/dump.pgc
docker exec equipment-postgres pg_restore -U postgres -d equipment_db --no-owner --no-privileges /tmp/dump.pgc 2>&1 | Out-Null
docker exec equipment-postgres rm /tmp/dump.pgc 2>&1 | Out-Null
# 验证导入结果
$tableCount = docker exec equipment-postgres psql -U postgres -d equipment_db -t -c "SELECT count(*) FROM information_schema.tables WHERE table_schema='public';" 2>&1
$tableCount = $tableCount.Trim()
Write-Host "      数据库导入完成（表数量: $tableCount）"
Write-Host ""

Write-Host "[5/7] 还原上传文件..." -ForegroundColor Yellow
if (Test-Path "data\uploads.zip") {
    if (-not (Test-Path "uploads")) { New-Item -ItemType Directory -Path "uploads" | Out-Null }
    Write-Host "      正在解压 uploads..."
    Expand-Archive -Path "data\uploads.zip" -DestinationPath "uploads" -Force
    Write-Host "      上传文件已还原"
} else {
    Write-Host "      [提示] 无上传文件压缩包，跳过" -ForegroundColor DarkYellow
}
Write-Host ""

Write-Host "[6/7] 检查前端构建产物..." -ForegroundColor Yellow
if (Test-Path "frontend\dist\index.html") {
    Write-Host "      前端 dist 已存在，无需构建"
} else {
    $nodeExists = Get-Command node -ErrorAction SilentlyContinue
    if ($nodeExists) {
        Write-Host "      正在构建前端..."
        & ".\更新前端.bat"
    } else {
        Write-Host "      [警告] 未检测到 Node.js 且无 dist 产物" -ForegroundColor DarkYellow
        Write-Host "      请安装 Node.js 18+ 后运行 更新前端.bat" -ForegroundColor DarkYellow
    }
}
Write-Host ""

Write-Host "[7/7] 重启所有服务使数据生效..." -ForegroundColor Yellow
docker compose restart 2>&1 | Out-Null
Start-Sleep -Seconds 5
Write-Host "      服务已重启"
Write-Host ""

Write-Host "============================================================" -ForegroundColor Green
Write-Host "  部署完成！" -ForegroundColor Green
Write-Host ""
Write-Host "  访问地址:" -ForegroundColor White
$ips = Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -ne '127.0.0.1' -and $_.PrefixOrigin -eq 'Dhcp' } | Select-Object -ExpandProperty IPAddress -Unique
foreach ($ip in $ips) {
    Write-Host "    http://${ip}:9000" -ForegroundColor Cyan
}
Write-Host "    http://127.0.0.1:9000" -ForegroundColor Cyan
Write-Host ""
Write-Host "  默认账号:" -ForegroundColor White
Write-Host "    root / root123        （超级管理员）" -ForegroundColor White
Write-Host "    admin_test / 123456   （管理员）" -ForegroundColor White
Write-Host "    user_test / 123456    （普通用户）" -ForegroundColor White
Write-Host ""
Write-Host "  提示:" -ForegroundColor Yellow
Write-Host "  - 首次访问请用 Ctrl+F5 强制刷新浏览器" -ForegroundColor White
Write-Host "  - 如需开机自启，将 启动系统.bat 加入启动文件夹" -ForegroundColor White
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Read-Host "按回车键退出"
