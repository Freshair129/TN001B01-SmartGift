@echo off
setlocal
title SmartGift - Server and UI Launcher

:: Set working directory to script location
cd /d "%~dp0"

echo ============================================================
echo   SmartGift Launcher - One-Click Server and UI
echo ============================================================
echo.

call :start_backend
call :start_ui

exit /b 0

:start_backend
netstat -ano | findstr /R /C:":5180 .*LISTENING" >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo [OK] Backend server [sv] is already running on http://localhost:5180
    echo.
    exit /b 0
)

echo [*] Starting SmartGift Backend Server [sv] on port 5180...
set "_PY=python"
where py >nul 2>&1 && set "_PY=py -3"

start "SmartGift Backend Server [Port 5180]" /D "%~dp0" cmd /k "title SmartGift Backend Server [Port 5180] && echo ============================================================ && echo   SmartGift Backend Server [Port 5180] && echo   API: http://localhost:5180/api/catalog && echo ============================================================ && echo. && %_PY% -u public\serve.py"

ping 127.0.0.1 -n 2 >nul
echo [OK] Backend server launched on http://localhost:5180
echo.
exit /b 0

:start_ui
set "_UI_DIR=%~dp0..\web-ui-smg"
if exist "%_UI_DIR%\package.json" (
    echo [*] Starting Web UI from %_UI_DIR%...
    cd /d "%_UI_DIR%"
    call "%_UI_DIR%\run.bat"
) else (
    echo [INFO] web-ui-smg not found. Opening backend catalog at http://localhost:5180
    start "" "http://localhost:5180"
)
exit /b 0
