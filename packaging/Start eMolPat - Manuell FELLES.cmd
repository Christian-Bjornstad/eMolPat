@echo off
setlocal
chcp 65001>nul
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "$p=(Resolve-Path -LiteralPath '%~dp0diagnose_emolpat_start.py').Path; Set-Clipboard -Value ('import runpy; runpy.run_path(r''' + $p + ''', run_name=''emolpat_felles'')[''main'']()')"
if errorlevel 1 (
  echo Startkommandoen kunne ikke kopieres.
  pause
  exit /b 1
)
echo Startkommandoen er kopiert.
echo Apne Python FELLES pa vanlig mate, lim inn med Ctrl+V og trykk Enter.
echo Hvis portalen ikke apnes, blir hele den tekniske feilen vist i FELLES.
pause
