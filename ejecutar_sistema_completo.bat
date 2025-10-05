@echo off
title NASA HACKATHON - Sistema Completo
color 0A

echo ================================================================
echo   🚀 NASA HACKATHON - PM2.5 PREDICTION SYSTEM
echo   🌐 Iniciando Frontend y Backend
echo ================================================================

echo 🔧 Activando entorno virtual Python...
call .venv\Scripts\activate.bat

echo 🚀 Iniciando Backend (Flask)...
start "Backend Server" cmd /k ".venv\Scripts\python.exe app.py"

echo ⏳ Esperando 3 segundos...
timeout /t 3 > nul

echo 📁 Navegando a FrontEnd...
cd FrontEnd

echo 📦 Verificando dependencias...
if not exist "node_modules" (
    echo 📦 Instalando dependencias...
    npm install
)

echo 🌐 Iniciando Frontend (React)...
start "Frontend React" cmd /k "npm run dev"

echo.
echo ✅ Sistema iniciado:
echo    🔙 Backend: http://localhost:5000
echo    🌐 Frontend: http://localhost:3000
echo.
echo 💡 Para detener: cierra las ventanas del Backend y Frontend
pause