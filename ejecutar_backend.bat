@echo off
title NASA HACKATHON - Backend Server
color 0A

echo ================================================================
echo   🚀 NASA HACKATHON - BACKEND SERVER
echo ================================================================

echo 🔧 Activando entorno virtual...
call .venv\Scripts\activate.bat

echo 🌐 Iniciando servidor Flask...
echo 💡 Presiona Ctrl+C para detener
echo 🌐 Servidor: http://localhost:5000
echo.

.venv\Scripts\python.exe app.py

echo.
echo 🛑 Servidor detenido
pause