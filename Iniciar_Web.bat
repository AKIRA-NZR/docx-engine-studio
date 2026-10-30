@echo off
title DOCX Engine Studio — Servidor Web
cd /d "%~dp0"

echo =====================================================
echo   Iniciando DOCX Engine Studio (React + FastAPI)
echo   Acesse no navegador: http://127.0.0.1:8000
echo =====================================================

start "" "http://127.0.0.1:8000"

set "PY_EXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
if exist "%PY_EXE%" (
    "%PY_EXE%" api_server.py
) else (
    python api_server.py
)

pause
