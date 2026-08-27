@echo off
REM ia-dev-toolkit — Comando global para Windows
REM
REM Este script se instala en %LOCALAPPDATA%\ia-dev-toolkit\bin\
REM y debe estar en el PATH del usuario

set PYTHON_CMD=python3
where python3 >nul 2>&1 || set PYTHON_CMD=python

set INSTALLER_PATH=%LOCALAPPDATA%\ia-dev-toolkit\repo\INSTALACION\instalar.py

if exist "%INSTALLER_PATH%" (
    %PYTHON_CMD% "%INSTALLER_PATH%" %*
) else (
    echo ❌ Error: No se encontró el instalador de ia-dev-toolkit
    echo    Ruta esperada: %INSTALLER_PATH%
    echo.
    echo    Para reinstalar, ejecuta:
    echo    irm https://github.com/JavierDevCol/ia-dev-toolkit/main/INSTALACION/bootstrap/install.ps1 ^| iex
    exit /b 1
)
