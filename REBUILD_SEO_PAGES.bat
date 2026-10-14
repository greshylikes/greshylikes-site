@echo off
cd /d "%~dp0"
py -3 scripts\rebuild_seo.py
if errorlevel 1 python scripts\rebuild_seo.py
pause
