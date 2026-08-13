@echo off
setlocal
chcp 65001>nul
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "$p=(Resolve-Path -LiteralPath '%~dp0install_emolpat.py').Path; Set-Clipboard -Value ('import runpy; runpy.run_path(r''' + $p + ''', run_name=''emolpat_felles'')[''main'']()')"
if errorlevel 1 (
  echo Installasjonskommandoen kunne ikke kopieres.
  pause
  exit /b 1
)
echo Installasjonskommandoen er kopiert.
echo Apne Python FELLES pa vanlig mate, lim inn med Ctrl+V og trykk Enter.
pause
