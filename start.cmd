@echo off
setlocal
cd /d "%~dp0"

echo Starting backend on http://127.0.0.1:8000 ...
start "Ruankao Backend" /min /D "%~dp0backend" "%~dp0tools\python\python.exe" -m uvicorn app.main:app --port 8000

echo Starting frontend on http://127.0.0.1:5173 ...
start "Ruankao Frontend" /min /D "%~dp0frontend" node.exe node_modules\vite\bin\vite.js --host 127.0.0.1

ping 127.0.0.1 -n 4 >nul
if not defined RUANKAO_NO_BROWSER start "Ruankao Study" http://127.0.0.1:5173
echo Started. You may close this window.
endlocal
