@echo off
echo Starting AirCast (AQI) Backend...
start "Streamlit-Backend" cmd /c "streamlit run app.py"

echo Starting SkyPlus (AQI) Frontend...
cd aqi-frontend
start "Vite-Frontend" cmd /c "npm run dev"

echo.
echo Buffering... Services should be up in a few seconds.
echo Backend: http://localhost:8501
echo Frontend: http://localhost:5173
pause
