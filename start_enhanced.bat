@echo off
echo 🌾 कृषि AI सलाहकार - Quick Start
echo ===============================

:: Start Ollama
echo Starting Ollama...
start /min ollama serve
timeout /t 3 /nobreak >nul

:: Start Backend
echo Starting Backend...
cd backend
start /min python server_enhanced.py
timeout /t 5 /nobreak >nul
cd ..

:: Start Frontend
echo Starting Frontend...
cd frontend
echo Clearing cache and starting...
if exist .env.local del .env.local
start npm start
cd ..

echo.
echo 🎉 Services are starting!
echo ========================
echo 🌐 Frontend: http://localhost:3000
echo 📚 Backend: http://localhost:8001/docs
echo.
echo Wait 30 seconds, then open http://localhost:3000
pause