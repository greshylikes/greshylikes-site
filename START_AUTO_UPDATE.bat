@echo off
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel% == 0 (
    py -3 scripts\watch_and_build.py
) else (
    python scripts\watch_and_build.py
)
pause
