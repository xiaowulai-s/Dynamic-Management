@echo off
title Equipment Management System - Deploy
color 0A

cd /d "%~dp0"

echo.
echo ============================================================
echo   Equipment Management System - One-Click Deploy
echo ============================================================
echo.

REM ===== 1. Check Docker =====
echo [1/5] Checking Docker...
docker info >nul 2>&1
if errorlevel 1 goto :docker_failed
echo       Docker is ready OK
echo.
goto :docker_ok

:docker_failed
echo.
echo [ERROR] Docker is not running or not installed!
echo.
echo Please do one of the following:
echo   1. Start Docker Desktop - search in Start Menu
echo   2. If not installed, download from docker.com
echo.
echo Run this script again after Docker is started.
echo.
pause
exit /b 1

:docker_ok

REM ===== 2. Check frontend dist =====
echo [2/5] Checking frontend build...
if not exist "frontend\dist\index.html" goto :build_frontend
echo       dist exists, skip build OK
echo.
goto :start_services

:build_frontend
echo       dist not found, building frontend...
pushd frontend
where npx >nul 2>&1
if errorlevel 1 goto :no_node
if not exist "node_modules" goto :npm_install
goto :do_build

:npm_install
echo       Installing dependencies...
call npm install

:do_build
echo       Building for production...
call npx vite build
if errorlevel 1 goto :build_failed
popd
echo       Frontend build done OK
echo.
goto :start_services

:no_node
echo [ERROR] Node.js not found, cannot build frontend.
echo Please install Node.js 18+ from nodejs.org
pause
exit /b 1

:build_failed
echo [ERROR] Frontend build failed!
pause
exit /b 1

:start_services

REM ===== 3. Start services =====
echo [3/5] Starting Docker services...
docker compose up -d postgres redis backend nginx
if errorlevel 1 goto :start_failed
echo       Services started OK
echo.

REM ===== bcrypt version self-check (fix passlib compatibility) =====
echo      Checking bcrypt version...
for /f "tokens=*" %%v in ('docker exec equipment-backend pip show bcrypt 2^>nul ^| findstr "Version"') do set "BCRYPT_VER=%%v"
echo %BCRYPT_VER% | findstr "5.0" >nul
if not errorlevel 1 (
    echo      [WARN] bcrypt 5.0 detected, downgrading to 4.0.1...
    docker exec equipment-backend pip install "bcrypt==4.0.1" -q
    docker restart equipment-backend >nul 2>&1
    echo      bcrypt fixed, backend restarted OK
)
echo.

goto :wait_ready

:start_failed
echo [ERROR] Failed to start services!
echo Please check docker-compose.yml
pause
exit /b 1

:wait_ready

REM ===== 4. Wait for ready =====
echo [4/5] Waiting for services to be ready...
set /a tries=0

:wait_loop
set /a tries+=1
curl -s -o nul -w "%%{http_code}" http://127.0.0.1:9000/ > "%TEMP%\eq_status.txt" 2>nul
set /p code=<"%TEMP%\eq_status.txt"
if "%code%"=="200" goto :ready
if %tries% geq 30 goto :ready_warn
timeout /t 2 /nobreak >nul
goto :wait_loop

:ready_warn
echo       [WARN] Services are slow, will try to open anyway...
goto :ready

:ready
echo       Services are ready OK
echo.

REM ===== 5. Show access URLs =====
echo [5/5] Getting access URLs...
echo.
echo ============================================================
echo   Deploy Success!
echo ============================================================
echo.
echo   Access URLs:
echo     http://127.0.0.1:9000
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
    for /f "tokens=* delims= " %%b in ("%%a") do (
        echo     http://%%b:9000
    )
)
echo.
echo   Default Accounts:
echo     Super Admin   root / root123
echo     Admin         admin / admin123
echo     Normal User   testuser / admin123
echo.
echo   Commands:
echo     Status:  docker compose ps
echo     Logs:    docker compose logs -f
echo     Stop:    run Stop-Service.bat
echo.
echo ============================================================
echo.

REM Open browser
start "" "http://127.0.0.1:9000"

echo Browser opened. If not, open the URL above manually.
echo.
echo This window can be closed. Services run in background.
echo.
pause
