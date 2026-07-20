@echo off
title Shorts Downloader - Local Server
color 0A
echo.
echo  ============================================
echo    Shorts Downloader - Local Network Server
echo  ============================================
echo.
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /C:"IPv4 Address"') do (
    set LOCAL_IP=%%a
    goto :found
)
:found
set LOCAL_IP=%LOCAL_IP: =%
echo  [*] Starting server...
echo.
echo  ============================================
echo   ACCESS FROM ANY DEVICE ON YOUR WIFI:
echo.
echo   Open this URL on Phone / Laptop / PC:
echo.
echo     http://%LOCAL_IP%:8000
echo.
echo   (Make sure all devices are on same WiFi)
echo  ============================================
echo.
echo  Press Ctrl+C to stop the server.
echo.
python -m uvicorn api.index:app --host 0.0.0.0 --port 8000 --reload
pause
