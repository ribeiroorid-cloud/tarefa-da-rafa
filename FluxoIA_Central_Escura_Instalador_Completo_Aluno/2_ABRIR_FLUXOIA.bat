@echo off
chcp 65001 >nul
set "DIR=%USERPROFILE%\Downloads\FluxoIA_CENTRAL_COMPLETA"
set "PY=%DIR%\.venv\Scripts\python.exe"
if not exist "%PY%" (
  echo O FluxoIA ainda nao foi instalado neste computador.
  echo Execute primeiro 1_INSTALAR_COMPLETO.bat
  pause
  exit /b 1
)
if not exist "%DIR%\fluxoia\app.py" (
  echo Nao foi encontrado: %DIR%\fluxoia\app.py
  pause
  exit /b 1
)
cd /d "%DIR%\fluxoia"
echo Abrindo FluxoIA na central de controle escura...
echo Acesse http://localhost:8501
"%PY%" -m streamlit run app.py --server.port 8501
pause
