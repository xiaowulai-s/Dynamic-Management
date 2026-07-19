@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ============================================================
echo   迁移导出工具 - 设备信息动态管理系统
echo   在【当前服务器】运行，导出数据供新服务器使用
echo ============================================================
echo.

REM 检查 Docker
docker info >nul 2>&1
if errorlevel 1 (
    echo [错误] Docker 未运行，请先启动 Docker Desktop
    pause
    exit /b 1
)

REM 检查 postgres 容器
docker ps --format "{{.Names}}" | findstr equipment-postgres >nul
if errorlevel 1 (
    echo [错误] equipment-postgres 容器未运行，请先启动系统
    pause
    exit /b 1
)

set EXPORT_DIR=迁移包
set EXPORT_TS=%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%
set EXPORT_TS=%EXPORT_TS: =0%

echo [1/5] 创建导出目录...
if exist "%EXPORT_DIR%" rmdir /s /q "%EXPORT_DIR%"
mkdir "%EXPORT_DIR%"
mkdir "%EXPORT_DIR%\data"
echo       目录已创建: %EXPORT_DIR%
echo.

echo [2/5] 导出数据库数据（pg_dump）...
docker exec equipment-postgres pg_dump -U postgres -d equipment_db -Fc -f /tmp/dump.pgc
if errorlevel 1 (
    echo [错误] 数据库导出失败
    pause
    exit /b 1
)
docker cp equipment-postgres:/tmp/dump.pgc "%EXPORT_DIR%\data\equipment_db.dump"
docker exec equipment-postgres rm /tmp/dump.pgc
echo       数据库已导出: data\equipment_db.dump
echo.

echo [3/5] 打包上传文件（uploads）...
if exist uploads (
    echo       正在打包 uploads 目录...
    powershell -Command "Compress-Archive -Path 'uploads\*' -DestinationPath '%EXPORT_DIR%\data\uploads.zip' -Force"
    echo       上传文件已打包: data\uploads.zip
) else (
    echo       [提示] uploads 目录不存在，跳过
)
echo.

echo [4/5] 复制部署必需文件...
REM 复制 docker-compose
copy docker-compose.yml "%EXPORT_DIR%\" >nul
REM 复制 nginx 配置
copy nginx.prod.conf "%EXPORT_DIR%\" >nul
REM 复制后端代码（含 Dockerfile、requirements.txt、app 目录）
xcopy backend "%EXPORT_DIR%\backend\" /E /I /Q /Y >nul
REM 复制前端源码（新机器需要重新构建）
xcopy frontend "%EXPORT_DIR%\frontend\" /E /I /Q /Y >nul
REM 复制部署脚本
copy 启动系统.bat "%EXPORT_DIR%\" >nul
copy 更新前端.bat "%EXPORT_DIR%\" >nul
copy 停止服务.bat "%EXPORT_DIR%\" >nul
REM 复制后端 init.sql（首次初始化用）
if exist backend\init.sql copy backend\init.sql "%EXPORT_DIR%\backend\" >nul
echo       代码与配置已复制
echo.

echo [5/5] 生成迁移说明...
(
echo # 设备信息动态管理系统 - 迁移包
echo.
echo ## 导出时间
echo %EXPORT_TS%
echo.
echo ## 包含内容
echo - data\equipment_db.dump  数据库备份（PostgreSQL 自定义格式^）
echo - data\uploads.zip        上传文件压缩包
echo - docker-compose.yml      服务编排配置
echo - nginx.prod.conf         Nginx 配置
echo - backend\                后端代码（含 Dockerfile^）
echo - frontend\               前端源码（需在新机器构建^）
echo - 启动系统.bat            启动脚本
echo - 更新前端.bat            前端构建脚本
echo.
echo ## 在新服务器上的部署步骤
echo 1. 安装 Docker Desktop for Windows
echo 2. 将整个"迁移包"文件夹拷贝到新服务器（建议 D:\Dynamic-Management^）
echo 3. 双击运行"迁移-导入.bat"，等待部署完成
echo 4. 浏览器访问 http://新服务器IP:9000
echo.
echo ## 默认账号
echo - root / root123 （超级管理员^）
echo - admin_test / 123456 （管理员^）
echo - user_test / 123456 （普通用户^）
) > "%EXPORT_DIR%\迁移说明.md"
echo       说明文档已生成: 迁移说明.md
echo.

echo ============================================================
echo   导出完成！
echo.
echo   迁移包位置: %CD%\%EXPORT_DIR%
echo.
echo   下一步:
echo   1. 将整个 "%EXPORT_DIR%" 文件夹拷贝到新服务器
echo   2. 在新服务器上运行"迁移-导入.bat"
echo ============================================================
echo.

REM 显示导出包大小
powershell -Command "$size = (Get-ChildItem -Recurse '%EXPORT_DIR%' | Measure-Object -Property Length -Sum).Sum / 1MB; Write-Host ('迁移包总大小: ' + [math]::Round($size,2) + ' MB')"

echo.
pause
