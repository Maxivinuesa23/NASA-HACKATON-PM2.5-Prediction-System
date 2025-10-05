@echo off
title NASA HACKATHON - Frontend React
color 0B

echo ================================================================
echo   🌐 NASA HACKATHON - FRONTEND REACT
echo ================================================================

echo 📁 Navegando a carpeta FrontEnd...
cd FrontEnd

echo 📦 Instalando dependencias (si es necesario)...
npm install

echo 🚀 Iniciando servidor React...
echo 💡 Presiona Ctrl+C para detener
echo 🌐 Frontend: http://localhost:3000
echo.

npm run dev

echo.
echo 🛑 Frontend detenido
pause