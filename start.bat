@echo off
REM Script para iniciar el servidor backend en Windows

REM Activar entorno virtual si existe
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM Ejecutar servidor
python main.py
