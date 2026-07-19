@echo off
title Equipment Management System - Stop
color 0E

cd /d "%~dp0"

echo.
echo ============================================================
echo   Stop Equipment Management System - All Services
echo ============================================================
echo.

docker compose down
if errorlevel 1 (
    echo [ERROR] Stop failed. Run manually: docker compose down
    pause
    exit /b 1
)

echo.
echo All services stopped.
echo.
pause
