@echo off
title DOCX Engine Studio
cd /d "%~dp0"

set "PY_EXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
if exist "%PY_EXE%" (
    "%PY_EXE%" app_gui.py
) else (
    python app_gui.py
)

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Ocorreu um erro ao iniciar. Pressione qualquer tecla para fechar.
    pause >nul
)
