@echo off
echo 🚀 INICIANDO SISTEMA COMPLETO DE CALIDAD DEL AIRE
echo ==============================================

echo.
echo 📍 Iniciando Backend...
cd /d "C:\Users\maxi-\Desktop\Hackaton\ppp"
start "Backend - Calidad del Aire" /D "C:\Users\maxi-\Desktop\Hackaton\ppp" cmd /k "C:/Users/maxi-/Desktop/Hackaton/ppp/.venv/Scripts/python.exe app.py"

echo.
echo ⏳ Esperando que el backend inicie...
timeout /t 5 /nobreak >nul

echo.
echo 💻 Iniciando Frontend...
cd /d "C:\Users\maxi-\Desktop\Hackaton\ppp\FrontEnd"
start "Frontend - React" /D "C:\Users\maxi-\Desktop\Hackaton\ppp\FrontEnd" cmd /k "npm run dev"

echo.
echo ✅ AMBOS SERVICIOS INICIADOS
echo.
echo 🌐 URLs:
echo    Backend:  http://localhost:5000
echo    Frontend: http://localhost:5173
echo.
echo 📋 Para ver el sistema funcionando:
echo    1. Espera 10-15 segundos que ambos servicios inicien
echo    2. Abre http://localhost:5173 en tu navegador
echo    3. Verás el widget de calidad del aire funcionando
echo.
echo 🎯 El sistema incluye:
echo    ✅ 7 ciudades con datos reales
echo    ✅ Predicciones con IA
echo    ✅ Datos meteorológicos
echo    ✅ Estado del servidor en tiempo real
echo.
pause