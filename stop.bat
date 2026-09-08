@echo off
setlocal
title SmartGift - Stop Servers
cd /d "%~dp0"

echo ============================================================
echo   Stopping SmartGift Servers: Ports 5173, 5175, 5180
echo ============================================================
echo.

set "_KILLED=0"

for %%P in (5173 5175 5180) do (
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr /R /C:":%%P .*LISTENING"') do (
        echo Stopping server on port %%P [PID %%a]
        taskkill /F /PID %%a >nul 2>&1
        set "_KILLED=1"
    )
)

if "%_KILLED%"=="1" (
    echo.
    echo [OK] Servers stopped successfully.
) else (
    echo.
    echo [INFO] No active servers found on ports 5173, 5175, or 5180.
)

ping 127.0.0.1 -n 2 >nul
exit /b 0
