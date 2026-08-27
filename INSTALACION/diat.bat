@echo off
REM diat — IA Dev Toolkit CLI para Windows
REM Ejecuta el instalador Python con los argumentos proporcionados

set SCRIPT_DIR=%~dp0
python "%SCRIPT_DIR%diat" %*
