#!/bin/bash
# Script para iniciar el servidor backend

# Activar entorno virtual si existe
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Ejecutar servidor
python main.py
