@echo off
chcp 65001 >nul
echo [1/2] 启动后端 (uvicorn :8000) ...
start "study-backend" cmd /c "cd /d %~dp0backend && ..\tools\python\python.exe -m uvicorn app.main:app --port 8000"
echo [2/2] 启动前端 (vite :5173) ...
start "study-frontend" cmd /c "cd /d %~dp0frontend && node node_modules\vite\bin\vite.js"
echo 打开浏览器访问 http://127.0.0.1:5173
