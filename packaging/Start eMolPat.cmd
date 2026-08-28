@echo off
setlocal
chcp 65001>nul
set "IVANTI=C:\Program Files (x86)\Ivanti\Workspace Control\pwrgate.exe"
if not exist "%IVANTI%" (
  echo Ivanti Workspace Control ble ikke funnet. Kontakt teknisk støtte.
  pause
  exit /b 1
)
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "$p=(Resolve-Path -LiteralPath '%~dp0suite\start_emolpat.py').Path; Set-Clipboard -Value ('import runpy; runpy.run_path(r''' + $p + ''', run_name=''emolpat_felles'')[''main'']()')"
if errorlevel 1 (
  echo Startkommandoen kunne ikke kopieres.
  pause
  exit /b 1
)
start "" "%IVANTI%" 15694
echo Python FELLES apnes. Lim inn kommandoen med Ctrl+V og trykk Enter.
pause
