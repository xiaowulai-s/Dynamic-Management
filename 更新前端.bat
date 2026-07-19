@echo off
title Equipment Management System - Update Frontend
color 0B

cd /d "%~dp0"

echo.
echo ============================================================
echo   Update Frontend to Port 9000
echo ============================================================
echo.

REM ===== 1. Check Node.js =====
echo [1/4] Checking Node.js...
where npx >nul 2>&1
if errorlevel 1 goto :no_node
echo       Node.js ready OK
echo.

REM ===== 2. Build frontend =====
echo [2/4] Building frontend for production...
pushd frontend
if not exist "node_modules" goto :install_deps
goto :do_build

:install_deps
echo       Installing dependencies first...
call npm install
if errorlevel 1 goto :install_failed

:do_build
echo       Running vite build...
call npx vite build
if errorlevel 1 goto :build_failed
popd
echo       Build done OK
echo.
goto :restart_nginx

:no_node
echo [ERROR] Node.js not found.
echo Please install Node.js 18+ from nodejs.org
pause
exit /b 1

:install_failed
echo [ERROR] npm install failed!
popd
pause
exit /b 1

:build_failed
echo [ERROR] vite build failed!
popd
pause
exit /b 1

:restart_nginx

REM ===== 3. Restart nginx to pick up new dist =====
echo [3/4] Restarting nginx container...
docker restart equipment-nginx >nul 2>&1
if errorlevel 1 goto :nginx_failed
echo       nginx restarted OK
echo.
goto :verify

:nginx_failed
echo [WARN] nginx restart failed, trying docker compose up...
docker compose up -d nginx
if errorlevel 1 goto :compose_failed
echo       nginx started via compose OK
echo.
goto :verify

:compose_failed
echo [ERROR] Failed to start nginx!
echo Please run: docker compose up -d nginx
pause
exit /b 1

:verify

REM ===== 4. Verify access =====
echo [4/4] Verifying access on port 9000...
set /a tries=0

:verify_loop
set /a tries+=1
curl -s -o nul -w "%%{http_code}" http://127.0.0.1:9000/ > "%TEMP%\eq_verify.txt" 2>nul
set /p vcode=<"%TEMP%\eq_verify.txt"
if "%vcode%"=="200" goto :verify_ok
if %tries% geq 15 goto :verify_timeout
timeout /t 2 /nobreak >nul
goto :verify_loop

:verify_timeout
echo [WARN] Cannot reach 9000, please check nginx manually.
pause
exit /b 1

:verify_ok
echo       Access verified OK - HTTP 200
echo.
echo ============================================================
echo   Update Success!
echo ============================================================
echo.
echo   New frontend is live on:
echo     http://127.0.0.1:9000
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
    for /f "tokens=* delims= " %%b in ("%%a") do (
        echo     http://%%b:9000
    )
)
echo.
echo   Tip: Hard refresh browser with Ctrl+F5 to clear cache.
echo.
echo ============================================================
echo.
pause
