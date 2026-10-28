@echo off
chcp 65001 >nul
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0INSTALAR_COMPLETO.ps1"
echo.
if errorlevel 1 (
  echo Houve um problema. Copie a mensagem exibida e envie ao ChatGPT.
)
pause
