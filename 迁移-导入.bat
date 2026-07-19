@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ============================================================
echo   迁移导入工具 - 设备信息动态管理系统
echo   在【新服务器】运行，部署系统并导入数据
echo ============================================================
echo.

REM 检查 Docker
docker info >nul 2>&1
if errorlevel 1 (
    echo [错误] Docker 未运行！
    echo.
    echo 请先安装并启动 Docker Desktop for Windows:
    echo   1. 下载: https://www.docker.com/products/docker-desktop/
    echo   2. 安装后启动 Docker Desktop
    echo   3. 等待右下角 Docker 图标变为绿色（运行中）
    echo   4. 再次运行本脚本
    echo.
    pause
    exit /b 1
)

echo [1/7] 检查项目文件...
if not exist docker-compose.yml (
    echo [错误] 未找到 docker-compose.yml，请确保在迁移包根目录运行本脚本
    pause
    exit /b 1
)
if not exist data\equipment_db.dump (
    echo [错误] 未找到 data\equipment_db.dump，迁移包不完整
    pause
    exit /b 1
)
echo       文件检查通过
echo.

echo [2/7] 构建 Docker 镜像并启动服务...
echo       （首次启动需要拉取 postgres/redis/nginx 镜像，可能需要 5-15 分钟）
echo.
docker compose up -d --build
if errorlevel 1 (
    echo [错误] 服务启动失败，请检查上方错误信息
    pause
    exit /b 1
)
echo.

echo [3/7] 等待 PostgreSQL 就绪...
set READY=0
for /L %%i in (1,1,30) do (
    docker exec equipment-postgres pg_isready -U postgres >nul 2>&1
    if not errorlevel 1 (
        set READY=1
        echo       PostgreSQL 已就绪
        goto :ready
    )
    echo       等待中... %%i/30
    timeout /t 2 /nobreak >nul
)
:ready
if "!READY!"=="0" (
    echo [错误] PostgreSQL 启动超时
    pause
    exit /b 1
)
echo.

echo [4/7] 导入数据库数据...
echo       （先清空新库，再导入备份数据）
REM 删除新库并重建，确保导入干净数据
docker exec equipment-postgres psql -U postgres -d postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='equipment_db' AND pid <> pg_backend_pid();" >nul 2>&1
docker exec equipment-postgres psql -U postgres -d postgres -c "DROP DATABASE IF EXISTS equipment_db;" >nul 2>&1
docker exec equipment-postgres psql -U postgres -d postgres -c "CREATE DATABASE equipment_db OWNER postgres;" >nul 2>&1
REM 拷贝备份文件进容器
docker cp data\equipment_db.dump equipment-postgres:/tmp/dump.pgc
docker exec equipment-postgres pg_restore -U postgres -d equipment_db --no-owner --no-privileges /tmp/dump.pgc
if errorlevel 1 (
    echo [警告] 数据库导入出现警告，通常可忽略（已存在的表/序列）
)
docker exec equipment-postgres rm /tmp/dump.pgc
echo       数据库导入完成
echo.

echo [5/7] 还原上传文件...
if exist data\uploads.zip (
    if not exist uploads mkdir uploads
    echo       正在解压 uploads...
    powershell -Command "Expand-Archive -Path 'data\uploads.zip' -DestinationPath 'uploads' -Force"
    echo       上传文件已还原
) else (
    echo       [提示] 无上传文件压缩包，跳过
)
echo.

echo [6/7] 构建前端...
echo       （需要 Node.js 环境，如果新服务器未装 Node.js 将跳过）
where node >nul 2>&1
if errorlevel 1 (
    echo       [警告] 未检测到 Node.js，跳过前端构建
    echo       [提示] 如果 frontend\dist 已存在，可直接使用；否则需安装 Node.js 后运行"更新前端.bat"
) else (
    call 更新前端.bat
)
echo.

echo [7/7] 重启所有服务使数据生效...
docker compose restart
timeout /t 5 /nobreak >nul
echo       服务已重启
echo.

echo ============================================================
echo   部署完成！
echo.
echo   访问地址:
echo.

REM 显示本机 IP
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr "IPv4"') do (
    set IP=%%a
    set IP=!IP: =!
    echo     http://!IP!:9000
)

echo     http://127.0.0.1:9000
echo.
echo   默认账号:
echo     root / root123        （超级管理员）
echo     admin_test / 123456   （管理员）
echo     user_test / 123456    （普通用户）
echo.
echo   提示:
echo   - 首次访问请用 Ctrl+F5 强制刷新浏览器
echo   - 如需开机自启，将"启动系统.bat"加入启动文件夹
echo ============================================================
echo.
pause
