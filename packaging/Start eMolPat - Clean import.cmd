@echo off
setlocal
chcp 65001>nul
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "$p=(Resolve-Path -LiteralPath '%~dp0diagnose_emolpat_start.py').Path; Set-Clipboard -Value ('import os, runpy; os.environ[''EMOLPAT_DIAGNOSTIC_CLEAN_IMPORT'']=''1''; runpy.run_path(r''' + $p + ''', run_name=''emolpat_felles'')[''main'']()')"
if errorlevel 1 (
  echo Clean-import-kommandoen kunne ikke kopieres.
  pause
  exit /b 1
)
echo Clean-import-kommandoen er kopiert.
echo Apne Python FELLES pa vanlig mate, lim inn med Ctrl+V og trykk Enter.
echo Kopier hele diagnoseteksten tilbake til Codex hvis portalen ikke apnes.
pause
